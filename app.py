import uvicorn
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyppeteer import launch

from config import URL_TO_OFFER, PATH_TO_PDF
from yandex_cloud_api import yandex_upload_file_s3

app = FastAPI()


class PDFRequest(BaseModel):
    calc_id: int
    user_login: str
    user_name: str
    user_email: str
    user_phone: str


async def generate_pdf_async(calc_id, data: PDFRequest):
    browser = await launch(
        executablePath="C:/Program Files/Google/Chrome/Application/chrome.exe"
    )
    page = await browser.newPage()

    # Формирование URL с параметрами
    full_url = f"{URL_TO_OFFER}/{calc_id}?user_login={data.user_login}&name={data.user_name}&email={data.user_email}&phone={data.user_phone}"
    # Переход на страницу с параметрами
    await page.goto(full_url, {"waitUntil": "networkidle2"})

    # Принудительно выполнить рендеринг всех шрифтов
    await page.evaluate(
        """() => {
            document.fonts.ready.then(() => console.log('Fonts loaded'));
        }"""
    )

    file_name = f"Коммерческое предложение (id_{calc_id}).pdf"
    output_pdf_path = os.path.join(PATH_TO_PDF, data.user_login, file_name)

    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

    await page.pdf({
        "path": output_pdf_path,
        "format": "A4",
        "printBackground": True,
    })

    await browser.close()

    yandex_upload_file_s3(output_pdf_path, file_name)

    return output_pdf_path


@app.post("/generate_pdf")
async def generate_pdf(request: PDFRequest):
    calc_id = request.calc_id

    if not calc_id or not request.user_login:
        raise HTTPException(status_code=400, detail="calc_id и user_login обязательны")

    # Запуск асинхронной задачи и ожидание ее завершения
    pdf_path = await generate_pdf_async(calc_id, request)

    return {"status": "Completed", "pdf_path": pdf_path}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

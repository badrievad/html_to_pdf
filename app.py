import asyncio
import base64
import os
import time

from concurrent.futures import ThreadPoolExecutor

from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import URL_TO_OFFER, PATH_TO_PDF

app = Flask(__name__)

executor = ThreadPoolExecutor(max_workers=4)


def generate_pdf_task(calc_id, output_pdf_path):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"{URL_TO_OFFER}/{calc_id}")

    time.sleep(3)

    result = driver.execute_cdp_cmd(
        "Page.printToPDF",
        {
            "printBackground": True,
            "preferCSSPageSize": True,
            "marginTop": 0,
            "marginBottom": 0,
            "marginLeft": 0,
            "marginRight": 0,
        },
    )

    with open(output_pdf_path, "wb") as file:
        file.write(base64.b64decode(result["data"]))

    driver.quit()
    return output_pdf_path


async def generate_pdf_async(calc_id, user_login):
    loop = asyncio.get_event_loop()

    output_dir = os.path.join(PATH_TO_PDF, user_login)
    os.makedirs(output_dir, exist_ok=True)  # Создает каталог, если его нет

    output_pdf_path = fr"{PATH_TO_PDF}\{user_login}\Коммерческое предложение (id_{calc_id}).pdf"

    start = time.time()
    result = await loop.run_in_executor(
        executor, generate_pdf_task, calc_id, output_pdf_path
    )
    print(f"PDF generated for {user_login} in {time.time() - start:.2f} seconds")
    return result


@app.route("/generate_pdf", methods=["POST"])
async def generate_pdf():
    data = request.json
    calc_id = data.get("calc_id")
    user_login = data.get("user_login")

    if not calc_id or not user_login:
        return jsonify({"status": "error", "message": "calc_id и user_login обязательны"}), 400

    task = asyncio.create_task(generate_pdf_async(calc_id, user_login))
    pdf_path = await task
    return jsonify({"status": "Completed", "pdf_path": pdf_path})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)

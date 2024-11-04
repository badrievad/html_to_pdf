from pydantic import BaseModel


class PDFRequest(BaseModel):
    calc_id: int
    user_login: str
    user_name: str
    user_email: str
    user_phone: str
    user_telegram: str
    include_rate: str

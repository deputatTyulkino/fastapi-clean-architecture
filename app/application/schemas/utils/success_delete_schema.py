from pydantic import BaseModel


class SuccessDeleteSchema(BaseModel):
    detail: str

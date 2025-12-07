from pydantic import BaseModel, HttpUrl


class UrlSchema(BaseModel):
    url: HttpUrl
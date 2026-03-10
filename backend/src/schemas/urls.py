from pydantic import BaseModel, HttpUrl


class UrlSchema(BaseModel):
    url: HttpUrl

    class Config:
        json_schema_extra = {
            "example" : {
                "url": "https://example.com/very/long/url"
            }
        }

        
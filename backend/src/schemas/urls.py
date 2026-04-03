from pydantic import BaseModel, HttpUrl


class UrlSchema(BaseModel):
    url: HttpUrl

    @property
    def original_url(self) -> str:
        return str(self.url)

    class Config:
        json_schema_extra = {
            "example" : {
                "url": "https://example.com/very/long/url"
            }
        }

        
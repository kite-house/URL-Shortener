from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Url
from src.db import crud

def normalize_url(url: str) -> str:
    return url.rstrip('/')

def assert_urls_equal(url1: str, url2: str):
    assert normalize_url(url1) == normalize_url(url2)

async def create_test_url(
    session: AsyncSession, 
    url: str, 
    custom_slug: Optional[str] = None
) -> str:
    slug = custom_slug if custom_slug else "test" + str(hash(url))[:5]
    await crud.write_url(slug, url, session)
    return slug

async def create_multiple_test_urls(
    session: AsyncSession, 
    urls_data: List[Dict[str, Any]]
) -> List[Url]:
    created_urls = []
    for data in urls_data:
        slug = data.get("slug") or await create_test_url(session, data["long_url"])
        if "count_clicks" in data and data["count_clicks"] > 0:
            for _ in range(data["count_clicks"]):
                await crud.increase_count_clicks(slug, session)
        
        url = await crud.get_url(slug=slug, session=session)
        created_urls.append(url)
    
    return created_urls

def create_url_instance(
    slug: str, 
    long_url: str, 
    count_clicks: int = 0,
    date_created: Optional[datetime] = None
) -> Url:
    return Url(
        slug=slug,
        long_url=long_url,
        count_clicks=count_clicks,
        date_created=date_created or datetime.now()
    )

def assert_url_equals(expected: Url, actual: Url):
    assert expected.slug == actual.slug
    assert expected.long_url == actual.long_url
    assert expected.count_clicks == actual.count_clicks
    assert expected.date_created.date() == actual.date_created.date()
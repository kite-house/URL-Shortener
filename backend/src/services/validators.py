from src.core.config import Settings

class SlugValidator:
    """Сервис для валидации слагов"""
    
    FORBIDDEN_CHARS = {'/', '?', '@', '#', '&', '=', '%', '+', ' '}
    
    @classmethod
    def validate_characters(cls, slug: str) -> None:
        """Валидация запрещенных символов"""
        for char in slug:
            if char in cls.FORBIDDEN_CHARS:
                raise ValueError(f"Forbidden character: '{char}'")
    
    @classmethod
    def validate_length(cls, slug: str, settings: Settings) -> None:
        """Валидация длины слага"""
        if not (settings.SLUG_MIN_LENGTH <= len(slug) <= settings.SLUG_MAX_LENGTH):
            raise ValueError(
                f"Slug length must be between {settings.SLUG_MIN_LENGTH} and {settings.SLUG_MAX_LENGTH}"
            )
    
    @classmethod
    def validate_system_routes(cls, slug: str, existing_routes: set[str]) -> None:
        """Проверка конфликта с системными маршрутами"""
        routes_without_slash = {route.lstrip('/') for route in existing_routes}
        if slug in routes_without_slash:
            raise ValueError(f"Slug '{slug}' is reserved by the system")

import pytest
from src.services.validators import SlugValidator
from src.core.config import Settings

class TestSlugValidator:
    
    def setup_method(self):
        self.settings = Settings()
        self.settings.SLUG_MIN_LENGTH = 3
        self.settings.SLUG_MAX_LENGTH = 10
    
    def test_validate_characters_valid(self):
        for slug in ["abc", "abc123", "ABC", "a1b2c3"]:
            SlugValidator.validate_characters(slug)
    
    def test_validate_characters_invalid(self):
        for slug in ["abc/", "?abc", "abc#", "abc space", "abc@"]:
            with pytest.raises(ValueError, match="Forbidden character"):
                SlugValidator.validate_characters(slug)
    
    def test_validate_length_valid(self):
        for slug in ["abc", "abcd", "abcdefghij"]:
            SlugValidator.validate_length(slug, self.settings)
    
    def test_validate_length_too_short(self):
        with pytest.raises(ValueError, match="between 3 and 10"):
            SlugValidator.validate_length("ab", self.settings)
    
    def test_validate_length_too_long(self):
        with pytest.raises(ValueError, match="between 3 and 10"):
            SlugValidator.validate_length("abcdefghijk", self.settings)
    
    def test_validate_system_routes(self):
        system_routes = {"/api", "/docs", "/openapi.json"}
        conflicting_slugs = ["api", "docs"]
        
        for slug in conflicting_slugs:
            with pytest.raises(ValueError, match="reserved"):
                SlugValidator.validate_system_routes(slug, system_routes)
    
    def test_validate_system_routes_valid(self):
        system_routes = {"/api", "/docs"}
        SlugValidator.validate_system_routes("custom", system_routes)
        SlugValidator.validate_system_routes("abc123", system_routes)
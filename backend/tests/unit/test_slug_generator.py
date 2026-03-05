import pytest
from unittest.mock import AsyncMock, Mock, patch, ANY
import random
import string
from sqlalchemy.exc import NoResultFound
from typing import Annotated
from fastapi import Depends

from src.services.slug_generator import create_url, ValidOutputUrl
from src.core.config import settings

@pytest.mark.unit
class TestSlugGenerator:
    
    def test_settings_import(self):
        assert hasattr(settings, 'RANDOM_SLUG_LENGTH')
        assert isinstance(settings.RANDOM_SLUG_LENGTH, int)
    
    @pytest.mark.asyncio
    async def test_create_url_default_length(self):
        mock_session = AsyncMock()
        
        original_length = settings.RANDOM_SLUG_LENGTH
        
        try:
            with patch.object(settings, 'RANDOM_SLUG_LENGTH', 7), \
                 patch('src.services.slug_generator.get_url') as mock_get_url, \
                 patch('random.choices') as mock_choices:
                
                mock_get_url.side_effect = NoResultFound()
                mock_choices.return_value = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
                
                slug = await create_url(mock_session)
                
                assert len(slug) == 7
                assert slug == 'abcdefg'
                mock_choices.assert_called_once_with(
                    string.ascii_letters + string.digits, 
                    k=7
                )
                mock_get_url.assert_called_once_with(slug='abcdefg', session=mock_session)
        finally:
            pass
    
    @pytest.mark.asyncio
    async def test_create_url_custom_length(self):
        mock_session = AsyncMock()
        
        with patch('src.services.slug_generator.get_url') as mock_get_url, \
             patch('random.choices') as mock_choices:
            
            mock_get_url.side_effect = NoResultFound()
            mock_choices.return_value = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
            
            length = 8
            slug = await create_url(mock_session, length)
            
            assert len(slug) == length
            assert slug == 'abcdefgh'
            mock_choices.assert_called_once_with(
                string.ascii_letters + string.digits, 
                k=length
            )
            mock_get_url.assert_called_once_with(slug='abcdefgh', session=mock_session)
    
    @pytest.mark.asyncio
    async def test_create_url_no_collision(self):
        mock_session = AsyncMock()
        
        with patch('src.services.slug_generator.get_url') as mock_get_url, \
             patch.object(settings, 'RANDOM_SLUG_LENGTH', 6), \
             patch('random.choices', return_value=['a', 'b', 'c', 'd', 'e', 'f']):
            
            mock_get_url.side_effect = NoResultFound()
            
            slug = await create_url(mock_session)
            
            assert slug == 'abcdef'
            mock_get_url.assert_called_once_with(slug='abcdef', session=mock_session)
    
    @pytest.mark.asyncio
    async def test_create_url_with_collision(self):
        mock_session = AsyncMock()
        
        mock_url = Mock()
        mock_url.slug = "abcdef"
        
        mock_get_url = AsyncMock(side_effect=[
            mock_url,  
            NoResultFound() 
        ])
        
        with patch('src.services.slug_generator.get_url', mock_get_url), \
             patch.object(settings, 'RANDOM_SLUG_LENGTH', 6), \
             patch('random.choices', side_effect=[
                 ['a', 'b', 'c', 'd', 'e', 'f'],  
                 ['g', 'h', 'i', 'j', 'k', 'l']   
             ]):
            
            slug = await create_url(mock_session)
            
            assert slug == 'ghijkl'
            assert mock_get_url.call_count == 2
            mock_get_url.assert_any_call(slug='abcdef', session=mock_session)
            mock_get_url.assert_any_call(slug='ghijkl', session=mock_session)
    
    @pytest.mark.asyncio
    async def test_create_url_multiple_collisions(self):
        mock_session = AsyncMock()
        
        mock_url = Mock()
        mock_url.slug = "collision"
        
        mock_get_url = AsyncMock(side_effect=[
            mock_url,   
            mock_url,   
            mock_url,  
            NoResultFound() 
        ])
        
        mock_choices_values = [
            ['a1', 'a2', 'a3', 'a4', 'a5', 'a6'],
            ['b1', 'b2', 'b3', 'b4', 'b5', 'b6'],
            ['c1', 'c2', 'c3', 'c4', 'c5', 'c6'],
            ['d1', 'd2', 'd3', 'd4', 'd5', 'd6']
        ]
        
        with patch('src.services.slug_generator.get_url', mock_get_url), \
             patch.object(settings, 'RANDOM_SLUG_LENGTH', 6), \
             patch('random.choices', side_effect=mock_choices_values):
            
            slug = await create_url(mock_session)
            
            assert slug == 'd1d2d3d4d5d6'
            assert mock_get_url.call_count == 4
    
    def test_valid_output_url_decorator(self):
        @ValidOutputUrl
        async def test_func(session, length=None):
            return "test_slug"
        
        assert test_func.__name__ == 'wrapper'

        import inspect
        closure_vars = inspect.getclosurevars(test_func)
        assert 'func' in closure_vars.nonlocals or 'func' in closure_vars.globals
    
    @pytest.mark.asyncio
    async def test_url_generation_charset(self):
        mock_session = AsyncMock()
        
        with patch('src.services.slug_generator.get_url') as mock_get_url, \
             patch.object(settings, 'RANDOM_SLUG_LENGTH', 10), \
             patch('random.choices') as mock_choices:
            
            mock_get_url.side_effect = NoResultFound()
            mock_choices.return_value = ['x'] * 10
            
            await create_url(mock_session)
            
            call_args = mock_choices.call_args[0]
            assert call_args[0] == string.ascii_letters + string.digits
            assert mock_choices.call_args[1]['k'] == 10
    
    @pytest.mark.asyncio
    async def test_decorator_recursion_on_collision(self):
        mock_session = AsyncMock()
        
        mock_inner = AsyncMock()
        mock_inner.side_effect = ["slug1", "slug2", "slug3"]
        
        decorated = ValidOutputUrl(mock_inner)
        
        with patch('src.services.slug_generator.get_url') as mock_get_url:
            mock_get_url.side_effect = [
                Mock(),
                Mock(), 
                NoResultFound() 
            ]
            
            result = await decorated(mock_session)
            
            assert result == "slug3"
            assert mock_inner.call_count == 3
            assert mock_get_url.call_count == 3
    
    @pytest.mark.asyncio
    async def test_create_url_passes_session_correctly(self):
        mock_session = AsyncMock()
        
        with patch('src.services.slug_generator.get_url') as mock_get_url, \
             patch.object(settings, 'RANDOM_SLUG_LENGTH', 6), \
             patch('random.choices', return_value=['x'] * 6):
            
            mock_get_url.side_effect = NoResultFound()
            
            await create_url(mock_session)
            mock_get_url.assert_called_once_with(slug='xxxxxx', session=mock_session)
    
    @pytest.mark.asyncio
    async def test_create_url_handles_none_length(self):
        mock_session = AsyncMock()
        
        with patch('src.services.slug_generator.get_url') as mock_get_url, \
             patch.object(settings, 'RANDOM_SLUG_LENGTH', 5), \
             patch('random.choices') as mock_choices:
            
            mock_get_url.side_effect = NoResultFound()
            mock_choices.return_value = ['a', 'b', 'c', 'd', 'e']
            
            await create_url(mock_session, None)
            
            mock_choices.assert_called_once_with(string.ascii_letters + string.digits, k=5)


# Интеграционные тесты
@pytest.mark.integration
class TestSlugGeneratorIntegration:
    @pytest.mark.asyncio
    async def test_create_url_with_real_settings(self):
        mock_session = AsyncMock()
        
        with patch('src.services.slug_generator.get_url') as mock_get_url, \
             patch('random.choices') as mock_choices:
            
            mock_get_url.side_effect = NoResultFound()
            mock_choices.return_value = ['x'] * settings.RANDOM_SLUG_LENGTH
            
            slug = await create_url(mock_session)
            
            assert len(slug) == settings.RANDOM_SLUG_LENGTH
            mock_choices.assert_called_once_with(
                string.ascii_letters + string.digits, 
                k=settings.RANDOM_SLUG_LENGTH
            )
    
    @pytest.mark.asyncio
    async def test_create_url_randomness(self):
        mock_session = AsyncMock()
        
        with patch('src.services.slug_generator.get_url') as mock_get_url:
            mock_get_url.side_effect = NoResultFound()
            
            slug1 = await create_url(mock_session, length=10)
            slug2 = await create_url(mock_session, length=10)
            
            assert slug1 != slug2
    
    @pytest.mark.asyncio
    async def test_create_url_with_different_lengths(self):
        mock_session = AsyncMock()
        
        with patch('src.services.slug_generator.get_url') as mock_get_url:
            mock_get_url.side_effect = NoResultFound()
            
            lengths = [3, 5, 7, 10]
            for length in lengths:
                slug = await create_url(mock_session, length)
                assert len(slug) == length
                assert all(c in string.ascii_letters + string.digits for c in slug)
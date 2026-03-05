// api.js - Модуль для работы с API
const API = (function() {
    // Конфигурация API
    const API_CONFIG = {
        baseURL: 'http://localhost:8000/api',  // для разработки
        // baseURL: '/api',  // для продакшна (через nginx)
        endpoints: {
            shorten: '/shorten',
            info: '/info',
            top: "/top"
        }
    };

    // Вспомогательная функция для обработки ответов
    async function handleResponse(response) {
        const data = await response.json();
        
        if (!response.ok && response.status !== 208) {
            throw new Error(data.message || 'Ошибка запроса');
        }
        
        return {
            status: response.status,
            data: data,
            success: data.success || false
        };
    }

    // Отправка запроса на сокращение ссылки с дополнительными параметрами
    async function shortenUrl(url, customSlug = null, length = null) {
        try {
            // Формируем URL с query параметрами
            let urlString = `${API_CONFIG.baseURL}${API_CONFIG.endpoints.shorten}`;
            
            // Создаем объект URLSearchParams для правильного формирования query строки
            const params = new URLSearchParams();
            
            // Добавляем параметр length если он есть
            if (length !== null && length !== undefined) {
                const lengthNum = parseInt(length);
                if (!isNaN(lengthNum) && lengthNum >= 3 && lengthNum <= 10) {
                    params.append('length', lengthNum);
                    console.log('✅ Добавлен параметр length:', lengthNum);
                }
            }
            
            // Добавляем параметр custom_slug если он есть
            if (customSlug && customSlug.trim() !== '') {
                const slug = customSlug.trim();
                // Проверяем валидность custom_slug
                if (/^[a-zA-Z0-9_-]{3,}$/.test(slug)) {
                    params.append('custom_slug', slug);
                    console.log('✅ Добавлен параметр custom_slug:', slug);
                } else {
                    console.warn('❌ Некорректный custom_slug:', slug);
                }
            }
            
            // Добавляем параметры к URL если они есть
            if (params.toString()) {
                urlString += `?${params.toString()}`;
                console.log('📤 Полный URL запроса:', urlString);
            } else {
                console.log('📤 Запрос без параметров:', urlString);
            }
            
            const response = await fetch(urlString, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({url: url})
            });
            
            console.log('📥 Статус ответа:', response.status);
            console.log('🔗 Полный URL:', response.url);
            
            const result = await handleResponse(response);
            console.log('📥 Данные ответа:', result);
            
            return result;
        } catch (error) {
            console.error('❌ API Error (shortenUrl):', error);
            throw error;
        }
    }

    // Получение статистики по ссылке
    async function getLinkStats(slug) {
        try {
            const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.info}/${slug}`);
            return await handleResponse(response);
        } catch (error) {
            console.error('API Error (getLinkStats):', error);
            throw error;
        }
    }

    // Получение топа ссылок
    async function getTopLinks(quantity = 10) {
        try {
            const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.top}?quantity=${quantity}`);
            return await handleResponse(response);
        } catch (error) {
            console.error('API Error (getTopLinks):', error);
            throw error;
        }
    }

    // Публичное API
    return {
        shortenUrl,
        getLinkStats,
        getTopLinks
    };
})();
// ui.js - Модуль для работы с API
const API = (function() {
    const API_CONFIG = {
        baseURL: 'http://localhost:8000/api',
        endpoints: {
            shorten: '/shorten',
            info: '/info',
            top: "/top",
            config: {
                slugLength: '/config/slug-length',
                frontend: '/config/frontend'
            }
        }
    };

    // Флаг для режима продакшн
    let isProdMode = false;

    // Функция для условного логирования
    function logIfDev(...args) {
        if (!isProdMode) {
            console.log(...args);
        }
    }

    function errorLogIfDev(...args) {
        if (!isProdMode) {
            console.error(...args);
        }
    }

    function warnLogIfDev(...args) {
        if (!isProdMode) {
            console.warn(...args);
        }
    }

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

    async function getFrontendConfig() {
        try {
            logIfDev('📡 Запрос к /api/config/frontend');
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000);
            
            const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.config.frontend}`, {
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Устанавливаем режим продакшн если нужно
            if (data.mode === 'PROD') {
                isProdMode = true;
                logIfDev('🔒 Продакшн режим: логирование отключено');
            }
            
            logIfDev('📦 Получены данные:', data);
            return data;
        } catch (error) {
            errorLogIfDev('❌ Ошибка загрузки конфигурации:', error);
            return null;
        }
    }

    async function shortenUrl(url, customSlug = null, length = null) {
        try {
            let urlString = `${API_CONFIG.baseURL}${API_CONFIG.endpoints.shorten}`;
            
            const params = new URLSearchParams();
            
            if (length !== null && length !== undefined) {
                const lengthNum = parseInt(length);
                if (!isNaN(lengthNum) && lengthNum >= 3 && lengthNum <= 10) {
                    params.append('length', lengthNum);
                }
            }
            
            if (customSlug && customSlug.trim() !== '') {
                const slug = customSlug.trim();
                if (/^[a-zA-Z0-9_-]{3,}$/.test(slug)) {
                    params.append('custom_slug', slug);
                }
            }
            
            if (params.toString()) {
                urlString += `?${params.toString()}`;
            }
            
            const response = await fetch(urlString, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({url: url})
            });
            
            const result = await handleResponse(response);
            return result;
        } catch (error) {
            errorLogIfDev('API Error:', error);
            throw error;
        }
    }

    async function getLinkStats(slug) {
        try {
            const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.info}/${slug}`);
            return await handleResponse(response);
        } catch (error) {
            errorLogIfDev('API Error:', error);
            throw error;
        }
    }

    async function getTopLinks(quantity = 10) {
        try {
            const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.top}?quantity=${quantity}`);
            return await handleResponse(response);
        } catch (error) {
            errorLogIfDev('API Error:', error);
            throw error;
        }
    }

    async function getSlugLengthConfig() {
        try {
            const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.config.slugLength}`);
            const result = await handleResponse(response);
            return result;
        } catch (error) {
            errorLogIfDev('API Error:', error);
            return {
                success: false,
                data: {
                    slug_min_length: 3,
                    slug_max_length: 10
                }
            };
        }
    }

    // Функция для проверки режима (может пригодиться в UI)
    function isProduction() {
        return isProdMode;
    }

    return {
        shortenUrl,
        getLinkStats,
        getTopLinks,
        getSlugLengthConfig,
        getFrontendConfig,
        isProduction
    };
})();
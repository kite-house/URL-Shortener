const API = (function() {
    const API_CONFIG = {
        baseURL: 'http://${BACKEND_HOST}:${BACKEND_PORT}/api',
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

    let isProdMode = false;

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

    async function handleResponse(response) {
        // Проверяем статус ответа
        if (!response.ok) {
            let errorMessage = 'Ошибка запроса';
            
            try {
                const errorData = await response.json();
                console.log('🔍 Детали ошибки:', errorData);
                
                // Обработка ошибки валидации Pydantic
                if (Array.isArray(errorData)) {
                    // Это ошибка валидации Pydantic
                    const firstError = errorData[0];
                    if (firstError && firstError.msg) {
                        errorMessage = firstError.msg;
                        // Добавляем контекст если есть
                        if (firstError.ctx) {
                            if (firstError.ctx.expected_schemes) {
                                errorMessage = `URL должен начинаться с http:// или https://`;
                            }
                        }
                    } else {
                        errorMessage = 'Ошибка валидации URL';
                    }
                }
                // Обработка стандартной ошибки FastAPI
                else if (errorData.detail) {
                    if (typeof errorData.detail === 'string') {
                        errorMessage = errorData.detail;
                    } else if (Array.isArray(errorData.detail)) {
                        // Массив ошибок валидации
                        const firstError = errorData.detail[0];
                        if (firstError && firstError.msg) {
                            errorMessage = firstError.msg;
                            if (firstError.ctx && firstError.ctx.expected_schemes) {
                                errorMessage = `URL должен начинаться с http:// или https://`;
                            }
                        }
                    } else if (typeof errorData.detail === 'object') {
                        errorMessage = JSON.stringify(errorData.detail);
                    } else {
                        errorMessage = errorData.detail;
                    }
                } else if (errorData.message) {
                    errorMessage = errorData.message;
                }
            } catch (e) {
                // Если не удалось распарсить JSON
                errorMessage = `HTTP ошибка ${response.status}`;
            }
            
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        // Проверяем, нет ли ошибки в теле ответа
        if (data.status_code && data.status_code >= 400) {
            const errorMsg = data.detail || data.message || 'Ошибка сервера';
            throw new Error(errorMsg);
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
            
            logIfDev('📤 Отправка запроса:', { url: urlString, body: { url } });
            
            const response = await fetch(urlString, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });
            
            logIfDev('📥 Получен ответ:', { 
                status: response.status, 
                statusText: response.statusText,
                ok: response.ok 
            });
            
            const result = await handleResponse(response);
            logIfDev('✅ Успешный ответ:', result);
            return result;
            
        } catch (error) {
            errorLogIfDev('❌ API Error:', error);
            // Убеждаемся, что ошибка - это строка
            if (error instanceof Error) {
                throw error;
            } else {
                throw new Error(String(error));
            }
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

    return {
        shortenUrl,
        getLinkStats,
        getTopLinks,
        getSlugLengthConfig,
        getFrontendConfig,
        isProduction: () => isProdMode
    };
})();
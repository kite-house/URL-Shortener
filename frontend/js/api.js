// api.js - Модуль для работы с API
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
        const responseText = await response.text();
        
        let data;
        try {
            data = JSON.parse(responseText);
        } catch (e) {
            errorLogIfDev('❌ Не удалось распарсить JSON:', responseText);
            throw new Error(`Сервер вернул ошибку: ${responseText.substring(0, 200)}`);
        }
        
        if (response.status === 409) {
            logIfDev('📌 Существующая ссылка:', data);
            return {
                status: response.status,
                data: data,
                success: true,
                isExisting: true
            };
        }
        
        if (!response.ok) {
            let errorMessage = 'Ошибка запроса';
            
            if (response.status === 422) {
                if (data.detail) {
                    if (Array.isArray(data.detail)) {
                        const firstError = data.detail[0];
                        if (firstError && firstError.msg) {
                            errorMessage = firstError.msg;
                            if (firstError.ctx && firstError.ctx.expected_schemes) {
                                errorMessage = 'URL должен начинаться с http:// или https://';
                            }
                        } else {
                            errorMessage = 'Ошибка валидации URL';
                        }
                    } else if (typeof data.detail === 'string') {
                        errorMessage = data.detail;
                    } else if (typeof data.detail === 'object') {
                        errorMessage = JSON.stringify(data.detail);
                    }
                } else if (data.message) {
                    errorMessage = data.message;
                } else {
                    errorMessage = 'Некорректный URL. Убедитесь, что ссылка начинается с http:// или https://';
                }
            } else if (data.detail) {
                errorMessage = data.detail;
            } else if (data.message) {
                errorMessage = data.message;
            }
            
            throw new Error(errorMessage);
        }
        
        return {
            status: response.status,
            data: data,
            success: data.success || false,
            isExisting: false
        };
    }

    async function getFrontendConfig() {
        try {
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
            }
            
            return data;
        } catch (error) {
            errorLogIfDev('❌ Ошибка загрузки конфигурации:', error);
            return null;
        }
    }

    async function shortenUrl(url, customSlug = null, length = null, ttlDays = null) {
        try {
            let urlString = `${API_CONFIG.baseURL}${API_CONFIG.endpoints.shorten}`;
            
            const params = new URLSearchParams();
            
            if (length !== null && length !== undefined && length !== 6) {
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
            
            if (ttlDays !== null && ttlDays !== undefined && ttlDays !== '') {
                const ttl = parseInt(ttlDays);
                if (!isNaN(ttl) && ttl >= 1 && ttl <= 365) {
                    params.append('ttl_days', ttl);
                }
            }
            
            if (params.toString()) {
                urlString += `?${params.toString()}`;
            }
            
            logIfDev('📤 Отправка запроса:', { url: urlString, body: { url: url } });
            
            const response = await fetch(urlString, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });
            
            const result = await handleResponse(response);
            
            if (result.isExisting || result.status === 409) {
                return {
                    success: true,
                    status: 409,
                    isNew: false,
                    data: result.data.data,
                    message: result.data.message || 'Ссылка уже существует!'
                };
            }
            
            if (result.status === 201) {
                return {
                    success: true,
                    status: 201,
                    isNew: true,
                    data: result.data.data,
                    message: result.data.message || 'Ссылка успешно сокращена!'
                };
            }
            
            return result;
            
        } catch (error) {
            errorLogIfDev('❌ API Error:', error);
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

    return {
        shortenUrl,
        getLinkStats,
        getTopLinks,
        getSlugLengthConfig,
        getFrontendConfig,
        isProduction: () => isProdMode
    };
})();
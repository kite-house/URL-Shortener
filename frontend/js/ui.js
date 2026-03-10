// ui.js - Модуль для работы с интерфейсом
const UI = (function() {
    // Состояние приложения
    const state = {
        currentSlug: null,
        isLoading: false,
        advancedOpen: false,
        appConfig: {
            app_name: "URL-Shortener",
            version: "1.0.0",
            mode: "DEV",
            example_url: "https://example.com/very/long/url",
            api_base_url: "http://localhost:8000/api"
        },
        slugLengthConfig: {
            min: 3,
            max: 10,
            default: 6
        },
        isProdMode: false
    };

    // DOM элементы
    const elements = {};

    // Функции для условного логирования
    function logIfDev(...args) {
        if (!state.isProdMode) {
            console.log(...args);
        }
    }

    function errorLogIfDev(...args) {
        if (!state.isProdMode) {
            console.error(...args);
        }
    }

    function warnLogIfDev(...args) {
        if (!state.isProdMode) {
            console.warn(...args);
        }
    }

    // Функция для инициализации элементов
    function initElements() {
        elements.form = document.getElementById('shortenForm');
        elements.urlInput = document.getElementById('urlInput');
        elements.shortenBtn = document.getElementById('shortenBtn');
        elements.resultCard = document.getElementById('resultCard');
        elements.closeResultBtn = document.getElementById('closeResultBtn');
        elements.shortUrl = document.getElementById('shortUrl');
        elements.originalUrl = document.getElementById('originalUrl');
        elements.themeToggle = document.querySelector('.theme-toggle');
        elements.toastContainer = document.getElementById('toastContainer');
        
        // Элементы дополнительных настроек
        elements.customSlug = document.getElementById('customSlug');
        elements.slugLength = document.getElementById('slugLength');
        elements.lengthValue = document.getElementById('lengthValue');
        elements.toggleAdvancedBtn = document.getElementById('toggleAdvancedBtn');
        elements.advancedSettings = document.getElementById('advancedSettings');
        elements.sliderMarkers = document.querySelector('.slider-markers');
        
        // Элементы для отображения статуса полей
        elements.slugLengthContainer = document.querySelector('.setting-item:has(#slugLength)');
        elements.customSlugContainer = document.querySelector('.setting-item:has(#customSlug)');
        
        // Элементы для динамических данных
        elements.footerParagraph = document.querySelector('.footer p');
        elements.logoText = document.querySelector('.logo-text');
        elements.pageTitle = document.querySelector('title');
    }

    // Обновление APP_NAME в интерфейсе
    function updateAppNameInUI(appName) {
        logIfDev(`🔄 Обновляем APP_NAME на: ${appName}`);
        
        // Обновляем title страницы
        if (elements.pageTitle) {
            elements.pageTitle.textContent = `${appName} | Сервис сокращения ссылок`;
        }
        
        // Обновляем логотип
        if (elements.logoText) {
            elements.logoText.innerHTML = appName;
        }
        
        // Обновляем футер
        if (elements.footerParagraph) {
            const currentYear = new Date().getFullYear();
            elements.footerParagraph.innerHTML = `© ${currentYear} ${appName}. Все права защищены.`;
        }
    }

    // Обновление placeholder'а
    function updatePlaceholder(exampleUrl) {
        if (elements.urlInput) {
            elements.urlInput.placeholder = exampleUrl;
        }
    }

    // Загрузка конфигурации с бэкенда
    async function loadFrontendConfig() {
        try {
            logIfDev('🔄 Загрузка конфигурации с бэкенда...');
            
            const config = await API.getFrontendConfig();
            
            if (config && config.app_name) {
                // Устанавливаем режим продакшн
                if (config.mode === 'PROD') {
                    state.isProdMode = true;
                    // В продакшне очищаем консоль от предыдущих логов
                    if (console.clear) {
                        console.clear();
                    }
                    logIfDev('🔒 Продакшн режим: логирование отключено');
                }
                
                logIfDev('✅ Конфигурация получена:', config);
                
                // Обновляем состояние
                state.appConfig = { ...state.appConfig, ...config };
                
                // Обновляем интерфейс
                updateAppNameInUI(config.app_name);
                updatePlaceholder(config.example_url || state.appConfig.example_url);
            } else {
                warnLogIfDev('⚠️ Конфигурация не получена, используем значения по умолчанию');
                updateAppNameInUI(state.appConfig.app_name);
                updatePlaceholder(state.appConfig.example_url);
            }
        } catch (error) {
            errorLogIfDev('❌ Ошибка загрузки конфигурации:', error);
            updateAppNameInUI(state.appConfig.app_name);
            updatePlaceholder(state.appConfig.example_url);
        }
    }

    // Загрузка конфигурации длины слага
    async function loadSlugLengthConfig() {
        try {
            const result = await API.getSlugLengthConfig();
            
            if (result.data) {
                state.slugLengthConfig = {
                    min: result.data.slug_min_length || 3,
                    max: result.data.slug_max_length || 10,
                    default: Math.floor((result.data.slug_min_length + result.data.slug_max_length) / 2) || 6
                };
                
                updateSliderConfig();
            }
        } catch (error) {
            warnLogIfDev('⚠️ Не удалось загрузить настройки длины');
        }
    }

    // Обновление конфигурации слайдера
    function updateSliderConfig() {
        if (!elements.slugLength) return;
        
        const { min, max, default: defaultValue } = state.slugLengthConfig;
        
        elements.slugLength.min = min;
        elements.slugLength.max = max;
        elements.slugLength.value = Math.min(Math.max(defaultValue, min), max);
        
        updateLengthDisplay();
        
        if (elements.sliderMarkers) {
            elements.sliderMarkers.innerHTML = `
                <span>${min}</span>
                <span>${Math.floor((min + max) / 2)}</span>
                <span>${max}</span>
            `;
        }
    }

    // Функция для показа подсказки у поля
    function showFieldHint(container, message, type = 'warning') {
        if (!container) return;
        
        hideFieldHint(container);
        
        const hint = document.createElement('div');
        hint.className = `field-hint field-hint-${type}`;
        hint.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        `;
        container.appendChild(hint);
    }

    function hideFieldHint(container) {
        if (!container) return;
        const oldHint = container.querySelector('.field-hint');
        if (oldHint) {
            oldHint.remove();
        }
    }

    function toggleFieldsState() {
        if (!elements.customSlug || !elements.slugLength) return;
        
        const customSlugValue = elements.customSlug.value.trim();
        const isCustomSlugFilled = customSlugValue !== '';
        
        elements.slugLength.disabled = isCustomSlugFilled;
        
        if (isCustomSlugFilled) {
            elements.slugLength.classList.add('disabled');
            elements.lengthValue.classList.add('disabled');
            elements.slugLengthContainer?.classList.add('field-disabled');
            showFieldHint(elements.slugLengthContainer, 'Недоступно при использовании своего варианта', 'warning');
        } else {
            elements.slugLength.classList.remove('disabled');
            elements.lengthValue.classList.remove('disabled');
            elements.slugLengthContainer?.classList.remove('field-disabled');
            hideFieldHint(elements.slugLengthContainer);
        }
    }

    function validateCustomSlug() {
        const slug = elements.customSlug.value;
        const { min, max } = state.slugLengthConfig;
        const pattern = /^[a-zA-Z0-9_-]*$/;
        
        hideFieldHint(elements.customSlugContainer);
        
        if (slug && !pattern.test(slug)) {
            elements.customSlug.setCustomValidity('Только латинские буквы, цифры, дефис и подчеркивание');
            elements.customSlug.classList.add('invalid');
            showFieldHint(elements.customSlugContainer, 'Только латинские буквы, цифры, дефис и подчеркивание', 'error');
        } else if (slug && slug.length < min) {
            elements.customSlug.setCustomValidity(`Минимум ${min} символа(ов)`);
            elements.customSlug.classList.add('invalid');
            showFieldHint(elements.customSlugContainer, `Минимальная длина: ${min} символа(ов)`, 'error');
        } else if (slug && slug.length > max) {
            elements.customSlug.setCustomValidity(`Максимум ${max} символов`);
            elements.customSlug.classList.add('invalid');
            showFieldHint(elements.customSlugContainer, `Максимальная длина: ${max} символов`, 'error');
        } else {
            elements.customSlug.setCustomValidity('');
            elements.customSlug.classList.remove('invalid');
            
            if (slug) {
                showFieldHint(elements.customSlugContainer, '✓ Корректный формат', 'success');
            }
        }
    }

    function handleCustomSlugChange() {
        validateCustomSlug();
        toggleFieldsState();
    }

    function closeResult() {
        if (!elements.resultCard) return;
        
        elements.resultCard.classList.add('hiding');
        
        setTimeout(() => {
            elements.resultCard.style.display = 'none';
            elements.resultCard.classList.remove('hiding');
            state.currentSlug = null;
        }, 300);
    }

    async function init() {
        // Только один лог при инициализации, который будет виден в DEV режиме
        logIfDev('🚀 Инициализация UI...');
        
        initElements();
        initTheme();
        
        // Сначала устанавливаем значения по умолчанию
        updateAppNameInUI(state.appConfig.app_name);
        updatePlaceholder(state.appConfig.example_url);
        
        // Затем пытаемся загрузить конфигурацию с бэкенда
        await loadFrontendConfig();
        await loadSlugLengthConfig();
        
        setupEventListeners();
        
        if (elements.customSlug) {
            toggleFieldsState();
        }
        
        // Финальный лог только в DEV
        if (!state.isProdMode) {
            logIfDev('✅ Инициализация завершена в режиме', state.appConfig.mode);
        }
    }

    function setupEventListeners() {
        if (elements.form) {
            elements.form.addEventListener('submit', handleFormSubmit);
        }
        
        if (elements.themeToggle) {
            elements.themeToggle.addEventListener('click', toggleTheme);
        }
        
        if (elements.slugLength) {
            elements.slugLength.addEventListener('input', updateLengthDisplay);
        }
        
        if (elements.customSlug) {
            elements.customSlug.addEventListener('input', handleCustomSlugChange);
        }
        
        if (elements.toggleAdvancedBtn) {
            elements.toggleAdvancedBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                toggleAdvancedSettings();
            });
        }
        
        if (elements.closeResultBtn) {
            elements.closeResultBtn.addEventListener('click', closeResult);
        }
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && elements.resultCard.style.display === 'block') {
                closeResult();
            }
        });
    }

    function toggleAdvancedSettings() {
        if (!elements.advancedSettings) return;
        
        state.advancedOpen = !state.advancedOpen;
        
        if (state.advancedOpen) {
            elements.advancedSettings.style.display = 'block';
            elements.toggleAdvancedBtn.classList.add('active');
            elements.toggleAdvancedBtn.querySelector('i').style.transform = 'rotate(90deg)';
            toggleFieldsState();
        } else {
            elements.advancedSettings.style.display = 'none';
            elements.toggleAdvancedBtn.classList.remove('active');
            elements.toggleAdvancedBtn.querySelector('i').style.transform = 'rotate(0deg)';
            resetAdvancedFields();
        }
    }

    function resetAdvancedFields() {
        if (elements.customSlug) {
            elements.customSlug.value = '';
            elements.customSlug.classList.remove('invalid');
            hideFieldHint(elements.customSlugContainer);
        }
        if (elements.slugLength) {
            const { min, max, default: defaultValue } = state.slugLengthConfig;
            elements.slugLength.value = Math.min(Math.max(defaultValue, min), max);
            elements.slugLength.disabled = false;
            elements.slugLength.classList.remove('disabled');
            elements.lengthValue.classList.remove('disabled');
            elements.slugLengthContainer?.classList.remove('field-disabled');
            hideFieldHint(elements.slugLengthContainer);
            updateLengthDisplay();
        }
    }

    function updateLengthDisplay() {
        if (elements.lengthValue && elements.slugLength) {
            elements.lengthValue.textContent = elements.slugLength.value;
        }
    }

    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const url = elements.urlInput.value.trim();
        if (!url) return;
        
        try {
            new URL(url);
        } catch {
            showToast('Пожалуйста, введите корректный URL', 'error');
            return;
        }
        
        let customSlug = elements.customSlug ? elements.customSlug.value.trim() : null;
        let length = elements.slugLength ? parseInt(elements.slugLength.value) : null;
        
        if (customSlug) {
            const { min, max } = state.slugLengthConfig;
            const pattern = /^[a-zA-Z0-9_-]+$/;
            
            if (!pattern.test(customSlug)) {
                showToast('Кастомная ссылка содержит недопустимые символы', 'error');
                return;
            }
            
            if (customSlug.length < min) {
                showToast(`Кастомная ссылка должна быть не короче ${min} символов`, 'error');
                return;
            }
            
            if (customSlug.length > max) {
                showToast(`Кастомная ссылка должна быть не длиннее ${max} символов`, 'error');
                return;
            }
            
            length = null;
        } else {
            if (length !== null) {
                const { min, max } = state.slugLengthConfig;
                if (isNaN(length) || length < min || length > max) {
                    length = state.slugLengthConfig.default;
                }
            }
        }
        
        setLoading(true);
        
        try {
            const result = await API.shortenUrl(url, customSlug, length);
            
            if (result.status === 201) {
                handleSuccessResponse(result.data.data, url, 'Ссылка успешно сокращена!');
            } else if (result.status === 208) {
                handleSuccessResponse(result.data.data, url, 'Ссылка уже существует!');
            } else {
                throw new Error(result.data.message || 'Ошибка при сокращении ссылки');
            }
            
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            setLoading(false);
        }
    }

    function handleSuccessResponse(responseData, originalUrl, message) {
        let displayUrl = responseData.short_url;
        if (displayUrl.includes('localhost')) {
            displayUrl = displayUrl.replace('localhost', window.location.hostname);
        }
        
        elements.shortUrl.value = displayUrl;
        elements.originalUrl.querySelector('span').textContent = responseData.long_url || originalUrl;
        elements.resultCard.style.display = 'block';
        
        state.currentSlug = responseData.slug;
        
        showToast(message, 'success');
        
        elements.urlInput.value = '';
        if (elements.customSlug) {
            elements.customSlug.value = '';
            elements.customSlug.classList.remove('invalid');
            hideFieldHint(elements.customSlugContainer);
        }
        if (elements.slugLength) {
            const { min, max, default: defaultValue } = state.slugLengthConfig;
            elements.slugLength.value = Math.min(Math.max(defaultValue, min), max);
            elements.slugLength.disabled = false;
            elements.slugLength.classList.remove('disabled');
            elements.lengthValue.classList.remove('disabled');
            elements.slugLengthContainer?.classList.remove('field-disabled');
            hideFieldHint(elements.slugLengthContainer);
            updateLengthDisplay();
        }
    }

    window.copyToClipboard = async function() {
        const shortUrl = elements.shortUrl.value;
        
        try {
            await navigator.clipboard.writeText(shortUrl);
            showToast('Ссылка скопирована!', 'success');
        } catch {
            const textarea = document.createElement('textarea');
            textarea.value = shortUrl;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showToast('Ссылка скопирована!', 'success');
        }
    };

    function toggleTheme() {
        document.body.classList.toggle('dark-theme');
        const icon = elements.themeToggle.querySelector('i');
        
        if (document.body.classList.contains('dark-theme')) {
            icon.className = 'fas fa-sun';
            localStorage.setItem('theme', 'dark');
        } else {
            icon.className = 'fas fa-moon';
            localStorage.setItem('theme', 'light');
        }
    }

    function initTheme() {
        const savedTheme = localStorage.getItem('theme');
        
        if (savedTheme === 'light') {
            document.body.classList.remove('dark-theme');
            if (elements.themeToggle) {
                elements.themeToggle.querySelector('i').className = 'fas fa-moon';
            }
        } else {
            document.body.classList.add('dark-theme');
            if (elements.themeToggle) {
                elements.themeToggle.querySelector('i').className = 'fas fa-sun';
            }
        }
    }

    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        `;
        
        elements.toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s reverse';
            setTimeout(() => {
                if (elements.toastContainer.contains(toast)) {
                    elements.toastContainer.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    function setLoading(isLoading) {
        state.isLoading = isLoading;
        const btn = elements.shortenBtn;
        const btnText = btn.querySelector('.btn-text');
        const btnLoader = btn.querySelector('.btn-loader');
        
        if (isLoading) {
            btn.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'inline-block';
        } else {
            btn.disabled = false;
            btnText.style.display = 'inline-block';
            btnLoader.style.display = 'none';
        }
    }

    return {
        init,
        showToast
    };
})();

document.addEventListener('DOMContentLoaded', () => {
    UI.init();
});
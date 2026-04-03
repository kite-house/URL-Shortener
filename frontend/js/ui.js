// ui.js - Модуль для работы с интерфейсом
const UI = (function() {
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

    const elements = {};

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

    function getUserFriendlyErrorMessage(error) {
        const errorStr = String(error).toLowerCase();
        
        if (errorStr.includes('url scheme') || errorStr.includes('http://') || errorStr.includes('https://')) {
            return 'URL должен начинаться с http:// или https://';
        }
        if (errorStr.includes('invalid') || errorStr.includes('корректн')) {
            return 'Пожалуйста, введите корректный URL';
        }
        if (errorStr.includes('недоступн')) {
            return 'Данная ссылка недоступна';
        }
        if (errorStr.includes('already') || errorStr.includes('уже существует')) {
            return 'Эта ссылка уже была сокращена';
        }
        
        return String(error);
    }

    function initElements() {
        elements.form = document.getElementById('shortenForm');
        elements.urlInput = document.getElementById('urlInput');
        elements.shortenBtn = document.getElementById('shortenBtn');
        elements.resultCard = document.getElementById('resultCard');
        elements.closeResultBtn = document.getElementById('closeResultBtn');
        elements.shortUrl = document.getElementById('shortUrl');
        elements.originalUrl = document.getElementById('originalUrl');
        elements.toastContainer = document.getElementById('toastContainer');
        elements.customSlug = document.getElementById('customSlug');
        elements.slugLength = document.getElementById('slugLength');
        elements.lengthValue = document.getElementById('lengthValue');
        elements.toggleAdvancedBtn = document.getElementById('toggleAdvancedBtn');
        elements.advancedSettings = document.getElementById('advancedSettings');
        elements.sliderMarkers = document.querySelector('.slider-markers');
        elements.ttlDays = document.getElementById('ttlDays');
        elements.slugLengthContainer = document.querySelector('.setting-item:has(#slugLength)');
        elements.customSlugContainer = document.querySelector('.setting-item:has(#customSlug)');
        elements.footerParagraph = document.querySelector('.footer p');
        elements.logoText = document.querySelector('.logo-text');
        elements.pageTitle = document.querySelector('title');
        elements.expiryInfo = document.getElementById('expiryInfo');
        elements.expiryText = document.getElementById('expiryText');
        
        addUrlErrorContainer();
    }

    function addUrlErrorContainer() {
        if (elements.urlInput && !document.getElementById('urlError')) {
            const errorDiv = document.createElement('div');
            errorDiv.id = 'urlError';
            errorDiv.className = 'url-error-message';
            errorDiv.style.display = 'none';
            errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i><span></span>`;
            
            const inputWrapper = elements.urlInput.closest('.input-wrapper');
            if (inputWrapper) {
                inputWrapper.appendChild(errorDiv);
            }
        }
    }

    function showUrlError(message) {
        const errorDiv = document.getElementById('urlError');
        if (errorDiv) {
            const span = errorDiv.querySelector('span');
            if (span) span.textContent = typeof message === 'string' ? message : 'Ошибка валидации URL';
            errorDiv.style.display = 'flex';
            if (elements.urlInput) elements.urlInput.classList.add('input-error');
        }
        showToast(typeof message === 'string' ? message : 'Ошибка валидации URL', 'error');
    }

    function hideUrlError() {
        const errorDiv = document.getElementById('urlError');
        if (errorDiv) errorDiv.style.display = 'none';
        if (elements.urlInput) elements.urlInput.classList.remove('input-error');
    }

    let cleanIndicator = null;
    let cleanIndicatorTimeout = null;
    
    function showCleanIndicator() {
        if (cleanIndicator) {
            cleanIndicator.remove();
            clearTimeout(cleanIndicatorTimeout);
        }
        
        cleanIndicator = document.createElement('div');
        cleanIndicator.className = 'clean-indicator';
        cleanIndicator.innerHTML = '<i class="fas fa-broom"></i>';
        cleanIndicator.title = 'Ссылка автоматически очищена от пробелов и переносов';
        
        const inputGroup = elements.urlInput.closest('.input-group');
        if (inputGroup) {
            inputGroup.appendChild(cleanIndicator);
            cleanIndicatorTimeout = setTimeout(() => {
                if (cleanIndicator) {
                    cleanIndicator.classList.add('fade-out');
                    setTimeout(() => {
                        if (cleanIndicator) cleanIndicator.remove();
                    }, 300);
                }
            }, 2000);
        }
    }
    
    function cleanUrlValue(rawValue) {
        if (!rawValue) return '';
        
        let cleaned = rawValue.trim();
        cleaned = cleaned.replace(/[\s\r\n\t]+/g, '');
        if (!cleaned) return '';
        
        const fixes = [
            { pattern: /^hp:\/\//, replacement: 'http://' },
            { pattern: /^hptp:\/\//, replacement: 'http://' },
            { pattern: /^hptt:\/\//, replacement: 'http://' },
            { pattern: /^htp:\/\//, replacement: 'http://' },
            { pattern: /^ttps:\/\//, replacement: 'https://' },
            { pattern: /^ttp:\/\//, replacement: 'http://' },
            { pattern: /^https:\/\/\//, replacement: 'https://' },
            { pattern: /^http:\/\/\//, replacement: 'http://' }
        ];
        
        for (const fix of fixes) {
            cleaned = cleaned.replace(fix.pattern, fix.replacement);
        }
        
        if (!cleaned.match(/^https?:\/\//i)) {
            if (cleaned.match(/^[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)) {
                cleaned = 'https://' + cleaned;
            }
        }
        
        return cleaned;
    }
    
    function cleanCustomSlugValue(rawValue) {
        if (!rawValue) return '';
        let cleaned = rawValue.trim();
        cleaned = cleaned.replace(/[\s\r\n\t]+/g, '');
        cleaned = cleaned.replace(/[^a-zA-Z0-9_-]/g, '');
        return cleaned;
    }
    
    function setupUrlInputHandlers() {
        if (!elements.urlInput) return;
        
        elements.urlInput.addEventListener('paste', function(e) {
            e.preventDefault();
            const paste = (e.clipboardData || window.clipboardData).getData('text');
            const cleaned = cleanUrlValue(paste);
            this.value = cleaned;
            if (cleaned !== paste) showCleanIndicator();
            this.dispatchEvent(new Event('input', { bubbles: true }));
        });
        
        elements.urlInput.addEventListener('blur', function() {
            const currentValue = this.value;
            const cleaned = cleanUrlValue(currentValue);
            if (cleaned !== currentValue) {
                this.value = cleaned;
                if (cleaned && cleaned !== currentValue) showCleanIndicator();
            }
        });
        
        elements.urlInput.addEventListener('input', function() {
            const currentValue = this.value;
            if (/[\s\r\n\t]/.test(currentValue)) {
                const cleaned = currentValue.replace(/[\s\r\n\t]+/g, '');
                this.value = cleaned;
                if (cleaned !== currentValue) showCleanIndicator();
            }
            hideUrlError();
        });
    }

    function setupCustomSlugHandlers() {
        if (!elements.customSlug) return;
        
        elements.customSlug.addEventListener('paste', function(e) {
            e.preventDefault();
            const paste = (e.clipboardData || window.clipboardData).getData('text');
            const cleaned = cleanCustomSlugValue(paste);
            this.value = cleaned;
            this.dispatchEvent(new Event('input', { bubbles: true }));
        });
        
        elements.customSlug.addEventListener('input', function() {
            const currentValue = this.value;
            if (/[\s\r\n\t]/.test(currentValue)) {
                this.value = currentValue.replace(/[\s\r\n\t]+/g, '');
            }
        });
    }

    function setupUrlInputSelection() {
        if (!elements.urlInput) return;
        elements.urlInput.addEventListener('focus', function() { this.select(); });
    }

    function updateAppNameInUI(appName) {
        if (elements.pageTitle) elements.pageTitle.textContent = `${appName} | Сервис сокращения ссылок`;
        if (elements.logoText) elements.logoText.innerHTML = appName;
        if (elements.footerParagraph) {
            elements.footerParagraph.innerHTML = `© ${new Date().getFullYear()} ${appName}. Все права защищены.`;
        }
    }

    function updatePlaceholder(exampleUrl) {
        if (elements.urlInput) elements.urlInput.placeholder = exampleUrl;
    }

    async function loadFrontendConfig() {
        try {
            const config = await API.getFrontendConfig();
            if (config && config.app_name) {
                if (config.mode === 'PROD') state.isProdMode = true;
                state.appConfig = { ...state.appConfig, ...config };
                updateAppNameInUI(config.app_name);
                updatePlaceholder(config.example_url || state.appConfig.example_url);
            }
        } catch (error) {
            errorLogIfDev('❌ Ошибка загрузки конфигурации:', error);
        }
    }

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

    function updateSliderConfig() {
        if (!elements.slugLength) return;
        const { min, max, default: defaultValue } = state.slugLengthConfig;
        elements.slugLength.min = min;
        elements.slugLength.max = max;
        elements.slugLength.value = Math.min(Math.max(defaultValue, min), max);
        updateLengthDisplay();
        if (elements.sliderMarkers) {
            elements.sliderMarkers.innerHTML = `<span>${min}</span><span>${Math.floor((min + max) / 2)}</span><span>${max}</span>`;
        }
    }

    function showFieldHint(container, message, type = 'warning') {
        if (!container) return;
        hideFieldHint(container);
        const hint = document.createElement('div');
        hint.className = `field-hint field-hint-${type}`;
        hint.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i><span>${message}</span>`;
        container.appendChild(hint);
    }

    function hideFieldHint(container) {
        if (!container) return;
        const oldHint = container.querySelector('.field-hint');
        if (oldHint) oldHint.remove();
    }

    function toggleFieldsState() {
        if (!elements.customSlug || !elements.slugLength) return;
        const isCustomSlugFilled = elements.customSlug.value.trim() !== '';
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
            elements.customSlug.classList.add('invalid');
            showFieldHint(elements.customSlugContainer, 'Только латинские буквы, цифры, дефис и подчеркивание', 'error');
        } else if (slug && slug.length < min) {
            elements.customSlug.classList.add('invalid');
            showFieldHint(elements.customSlugContainer, `Минимальная длина: ${min} символа(ов)`, 'error');
        } else if (slug && slug.length > max) {
            elements.customSlug.classList.add('invalid');
            showFieldHint(elements.customSlugContainer, `Максимальная длина: ${max} символов`, 'error');
        } else {
            elements.customSlug.classList.remove('invalid');
            if (slug) showFieldHint(elements.customSlugContainer, '✓ Корректный формат', 'success');
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

    function setupEventListeners() {
        if (elements.form) elements.form.addEventListener('submit', handleFormSubmit);
        if (elements.slugLength) elements.slugLength.addEventListener('input', updateLengthDisplay);
        if (elements.customSlug) elements.customSlug.addEventListener('input', handleCustomSlugChange);
        if (elements.toggleAdvancedBtn) {
            elements.toggleAdvancedBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                toggleAdvancedSettings();
            });
        }
        if (elements.closeResultBtn) elements.closeResultBtn.addEventListener('click', closeResult);
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && elements.resultCard.style.display === 'block') closeResult();
        });
    }

    function toggleAdvancedSettings() {
        if (!elements.advancedSettings) return;
        state.advancedOpen = !state.advancedOpen;
        if (state.advancedOpen) {
            elements.advancedSettings.style.display = 'block';
            elements.toggleAdvancedBtn.classList.add('active');
            if (elements.toggleAdvancedBtn.querySelector('i')) {
                elements.toggleAdvancedBtn.querySelector('i').style.transform = 'rotate(90deg)';
            }
            toggleFieldsState();
        } else {
            elements.advancedSettings.style.display = 'none';
            elements.toggleAdvancedBtn.classList.remove('active');
            if (elements.toggleAdvancedBtn.querySelector('i')) {
                elements.toggleAdvancedBtn.querySelector('i').style.transform = 'rotate(0deg)';
            }
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
        if (elements.ttlDays) elements.ttlDays.value = '';
    }

    function updateLengthDisplay() {
        if (elements.lengthValue && elements.slugLength) {
            elements.lengthValue.textContent = elements.slugLength.value;
        }
    }

    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const rawUrl = elements.urlInput.value.trim();
        const url = cleanUrlValue(rawUrl);
        
        if (url !== rawUrl) {
            elements.urlInput.value = url;
            if (rawUrl && url !== rawUrl) showCleanIndicator();
        }
        
        if (!url) {
            showUrlError('Пожалуйста, введите ссылку');
            return;
        }
        
        hideUrlError();
        
        if (!url.match(/^https?:\/\//i)) {
            showUrlError('URL должен начинаться с http:// или https://');
            return;
        }
        
        try {
            new URL(url);
        } catch (error) {
            showUrlError('Пожалуйста, введите корректный URL');
            return;
        }
        
        let customSlug = elements.customSlug ? elements.customSlug.value.trim() : null;
        
        let length = null;
        if (elements.slugLength && elements.slugLength.value !== '6') {
            length = parseInt(elements.slugLength.value);
        }
        
        let ttlDays = elements.ttlDays ? elements.ttlDays.value : null;
        
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
        }
        
        setLoading(true);
        
        try {
            const result = await API.shortenUrl(url, customSlug, length, ttlDays);
            
            if (result.success) {
                showToast(result.message || (result.isNew ? 'Ссылка успешно сокращена!' : 'Ссылка уже существует!'), 
                         result.isNew ? 'success' : 'info');
                handleSuccessResponse(result.data, url);
            }
        } catch (error) {
            const errorMessage = getUserFriendlyErrorMessage(error.message || error);
            if (errorMessage.includes('недоступн') || errorMessage.includes('404')) {
                showUrlError(errorMessage);
            } else {
                showToast(errorMessage, 'error');
            }
        } finally {
            setLoading(false);
        }
    }

    function handleSuccessResponse(responseData, originalUrl) {
        let displayUrl = responseData.short_url;
        
        if (displayUrl.includes('localhost:8000')) {
            displayUrl = displayUrl.replace('localhost:8000', window.location.host);
        }
        if (displayUrl.includes('127.0.0.1:8000')) {
            displayUrl = displayUrl.replace('127.0.0.1:8000', window.location.host);
        }
        
        if (displayUrl.includes('/api/')) {
            displayUrl = displayUrl.replace('/api/', '/');
        }
        
        elements.shortUrl.value = displayUrl;
        const originalUrlSpan = elements.originalUrl.querySelector('span');
        if (originalUrlSpan) {
            originalUrlSpan.textContent = responseData.long_url || originalUrl;
        }
        
        if (elements.expiryInfo && elements.expiryText) {
            if (responseData.ttl) {
                const expiryDate = new Date(responseData.ttl);
                const formattedDate = expiryDate.toLocaleString('ru-RU', {
                    day: '2-digit', month: '2-digit', year: 'numeric',
                    hour: '2-digit', minute: '2-digit'
                });
                elements.expiryText.innerHTML = `<i class="fas fa-hourglass-half"></i> Ссылка действительна до: ${formattedDate}`;
                elements.expiryInfo.style.display = 'block';
            } else {
                elements.expiryText.innerHTML = `<i class="fas fa-infinity"></i> Бессрочная ссылка`;
                elements.expiryInfo.style.display = 'block';
            }
        }
        
        elements.resultCard.style.display = 'block';
        state.currentSlug = responseData.slug;
        
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
        if (elements.ttlDays) elements.ttlDays.value = '';
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

    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i><span>${message}</span>`;
        elements.toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s reverse';
            setTimeout(() => {
                if (elements.toastContainer.contains(toast)) elements.toastContainer.removeChild(toast);
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
            if (btnText) btnText.style.display = 'none';
            if (btnLoader) btnLoader.style.display = 'inline-block';
        } else {
            btn.disabled = false;
            if (btnText) btnText.style.display = 'inline-block';
            if (btnLoader) btnLoader.style.display = 'none';
        }
    }

    async function init() {
        logIfDev('🚀 Инициализация UI...');
        initElements();
        setupUrlInputHandlers();
        setupUrlInputSelection();
        setupCustomSlugHandlers();
        updateAppNameInUI(state.appConfig.app_name);
        updatePlaceholder(state.appConfig.example_url);
        await loadFrontendConfig();
        await loadSlugLengthConfig();
        setupEventListeners();
        if (elements.customSlug) toggleFieldsState();
    }

    return { init, showToast };
})();

document.addEventListener('DOMContentLoaded', () => {
    UI.init();
});
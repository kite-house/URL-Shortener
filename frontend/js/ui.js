// ui.js - Модуль для работы с интерфейсом
const UI = (function() {
    // Состояние приложения
    const state = {
        currentSlug: null,
        isLoading: false,
        advancedOpen: false,
        slugLengthConfig: {
            min: 3,
            max: 10,
            default: 6
        }
    };

    // DOM элементы
    const elements = {};

    // Функция для инициализации элементов
    function initElements() {
        elements.form = document.getElementById('shortenForm');
        elements.urlInput = document.getElementById('urlInput');
        elements.shortenBtn = document.getElementById('shortenBtn');
        elements.resultCard = document.getElementById('resultCard');
        elements.statsMini = document.getElementById('statsMini');
        elements.shortUrl = document.getElementById('shortUrl');
        elements.originalUrl = document.getElementById('originalUrl');
        elements.clickCount = document.getElementById('clickCount');
        elements.createdDate = document.getElementById('createdDate');
        elements.themeToggle = document.querySelector('.theme-toggle');
        elements.toastContainer = document.getElementById('toastContainer');
        
        // Элементы дополнительных настроек
        elements.customSlug = document.getElementById('customSlug');
        elements.slugLength = document.getElementById('slugLength');
        elements.lengthValue = document.getElementById('lengthValue');
        elements.toggleAdvancedBtn = document.getElementById('toggleAdvancedBtn');
        elements.advancedSettings = document.getElementById('advancedSettings');
        elements.sliderMarkers = document.querySelector('.slider-markers');
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
                
                // Обновляем слайдер с новыми значениями
                updateSliderConfig();
            }
        } catch (error) {
            // Используем значения по умолчанию
            showToast('Используются стандартные настройки длины', 'info');
        }
    }

    // Обновление конфигурации слайдера
    function updateSliderConfig() {
        if (!elements.slugLength) return;
        
        const { min, max, default: defaultValue } = state.slugLengthConfig;
        
        // Обновляем атрибуты слайдера
        elements.slugLength.min = min;
        elements.slugLength.max = max;
        elements.slugLength.value = Math.min(Math.max(defaultValue, min), max);
        
        // Обновляем отображение значения
        updateLengthDisplay();
        
        // Обновляем маркеры слайдера
        if (elements.sliderMarkers) {
            elements.sliderMarkers.innerHTML = `
                <span>${min}</span>
                <span>${Math.floor((min + max) / 2)}</span>
                <span>${max}</span>
            `;
        }
    }

    // Функция для управления состоянием полей
    function toggleFieldsState() {
        if (!elements.customSlug || !elements.slugLength) return;
        
        const customSlugValue = elements.customSlug.value.trim();
        
        if (customSlugValue !== '') {
            // Если custom_slug не пустой, блокируем слайдер длины
            elements.slugLength.disabled = true;
            elements.slugLength.classList.add('disabled');
            elements.lengthValue.classList.add('disabled');
        } else {
            // Если custom_slug пустой, разблокируем слайдер
            elements.slugLength.disabled = false;
            elements.slugLength.classList.remove('disabled');
            elements.lengthValue.classList.remove('disabled');
        }
    }

    // Инициализация
    async function init() {
        initElements();
        initTheme();
        
        // Загружаем конфигурацию перед настройкой слушателей
        await loadSlugLengthConfig();
        
        setupEventListeners();
        
        // Инициализируем состояние полей
        if (elements.customSlug) {
            toggleFieldsState();
        }
    }

    // Настройка обработчиков событий
    function setupEventListeners() {
        if (elements.form) {
            elements.form.addEventListener('submit', handleFormSubmit);
        }
        
        if (elements.themeToggle) {
            elements.themeToggle.addEventListener('click', toggleTheme);
        }
        
        // Слушатель для слайдера длины
        if (elements.slugLength) {
            elements.slugLength.addEventListener('input', updateLengthDisplay);
        }
        
        // Валидация custom slug при вводе
        if (elements.customSlug) {
            elements.customSlug.addEventListener('input', validateCustomSlug);
        }
        
        // Кнопка открытия/закрытия доп. настроек
        if (elements.toggleAdvancedBtn) {
            elements.toggleAdvancedBtn.addEventListener('click', function(event) {
                event.preventDefault();
                event.stopPropagation();
                toggleAdvancedSettings();
            });
        }
    }

    // Открыть/закрыть дополнительные настройки
    function toggleAdvancedSettings() {
        if (!elements.advancedSettings) return;
        
        state.advancedOpen = !state.advancedOpen;
        
        if (state.advancedOpen) {
            elements.advancedSettings.style.display = 'block';
            elements.toggleAdvancedBtn.classList.add('active');
            elements.toggleAdvancedBtn.querySelector('i').style.transform = 'rotate(90deg)';
            
            // При открытии проверяем состояние полей
            toggleFieldsState();
        } else {
            elements.advancedSettings.style.display = 'none';
            elements.toggleAdvancedBtn.classList.remove('active');
            elements.toggleAdvancedBtn.querySelector('i').style.transform = 'rotate(0deg)';
            
            // Сбрасываем значения при закрытии
            if (elements.customSlug) {
                elements.customSlug.value = '';
            }
            if (elements.slugLength) {
                const { min, max, default: defaultValue } = state.slugLengthConfig;
                elements.slugLength.value = Math.min(Math.max(defaultValue, min), max);
                elements.slugLength.disabled = false;
                elements.slugLength.classList.remove('disabled');
                elements.lengthValue.classList.remove('disabled');
                updateLengthDisplay();
            }
        }
    }

    // Обновление отображения длины слайдера
    function updateLengthDisplay() {
        if (elements.lengthValue && elements.slugLength) {
            elements.lengthValue.textContent = elements.slugLength.value;
        }
    }

    // Валидация кастомного slug
    function validateCustomSlug() {
        const slug = elements.customSlug.value;
        const { min } = state.slugLengthConfig;
        const pattern = /^[a-zA-Z0-9_-]*$/;
        
        if (slug && !pattern.test(slug)) {
            elements.customSlug.setCustomValidity('Только латинские буквы, цифры, дефис и подчеркивание');
            elements.customSlug.classList.add('invalid');
        } else if (slug && slug.length < min) {
            elements.customSlug.setCustomValidity(`Минимум ${min} символа(ов)`);
            elements.customSlug.classList.add('invalid');
        } else {
            elements.customSlug.setCustomValidity('');
            elements.customSlug.classList.remove('invalid');
        }
        
        // Вызываем toggleFieldsState при изменении custom_slug
        toggleFieldsState();
    }

    // Обработка отправки формы
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const url = elements.urlInput.value.trim();
        if (!url) return;
        
        // Валидация URL
        try {
            new URL(url);
        } catch {
            showToast('Пожалуйста, введите корректный URL', 'error');
            return;
        }
        
        // Получаем дополнительные параметры
        let customSlug = elements.customSlug ? elements.customSlug.value.trim() : null;
        let length = elements.slugLength ? parseInt(elements.slugLength.value) : null;
        
        // Проверяем, открыты ли дополнительные настройки
        const useLength = state.advancedOpen;
        
        // Если customSlug пустая строка, передаем null
        if (customSlug === '') {
            customSlug = null;
        }
        
        // Если указан custom_slug, не передаем length
        if (customSlug) {
            length = null;
        }
        // Проверяем валидность length если настройки открыты и нет custom_slug
        else if (useLength && length !== null) {
            const { min, max } = state.slugLengthConfig;
            length = parseInt(length);
            if (isNaN(length) || length < min || length > max) {
                length = null;
            }
        } else {
            length = null;
        }
        
        // Валидация кастомного slug если он указан
        if (customSlug) {
            const { min } = state.slugLengthConfig;
            const pattern = /^[a-zA-Z0-9_-]{3,}$/;
            if (!pattern.test(customSlug) || customSlug.length < min) {
                showToast(`Некорректный формат кастомной ссылки (минимум ${min} символов)`, 'error');
                return;
            }
        }
        
        setLoading(true);
        
        try {
            // Передаем параметры в API
            const result = await API.shortenUrl(url, customSlug, length);
            
            // Обрабатываем разные статусы ответа
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

    // Обработка успешного ответа
    function handleSuccessResponse(responseData, originalUrl, message) {
        let displayUrl = responseData.short_url;
        if (displayUrl.includes('localhost')) {
            displayUrl = displayUrl.replace('localhost', window.location.hostname);
        }
        
        elements.shortUrl.value = displayUrl;
        elements.originalUrl.textContent = responseData.long_url || originalUrl;
        elements.resultCard.style.display = 'block';
        
        state.currentSlug = responseData.slug;
        
        loadLinkStats(responseData.slug);
        showToast(message, 'success');
        
        elements.urlInput.value = '';
        if (elements.customSlug) {
            elements.customSlug.value = '';
        }
        if (elements.slugLength) {
            const { min, max, default: defaultValue } = state.slugLengthConfig;
            elements.slugLength.value = Math.min(Math.max(defaultValue, min), max);
            elements.slugLength.disabled = false;
            elements.slugLength.classList.remove('disabled');
            elements.lengthValue.classList.remove('disabled');
            updateLengthDisplay();
        }
    }

    // Загрузка статистики по ссылке
    async function loadLinkStats(slug) {
        try {
            const result = await API.getLinkStats(slug);
            
            if (result.success) {
                const urlData = result.data.data;
                
                elements.clickCount.textContent = urlData.count_clicks || 0;
                
                if (urlData.date_created && urlData.date_created !== '-') {
                    elements.createdDate.textContent = urlData.date_created;
                } else {
                    elements.createdDate.textContent = 'сегодня';
                }
                
                elements.statsMini.style.display = 'flex';
            }
        } catch (error) {
            // Ошибка загрузки статистики - просто не показываем
        }
    }

    // Копирование в буфер обмена
    window.copyToClipboard = async function() {
        const shortUrl = elements.shortUrl.value;
        
        try {
            await navigator.clipboard.writeText(shortUrl);
            showToast('Ссылка скопирована!', 'success');
        } catch (err) {
            const textarea = document.createElement('textarea');
            textarea.value = shortUrl;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showToast('Ссылка скопирована!', 'success');
        }
    };

    // Переключение темы
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

    // Инициализация темы
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
            localStorage.setItem('theme', 'dark');
        }
    }

    // Показ уведомлений
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        
        elements.toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s reverse';
            setTimeout(() => {
                elements.toastContainer.removeChild(toast);
            }, 300);
        }, 3000);
    }

    // Управление состоянием загрузки
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

    // Публичное API UI модуля
    return {
        init,
        showToast
    };
})();

// Инициализация приложения после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    UI.init();
});
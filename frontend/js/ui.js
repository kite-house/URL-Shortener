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
        elements.closeResultBtn = document.getElementById('closeResultBtn'); // Добавлено
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

    // Функция для показа подсказки у поля
    function showFieldHint(container, message, type = 'warning') {
        if (!container) return;
        
        // Удаляем старую подсказку если есть
        hideFieldHint(container);
        
        const hint = document.createElement('div');
        hint.className = `field-hint field-hint-${type}`;
        hint.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        `;
        container.appendChild(hint);
    }

    // Функция для скрытия подсказки
    function hideFieldHint(container) {
        if (!container) return;
        const oldHint = container.querySelector('.field-hint');
        if (oldHint) {
            oldHint.remove();
        }
    }

    // Функция для управления состоянием полей
    function toggleFieldsState() {
        if (!elements.customSlug || !elements.slugLength) return;
        
        const customSlugValue = elements.customSlug.value.trim();
        const isCustomSlugFilled = customSlugValue !== '';
        
        // Блокируем/разблокируем слайдер длины
        elements.slugLength.disabled = isCustomSlugFilled;
        
        // Добавляем/убираем класс disabled для визуального эффекта
        if (isCustomSlugFilled) {
            elements.slugLength.classList.add('disabled');
            elements.lengthValue.classList.add('disabled');
            elements.slugLengthContainer?.classList.add('field-disabled');
            
            // Добавляем подсказку
            showFieldHint(elements.slugLengthContainer, 'Недоступно при использовании своего варианта', 'warning');
        } else {
            elements.slugLength.classList.remove('disabled');
            elements.lengthValue.classList.remove('disabled');
            elements.slugLengthContainer?.classList.remove('field-disabled');
            
            // Убираем подсказку
            hideFieldHint(elements.slugLengthContainer);
        }
    }

    // Валидация кастомного slug
    function validateCustomSlug() {
        const slug = elements.customSlug.value;
        const { min, max } = state.slugLengthConfig;
        const pattern = /^[a-zA-Z0-9_-]*$/;
        
        // Удаляем старые сообщения об ошибках
        hideFieldHint(elements.customSlugContainer);
        
        if (slug && !pattern.test(slug)) {
            elements.customSlug.setCustomValidity('Только латинские буквы, цифры, дефис и подчеркивание');
            elements.customSlug.classList.add('invalid');
            
            // Показываем сообщение об ошибке
            showFieldHint(elements.customSlugContainer, 'Только латинские буквы, цифры, дефис и подчеркивание', 'error');
        } else if (slug && slug.length < min) {
            elements.customSlug.setCustomValidity(`Минимум ${min} символа(ов)`);
            elements.customSlug.classList.add('invalid');
            
            // Показываем сообщение об ошибке
            showFieldHint(elements.customSlugContainer, `Минимальная длина: ${min} символа(ов)`, 'error');
        } else if (slug && slug.length > max) {
            elements.customSlug.setCustomValidity(`Максимум ${max} символов`);
            elements.customSlug.classList.add('invalid');
            
            // Показываем сообщение об ошибке
            showFieldHint(elements.customSlugContainer, `Максимальная длина: ${max} символов`, 'error');
        } else {
            elements.customSlug.setCustomValidity('');
            elements.customSlug.classList.remove('invalid');
            
            // Если поле не пустое и валидное, показываем подсказку об успехе
            if (slug) {
                showFieldHint(elements.customSlugContainer, '✓ Корректный формат', 'success');
            }
        }
    }

    // Объединенная функция для обработки изменений в custom slug
    function handleCustomSlugChange() {
        validateCustomSlug();
        toggleFieldsState();
    }

    // Функция для закрытия результата
    function closeResult() {
        if (!elements.resultCard) return;
        
        // Добавляем класс для анимации
        elements.resultCard.classList.add('hiding');
        
        // Ждем окончания анимации и скрываем
        setTimeout(() => {
            elements.resultCard.style.display = 'none';
            elements.resultCard.classList.remove('hiding');
            state.currentSlug = null;
        }, 300);
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
            elements.customSlug.addEventListener('input', handleCustomSlugChange);
        }
        
        // Кнопка открытия/закрытия доп. настроек
        if (elements.toggleAdvancedBtn) {
            elements.toggleAdvancedBtn.addEventListener('click', function(event) {
                event.preventDefault();
                event.stopPropagation();
                toggleAdvancedSettings();
            });
        }
        
        // Кнопка закрытия результата
        if (elements.closeResultBtn) {
            elements.closeResultBtn.addEventListener('click', closeResult);
        }
        
        // Закрытие по клавише Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && elements.resultCard.style.display === 'block') {
                closeResult();
            }
        });
        
        // Закрытие по клику вне карточки (опционально)
        document.addEventListener('click', function(e) {
            if (elements.resultCard.style.display === 'block' && 
                !elements.resultCard.contains(e.target) && 
                !elements.form.contains(e.target)) {
                closeResult();
            }
        });
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
            resetAdvancedFields();
        }
    }

    // Функция для сброса дополнительных полей
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

    // Обновление отображения длины слайдера
    function updateLengthDisplay() {
        if (elements.lengthValue && elements.slugLength) {
            elements.lengthValue.textContent = elements.slugLength.value;
        }
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
        
        // Проверяем валидность custom_slug
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
            
            // Если custom_slug валидный, length не используется
            length = null;
        }
        // Если custom_slug пустой, используем length
        else {
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

    // Обработка успешного ответа
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
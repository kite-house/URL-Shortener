// ui.js - Модуль для работы с интерфейсом
const UI = (function() {
    // Состояние приложения
    const state = {
        currentSlug: null,
        topLinks: [],
        isLoading: false,
        advancedOpen: false
    };

    // DOM элементы
    const elements = {};

    // Функция для инициализации элементов
    function initElements() {
        console.log('Initializing DOM elements');
        
        elements.form = document.getElementById('shortenForm');
        elements.urlInput = document.getElementById('urlInput');
        elements.shortenBtn = document.getElementById('shortenBtn');
        elements.resultCard = document.getElementById('resultCard');
        elements.statsMini = document.getElementById('statsMini');
        elements.shortUrl = document.getElementById('shortUrl');
        elements.originalUrl = document.getElementById('originalUrl');
        elements.clickCount = document.getElementById('clickCount');
        elements.createdDate = document.getElementById('createdDate');
        elements.tableBody = document.getElementById('tableBody');
        elements.totalClicksValue = document.getElementById('totalClicksValue');
        elements.refreshBtn = document.getElementById('refreshBtn');
        elements.themeToggle = document.querySelector('.theme-toggle');
        elements.toastContainer = document.getElementById('toastContainer');
        elements.updateBadge = document.getElementById('updateBadge');
        
        // Новые элементы - с проверкой существования
        elements.customSlug = document.getElementById('customSlug');
        elements.slugLength = document.getElementById('slugLength');
        elements.lengthValue = document.getElementById('lengthValue');
        elements.toggleAdvancedBtn = document.getElementById('toggleAdvancedBtn');
        elements.advancedSettings = document.getElementById('advancedSettings');
        
        // Проверяем, что все элементы найдены
        console.log('Toggle button found:', !!elements.toggleAdvancedBtn);
        console.log('Advanced settings found:', !!elements.advancedSettings);
        
        if (!elements.toggleAdvancedBtn) {
            console.error('Toggle button not found! Check ID in HTML: toggleAdvancedBtn');
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
            console.log('🔒 Slider disabled - custom slug active');
        } else {
            // Если custom_slug пустой, разблокируем слайдер
            elements.slugLength.disabled = false;
            elements.slugLength.classList.remove('disabled');
            elements.lengthValue.classList.remove('disabled');
            console.log('🔓 Slider enabled - no custom slug');
        }
    }

    // Инициализация
    function init() {
        console.log('UI initialized');
        initElements();
        initTheme();
        setupEventListeners();
        loadTopLinks();
        
        // Инициализируем состояние полей
        if (elements.customSlug) {
            toggleFieldsState();
        }
        
        // Обновлять топ каждые 30 секунд
        setInterval(loadTopLinks, 30000);
    }

    // Настройка обработчиков событий
    function setupEventListeners() {
        console.log('Setting up event listeners');
        
        if (elements.form) {
            elements.form.addEventListener('submit', handleFormSubmit);
            console.log('Form listener added');
        }
        
        if (elements.refreshBtn) {
            elements.refreshBtn.addEventListener('click', loadTopLinks);
            console.log('Refresh listener added');
        }
        
        if (elements.themeToggle) {
            elements.themeToggle.addEventListener('click', toggleTheme);
            console.log('Theme toggle listener added');
        }
        
        // Слушатель для слайдера длины
        if (elements.slugLength) {
            elements.slugLength.addEventListener('input', updateLengthDisplay);
            console.log('Slider listener added');
        }
        
        // Валидация custom slug при вводе
        if (elements.customSlug) {
            elements.customSlug.addEventListener('input', validateCustomSlug);
            console.log('Custom slug validation added');
        }
        
        // Кнопка открытия/закрытия доп. настроек
        if (elements.toggleAdvancedBtn) {
            console.log('✅ Toggle button found, adding click listener');
            
            // Убираем все предыдущие обработчики
            elements.toggleAdvancedBtn.removeEventListener('click', toggleAdvancedSettings);
            
            // Добавляем новый обработчик
            elements.toggleAdvancedBtn.addEventListener('click', function(event) {
                event.preventDefault();
                event.stopPropagation();
                console.log('🔘 Toggle button clicked! Current state:', state.advancedOpen);
                toggleAdvancedSettings();
            });
            
            console.log('✅ Click listener added to toggle button');
        } else {
            console.error('❌ Toggle button NOT found! Check HTML ID');
        }
    }

    // Открыть/закрыть дополнительные настройки
    function toggleAdvancedSettings() {
        console.log('🔄 toggleAdvancedSettings called, current state:', state.advancedOpen);
        
        if (!elements.advancedSettings) {
            console.error('❌ Advanced settings element not found!');
            return;
        }
        
        state.advancedOpen = !state.advancedOpen;
        console.log('New state:', state.advancedOpen);
        
        if (state.advancedOpen) {
            elements.advancedSettings.style.display = 'block';
            elements.toggleAdvancedBtn.classList.add('active');
            elements.toggleAdvancedBtn.querySelector('i').style.transform = 'rotate(90deg)';
            console.log('✅ Advanced settings opened');
            
            // При открытии проверяем состояние полей
            toggleFieldsState();
        } else {
            elements.advancedSettings.style.display = 'none';
            elements.toggleAdvancedBtn.classList.remove('active');
            elements.toggleAdvancedBtn.querySelector('i').style.transform = 'rotate(0deg)';
            console.log('✅ Advanced settings closed');
            
            // Сбрасываем значения при закрытии
            if (elements.customSlug) {
                elements.customSlug.value = '';
            }
            if (elements.slugLength) {
                elements.slugLength.value = 6;
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
        const pattern = /^[a-zA-Z0-9_-]*$/;
        
        if (slug && !pattern.test(slug)) {
            elements.customSlug.setCustomValidity('Только латинские буквы, цифры, дефис и подчеркивание');
            elements.customSlug.classList.add('invalid');
        } else if (slug && slug.length < 3) {
            elements.customSlug.setCustomValidity('Минимум 3 символа');
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
            console.log('Custom slug is empty, using null');
        }
        
        // ВАЖНО: Если указан custom_slug, не передаем length
        if (customSlug) {
            length = null;
            console.log('Custom slug provided, length will not be used');
        }
        // Проверяем валидность length ТОЛЬКО если настройки открыты И нет custom_slug
        else if (useLength && length !== null) {
            length = parseInt(length);
            if (isNaN(length) || length < 3 || length > 10) {
                console.warn('Invalid length value, using default');
                length = null;
            } else {
                console.log('Using length:', length);
            }
        } else {
            // Если настройки закрыты или есть custom_slug, не передаем length
            length = null;
            console.log('Length not used');
        }
        
        // Валидация кастомного slug если он указан
        if (customSlug) {
            const pattern = /^[a-zA-Z0-9_-]{3,}$/;
            if (!pattern.test(customSlug)) {
                showToast('Некорректный формат кастомной ссылки', 'error');
                return;
            }
            console.log('✅ Using custom slug:', customSlug);
        }
        
        console.log('🚀 Отправка запроса с параметрами:', { 
            url, 
            customSlug: customSlug || 'не указан', 
            length: length || 'не указан',
            useLength: useLength
        });
        
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
            console.error('❌ Error:', error);
        } finally {
            setLoading(false);
        }
    }

    // Обработка успешного ответа
    function handleSuccessResponse(responseData, originalUrl, message) {
        console.log('Response data:', responseData);
        
        let displayUrl = responseData.short_url;
        if (displayUrl.includes('localhost')) {
            displayUrl = displayUrl.replace('localhost', window.location.hostname);
        }
        
        elements.shortUrl.value = displayUrl;
        elements.originalUrl.textContent = responseData.long_url || originalUrl;
        elements.resultCard.style.display = 'block';
        
        state.currentSlug = responseData.slug;
        
        loadLinkStats(responseData.slug);
        loadTopLinks();
        showToast(message, 'success');
        
        elements.urlInput.value = '';
        if (elements.customSlug) {
            elements.customSlug.value = '';
        }
        if (elements.slugLength) {
            elements.slugLength.value = 6;
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
            console.error('Error loading stats:', error);
        }
    }

    // Загрузка топа ссылок
    async function loadTopLinks() {
        elements.tableBody.innerHTML = `
            <tr class="loading-row">
                <td colspan="4" class="loading-message">
                    <i class="fas fa-spinner fa-spin"></i> Загрузка...
                </td>
            </tr>
        `;
        
        try {
            const result = await API.getTopLinks(10);
            
            if (result.success) {
                renderTopLinks(result.data.data);
            } else {
                throw new Error(result.data.message || 'Ошибка загрузки');
            }
            
            updateTimestamp();
            
        } catch (error) {
            console.error('Error loading top links:', error);
            elements.tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="loading-message" style="color: var(--danger-color);">
                        <i class="fas fa-exclamation-circle"></i> Ошибка загрузки
                    </td>
                </tr>
            `;
        }
    }

    // Рендер таблицы топ ссылок
    function renderTopLinks(links) {
        if (!links || links.length === 0) {
            elements.tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="loading-message">
                        <i class="fas fa-info-circle"></i> Пока нет ссылок
                    </td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        let totalClicks = 0;
        
        links.forEach((link, index) => {
            totalClicks += link.count_clicks || 0;
            
            const shortDisplay = link.short_url?.replace(/^https?:\/\//, '').substring(0, 25) + '...' || 'N/A';
            const originalDisplay = link.long_url?.substring(0, 30) + '...' || 'N/A';
            
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td title="${link.short_url || ''}">
                        <a href="${link.short_url}" target="_blank" style="color: var(--accent-color); text-decoration: none;">
                            ${shortDisplay}
                        </a>
                    </td>
                    <td title="${link.long_url || ''}">${originalDisplay}</td>
                    <td><span class="click-badge">${link.count_clicks || 0}</span></td>
                </tr>
            `;
        });
        
        elements.tableBody.innerHTML = html;
        elements.totalClicksValue.textContent = totalClicks;
    }

    // Обновление временной метки
    function updateTimestamp() {
        const now = new Date();
        elements.updateBadge.innerHTML = `<i class="fas fa-sync-alt"></i> ${formatTime(now)}`;
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

    // Вспомогательные функции
    function formatTime(date) {
        const options = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
        return date.toLocaleTimeString('ru-RU', options);
    }

    // Публичное API UI модуля
    return {
        init,
        loadTopLinks,
        showToast
    };
})();

// Инициализация приложения после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, initializing UI');
    UI.init();
});

// Дополнительная проверка на случай, если DOM загрузился слишком быстро
if (document.readyState === 'loading') {
    console.log('Document still loading, waiting for DOMContentLoaded');
} else {
    console.log('Document already loaded, initializing UI now');
    UI.init();
}
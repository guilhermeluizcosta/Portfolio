const ChatWidget = (() => {
    const config = window.__CHAT_CONFIG__ || {
        endpoint: '/api/chat',
        statusEndpoint: '/api/chat/status',
        questionLimit: 7,
        timeoutMs: 120000,
    };

    let remaining = config.questionLimit;
    let isProcessing = false;
    let limitReached = false;

    const fab = document.getElementById('chat-fab');
    const panel = document.getElementById('chat-panel');
    const overlay = document.getElementById('chat-overlay');
    const closeBtn = document.getElementById('chat-close');
    const messagesEl = document.getElementById('chat-messages');
    const inputEl = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send');
    const quotaEl = document.getElementById('chat-quota');



    function updateQuotaDisplay() {
        if (!quotaEl) {
            return;
        }
        if (limitReached || remaining <= 0) {
            quotaEl.textContent = I18n.t('chat.limit_reached');
            return;
        }
        if (remaining === 1) {
            quotaEl.textContent = I18n.t('chat.remaining_one');
            return;
        }
        quotaEl.textContent = I18n.t('chat.remaining', { count: remaining });
    }



    async function refreshStatus() {
        try {
            const response = await fetch(config.statusEndpoint);
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            remaining = data.remaining;
            limitReached = remaining <= 0;
            updateQuotaDisplay();
            updateInputState();
        } catch {

        }
    }



    function updateInputState() {
        const disabled = isProcessing || limitReached || remaining <= 0;
        inputEl.disabled = disabled;
        sendBtn.disabled = disabled;
    }



    function scrollToBottom() {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }



    function appendMessage(text, type) {
        const bubble = document.createElement('div');
        bubble.className = `chat-message chat-message--${type}`;
        bubble.setAttribute('role', type === 'error' ? 'alert' : 'listitem');
        bubble.textContent = text;
        messagesEl.appendChild(bubble);
        scrollToBottom();
        return bubble;
    }



    function showLoading() {
        const bubble = document.createElement('div');
        bubble.className = 'chat-message chat-message--loading';
        bubble.setAttribute('aria-busy', 'true');
        bubble.setAttribute('aria-label', I18n.t('chat.loading'));

        const label = document.createElement('span');
        label.textContent = I18n.t('chat.loading');

        const dots = document.createElement('span');
        dots.className = 'chat-typing-dots';
        dots.innerHTML = '<span></span><span></span><span></span>';

        bubble.appendChild(label);
        bubble.appendChild(dots);
        messagesEl.appendChild(bubble);
        scrollToBottom();
        return bubble;
    }



    function friendlyError(status) {
        if (status === 429) {
            return I18n.t('chat.error_limit');
        }
        if (status === 504) {
            return I18n.t('chat.error_timeout');
        }
        if (status === 503 || status === 0) {
            return I18n.t('chat.error_offline');
        }
        return I18n.t('chat.error_generic');
    }



    function showError(text, onRetry) {
        const bubble = appendMessage(text, 'error');
        if (onRetry) {
            const retryBtn = document.createElement('button');
            retryBtn.className = 'chat-retry-btn';
            retryBtn.type = 'button';
            retryBtn.textContent = I18n.t('chat.retry');
            retryBtn.addEventListener('click', () => {
                bubble.remove();
                onRetry();
            });
            bubble.appendChild(retryBtn);
        }
    }



    async function sendQuestion(question) {
        if (isProcessing || limitReached || remaining <= 0) {
            return;
        }

        const trimmed = question.trim();
        if (!trimmed) {
            showError(I18n.t('chat.empty'), null);
            return;
        }

        isProcessing = true;
        updateInputState();
        appendMessage(trimmed, 'visitor');
        inputEl.value = '';

        const loadingEl = showLoading();
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), config.timeoutMs);

        try {
            const response = await fetch(config.endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: trimmed }),
                signal: controller.signal,
            });

            loadingEl.remove();

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                const errorText = data.error || friendlyError(response.status);
                if (response.status === 429) {
                    limitReached = true;
                    remaining = 0;
                    updateQuotaDisplay();
                }
                showError(errorText, response.status !== 429 ? () => sendQuestion(trimmed) : null);
                return;
            }

            if (typeof data.remaining === 'number') {
                remaining = data.remaining;
                limitReached = remaining <= 0;
                updateQuotaDisplay();
            }

            appendMessage(data.answer || '', 'assistant');
        } catch (error) {
            loadingEl.remove();
            const isTimeout = error.name === 'AbortError';
            const message = isTimeout ? I18n.t('chat.error_timeout') : I18n.t('chat.error_offline');
            showError(message, () => sendQuestion(trimmed));
        } finally {
            clearTimeout(timeoutId);
            isProcessing = false;
            updateInputState();
        }
    }



    function openPanel() {
        panel.classList.add('is-open');
        overlay.classList.add('is-visible');
        panel.setAttribute('aria-hidden', 'false');
        refreshStatus();
        inputEl.focus();
    }



    function closePanel() {
        panel.classList.remove('is-open');
        overlay.classList.remove('is-visible');
        panel.setAttribute('aria-hidden', 'true');
        fab.focus();
    }



    function bindEvents() {
        fab.addEventListener('click', openPanel);
        closeBtn.addEventListener('click', closePanel);
        overlay.addEventListener('click', closePanel);

        sendBtn.addEventListener('click', () => sendQuestion(inputEl.value));

        inputEl.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendQuestion(inputEl.value);
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && panel.classList.contains('is-open')) {
                closePanel();
            }
        });

        document.addEventListener('localechange', () => {
            updateQuotaDisplay();
        });
    }



    function init() {
        if (!fab || !panel) {
            return;
        }
        panel.setAttribute('aria-hidden', 'true');
        bindEvents();
        updateQuotaDisplay();
        updateInputState();
    }

    return { init };
})();

document.addEventListener('DOMContentLoaded', () => ChatWidget.init());
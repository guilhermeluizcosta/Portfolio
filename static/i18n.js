const I18n = (() => {
    const COOKIE_NAME = 'locale';
    const COOKIE_MAX_AGE_DAYS = 7;
    const LOCALE_URLS = {
        en: '/static/locales/en.json',
        'pt-BR': '/static/locales/pt-BR.json',
    };

    const translations = { en: { ui: {} }, 'pt-BR': { ui: {} } };
    let currentLocale = 'en';
    let initialized = false;



    function detectLocale() {
        const cookie = document.cookie
            .split('; ')
            .find((row) => row.startsWith(`${COOKIE_NAME}=`));
        if (cookie) {
            const value = cookie.split('=')[1];
            if (translations[value]) {
                return value;
            }
        }
        const browserLang = navigator.language || navigator.userLanguage || 'en';
        return browserLang.toLowerCase().startsWith('pt') ? 'pt-BR' : 'en';
    }



    function setLocaleCookie(locale) {
        const maxAge = COOKIE_MAX_AGE_DAYS * 24 * 60 * 60;
        document.cookie = `${COOKIE_NAME}=${locale};path=/;max-age=${maxAge};SameSite=Lax`;
    }



    function t(key, params = {}) {
        const catalog = translations[currentLocale]?.ui || translations.en.ui;
        const fallback = translations.en.ui[key] || key;
        const text = catalog[key] || fallback;
        return Object.entries(params).reduce(
            (result, [placeholder, value]) => result.replace(`{${placeholder}}`, value),
            text,
        );
    }



    function applyTranslations() {
        document.querySelectorAll('[data-i18n]').forEach((element) => {
            const key = element.getAttribute('data-i18n');
            const attrTarget = element.getAttribute('data-i18n-attr');
            const text = t(key);
            if (attrTarget) {
                element.setAttribute(attrTarget, text);
                return;
            }
            if (text.trim() === '') {
                element.hidden = true;
                return;
            }
            element.hidden = false;
            element.textContent = text;
        });

        document.querySelectorAll('[data-i18n-placeholder]').forEach((element) => {
            element.placeholder = t(element.getAttribute('data-i18n-placeholder'));
        });

        document.documentElement.lang = currentLocale === 'pt-BR' ? 'pt-BR' : 'en';
    }



    async function loadCatalogs() {
        const entries = await Promise.all(
            Object.entries(LOCALE_URLS).map(async ([locale, url]) => {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`Failed to load locale: ${locale}`);
                }
                return [locale, await response.json()];
            }),
        );
        entries.forEach(([locale, data]) => {
            translations[locale] = data;
        });
    }



    function bindToggle() {
        const toggleLocale = () => {
            currentLocale = currentLocale === 'en' ? 'pt-BR' : 'en';
            setLocaleCookie(currentLocale);
            applyTranslations();
            document.dispatchEvent(new CustomEvent('localechange', { detail: { locale: currentLocale } }));
        };

        document.getElementById('lang-toggle')?.addEventListener('click', toggleLocale);
    }



    async function init() {
        if (initialized) {
            return;
        }
        await loadCatalogs();
        currentLocale = detectLocale();
        setLocaleCookie(currentLocale);
        applyTranslations();
        bindToggle();
        initialized = true;
    }

    return { init, t, getLocale: () => currentLocale };
})();

document.addEventListener('DOMContentLoaded', () => {
    I18n.init().catch(() => {

    });
});
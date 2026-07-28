(function () {
    'use strict';

    const storageKey = 'copilot-sdk-workshop.language';
    const picker = document.getElementById('languagePicker');
    const startLink = document.getElementById('startWorkshopLink');
    const docsLink = document.getElementById('sdkDocsLink');
    const summary = document.getElementById('languageSummary');
    const installCommand = document.getElementById('installCommand');
    const runtimeNote = document.getElementById('runtimeNote');
    const heroTitle = document.getElementById('hero-title');
    const heroEyebrow = document.getElementById('heroEyebrow');

    function getStoredLanguageId() {
        try {
            return window.localStorage.getItem(storageKey);
        } catch (error) {
            return null;
        }
    }

    function storeLanguageId(languageId) {
        try {
            window.localStorage.setItem(storageKey, languageId);
        } catch (error) {
            // Local storage can be unavailable in private browsing contexts.
        }
    }

    function updateLanguage(languageId) {
        const language = WorkshopLanguages.getLanguage(languageId);
        const hasLanguage = language !== null;

        startLink.classList.toggle('disabled', !hasLanguage);
        startLink.setAttribute('aria-disabled', String(!hasLanguage));
        startLink.href = hasLanguage
            ? `workshop/step.html?step=00-preflight&lang=${encodeURIComponent(language.id)}`
            : '#language-picker';

        if (!hasLanguage) {
            docsLink.removeAttribute('href');
            docsLink.setAttribute('aria-disabled', 'true');
            summary.textContent = 'Choose a language to tailor the workshop links and setup guidance.';
            installCommand.textContent = '';
            runtimeNote.textContent = '';
            heroTitle.textContent = 'Build an AI-powered accessibility reviewer';
            heroEyebrow.textContent = 'GitHub Copilot SDK / 90-minute core workshop';
            return;
        }

        docsLink.href = language.docsUrl;
        docsLink.removeAttribute('aria-disabled');
        docsLink.textContent = `${language.displayName} SDK docs ↗`;
        summary.textContent = `Your ${language.displayName} workshop uses the GitHub Copilot SDK.`;
        installCommand.textContent = language.installCommand;
        runtimeNote.textContent = language.runtimeNote;
        heroTitle.textContent = `Build an AI-powered accessibility reviewer with ${language.displayName}`;
        heroEyebrow.textContent = `${language.displayName} / GitHub Copilot SDK / 90-minute core workshop`;
    }

    picker.addEventListener('change', () => {
        const language = WorkshopLanguages.getLanguage(picker.value);
        if (!language) {
            updateLanguage(null);
            return;
        }
        storeLanguageId(language.id);
        updateLanguage(language.id);
    });

    startLink.addEventListener('click', event => {
        if (startLink.getAttribute('aria-disabled') === 'true') {
            event.preventDefault();
            picker.focus();
            picker.reportValidity();
        }
    });

    const requestedLanguageId = new URLSearchParams(window.location.search).get('lang');
    const requestedLanguage = WorkshopLanguages.getLanguage(requestedLanguageId);
    const storedLanguage = WorkshopLanguages.getLanguage(getStoredLanguageId());
    const initialLanguage = requestedLanguageId === null ? storedLanguage : requestedLanguage;
    if (initialLanguage) {
        picker.value = initialLanguage.id;
        storeLanguageId(initialLanguage.id);
        updateLanguage(initialLanguage.id);
    } else {
        updateLanguage(null);
    }
}());

(function (root, factory) {
    const api = factory();
    if (typeof module === 'object' && module.exports) {
        module.exports = api;
    }
    root.WorkshopLanguageNavigation = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    function resolveLanguage(search, storedLanguageId, getLanguage) {
        const parameters = new URLSearchParams(search);
        if (parameters.has('lang')) {
            return getLanguage(parameters.get('lang'));
        }
        return getLanguage(storedLanguageId);
    }

    function lessonUrl(stepId, languageId) {
        const parameters = new URLSearchParams({ step: stepId });
        if (languageId) {
            parameters.set('lang', languageId);
        }
        return `?${parameters.toString()}`;
    }

    function homeUrl(languageId) {
        return languageId
            ? `../index.html?lang=${encodeURIComponent(languageId)}`
            : '../index.html';
    }

    function firstLessonUrl(languageId) {
        return `workshop/step.html${lessonUrl('00-preflight', languageId)}`;
    }

    return Object.freeze({ resolveLanguage, lessonUrl, homeUrl, firstLessonUrl });
}));

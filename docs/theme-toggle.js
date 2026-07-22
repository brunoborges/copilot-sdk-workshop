(function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    const preferredTheme = window.matchMedia('(prefers-color-scheme: light)').matches
        ? 'light'
        : 'dark';
    document.documentElement.dataset.theme = savedTheme ?? preferredTheme;
})();

function toggleTheme() {
    const nextTheme = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = nextTheme;
    localStorage.setItem('theme', nextTheme);
    updateToggleIcon();
}

function updateToggleIcon() {
    const isLight = document.documentElement.dataset.theme === 'light';
    document.querySelectorAll('.theme-toggle').forEach(button => {
        button.textContent = isLight ? 'Dark theme' : 'Light theme';
        button.setAttribute('aria-label', `Switch to ${isLight ? 'dark' : 'light'} theme`);
    });
}

document.addEventListener('DOMContentLoaded', updateToggleIcon);

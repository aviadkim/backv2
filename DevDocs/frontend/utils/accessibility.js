/**
 * Accessibility Utilities
 * 
 * Provides utilities for improving application accessibility.
 */

/**
 * Initialize accessibility features
 * @param {Object} options - Accessibility options
 */
function initAccessibility(options = {}) {
  // Apply theme
  applyTheme(localStorage.getItem('theme') || 'light');
  
  // Apply high contrast if enabled
  if (localStorage.getItem('highContrast') === 'true') {
    document.documentElement.classList.add('high-contrast');
  }
  
  // Apply reduced motion if enabled
  if (localStorage.getItem('reducedMotion') === 'true') {
    document.documentElement.classList.add('reduced-motion');
  }
  
  // Apply font size
  applyFontSize(localStorage.getItem('fontSize') || 'medium');
  
  // Add ARIA roles to improve screen reader experience
  addAriaRoles();
  
  // Log initialization
  console.log('Accessibility features initialized');
}

/**
 * Apply theme
 * @param {string} theme - Theme name (light, dark, system)
 */
function applyTheme(theme) {
  // If theme is system, use system preference
  if (theme === 'system') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    theme = prefersDark ? 'dark' : 'light';
  }
  
  // Apply theme
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

/**
 * Apply font size
 * @param {string} size - Font size (small, medium, large, x-large)
 */
function applyFontSize(size) {
  let fontSize;
  
  switch (size) {
    case 'small':
      fontSize = '14px';
      break;
    case 'medium':
      fontSize = '16px';
      break;
    case 'large':
      fontSize = '18px';
      break;
    case 'x-large':
      fontSize = '20px';
      break;
    default:
      fontSize = '16px';
  }
  
  document.documentElement.style.fontSize = fontSize;
  localStorage.setItem('fontSize', size);
}

/**
 * Toggle high contrast mode
 * @param {boolean} enabled - Whether high contrast is enabled
 */
function toggleHighContrast(enabled) {
  if (enabled) {
    document.documentElement.classList.add('high-contrast');
  } else {
    document.documentElement.classList.remove('high-contrast');
  }
  
  localStorage.setItem('highContrast', enabled);
}

/**
 * Toggle reduced motion
 * @param {boolean} enabled - Whether reduced motion is enabled
 */
function toggleReducedMotion(enabled) {
  if (enabled) {
    document.documentElement.classList.add('reduced-motion');
  } else {
    document.documentElement.classList.remove('reduced-motion');
  }
  
  localStorage.setItem('reducedMotion', enabled);
}

/**
 * Add ARIA roles to improve screen reader experience
 */
function addAriaRoles() {
  // Add role="navigation" to navigation elements
  document.querySelectorAll('.sidebar-nav').forEach(nav => {
    nav.setAttribute('role', 'navigation');
    nav.setAttribute('aria-label', 'Main Navigation');
  });
  
  // Add role="main" to main content
  document.querySelectorAll('.main-content').forEach(main => {
    main.setAttribute('role', 'main');
  });
  
  // Add role="banner" to header
  document.querySelectorAll('.header').forEach(header => {
    header.setAttribute('role', 'banner');
  });
  
  // Add role="contentinfo" to footer
  document.querySelectorAll('.footer').forEach(footer => {
    footer.setAttribute('role', 'contentinfo');
  });
  
  // Add aria-current="page" to active navigation items
  document.querySelectorAll('.sidebar-nav .active a').forEach(link => {
    link.setAttribute('aria-current', 'page');
  });
}

/**
 * Get current accessibility settings
 * @returns {Object} - Accessibility settings
 */
function getAccessibilitySettings() {
  return {
    theme: localStorage.getItem('theme') || 'light',
    fontSize: localStorage.getItem('fontSize') || 'medium',
    highContrast: localStorage.getItem('highContrast') === 'true',
    reducedMotion: localStorage.getItem('reducedMotion') === 'true'
  };
}

// Export functions
export {
  initAccessibility,
  applyTheme,
  applyFontSize,
  toggleHighContrast,
  toggleReducedMotion,
  getAccessibilitySettings
};

/**
 * Keyboard Shortcuts Utility
 * 
 * Manages keyboard shortcuts for the application.
 */

// Default keyboard shortcuts
const DEFAULT_SHORTCUTS = [
  { id: 'save', key: 's', ctrl: true, description: 'Save the current document' },
  { id: 'new', key: 'n', ctrl: true, description: 'Create a new document' },
  { id: 'open', key: 'o', ctrl: true, description: 'Open a document' },
  { id: 'search', key: 'f', ctrl: true, description: 'Search within the document' },
  { id: 'help', key: 'F1', description: 'Open the help menu' },
  { id: 'settings', key: ',', ctrl: true, description: 'Open settings' },
  { id: 'fullscreen', key: 'F11', description: 'Toggle fullscreen mode' },
  { id: 'print', key: 'p', ctrl: true, description: 'Print the current document' },
  { id: 'undo', key: 'z', ctrl: true, description: 'Undo the last action' },
  { id: 'redo', key: 'y', ctrl: true, description: 'Redo the last action' }
];

// Shortcut handlers
const shortcutHandlers = {};

/**
 * Initialize keyboard shortcuts
 * @param {Object} options - Options for keyboard shortcuts
 */
function initKeyboardShortcuts(options = {}) {
  const enabled = localStorage.getItem('keyboardShortcutsEnabled');
  
  if (enabled === 'false') {
    return;
  }
  
  // Add event listener for keyboard shortcuts
  document.addEventListener('keydown', handleKeyDown);
  
  // Log initialization
  console.log('Keyboard shortcuts initialized');
}

/**
 * Handle keydown events
 * @param {KeyboardEvent} event - Keyboard event
 */
function handleKeyDown(event) {
  // Skip if target is an input, textarea, or select
  if (
    event.target.tagName === 'INPUT' ||
    event.target.tagName === 'TEXTAREA' ||
    event.target.tagName === 'SELECT'
  ) {
    return;
  }
  
  // Check for matching shortcuts
  DEFAULT_SHORTCUTS.forEach(shortcut => {
    const keyMatch = event.key === shortcut.key || 
                     event.key === shortcut.key.toUpperCase() ||
                     event.code === `Key${shortcut.key.toUpperCase()}` ||
                     event.code === shortcut.key;
    
    const ctrlMatch = shortcut.ctrl ? event.ctrlKey : true;
    const altMatch = shortcut.alt ? event.altKey : true;
    const shiftMatch = shortcut.shift ? event.shiftKey : true;
    
    if (keyMatch && ctrlMatch && altMatch && shiftMatch) {
      // Prevent default browser behavior
      event.preventDefault();
      
      // Execute handler if registered
      if (shortcutHandlers[shortcut.id]) {
        shortcutHandlers[shortcut.id](event);
      } else {
        console.log(`Keyboard shortcut triggered: ${getShortcutDisplay(shortcut)} (${shortcut.description})`);
      }
    }
  });
}

/**
 * Register a shortcut handler
 * @param {string} id - Shortcut ID
 * @param {Function} handler - Handler function
 */
function registerShortcutHandler(id, handler) {
  shortcutHandlers[id] = handler;
}

/**
 * Get display text for a shortcut
 * @param {Object} shortcut - Shortcut object
 * @returns {string} - Display text
 */
function getShortcutDisplay(shortcut) {
  let display = '';
  
  if (shortcut.ctrl) {
    display += 'Ctrl+';
  }
  
  if (shortcut.alt) {
    display += 'Alt+';
  }
  
  if (shortcut.shift) {
    display += 'Shift+';
  }
  
  display += shortcut.key.toUpperCase();
  
  return display;
}

/**
 * Get all keyboard shortcuts
 * @returns {Array} - Array of shortcut objects
 */
function getAllShortcuts() {
  return DEFAULT_SHORTCUTS.map(shortcut => ({
    ...shortcut,
    display: getShortcutDisplay(shortcut)
  }));
}

/**
 * Enable or disable keyboard shortcuts
 * @param {boolean} enabled - Whether shortcuts are enabled
 */
function setShortcutsEnabled(enabled) {
  localStorage.setItem('keyboardShortcutsEnabled', enabled);
  
  if (enabled) {
    document.addEventListener('keydown', handleKeyDown);
  } else {
    document.removeEventListener('keydown', handleKeyDown);
  }
}

// Export functions
export {
  initKeyboardShortcuts,
  registerShortcutHandler,
  getAllShortcuts,
  setShortcutsEnabled
};

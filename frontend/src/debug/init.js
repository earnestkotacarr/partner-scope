/**
 * Debug Mode Initialization
 *
 * This file exposes debug utilities to the browser console for easy access.
 * Import this file in main.jsx to enable console access.
 *
 * Console usage:
 *   window.debug.enable()   - Enable debug mode
 *   window.debug.disable()  - Disable debug mode
 *   window.debug.toggle()   - Toggle debug mode
 *   window.debug.status()   - Check current status
 *   window.debug.getData()  - Get generated fake data
 */

import {
  isDebugMode,
  enableDebugMode,
  disableDebugMode,
  toggleDebugMode,
  debugSettings,
  setDebugSetting,
} from './config';

import { generateFakeData } from './fakeData';

// Expose debug utilities to window for console access
if (typeof window !== 'undefined') {
  window.debug = {
    // Enable debug mode
    enable: () => {
      console.log('[Debug] Enabling debug mode...');
      enableDebugMode();
    },

    // Disable debug mode
    disable: () => {
      console.log('[Debug] Disabling debug mode...');
      disableDebugMode();
    },

    // Toggle debug mode
    toggle: () => {
      console.log('[Debug] Toggling debug mode...');
      toggleDebugMode();
    },

    // Check current status
    status: () => {
      const enabled = isDebugMode();
      console.log('[Debug] Debug mode is:', enabled ? 'ENABLED' : 'DISABLED');
      console.log('[Debug] Settings:', debugSettings);
      return { enabled, settings: debugSettings };
    },

    // Get generated fake data
    getData: (candidatesCount = 10, seed = 42) => {
      const data = generateFakeData(candidatesCount, seed);
      console.log('[Debug] Generated fake data:', data);
      return data;
    },

    // Update a setting
    setSetting: (key, value) => {
      setDebugSetting(key, value);
      console.log(`[Debug] Setting ${key} = ${value}`);
    },

    // Quick enable for specific page
    goTo: (page) => {
      if (!isDebugMode()) {
        localStorage.setItem('debug_mode', 'true');
      }
      localStorage.setItem('debug_start_page', page);
      window.location.href = page;
    },

    // Help
    help: () => {
      console.log(`
Debug Mode Commands:
--------------------
window.debug.enable()     - Enable debug mode (page will reload)
window.debug.disable()    - Disable debug mode (page will reload)
window.debug.toggle()     - Toggle debug mode
window.debug.status()     - Check current debug status
window.debug.getData()    - Get generated fake data
window.debug.setSetting(key, value) - Update a debug setting
window.debug.goTo('/path') - Navigate to a page in debug mode

Available Pages:
  /          - Landing page
  /chat      - Discovery chat
  /review    - Template review
  /results   - Search results
  /evaluate  - AI evaluation

Example:
  window.debug.enable()   // Enable debug mode
  window.debug.goTo('/evaluate')  // Go directly to evaluation page
      `);
    },
  };

  // Log availability on load
  if (import.meta.env.DEV) {
    console.log('[Debug] Debug utilities available. Type window.debug.help() for commands.');
  }
}

export default window.debug;

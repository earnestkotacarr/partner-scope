/**
 * Frontend Debug Configuration
 *
 * Controls debug mode behavior and settings for the frontend.
 * Allows direct navigation to any page with pre-populated fake data.
 */

// Check if debug mode is enabled via environment variable or localStorage
export const isDebugMode = () => {
  // Check environment variable (set during build)
  if (import.meta.env.VITE_DEBUG_MODE === 'true') {
    return true;
  }

  // Check localStorage (can be toggled at runtime)
  if (typeof window !== 'undefined') {
    return localStorage.getItem('debug_mode') === 'true';
  }

  return false;
};

// Enable debug mode at runtime
export const enableDebugMode = () => {
  localStorage.setItem('debug_mode', 'true');
  window.location.reload();
};

// Disable debug mode at runtime
export const disableDebugMode = () => {
  localStorage.removeItem('debug_mode');
  window.location.reload();
};

// Toggle debug mode
export const toggleDebugMode = () => {
  if (isDebugMode()) {
    disableDebugMode();
  } else {
    enableDebugMode();
  }
};

// Debug settings
export const debugSettings = {
  // Which page to start on (null = normal flow)
  startPage: localStorage.getItem('debug_start_page') || null,

  // Number of fake candidates to generate
  fakeCandidatesCount: parseInt(localStorage.getItem('debug_candidates_count') || '10', 10),

  // Whether to show the debug panel
  showDebugPanel: localStorage.getItem('debug_show_panel') !== 'false',

  // Random seed for reproducible data
  seed: parseInt(localStorage.getItem('debug_seed') || '42', 10),
};

// Update a debug setting
export const setDebugSetting = (key, value) => {
  localStorage.setItem(`debug_${key}`, String(value));
  debugSettings[key] = value;
};

// Available pages for debug navigation
export const debugPages = [
  { path: '/', name: 'Landing', description: 'Home page' },
  { path: '/chat', name: 'Discovery Chat', description: 'AI chat for discovery' },
  { path: '/review', name: 'Template Review', description: 'Review & start search' },
  { path: '/results', name: 'Results', description: 'Search results' },
  { path: '/evaluate', name: 'Evaluation', description: 'AI partner evaluation' },
];

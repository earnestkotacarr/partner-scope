/**
 * useDebugMode Hook
 *
 * Provides debug mode state and controls for components.
 * Automatically initializes context with fake data when in debug mode.
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { isDebugMode, enableDebugMode, disableDebugMode, debugSettings, setDebugSetting, debugPages } from '../debug/config';
import { generateFakeData } from '../debug/fakeData';

/**
 * Hook for managing debug mode in components
 */
export function useDebugMode() {
  const [enabled, setEnabled] = useState(isDebugMode());
  const [settings, setSettings] = useState(debugSettings);

  // Listen for storage changes (debug mode toggled in another tab)
  useEffect(() => {
    const handleStorageChange = () => {
      setEnabled(isDebugMode());
      setSettings({ ...debugSettings });
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const toggle = useCallback(() => {
    if (enabled) {
      disableDebugMode();
    } else {
      enableDebugMode();
    }
  }, [enabled]);

  const updateSetting = useCallback((key, value) => {
    setDebugSetting(key, value);
    setSettings(prev => ({ ...prev, [key]: value }));
  }, []);

  return {
    enabled,
    settings,
    toggle,
    updateSetting,
    pages: debugPages,
  };
}

/**
 * Hook to initialize context with debug data
 * Call this in components that need pre-populated data in debug mode
 */
export function useDebugDataInitializer(contextSetters) {
  const { enabled, settings } = useDebugMode();
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (!enabled || initialized) return;

    const {
      setScenario,
      setResults,
      setChatHistory,
      setSessionCosts,
    } = contextSetters;

    // Generate fake data
    const fakeData = generateFakeData(settings.fakeCandidatesCount, settings.seed);

    // Initialize context with fake data
    if (setScenario) setScenario(fakeData.scenario);
    if (setResults) setResults(fakeData.results);
    if (setChatHistory) setChatHistory(fakeData.chatHistory);
    if (setSessionCosts) setSessionCosts([{
      total_cost: 0.05,
      input_tokens: 1500,
      output_tokens: 2000,
      web_search_calls: 3,
      operation: 'debug_init',
      timestamp: new Date().toISOString(),
    }]);

    setInitialized(true);
    console.log('[Debug Mode] Context initialized with fake data');
  }, [enabled, initialized, settings, contextSetters]);

  return { initialized, enabled };
}

/**
 * Hook for debug navigation
 * Provides functions to navigate to any page with appropriate fake data
 */
export function useDebugNavigation() {
  const navigate = useNavigate();
  const { enabled, settings } = useDebugMode();

  const navigateToPage = useCallback((path, additionalState = {}) => {
    if (!enabled) {
      console.warn('[Debug] Debug mode is not enabled');
      navigate(path);
      return;
    }

    const fakeData = generateFakeData(settings.fakeCandidatesCount, settings.seed);

    // Prepare state based on target page
    let state = {};

    switch (path) {
      case '/evaluate':
        state = {
          candidates: fakeData.candidates,
          startupProfile: fakeData.startupProfile,
          ...additionalState,
        };
        break;
      case '/results':
        // Results page reads from context, no state needed
        break;
      case '/review':
        // Review page reads from context, no state needed
        break;
      default:
        break;
    }

    navigate(path, { state });
    console.log(`[Debug] Navigating to ${path}`, state);
  }, [enabled, settings, navigate]);

  return {
    enabled,
    navigateToPage,
    pages: debugPages,
  };
}

export default useDebugMode;

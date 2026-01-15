import { useState, useCallback, useRef, useEffect } from 'react';

// Timeout constants
const PROGRESS_TIMEOUT = 120000; // 2 minutes without any progress event (web search can be slow)
const MAX_SEARCH_TIMEOUT = 300000; // 5 minutes maximum for entire search

/**
 * Custom hook for streaming search with real-time cost updates via SSE.
 *
 * @param {Object} options
 * @param {Function} options.onProgress - Called with progress updates (phase, cost, etc.)
 * @param {Function} options.onComplete - Called when search completes with results
 * @param {Function} options.onError - Called if an error occurs
 *
 * @returns {Object} { startSearch, cancelSearch, isSearching, progress, error }
 */
export function useStreamingSearch({ onProgress, onComplete, onError } = {}) {
  const [isSearching, setIsSearching] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);
  const eventSourceRef = useRef(null);
  const progressTimeoutRef = useRef(null);
  const maxTimeoutRef = useRef(null);
  const isActiveRef = useRef(false); // Track if search is active (avoids stale closure issues)

  // Clear all timeouts helper
  const clearTimeouts = useCallback(() => {
    if (progressTimeoutRef.current) {
      clearTimeout(progressTimeoutRef.current);
      progressTimeoutRef.current = null;
    }
    if (maxTimeoutRef.current) {
      clearTimeout(maxTimeoutRef.current);
      maxTimeoutRef.current = null;
    }
  }, []);

  const cancelSearch = useCallback(() => {
    clearTimeouts();
    isActiveRef.current = false;
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsSearching(false);
    setProgress(null);
  }, [clearTimeouts]);

  // Reset progress timeout (called on each progress event)
  const resetProgressTimeout = useCallback((onTimeoutFn) => {
    if (progressTimeoutRef.current) {
      clearTimeout(progressTimeoutRef.current);
    }
    progressTimeoutRef.current = setTimeout(() => {
      console.warn('[Search] Progress timeout - no events received');
      onTimeoutFn?.();
    }, PROGRESS_TIMEOUT);
  }, []);

  const startSearch = useCallback(async (searchParams) => {
    // Cancel any existing search
    cancelSearch();
    setError(null);
    setIsSearching(true);
    isActiveRef.current = true;
    setProgress({ phase: 'starting', message: 'Initializing search...', cost: null });

    // Helper to handle timeout
    const handleTimeout = (message) => {
      clearTimeouts();
      isActiveRef.current = false;
      setError(message);
      setIsSearching(false);
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      onError?.(new Error(message));
    };

    try {
      // Build query string from search params
      const params = new URLSearchParams({
        startup_name: searchParams.startup_name || '',
        investment_stage: searchParams.investment_stage || '',
        product_stage: searchParams.product_stage || '',
        partner_needs: searchParams.partner_needs || '',
        industry: searchParams.industry || '',
        description: searchParams.description || '',
        max_results: String(searchParams.max_results || 20),
        use_csv: String(searchParams.use_csv !== false),
        use_web_search: String(searchParams.use_web_search === true),
      });

      const url = `/api/search/stream?${params.toString()}`;
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // Set up max timeout (3 minutes total)
      maxTimeoutRef.current = setTimeout(() => {
        console.warn('[Search] Max timeout reached');
        handleTimeout('Search timed out. Please try again with different search criteria.');
      }, MAX_SEARCH_TIMEOUT);

      // Set up initial progress timeout
      resetProgressTimeout(() => {
        handleTimeout('Search appears to be stuck. Please try again.');
      });

      eventSource.addEventListener('progress', (event) => {
        try {
          const data = JSON.parse(event.data);
          setProgress(data);
          onProgress?.(data);
          // Reset progress timeout on each progress event
          resetProgressTimeout(() => {
            handleTimeout('Search appears to be stuck. Please try again.');
          });
        } catch (e) {
          console.error('Failed to parse progress event:', e);
        }
      });

      eventSource.addEventListener('complete', (event) => {
        clearTimeouts();
        isActiveRef.current = false;
        try {
          const data = JSON.parse(event.data);
          setIsSearching(false);
          setProgress(null);
          eventSource.close();
          eventSourceRef.current = null;
          onComplete?.(data);
        } catch (e) {
          console.error('Failed to parse complete event:', e);
          setError('Failed to parse search results');
          onError?.(e);
        }
      });

      eventSource.addEventListener('error', (event) => {
        clearTimeouts();
        isActiveRef.current = false;
        try {
          const data = JSON.parse(event.data);
          setError(data.error || 'Search failed');
          onError?.(new Error(data.error));
        } catch (e) {
          // SSE connection error
          setError('Connection error');
          onError?.(e);
        }
        setIsSearching(false);
        eventSource.close();
        eventSourceRef.current = null;
      });

      // Handle connection errors
      eventSource.onerror = (e) => {
        // Check if it's a normal close after complete (use ref instead of stale state)
        if (!isActiveRef.current && eventSourceRef.current === null) {
          return;
        }
        clearTimeouts();
        isActiveRef.current = false;
        console.error('SSE error:', e);
        setError('Connection lost');
        setIsSearching(false);
        eventSource.close();
        eventSourceRef.current = null;
        onError?.(new Error('Connection lost'));
      };

    } catch (e) {
      clearTimeouts();
      isActiveRef.current = false;
      console.error('Failed to start search:', e);
      setError(e.message);
      setIsSearching(false);
      onError?.(e);
    }
  }, [cancelSearch, clearTimeouts, resetProgressTimeout, onProgress, onComplete, onError]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearTimeouts();
      isActiveRef.current = false;
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [clearTimeouts]);

  return {
    startSearch,
    cancelSearch,
    isSearching,
    progress,
    error,
  };
}

export default useStreamingSearch;

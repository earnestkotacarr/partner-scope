import { useState, useCallback, useRef } from 'react';

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

  const cancelSearch = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsSearching(false);
    setProgress(null);
  }, []);

  const startSearch = useCallback(async (searchParams) => {
    // Cancel any existing search
    cancelSearch();
    setError(null);
    setIsSearching(true);
    setProgress({ phase: 'starting', message: 'Initializing search...', cost: null });

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

      eventSource.addEventListener('progress', (event) => {
        try {
          const data = JSON.parse(event.data);
          setProgress(data);
          onProgress?.(data);
        } catch (e) {
          console.error('Failed to parse progress event:', e);
        }
      });

      eventSource.addEventListener('complete', (event) => {
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
        // Check if it's a normal close after complete
        if (!isSearching && eventSourceRef.current === null) {
          return;
        }
        console.error('SSE error:', e);
        setError('Connection lost');
        setIsSearching(false);
        eventSource.close();
        eventSourceRef.current = null;
        onError?.(new Error('Connection lost'));
      };

    } catch (e) {
      console.error('Failed to start search:', e);
      setError(e.message);
      setIsSearching(false);
      onError?.(e);
    }
  }, [cancelSearch, onProgress, onComplete, onError]);

  return {
    startSearch,
    cancelSearch,
    isSearching,
    progress,
    error,
  };
}

export default useStreamingSearch;

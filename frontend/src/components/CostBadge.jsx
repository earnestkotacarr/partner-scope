import { useState, useEffect } from 'react';

/**
 * Floating cost badge that displays running API costs.
 * Shows in bottom-right corner with expandable breakdown.
 */
export default function CostBadge({ cost, isSearching = false }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showPulse, setShowPulse] = useState(false);
  const [prevCost, setPrevCost] = useState(0);

  // Pulse animation when cost increases
  useEffect(() => {
    const totalCost = cost?.total_cost || 0;
    if (totalCost > prevCost) {
      setShowPulse(true);
      const timer = setTimeout(() => setShowPulse(false), 500);
      setPrevCost(totalCost);
      return () => clearTimeout(timer);
    }
  }, [cost?.total_cost, prevCost]);

  // Don't show if no cost data
  if (!cost && !isSearching) {
    return null;
  }

  const totalCost = cost?.total_cost || 0;
  const inputTokens = cost?.input_tokens || 0;
  const outputTokens = cost?.output_tokens || 0;
  const webSearchCalls = cost?.web_search_calls || 0;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Expanded breakdown panel */}
      {isExpanded && (
        <div className="mb-2 bg-slate-800 text-white rounded-lg shadow-xl p-4 min-w-64 animate-in fade-in slide-in-from-bottom-2">
          <div className="flex justify-between items-center mb-3 border-b border-slate-600 pb-2">
            <h3 className="font-semibold">Cost Breakdown</h3>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-slate-400 hover:text-white"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-400">Input tokens:</span>
              <span>{inputTokens.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Output tokens:</span>
              <span>{outputTokens.toLocaleString()}</span>
            </div>
            {webSearchCalls > 0 && (
              <div className="flex justify-between">
                <span className="text-slate-400">Web searches:</span>
                <span>{webSearchCalls}</span>
              </div>
            )}
            <div className="flex justify-between pt-2 border-t border-slate-600 font-semibold">
              <span>Total cost:</span>
              <span className="text-green-400">${totalCost.toFixed(6)}</span>
            </div>
          </div>

          {cost?.input_cost !== undefined && (
            <div className="mt-3 pt-2 border-t border-slate-600 text-xs text-slate-400">
              <div className="flex justify-between">
                <span>Input cost:</span>
                <span>${(cost.input_cost || 0).toFixed(6)}</span>
              </div>
              <div className="flex justify-between">
                <span>Output cost:</span>
                <span>${(cost.output_cost || 0).toFixed(6)}</span>
              </div>
              {(cost.web_search_cost || 0) > 0 && (
                <div className="flex justify-between">
                  <span>Web search cost:</span>
                  <span>${(cost.web_search_cost || 0).toFixed(6)}</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Main badge */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`
          flex items-center gap-2 bg-slate-800 text-white
          rounded-full px-4 py-2 shadow-lg hover:bg-slate-700
          transition-all duration-200
          ${showPulse ? 'ring-2 ring-green-400 ring-opacity-75' : ''}
          ${isSearching ? 'animate-pulse' : ''}
        `}
      >
        {isSearching && (
          <svg className="w-4 h-4 animate-spin text-blue-400" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
        <span className="text-green-400 font-mono">$</span>
        <span className="font-mono">{totalCost.toFixed(4)}</span>
        <svg
          className={`w-4 h-4 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
        </svg>
      </button>
    </div>
  );
}

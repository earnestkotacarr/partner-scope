/**
 * ChatStrategyDisplay Component
 *
 * Inline strategy display for embedding in chat messages.
 * Shows evaluation dimensions and weights in a compact format.
 *
 * Design: Grayscale with bg-gray-50 background
 */

export default function ChatStrategyDisplay({ strategy }) {
  if (!strategy) return null;

  const dimensions = strategy.dimensions || [];
  const sortedDimensions = [...dimensions].sort((a, b) => a.priority - b.priority);

  return (
    <div className="mt-3 bg-gray-50 rounded-lg p-4 border border-gray-100">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-gray-800 text-sm">Evaluation Strategy</h4>
        <span className="text-xs text-gray-500">{dimensions.length} dimensions</span>
      </div>

      <div className="space-y-2">
        {sortedDimensions.map((dim, index) => {
          const percentage = Math.round(dim.weight * 100);
          const displayName = dim.dimension.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

          return (
            <div key={dim.dimension} className="flex items-center gap-3">
              <span className="text-xs text-gray-400 w-4">{index + 1}.</span>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-sm text-gray-700">{displayName}</span>
                  <span className="px-1.5 py-0.5 text-xs font-medium rounded bg-gray-200 text-gray-700">
                    {percentage}%
                  </span>
                </div>
                <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gray-800 transition-all duration-500"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {strategy.exclusion_criteria && strategy.exclusion_criteria.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <span className="text-xs font-medium text-gray-500">Exclusions: </span>
          {strategy.exclusion_criteria.map((c, i) => (
            <span key={i} className="inline-block px-2 py-0.5 bg-gray-200 text-gray-600 text-xs rounded mr-1">
              {c}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

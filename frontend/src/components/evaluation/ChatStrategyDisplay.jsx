/**
 * ChatStrategyDisplay Component
 *
 * Inline strategy display for embedding in chat messages - OpenAI style.
 * Shows evaluation dimensions and weights in a clean, minimal format.
 */

export default function ChatStrategyDisplay({ strategy }) {
  if (!strategy) return null;

  const dimensions = strategy.dimensions || [];
  const sortedDimensions = [...dimensions].sort((a, b) => a.priority - b.priority);

  return (
    <div className="mt-4 bg-gray-50 rounded-xl p-4 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-medium text-gray-900 text-sm">Evaluation Strategy</h4>
        <span className="text-xs text-gray-400">{dimensions.length} dimensions</span>
      </div>

      <div className="space-y-3">
        {sortedDimensions.map((dim, index) => {
          const percentage = Math.round(dim.weight * 100);
          const displayName = dim.dimension.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

          return (
            <div key={dim.dimension} className="flex items-center gap-3">
              <span className="text-xs text-gray-400 w-4">{index + 1}.</span>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-700">{displayName}</span>
                  <span className="text-xs font-medium text-gray-500">
                    {percentage}%
                  </span>
                </div>
                <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gray-800 rounded-full transition-all duration-500"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {strategy.exclusion_criteria && strategy.exclusion_criteria.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <span className="text-xs font-medium text-gray-500">Exclusions: </span>
          <div className="flex flex-wrap gap-2 mt-2">
            {strategy.exclusion_criteria.map((c, i) => (
              <span key={i} className="inline-block px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                {c}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

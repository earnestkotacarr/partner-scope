/**
 * ChatStrategyDisplay Component
 *
 * Inline strategy display for embedding in chat messages.
 * Shows evaluation dimensions and weights in a compact format.
 */

const DIMENSION_COLORS = {
  market_compatibility: { bg: 'bg-blue-100', text: 'text-blue-700', bar: 'bg-blue-500' },
  financial_health: { bg: 'bg-green-100', text: 'text-green-700', bar: 'bg-green-500' },
  technical_synergy: { bg: 'bg-purple-100', text: 'text-purple-700', bar: 'bg-purple-500' },
  operational_capacity: { bg: 'bg-orange-100', text: 'text-orange-700', bar: 'bg-orange-500' },
  geographic_coverage: { bg: 'bg-cyan-100', text: 'text-cyan-700', bar: 'bg-cyan-500' },
  strategic_alignment: { bg: 'bg-indigo-100', text: 'text-indigo-700', bar: 'bg-indigo-500' },
  cultural_fit: { bg: 'bg-pink-100', text: 'text-pink-700', bar: 'bg-pink-500' },
  resource_complementarity: { bg: 'bg-yellow-100', text: 'text-yellow-700', bar: 'bg-yellow-500' },
  growth_potential: { bg: 'bg-emerald-100', text: 'text-emerald-700', bar: 'bg-emerald-500' },
  risk_profile: { bg: 'bg-red-100', text: 'text-red-700', bar: 'bg-red-500' },
};

export default function ChatStrategyDisplay({ strategy }) {
  if (!strategy) return null;

  const dimensions = strategy.dimensions || [];
  const sortedDimensions = [...dimensions].sort((a, b) => a.priority - b.priority);

  return (
    <div className="mt-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 border border-indigo-100">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-slate-800 text-sm">Evaluation Strategy</h4>
        <span className="text-xs text-slate-500">{dimensions.length} dimensions</span>
      </div>

      <div className="space-y-2">
        {sortedDimensions.map((dim, index) => {
          const colors = DIMENSION_COLORS[dim.dimension] || { bg: 'bg-gray-100', text: 'text-gray-700', bar: 'bg-gray-500' };
          const percentage = Math.round(dim.weight * 100);
          const displayName = dim.dimension.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

          return (
            <div key={dim.dimension} className="flex items-center gap-3">
              <span className="text-xs text-slate-400 w-4">{index + 1}.</span>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-sm text-slate-700">{displayName}</span>
                  <span className={`px-1.5 py-0.5 text-xs font-medium rounded ${colors.bg} ${colors.text}`}>
                    {percentage}%
                  </span>
                </div>
                <div className="h-1 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${colors.bar} transition-all duration-500`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {strategy.exclusion_criteria && strategy.exclusion_criteria.length > 0 && (
        <div className="mt-3 pt-3 border-t border-indigo-100">
          <span className="text-xs font-medium text-slate-500">Exclusions: </span>
          {strategy.exclusion_criteria.map((c, i) => (
            <span key={i} className="inline-block px-2 py-0.5 bg-red-50 text-red-600 text-xs rounded mr-1">
              {c}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

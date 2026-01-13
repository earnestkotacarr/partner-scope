/**
 * StrategyCard Component
 *
 * Displays the evaluation strategy with dimensions and weights.
 * Maps to the EvaluationStrategy data model.
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

export default function StrategyCard({ strategy }) {
  if (!strategy) return null;

  const dimensions = strategy.dimensions || [];
  const sortedDimensions = [...dimensions].sort((a, b) => a.priority - b.priority);

  return (
    <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-slate-200">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-slate-800 text-sm">Evaluation Strategy</h3>
          {strategy.confirmed_by_user && (
            <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
              Confirmed
            </span>
          )}
        </div>
        <p className="text-xs text-slate-500 mt-1">
          {dimensions.length} dimensions • {strategy.total_candidates} candidates
        </p>
      </div>

      {/* Dimensions */}
      <div className="p-4 space-y-3">
        {sortedDimensions.map((dim, index) => {
          const colors = DIMENSION_COLORS[dim.dimension] || { bg: 'bg-gray-100', text: 'text-gray-700', bar: 'bg-gray-500' };
          const percentage = Math.round(dim.weight * 100);
          const displayName = dim.dimension.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

          return (
            <div key={dim.dimension} className="group">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400 w-4">{index + 1}.</span>
                  <span className="text-sm text-slate-700">{displayName}</span>
                </div>
                <span className={`px-2 py-0.5 text-xs font-medium rounded ${colors.bg} ${colors.text}`}>
                  {percentage}%
                </span>
              </div>

              {/* Progress bar */}
              <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden ml-6">
                <div
                  className={`h-full ${colors.bar} transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                />
              </div>

              {/* Rationale on hover */}
              {dim.rationale && (
                <p className="text-xs text-slate-400 ml-6 mt-1 opacity-0 group-hover:opacity-100 transition-opacity line-clamp-2">
                  {dim.rationale}
                </p>
              )}
            </div>
          );
        })}
      </div>

      {/* Exclusion Criteria */}
      {strategy.exclusion_criteria && strategy.exclusion_criteria.length > 0 && (
        <div className="px-4 py-3 border-t border-slate-100 bg-slate-50">
          <h4 className="text-xs font-medium text-slate-500 mb-2">Exclusion Criteria</h4>
          <div className="flex flex-wrap gap-1">
            {strategy.exclusion_criteria.map((criterion, i) => (
              <span
                key={i}
                className="px-2 py-0.5 bg-red-50 text-red-600 text-xs rounded"
              >
                {criterion}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

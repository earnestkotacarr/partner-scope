/**
 * DimensionScoresCard Component
 *
 * Displays dimension scores for a specific candidate.
 * Maps to the DimensionScore data model.
 */

const DIMENSION_COLORS = {
  market_compatibility: { bar: 'bg-blue-500', light: 'bg-blue-50' },
  financial_health: { bar: 'bg-green-500', light: 'bg-green-50' },
  technical_synergy: { bar: 'bg-purple-500', light: 'bg-purple-50' },
  operational_capacity: { bar: 'bg-orange-500', light: 'bg-orange-50' },
  geographic_coverage: { bar: 'bg-cyan-500', light: 'bg-cyan-50' },
  strategic_alignment: { bar: 'bg-indigo-500', light: 'bg-indigo-50' },
  cultural_fit: { bar: 'bg-pink-500', light: 'bg-pink-50' },
  resource_complementarity: { bar: 'bg-yellow-500', light: 'bg-yellow-50' },
  growth_potential: { bar: 'bg-emerald-500', light: 'bg-emerald-50' },
  risk_profile: { bar: 'bg-red-500', light: 'bg-red-50' },
};

export default function DimensionScoresCard({ scores, candidateName }) {
  if (!scores || scores.length === 0) return null;

  // Sort by score descending
  const sortedScores = [...scores].sort((a, b) => (b.score || 0) - (a.score || 0));

  return (
    <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-emerald-50 to-teal-50 border-b border-slate-200">
        <h3 className="font-semibold text-slate-800 text-sm">Dimension Scores</h3>
        <p className="text-xs text-slate-500 mt-0.5">{candidateName}</p>
      </div>

      {/* Scores */}
      <div className="p-4 space-y-3">
        {sortedScores.map((ds, index) => {
          const dimension = ds.dimension || ds.dimension_name || 'unknown';
          const dimensionKey = dimension.toLowerCase().replace(/\s+/g, '_');
          const colors = DIMENSION_COLORS[dimensionKey] || { bar: 'bg-gray-500', light: 'bg-gray-50' };
          const score = Math.round(ds.score || 0);
          const confidence = ds.confidence || 0;
          const displayName = (ds.dimension_name || dimension).replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

          // Color based on score
          const scoreColor = score >= 80 ? 'text-green-600' :
                            score >= 60 ? 'text-yellow-600' :
                            'text-red-600';

          return (
            <div key={dimension} className="group">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-slate-700">{displayName}</span>
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-bold ${scoreColor}`}>
                    {score}
                  </span>
                  <span className="text-xs text-slate-400">
                    ({Math.round(confidence * 100)}%)
                  </span>
                </div>
              </div>

              {/* Progress bar */}
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full ${colors.bar} transition-all duration-500`}
                  style={{ width: `${score}%`, opacity: 0.3 + confidence * 0.7 }}
                />
              </div>

              {/* Evidence on hover */}
              {ds.evidence && ds.evidence.length > 0 && (
                <div className="mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <p className="text-xs text-slate-400">
                    {ds.evidence[0]}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="px-4 py-2 border-t border-slate-100 bg-slate-50">
        <div className="flex items-center justify-center gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            80+ High
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
            60-79 Medium
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500"></span>
            &lt;60 Low
          </span>
        </div>
      </div>
    </div>
  );
}

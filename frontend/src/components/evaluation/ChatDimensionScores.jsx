/**
 * ChatDimensionScores Component
 *
 * Compact dimension scores display for embedding in chat messages.
 */

const DIMENSION_COLORS = {
  market_compatibility: { bar: 'bg-blue-500' },
  financial_health: { bar: 'bg-green-500' },
  technical_synergy: { bar: 'bg-purple-500' },
  operational_capacity: { bar: 'bg-orange-500' },
  geographic_coverage: { bar: 'bg-cyan-500' },
  strategic_alignment: { bar: 'bg-indigo-500' },
  cultural_fit: { bar: 'bg-pink-500' },
  resource_complementarity: { bar: 'bg-yellow-500' },
  growth_potential: { bar: 'bg-emerald-500' },
  risk_profile: { bar: 'bg-red-500' },
};

export default function ChatDimensionScores({ scores, candidateName }) {
  if (!scores || scores.length === 0) return null;

  const sortedScores = [...scores].sort((a, b) => (b.score || 0) - (a.score || 0));

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="mt-3 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg p-4 border border-emerald-100">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-slate-800 text-sm">Dimension Scores</h4>
        <span className="text-xs text-slate-500">{candidateName}</span>
      </div>

      <div className="space-y-2">
        {sortedScores.map((ds) => {
          const dimension = ds.dimension || ds.dimension_name || 'unknown';
          const dimensionKey = dimension.toLowerCase().replace(/\s+/g, '_');
          const colors = DIMENSION_COLORS[dimensionKey] || { bar: 'bg-gray-500' };
          const score = Math.round(ds.score || 0);
          const confidence = ds.confidence || 0;
          const displayName = (ds.dimension_name || dimension).replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

          return (
            <div key={dimension}>
              <div className="flex items-center justify-between mb-0.5">
                <span className="text-sm text-slate-700">{displayName}</span>
                <div className="flex items-center gap-1">
                  <span className={`text-sm font-bold ${getScoreColor(score)}`}>
                    {score}
                  </span>
                  <span className="text-xs text-slate-400">
                    ({Math.round(confidence * 100)}%)
                  </span>
                </div>
              </div>
              <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${colors.bar} transition-all duration-500`}
                  style={{ width: `${score}%`, opacity: 0.4 + confidence * 0.6 }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-3 pt-2 border-t border-emerald-100 flex items-center justify-center gap-4 text-xs text-slate-500">
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
  );
}

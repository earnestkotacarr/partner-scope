/**
 * EvaluationInsightsCard Component
 *
 * Displays insights and analysis from the evaluation.
 * Maps to the EvaluationResult.insights data model.
 */

export default function EvaluationInsightsCard({ insights, conflicts }) {
  if ((!insights || insights.length === 0) && (!conflicts || conflicts.length === 0)) {
    return null;
  }

  return (
    <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-violet-50 to-purple-50 border-b border-slate-200">
        <h3 className="font-semibold text-slate-800 text-sm">Evaluation Insights</h3>
      </div>

      {/* Insights */}
      {insights && insights.length > 0 && (
        <div className="p-4">
          <ul className="space-y-2">
            {insights.map((insight, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <svg className="w-4 h-4 text-indigo-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-slate-600">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Conflicts Resolved */}
      {conflicts && conflicts.length > 0 && (
        <div className="px-4 py-3 border-t border-slate-100 bg-amber-50">
          <h4 className="text-xs font-medium text-amber-800 mb-2">Conflicts Resolved</h4>
          <ul className="space-y-2">
            {conflicts.map((conflict, index) => (
              <li key={index} className="text-xs text-amber-700">
                <span className="font-medium">{conflict.candidate}:</span> {conflict.conflict}
                {conflict.resolution && (
                  <span className="text-amber-600"> → {conflict.resolution}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

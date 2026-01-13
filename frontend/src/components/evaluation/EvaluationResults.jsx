/**
 * EvaluationResults Component
 *
 * Displays detailed evaluation results from the Supervisor Agent.
 * Shows multi-dimensional scores, insights, and allows refinement.
 *
 * Phase 3 of the evaluation framework.
 */

import React, { useState } from 'react';

const DIMENSION_COLORS = {
  market_compatibility: 'bg-blue-500',
  financial_health: 'bg-green-500',
  technical_synergy: 'bg-purple-500',
  operational_capacity: 'bg-orange-500',
  geographic_coverage: 'bg-cyan-500',
  strategic_alignment: 'bg-indigo-500',
  cultural_fit: 'bg-pink-500',
  resource_complementarity: 'bg-yellow-500',
  growth_potential: 'bg-emerald-500',
  risk_profile: 'bg-red-500',
};

export default function EvaluationResults({
  result,
  onExcludeCandidate,
  onAdjustWeight,
  onRefine,
  isRefining,
}) {
  const [refinementInput, setRefinementInput] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  if (!result) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-gray-500">
          No evaluation results available
        </div>
      </div>
    );
  }

  const { top_candidates, summary, insights, conflicts_resolved, strategy } = result;

  const handleRefine = async () => {
    if (!refinementInput.trim()) return;
    await onRefine?.(refinementInput);
    setRefinementInput('');
  };

  const handleExclude = async (candidateId, candidateName) => {
    if (window.confirm(`Are you sure you want to exclude "${candidateName}" from the results?`)) {
      await onExcludeCandidate?.(candidateId, `User excluded: ${candidateName}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Summary Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Evaluation Summary
        </h2>
        {summary && (
          <p className="text-gray-600">{summary}</p>
        )}

        {/* Insights */}
        {insights && insights.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Key Insights</h3>
            <ul className="space-y-1">
              {insights.map((insight, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                  <span className="text-blue-500 mt-1">•</span>
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Conflicts Resolved */}
        {conflicts_resolved && conflicts_resolved.length > 0 && (
          <div className="mt-4 p-4 bg-amber-50 rounded-lg">
            <h3 className="text-sm font-medium text-amber-800 mb-2">
              Conflicts Resolved
            </h3>
            <ul className="space-y-2">
              {conflicts_resolved.map((conflict, i) => (
                <li key={i} className="text-sm text-amber-700">
                  <strong>{conflict.candidate}:</strong> {conflict.conflict}
                  {conflict.resolution && (
                    <span className="text-amber-600"> → {conflict.resolution}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Top Candidates */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold text-gray-900">
            Top Recommended Partners
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Ranked by weighted multi-dimensional evaluation
          </p>
        </div>

        <div className="divide-y">
          {top_candidates?.map((candidate, index) => (
            <CandidateCard
              key={candidate.candidate_id}
              candidate={candidate}
              rank={index + 1}
              isSelected={selectedCandidate === candidate.candidate_id}
              onSelect={() => setSelectedCandidate(
                selectedCandidate === candidate.candidate_id ? null : candidate.candidate_id
              )}
              onExclude={() => handleExclude(candidate.candidate_id, candidate.candidate_name)}
              strategy={strategy}
            />
          ))}
        </div>
      </div>

      {/* Refinement Panel */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-sm font-medium text-gray-700 mb-2">
          Refine Results
        </h3>
        <p className="text-xs text-gray-500 mb-3">
          Examples: "Remove competitors", "Focus more on cultural fit",
          "Show only companies in Asia"
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={refinementInput}
            onChange={(e) => setRefinementInput(e.target.value)}
            placeholder="Enter refinement request..."
            className="flex-1 px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isRefining}
          />
          <button
            onClick={handleRefine}
            disabled={isRefining || !refinementInput.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRefining ? 'Refining...' : 'Refine'}
          </button>
        </div>
      </div>
    </div>
  );
}

function CandidateCard({ candidate, rank, isSelected, onSelect, onExclude, strategy }) {
  const {
    candidate_name,
    candidate_info,
    final_score,
    dimension_scores,
    strengths,
    weaknesses,
    recommendations,
    flags,
  } = candidate;

  const scoreColor = final_score >= 80 ? 'text-green-600 bg-green-100' :
                     final_score >= 60 ? 'text-yellow-600 bg-yellow-100' :
                     'text-red-600 bg-red-100';

  return (
    <div className={`p-6 transition-colors ${isSelected ? 'bg-blue-50' : 'hover:bg-gray-50'}`}>
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-8 h-8 bg-gray-100 rounded-full text-gray-600 font-bold">
            {rank}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {candidate_name}
            </h3>
            {candidate_info && (
              <p className="text-sm text-gray-500">
                {candidate_info.industry} • {candidate_info.location}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className={`px-3 py-1 rounded-lg font-bold ${scoreColor}`}>
            {Math.round(final_score)}
          </div>
          <button
            onClick={onSelect}
            className="p-1 text-gray-400 hover:text-gray-600"
            title="Show details"
          >
            <svg className={`w-5 h-5 transition-transform ${isSelected ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Dimension Scores Bar */}
      {dimension_scores && dimension_scores.length > 0 && (
        <div className="mt-4">
          <div className="flex h-2 rounded-full overflow-hidden bg-gray-100">
            {dimension_scores.map((ds, i) => {
              const weight = strategy?.dimensions?.find(d => d.dimension === ds.dimension)?.weight || 0.1;
              const color = DIMENSION_COLORS[ds.dimension] || 'bg-gray-400';
              return (
                <div
                  key={i}
                  className={`${color} transition-all`}
                  style={{ width: `${weight * 100}%`, opacity: ds.score / 100 }}
                  title={`${ds.dimension_name || ds.dimension}: ${Math.round(ds.score)}`}
                />
              );
            })}
          </div>
          <div className="flex justify-between mt-1">
            {dimension_scores.slice(0, 4).map((ds, i) => (
              <span key={i} className="text-xs text-gray-400">
                {(ds.dimension_name || ds.dimension).split('_').map(w => w[0].toUpperCase()).join('')}: {Math.round(ds.score)}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Flags */}
      {flags && flags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {flags.map((flag, i) => (
            <span key={i} className="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded">
              {flag}
            </span>
          ))}
        </div>
      )}

      {/* Expanded Details */}
      {isSelected && (
        <div className="mt-4 pt-4 border-t space-y-4">
          {/* Dimension Details */}
          {dimension_scores && dimension_scores.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Dimension Scores
              </h4>
              <div className="grid grid-cols-2 gap-2">
                {dimension_scores.map((ds, i) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-xs text-gray-600">
                      {ds.dimension_name || ds.dimension.replace(/_/g, ' ')}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-medium ${
                        ds.score >= 80 ? 'text-green-600' :
                        ds.score >= 60 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {Math.round(ds.score)}
                      </span>
                      <span className="text-xs text-gray-400">
                        ({Math.round(ds.confidence * 100)}%)
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Strengths */}
          {strengths && strengths.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-green-700 mb-1">Strengths</h4>
              <ul className="space-y-1">
                {strengths.map((s, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start gap-1">
                    <span className="text-green-500">+</span> {s}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Weaknesses */}
          {weaknesses && weaknesses.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-red-700 mb-1">Weaknesses</h4>
              <ul className="space-y-1">
                {weaknesses.map((w, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start gap-1">
                    <span className="text-red-500">-</span> {w}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {recommendations && recommendations.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-blue-700 mb-1">Recommendations</h4>
              <ul className="space-y-1">
                {recommendations.map((r, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start gap-1">
                    <span className="text-blue-500">→</span> {r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-2">
            <button
              onClick={onExclude}
              className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded"
            >
              Exclude
            </button>
            {candidate_info?.website && (
              <a
                href={candidate_info.website}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
              >
                Visit Website →
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
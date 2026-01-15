/**
 * ChatRankingDisplay Component
 *
 * Inline ranking display for chat - OpenAI style.
 * Shows top 3 with expandable full list.
 */

import { useState } from 'react';

export default function ChatRankingDisplay({ candidates, onCandidateClick }) {
  const [expanded, setExpanded] = useState(false);

  if (!candidates || candidates.length === 0) return null;

  const displayCount = expanded ? candidates.length : 3;
  const hasMore = candidates.length > 3;

  // Score color
  const getScoreStyle = (score) => {
    if (score >= 80) return 'text-gray-900 bg-gray-100';
    if (score >= 60) return 'text-gray-700 bg-gray-100';
    return 'text-gray-500 bg-gray-50';
  };

  return (
    <div className="mt-4 bg-gray-50 rounded-xl border border-gray-100 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h4 className="font-medium text-gray-900 text-sm">Candidate Rankings</h4>
        <p className="text-xs text-gray-400 mt-0.5">{candidates.length} partners evaluated</p>
      </div>

      <div className="divide-y divide-gray-100">
        {candidates.slice(0, displayCount).map((candidate, index) => {
          const rank = candidate.rank || index + 1;
          const score = Math.round(candidate.final_score || 0);

          return (
            <button
              key={candidate.candidate_id || index}
              onClick={() => onCandidateClick?.(candidate)}
              className="w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-100 transition-colors text-left"
            >
              {/* Rank Badge */}
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0 ${
                rank === 1 ? 'bg-gray-900 text-white' :
                rank === 2 ? 'bg-gray-600 text-white' :
                rank === 3 ? 'bg-gray-400 text-white' :
                'bg-gray-200 text-gray-600'
              }`}>
                {rank}
              </div>

              {/* Candidate Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {candidate.candidate_name}
                </p>
                {candidate.candidate_info && (
                  <p className="text-xs text-gray-500 truncate">
                    {candidate.candidate_info.industry || 'N/A'} • {candidate.candidate_info.location || 'N/A'}
                  </p>
                )}
              </div>

              {/* Score */}
              <div className={`px-2 py-1 rounded-full text-xs font-medium flex-shrink-0 ${getScoreStyle(score)}`}>
                {score}
              </div>

              {/* Arrow */}
              <svg className="w-4 h-4 text-gray-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          );
        })}
      </div>

      {/* Expand/Collapse Button */}
      {hasMore && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full px-4 py-2.5 text-sm text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors border-t border-gray-100 flex items-center justify-center gap-1"
        >
          {expanded ? (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
              Show less
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
              Show all {candidates.length} candidates
            </>
          )}
        </button>
      )}
    </div>
  );
}

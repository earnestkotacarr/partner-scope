/**
 * ChatRankingDisplay Component
 *
 * Inline ranking display for chat - shows top 3 with expandable full list.
 * Clicking a company opens the detail modal.
 */

import { useState } from 'react';

export default function ChatRankingDisplay({ candidates, onCandidateClick }) {
  const [expanded, setExpanded] = useState(false);

  if (!candidates || candidates.length === 0) return null;

  const displayCount = expanded ? candidates.length : 3;
  const hasMore = candidates.length > 3;

  // Rank badge colors
  const getRankColor = (rank) => {
    if (rank === 1) return 'bg-amber-400 text-white';
    if (rank === 2) return 'bg-slate-400 text-white';
    if (rank === 3) return 'bg-amber-600 text-white';
    return 'bg-slate-200 text-slate-600';
  };

  // Score color
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="mt-3 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg border border-amber-100 overflow-hidden">
      <div className="px-4 py-3 border-b border-amber-100">
        <h4 className="font-semibold text-slate-800 text-sm">Candidate Rankings</h4>
        <p className="text-xs text-slate-500">{candidates.length} partners evaluated</p>
      </div>

      <div className="divide-y divide-amber-100">
        {candidates.slice(0, displayCount).map((candidate, index) => {
          const rank = candidate.rank || index + 1;
          const score = Math.round(candidate.final_score || 0);

          return (
            <button
              key={candidate.candidate_id || index}
              onClick={() => onCandidateClick?.(candidate)}
              className="w-full px-4 py-3 flex items-center gap-3 hover:bg-amber-50/50 transition-colors text-left"
            >
              {/* Rank Badge */}
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${getRankColor(rank)}`}>
                {rank}
              </div>

              {/* Candidate Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-800 truncate">
                  {candidate.candidate_name}
                </p>
                {candidate.candidate_info && (
                  <p className="text-xs text-slate-500 truncate">
                    {candidate.candidate_info.industry || 'N/A'} • {candidate.candidate_info.location || 'N/A'}
                  </p>
                )}
              </div>

              {/* Score */}
              <div className={`px-2 py-1 rounded text-xs font-bold flex-shrink-0 ${getScoreColor(score)}`}>
                {score}
              </div>

              {/* Arrow */}
              <svg className="w-4 h-4 text-slate-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
          className="w-full px-4 py-2 text-sm text-amber-700 hover:bg-amber-100/50 transition-colors border-t border-amber-100 flex items-center justify-center gap-1"
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

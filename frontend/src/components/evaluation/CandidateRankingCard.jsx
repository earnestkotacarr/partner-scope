/**
 * CandidateRankingCard Component
 *
 * Displays ranked list of candidates with final scores.
 * Maps to the CandidateEvaluation data model.
 */

export default function CandidateRankingCard({ candidates, selectedId, onSelect }) {
  if (!candidates || candidates.length === 0) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-amber-50 to-orange-50 border-b border-slate-200">
        <h3 className="font-semibold text-slate-800 text-sm">Candidate Rankings</h3>
        <p className="text-xs text-slate-500 mt-0.5">Top {candidates.length} partners</p>
      </div>

      {/* Candidates List */}
      <div className="divide-y divide-slate-100">
        {candidates.slice(0, 10).map((candidate, index) => {
          const rank = candidate.rank || index + 1;
          const score = Math.round(candidate.final_score || 0);
          const isSelected = candidate.candidate_id === selectedId;

          // Score color
          const scoreColor = score >= 80 ? 'bg-green-100 text-green-700' :
                            score >= 60 ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700';

          // Rank badge color
          const rankColor = rank === 1 ? 'bg-amber-400 text-white' :
                           rank === 2 ? 'bg-slate-400 text-white' :
                           rank === 3 ? 'bg-amber-600 text-white' :
                           'bg-slate-200 text-slate-600';

          return (
            <button
              key={candidate.candidate_id}
              onClick={() => onSelect?.(candidate)}
              className={`w-full px-4 py-3 flex items-center gap-3 hover:bg-slate-50 transition-colors text-left ${
                isSelected ? 'bg-indigo-50 border-l-2 border-indigo-500' : ''
              }`}
            >
              {/* Rank Badge */}
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${rankColor}`}>
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
              <div className={`px-2 py-1 rounded text-xs font-bold ${scoreColor}`}>
                {score}
              </div>

              {/* Flags indicator */}
              {candidate.flags && candidate.flags.length > 0 && (
                <div className="w-2 h-2 rounded-full bg-amber-400" title={candidate.flags.join(', ')} />
              )}
            </button>
          );
        })}
      </div>

      {/* More indicator */}
      {candidates.length > 10 && (
        <div className="px-4 py-2 text-center text-xs text-slate-400 bg-slate-50 border-t border-slate-100">
          +{candidates.length - 10} more candidates
        </div>
      )}
    </div>
  );
}

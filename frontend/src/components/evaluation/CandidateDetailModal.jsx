/**
 * CandidateDetailModal Component
 *
 * Full-screen modal showing detailed candidate information - OpenAI style.
 * Clean, minimal design with white background and subtle borders.
 */

import { useEffect } from 'react';

export default function CandidateDetailModal({ candidate, onClose }) {
  // Handle ESC key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose?.();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!candidate) return null;

  const info = candidate.candidate_info || {};
  const scores = candidate.dimension_scores || [];
  const sortedScores = [...scores].sort((a, b) => (b.score || 0) - (a.score || 0));
  const finalScore = Math.round(candidate.final_score || 0);

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-gray-900';
    if (score >= 60) return 'text-gray-700';
    return 'text-gray-500';
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative min-h-screen flex items-start justify-center p-4 pt-10">
        <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-3xl overflow-hidden">
          {/* Header */}
          <div className="px-6 py-5 border-b border-gray-100">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700">
                    #{candidate.rank}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium bg-gray-900 text-white`}>
                    Score: {finalScore}
                  </span>
                  {candidate.flags && candidate.flags.length > 0 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                      {candidate.flags.length} flags
                    </span>
                  )}
                </div>
                <h2 className="text-xl font-semibold text-gray-900">{candidate.candidate_name}</h2>
                <p className="text-gray-500 text-sm mt-1">
                  {info.industry || 'N/A'} • {info.location || 'N/A'}
                </p>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors text-gray-400 hover:text-gray-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 max-h-[70vh] overflow-y-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Column: Search Data */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-4 flex items-center gap-2">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Company Information
                </h3>

                {/* Company Description */}
                {info.description && (
                  <div className="mb-4">
                    <p className="text-sm text-gray-600 leading-relaxed">{info.description}</p>
                  </div>
                )}

                {/* Key Info Grid */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {info.industry && (
                    <div className="bg-gray-50 rounded-xl p-3">
                      <p className="text-xs text-gray-400">Industry</p>
                      <p className="text-sm font-medium text-gray-800">{info.industry}</p>
                    </div>
                  )}
                  {info.location && (
                    <div className="bg-gray-50 rounded-xl p-3">
                      <p className="text-xs text-gray-400">Location</p>
                      <p className="text-sm font-medium text-gray-800">{info.location}</p>
                    </div>
                  )}
                  {info.founded && (
                    <div className="bg-gray-50 rounded-xl p-3">
                      <p className="text-xs text-gray-400">Founded</p>
                      <p className="text-sm font-medium text-gray-800">{info.founded}</p>
                    </div>
                  )}
                  {info.employees && (
                    <div className="bg-gray-50 rounded-xl p-3">
                      <p className="text-xs text-gray-400">Employees</p>
                      <p className="text-sm font-medium text-gray-800">{info.employees}</p>
                    </div>
                  )}
                  {info.funding_total && (
                    <div className="bg-gray-50 rounded-xl p-3">
                      <p className="text-xs text-gray-400">Total Funding</p>
                      <p className="text-sm font-medium text-gray-800">{info.funding_total}</p>
                    </div>
                  )}
                  {info.last_funding_date && (
                    <div className="bg-gray-50 rounded-xl p-3">
                      <p className="text-xs text-gray-400">Last Funding</p>
                      <p className="text-sm font-medium text-gray-800">{info.last_funding_date}</p>
                    </div>
                  )}
                </div>

                {/* Website */}
                {info.website && (
                  <a
                    href={info.website.startsWith('http') ? info.website : `https://${info.website}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors text-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    Visit Website
                  </a>
                )}
              </div>

              {/* Right Column: AI Evaluation */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-4 flex items-center gap-2">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  AI Evaluation
                </h3>

                {/* Dimension Scores */}
                <div className="mb-4 bg-gray-50 rounded-xl p-4">
                  <h4 className="text-xs font-medium text-gray-500 mb-3">Dimension Scores</h4>
                  <div className="space-y-3">
                    {sortedScores.map((ds) => {
                      const dimension = ds.dimension || ds.dimension_name || 'unknown';
                      const score = Math.round(ds.score || 0);
                      const displayName = (ds.dimension_name || dimension).replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                      return (
                        <div key={dimension}>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs text-gray-600">{displayName}</span>
                            <span className={`text-xs font-medium ${getScoreColor(score)}`}>
                              {score}
                            </span>
                          </div>
                          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gray-800 rounded-full"
                              style={{ width: `${score}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Strengths */}
                {candidate.strengths && candidate.strengths.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-xs font-medium text-gray-500 mb-2 flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Strengths
                    </h4>
                    <ul className="space-y-1.5">
                      {candidate.strengths.map((s, i) => (
                        <li key={i} className="text-sm text-gray-700 bg-gray-50 px-3 py-2 rounded-lg">
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Weaknesses */}
                {candidate.weaknesses && candidate.weaknesses.length > 0 && (
                  <div className="mb-4">
                    <h4 className="text-xs font-medium text-gray-500 mb-2 flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      Weaknesses
                    </h4>
                    <ul className="space-y-1.5">
                      {candidate.weaknesses.map((w, i) => (
                        <li key={i} className="text-sm text-gray-700 bg-gray-50 px-3 py-2 rounded-lg">
                          {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {candidate.recommendations && candidate.recommendations.length > 0 && (
                  <div>
                    <h4 className="text-xs font-medium text-gray-500 mb-2 flex items-center gap-1">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      Recommendations
                    </h4>
                    <ul className="space-y-1.5">
                      {candidate.recommendations.map((r, i) => (
                        <li key={i} className="text-sm text-gray-700 bg-gray-50 px-3 py-2 rounded-lg">
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Flags */}
                {candidate.flags && candidate.flags.length > 0 && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-xl border border-gray-100">
                    <h4 className="text-xs font-medium text-gray-500 mb-2">Flags</h4>
                    <div className="flex flex-wrap gap-2">
                      {candidate.flags.map((f, i) => (
                        <span key={i} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end">
            <button
              onClick={onClose}
              className="px-5 py-2 bg-gray-900 text-white text-sm font-medium rounded-full hover:bg-gray-800 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

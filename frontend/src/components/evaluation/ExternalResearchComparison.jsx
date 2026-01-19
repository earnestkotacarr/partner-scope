/**
 * ExternalResearchComparison Component
 *
 * Allows users to paste results from external deep research tools
 * (Gemini, OpenAI, Claude) and compare them against PartnerScope results
 * using the same evaluation criteria.
 *
 * Design: Expandable section with side-by-side vertical comparison
 */

import { useState } from 'react';

export default function ExternalResearchComparison({
  partnerScopeResults,
  startupProfile,
  strategy,
  onCandidateClick,
}) {
  const [isExpanded, setIsExpanded] = useState(true); // Start expanded so users can see it
  const [externalText, setExternalText] = useState('');
  const [source, setSource] = useState('gemini');
  const [externalResults, setExternalResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Calculate top-8 average for a result set
  const calculateTop8Avg = (candidates) => {
    if (!candidates || candidates.length === 0) return 0;
    const scores = candidates.slice(0, 8).map(c => c.final_score || 0);
    return scores.reduce((a, b) => a + b, 0) / scores.length;
  };

  // Calculate overall average
  const calculateAvg = (candidates) => {
    if (!candidates || candidates.length === 0) return 0;
    const scores = candidates.map(c => c.final_score || 0);
    return scores.reduce((a, b) => a + b, 0) / scores.length;
  };

  // Handle evaluating external results
  const handleEvaluate = async () => {
    if (!externalText.trim()) {
      setError('Please paste external research results first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/compare/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: externalText,
          source: source,
          startup_profile: startupProfile,
          strategy: strategy,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to evaluate external results');
      }

      const data = await response.json();
      setExternalResults(data);
    } catch (err) {
      console.error('Comparison error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Clear comparison
  const handleClear = () => {
    setExternalResults(null);
    setExternalText('');
    setError(null);
  };

  // Get source display name
  const getSourceName = (src) => {
    switch (src) {
      case 'gemini': return 'Gemini Deep Research';
      case 'openai': return 'OpenAI Deep Research';
      case 'claude': return 'Claude Deep Research';
      default: return 'External Research';
    }
  };

  // Score badge color
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-gray-900 bg-gray-100';
    if (score >= 60) return 'text-gray-700 bg-gray-100';
    return 'text-gray-500 bg-gray-100';
  };

  // Rank badge color
  const getRankColor = (rank) => {
    if (rank === 1) return 'bg-gray-900 text-white';
    if (rank === 2) return 'bg-gray-600 text-white';
    if (rank === 3) return 'bg-gray-400 text-white';
    return 'bg-gray-200 text-gray-600';
  };

  const psTop8 = calculateTop8Avg(partnerScopeResults?.top_candidates || []);
  const psAvg = calculateAvg(partnerScopeResults?.top_candidates || []);
  const extTop8 = externalResults ? calculateTop8Avg(externalResults.evaluation_result?.top_candidates || []) : 0;
  const extAvg = externalResults ? calculateAvg(externalResults.evaluation_result?.top_candidates || []) : 0;

  return (
    <div className="mt-4 bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header - Always visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span className="font-medium text-gray-800">Compare with External Research</span>
          {externalResults && (
            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
              Comparison ready
            </span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-200">
          {/* Input Section */}
          {!externalResults && (
            <div className="p-4 space-y-4">
              <p className="text-sm text-gray-600">
                Paste results from Gemini, OpenAI, or Claude deep research to compare against PartnerScope using the same evaluation criteria.
              </p>

              {/* Source Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
                <select
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400"
                >
                  <option value="gemini">Gemini Deep Research</option>
                  <option value="openai">OpenAI Deep Research</option>
                  <option value="claude">Claude Deep Research</option>
                  <option value="external">Other</option>
                </select>
              </div>

              {/* Text Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Research Results
                </label>
                <textarea
                  value={externalText}
                  onChange={(e) => setExternalText(e.target.value)}
                  placeholder="Paste the full research output here..."
                  rows={8}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-400 resize-y text-sm"
                />
              </div>

              {/* Error Display */}
              {error && (
                <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
                  {error}
                </div>
              )}

              {/* Evaluate Button */}
              <button
                onClick={handleEvaluate}
                disabled={loading || !externalText.trim()}
                className="w-full py-2 px-4 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    Parsing & Evaluating...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Parse & Evaluate
                  </>
                )}
              </button>
            </div>
          )}

          {/* Comparison Results */}
          {externalResults && (
            <div className="p-4">
              {/* Side-by-Side Score Summary */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                {/* PartnerScope Column */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-6 h-6 bg-gray-900 rounded flex items-center justify-center">
                      <span className="text-white text-xs font-bold">PS</span>
                    </div>
                    <h4 className="font-semibold text-gray-800 text-sm">PartnerScope</h4>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-600">Top-8 Avg</span>
                      <span className={`text-lg font-bold ${psTop8 >= 80 ? 'text-gray-900' : psTop8 >= 60 ? 'text-gray-700' : 'text-gray-500'}`}>
                        {psTop8.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-600">Overall Avg</span>
                      <span className="text-sm font-medium text-gray-600">{psAvg.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-600">Companies</span>
                      <span className="text-sm text-gray-600">{partnerScopeResults?.top_candidates?.length || 0}</span>
                    </div>
                  </div>
                </div>

                {/* External Column */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-6 h-6 bg-gray-600 rounded flex items-center justify-center">
                      <span className="text-white text-xs font-bold">{source.charAt(0).toUpperCase()}</span>
                    </div>
                    <h4 className="font-semibold text-gray-800 text-sm">{getSourceName(source)}</h4>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-600">Top-8 Avg</span>
                      <span className={`text-lg font-bold ${extTop8 >= 80 ? 'text-gray-900' : extTop8 >= 60 ? 'text-gray-700' : 'text-gray-500'}`}>
                        {extTop8.toFixed(1)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-600">Overall Avg</span>
                      <span className="text-sm font-medium text-gray-600">{extAvg.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-600">Companies</span>
                      <span className="text-sm text-gray-600">{externalResults.evaluation_result?.top_candidates?.length || 0}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Score Difference */}
              <div className="bg-gray-100 rounded-lg p-3 mb-4 text-center">
                <span className="text-sm text-gray-600">Top-8 Score Difference: </span>
                <span className={`font-bold ${psTop8 > extTop8 ? 'text-gray-900' : psTop8 < extTop8 ? 'text-gray-600' : 'text-gray-500'}`}>
                  {psTop8 > extTop8 ? '+' : ''}{(psTop8 - extTop8).toFixed(1)}
                  {psTop8 > extTop8 ? ' (PartnerScope leads)' : psTop8 < extTop8 ? ` (${getSourceName(source)} leads)` : ' (Tied)'}
                </span>
              </div>

              {/* Side-by-Side Candidate Lists */}
              <div className="grid grid-cols-2 gap-4">
                {/* PartnerScope Candidates */}
                <div>
                  <h5 className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">PartnerScope Results</h5>
                  <div className="space-y-2">
                    {(partnerScopeResults?.top_candidates || []).slice(0, 8).map((candidate, index) => {
                      const rank = candidate.rank || index + 1;
                      const score = Math.round(candidate.final_score || 0);
                      return (
                        <button
                          key={candidate.candidate_id || index}
                          onClick={() => onCandidateClick?.(candidate)}
                          className="w-full p-2 flex items-center gap-2 hover:bg-gray-50 rounded-lg transition-colors text-left border border-gray-100"
                        >
                          <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${getRankColor(rank)}`}>
                            {rank}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-medium text-gray-800 truncate">
                              {candidate.candidate_name}
                            </p>
                          </div>
                          <div className={`px-1.5 py-0.5 rounded text-xs font-bold flex-shrink-0 ${getScoreColor(score)}`}>
                            {score}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* External Candidates */}
                <div>
                  <h5 className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">{getSourceName(source)}</h5>
                  <div className="space-y-2">
                    {(externalResults.evaluation_result?.top_candidates || []).slice(0, 8).map((candidate, index) => {
                      const rank = candidate.rank || index + 1;
                      const score = Math.round(candidate.final_score || 0);
                      return (
                        <button
                          key={candidate.candidate_id || index}
                          onClick={() => onCandidateClick?.(candidate)}
                          className="w-full p-2 flex items-center gap-2 hover:bg-gray-50 rounded-lg transition-colors text-left border border-gray-100"
                        >
                          <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${getRankColor(rank)}`}>
                            {rank}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-medium text-gray-800 truncate">
                              {candidate.candidate_name}
                            </p>
                          </div>
                          <div className={`px-1.5 py-0.5 rounded text-xs font-bold flex-shrink-0 ${getScoreColor(score)}`}>
                            {score}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Clear Button */}
              <button
                onClick={handleClear}
                className="mt-4 w-full py-2 px-4 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 flex items-center justify-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Compare Different Source
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

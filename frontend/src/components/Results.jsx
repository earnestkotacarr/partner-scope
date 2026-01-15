import { useState, useRef, useEffect } from 'react'

// Info score criteria explanation
const INFO_SCORE_CRITERIA = [
  { name: 'Company Name', maxPoints: 5, description: 'Basic identification' },
  { name: 'Website URL', maxPoints: 20, description: 'Direct link available (+5 if not just Crunchbase)' },
  { name: 'Description', maxPoints: 30, description: 'Quality and length of company description' },
  { name: 'Industry', maxPoints: 15, description: 'Industry classification (+5 if multiple)' },
  { name: 'Location', maxPoints: 15, description: 'Geographic information (+5 if detailed)' },
  { name: 'Company Size', maxPoints: 10, description: 'Employee count or size category' },
  { name: 'Social Presence', maxPoints: 5, description: 'LinkedIn, Twitter, or other profiles' },
]

// Score Popover Component
function ScorePopover({ isOpen, onClose, type, match, strategy, anchorRef }) {
  const popoverRef = useRef(null)

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target) &&
          anchorRef.current && !anchorRef.current.contains(e.target)) {
        onClose()
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen, onClose, anchorRef])

  if (!isOpen) return null

  const formatDimensionName = (name) => {
    return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  }

  return (
    <div
      ref={popoverRef}
      className="absolute z-50 top-full mt-2 right-0 w-72 bg-white rounded-xl shadow-xl border border-gray-200 p-4 animate-in fade-in slide-in-from-top-2 duration-200"
    >
      {/* Arrow */}
      <div className="absolute -top-2 right-6 w-4 h-4 bg-white border-l border-t border-gray-200 transform rotate-45" />

      {type === 'fit' ? (
        <>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h4 className="font-bold text-gray-900">Fit Score</h4>
              <p className="text-xs text-gray-500">AI-evaluated partnership fit</p>
            </div>
          </div>

          {match.fit_score != null ? (
            <>
              <p className="text-xs text-gray-600 mb-3">
                Based on multi-dimensional analysis of how well this partner aligns with your needs.
              </p>

              {/* Show dimension scores if available */}
              {match.evaluation?.dimension_scores && (
                <div className="space-y-2">
                  <p className="text-xs font-semibold text-gray-700 uppercase">Evaluation Criteria</p>
                  {match.evaluation.dimension_scores.map((dim, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <span className="text-xs text-gray-600 w-24 truncate" title={formatDimensionName(dim.dimension)}>
                        {formatDimensionName(dim.dimension)}
                      </span>
                      <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-black rounded-full"
                          style={{ width: `${dim.score}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-gray-700 w-6 text-right">
                        {Math.round(dim.score)}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Show strategy weights if available */}
              {strategy?.dimensions && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-xs font-semibold text-gray-700 uppercase mb-2">Dimension Weights</p>
                  {strategy.dimensions.map((dim, i) => (
                    <div key={i} className="flex items-center gap-2 mb-1">
                      <span className="text-xs text-gray-500 w-24 truncate">
                        {formatDimensionName(dim.dimension)}
                      </span>
                      <div className="flex-1 h-1 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${(dim.weight || 0) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 w-8 text-right">
                        {Math.round((dim.weight || 0) * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-4">
              <p className="text-gray-500 text-sm">Not yet evaluated</p>
              <p className="text-xs text-gray-400 mt-1">Run AI Evaluation to get a Fit Score</p>
            </div>
          )}
        </>
      ) : (
        <>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h4 className="font-bold text-gray-900">Info Score</h4>
              <p className="text-xs text-gray-500">Data completeness</p>
            </div>
          </div>

          <p className="text-xs text-gray-600 mb-3">
            How complete the available information is for this company. Higher = more actionable data.
          </p>

          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-700 uppercase">Scoring Criteria</p>
            {INFO_SCORE_CRITERIA.map((criterion, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span className="text-gray-600">{criterion.name}</span>
                <span className="text-gray-400">up to {criterion.maxPoints} pts</span>
              </div>
            ))}
          </div>

          <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
            Total possible: 100 points
          </div>
        </>
      )}

      <button
        onClick={onClose}
        className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}

const Results = ({ results, loading, error, compact = false, evaluationStrategy = null }) => {
  const Wrapper = ({ children }) => compact ? <>{children}</> : (
    <div className="bg-white rounded-xl shadow-lg p-8">{children}</div>
  )

  if (loading) {
    return (
      <Wrapper>
        <div className="flex flex-col items-center justify-center py-12">
          <svg className="animate-spin h-12 w-12 text-gray-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-lg text-gray-600">Searching for partners...</p>
          <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
        </div>
      </Wrapper>
    )
  }

  if (error) {
    return (
      <Wrapper>
        <div className="flex flex-col items-center justify-center py-12">
          <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      </Wrapper>
    )
  }

  if (!results) {
    return (
      <Wrapper>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <svg className="h-16 w-16 text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 className="text-lg font-medium text-black mb-2">No results yet</h3>
          <p className="text-gray-600">Fill out the form and click "Find Partners" to start searching</p>
        </div>
      </Wrapper>
    )
  }

  return (
    <Wrapper>
      {!compact && (
        <h2 className="text-2xl font-bold text-black mb-6">
          Partner Matches ({results.matches?.length || 0})
        </h2>
      )}

      {results.matches && results.matches.length > 0 ? (
        <div className={`space-y-4 ${compact ? '' : 'max-h-[calc(100vh-300px)] overflow-y-auto pr-2'}`}>
          {results.matches.map((match, index) => (
            <ResultCard key={index} match={match} strategy={evaluationStrategy} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-600">No matches found</p>
        </div>
      )}
    </Wrapper>
  )
}

// Individual Result Card component with evaluation support
function ResultCard({ match, strategy }) {
  const [expanded, setExpanded] = useState(false)
  const [activePopover, setActivePopover] = useState(null) // 'fit' | 'info' | null
  const fitScoreRef = useRef(null)
  const infoScoreRef = useRef(null)
  const hasEvaluation = !!match.evaluation

  return (
    <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition bg-white">
      {/* Company Header */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-xl font-bold text-black">
              {match.company_name}
            </h3>
            {/* Evaluation Rank Badge */}
            {hasEvaluation && (
              <span className="inline-flex items-center gap-1 text-xs bg-black text-white px-2 py-0.5 rounded-full font-medium">
                #{match.evaluation.rank}
              </span>
            )}
          </div>
          {match.company_info?.website && (
            <a
              href={match.company_info.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-gray-500 hover:text-black hover:underline block truncate"
              title={match.company_info.website}
            >
              {match.company_info.website.replace(/^https?:\/\/(www\.)?/, '').slice(0, 40)}
              {match.company_info.website.replace(/^https?:\/\/(www\.)?/, '').length > 40 ? '...' : ''}
            </a>
          )}
        </div>

        {/* Two Score Display - Clickable */}
        <div className="flex-shrink-0 flex gap-2 relative">
          {/* Fit Score (from AI evaluation) */}
          <div className="text-center relative" ref={fitScoreRef}>
            <button
              onClick={() => setActivePopover(activePopover === 'fit' ? null : 'fit')}
              className={`text-xl font-bold px-2.5 py-1 rounded-lg cursor-pointer transition-all hover:scale-105 ${
                match.fit_score != null
                  ? match.fit_score >= 80 ? 'bg-black text-white hover:bg-gray-800' :
                    match.fit_score >= 60 ? 'bg-gray-800 text-white hover:bg-gray-700' :
                    'bg-gray-600 text-white hover:bg-gray-500'
                  : 'bg-gray-200 text-gray-400 hover:bg-gray-300'
              }`}
              title="Click for details"
            >
              {match.fit_score != null ? Math.round(match.fit_score) : '—'}
            </button>
            <p className="text-xs text-gray-500 mt-1">Fit</p>
            <ScorePopover
              isOpen={activePopover === 'fit'}
              onClose={() => setActivePopover(null)}
              type="fit"
              match={match}
              strategy={strategy}
              anchorRef={fitScoreRef}
            />
          </div>

          {/* Info Score (data completeness) */}
          <div className="text-center relative" ref={infoScoreRef}>
            <button
              onClick={() => setActivePopover(activePopover === 'info' ? null : 'info')}
              className={`text-xl font-bold px-2.5 py-1 rounded-lg cursor-pointer transition-all hover:scale-105 ${
                (match.info_score ?? match.match_score) >= 80 ? 'bg-blue-100 text-blue-800 hover:bg-blue-200' :
                (match.info_score ?? match.match_score) >= 60 ? 'bg-blue-50 text-blue-700 hover:bg-blue-100' :
                'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
              title="Click for details"
            >
              {Math.round(match.info_score ?? match.match_score)}
            </button>
            <p className="text-xs text-gray-500 mt-1">Info</p>
            <ScorePopover
              isOpen={activePopover === 'info'}
              onClose={() => setActivePopover(null)}
              type="info"
              match={match}
              strategy={strategy}
              anchorRef={infoScoreRef}
            />
          </div>
        </div>
      </div>

      {/* Company Info Badges */}
      <div className="mb-3 flex flex-wrap gap-2">
        {hasEvaluation && (
          <span className="inline-flex items-center gap-1 text-xs bg-gray-900 text-white px-2 py-1 rounded-full font-medium">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            AI Evaluated
          </span>
        )}
        {match.company_info?.source && (
          <span className={`inline-block text-xs px-2 py-1 rounded-full font-medium ${
            match.company_info.source === 'AI Web Search'
              ? 'bg-gray-200 text-gray-700'
              : 'bg-gray-100 text-gray-600'
          }`}>
            {match.company_info.source}
          </span>
        )}
        {match.company_info?.industry && (
          <span className="inline-block bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full">
            {match.company_info.industry}
          </span>
        )}
        {match.company_info?.location && (
          <span className="inline-block bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full">
            {match.company_info.location}
          </span>
        )}
        {match.company_info?.size && (
          <span className="inline-block bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full">
            {match.company_info.size}
          </span>
        )}
      </div>

      {/* Company Description / Rationale */}
      <div className="mb-4">
        <p className="text-gray-700 text-sm leading-relaxed">
          {match.rationale || match.company_info?.description}
        </p>
      </div>

      {/* Expandable Company Details Section */}
      <div className="mb-4">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-black transition"
        >
          <svg
            className={`w-4 h-4 transition-transform ${expanded ? 'rotate-90' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <span className="font-medium">
            {hasEvaluation ? 'View Company Details & Partnership Insights' : 'View Company Details'}
          </span>
        </button>

        {expanded && (
          <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-4">
            {/* Contact Information */}
            {(match.company_info?.contact_name || match.company_info?.contact_email || match.company_info?.linkedin_url) && (
              <div>
                <p className="text-xs font-semibold text-gray-700 uppercase mb-2 flex items-center gap-1">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  Contact Information
                </p>
                <div className="space-y-1">
                  {match.company_info?.contact_name && (
                    <p className="text-sm text-gray-700">
                      <span className="text-gray-500">Point of Contact:</span> {match.company_info.contact_name}
                      {match.company_info?.contact_title && <span className="text-gray-400"> ({match.company_info.contact_title})</span>}
                    </p>
                  )}
                  {match.company_info?.contact_email && (
                    <p className="text-sm">
                      <a href={`mailto:${match.company_info.contact_email}`} className="text-blue-600 hover:underline">
                        {match.company_info.contact_email}
                      </a>
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Partnership Potentials (from evaluation) */}
            {hasEvaluation && match.evaluation.recommendations?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-700 uppercase mb-2 flex items-center gap-1">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Partnership Opportunities
                </p>
                <ul className="space-y-1">
                  {match.evaluation.recommendations.slice(0, 3).map((rec, i) => (
                    <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-green-500 mt-0.5">&#x2192;</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Strengths & Considerations */}
            {hasEvaluation && (match.evaluation.strengths?.length > 0 || match.evaluation.weaknesses?.length > 0) && (
              <div className="grid grid-cols-2 gap-4">
                {match.evaluation.strengths?.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-gray-700 uppercase mb-2 flex items-center gap-1">
                      <svg className="w-3.5 h-3.5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Key Strengths
                    </p>
                    <ul className="space-y-1">
                      {match.evaluation.strengths.slice(0, 3).map((s, i) => (
                        <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                          <span className="text-green-600">+</span> {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {match.evaluation.weaknesses?.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-gray-700 uppercase mb-2 flex items-center gap-1">
                      <svg className="w-3.5 h-3.5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      Considerations
                    </p>
                    <ul className="space-y-1">
                      {match.evaluation.weaknesses.slice(0, 3).map((w, i) => (
                        <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                          <span className="text-amber-600">!</span> {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Key Strengths (from search, shown if no evaluation) */}
            {!hasEvaluation && match.key_strengths?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-700 uppercase mb-2">Key Strengths</p>
                <ul className="space-y-1">
                  {match.key_strengths.map((strength, i) => (
                    <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-green-500">+</span> {strength}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Company Details */}
            <div>
              <p className="text-xs font-semibold text-gray-700 uppercase mb-2 flex items-center gap-1">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                Company Details
              </p>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {match.company_info?.industry && (
                  <div>
                    <span className="text-gray-500">Industry:</span>
                    <span className="ml-1 text-gray-700">{match.company_info.industry}</span>
                  </div>
                )}
                {match.company_info?.location && (
                  <div>
                    <span className="text-gray-500">Location:</span>
                    <span className="ml-1 text-gray-700">{match.company_info.location}</span>
                  </div>
                )}
                {match.company_info?.size && (
                  <div>
                    <span className="text-gray-500">Size:</span>
                    <span className="ml-1 text-gray-700">{match.company_info.size}</span>
                  </div>
                )}
                {match.company_info?.founded && (
                  <div>
                    <span className="text-gray-500">Founded:</span>
                    <span className="ml-1 text-gray-700">{match.company_info.founded}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Social Links */}
            {(match.company_info?.linkedin_url || match.company_info?.twitter_url || match.company_info?.website) && (
              <div className="flex gap-3 pt-2 border-t border-gray-200">
                {match.company_info?.website && (
                  <a
                    href={match.company_info.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    Website
                  </a>
                )}
                {match.company_info?.linkedin_url && (
                  <a
                    href={match.company_info.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                  >
                    LinkedIn
                  </a>
                )}
                {match.company_info?.twitter_url && (
                  <a
                    href={match.company_info.twitter_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                  >
                    Twitter
                  </a>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Recommended Action */}
      {match.recommended_action && (
        <div className="pt-3 border-t border-gray-200">
          <p className="text-sm">
            <span className="font-semibold text-gray-700">Next Step: </span>
            <span className="text-gray-600">{match.recommended_action}</span>
          </p>
        </div>
      )}
    </div>
  )
}

export default Results

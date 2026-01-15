import { useState } from 'react'

const Results = ({ results, loading, error, compact = false }) => {
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
            <ResultCard key={index} match={match} />
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
function ResultCard({ match }) {
  const [expanded, setExpanded] = useState(false)
  const hasEvaluation = !!match.evaluation

  // Format dimension name for display
  const formatDimensionName = (name) => {
    return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  }

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
        <div className="flex-shrink-0 text-center">
          <div className={`text-2xl font-bold px-3 py-1 rounded-lg ${
            match.match_score >= 80 ? 'bg-gray-100 text-black' :
            match.match_score >= 60 ? 'bg-gray-100 text-gray-700' :
            'bg-gray-100 text-gray-500'
          }`}>
            {Math.round(match.match_score)}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {hasEvaluation ? 'AI Score' : 'Score'}
          </p>
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
      </div>

      {/* Evaluation Dimension Scores (Expandable) */}
      {hasEvaluation && match.evaluation.dimension_scores && (
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
            <span className="font-medium">View Dimension Scores</span>
            <span className="text-gray-400">({match.evaluation.dimension_scores.length} dimensions)</span>
          </button>

          {expanded && (
            <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-3">
              {match.evaluation.dimension_scores.map((dim, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-xs text-gray-600 w-36 truncate" title={formatDimensionName(dim.dimension)}>
                    {formatDimensionName(dim.dimension)}
                  </span>
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-black rounded-full transition-all"
                      style={{ width: `${dim.score}%`, opacity: dim.confidence || 1 }}
                    />
                  </div>
                  <span className="text-xs font-medium text-gray-700 w-8 text-right">
                    {Math.round(dim.score)}
                  </span>
                </div>
              ))}

              {/* Evaluation Strengths/Weaknesses */}
              {(match.evaluation.strengths?.length > 0 || match.evaluation.weaknesses?.length > 0) && (
                <div className="pt-3 mt-3 border-t border-gray-200 grid grid-cols-2 gap-4">
                  {match.evaluation.strengths?.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-gray-600 mb-2">Strengths</p>
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
                      <p className="text-xs font-semibold text-gray-600 mb-2">Weaknesses</p>
                      <ul className="space-y-1">
                        {match.evaluation.weaknesses.slice(0, 3).map((w, i) => (
                          <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                            <span className="text-red-600">-</span> {w}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Rationale */}
      <div className="mb-4">
        <p className="text-gray-700 text-sm leading-relaxed">
          {match.rationale}
        </p>
      </div>

      {/* Key Strengths (from search, shown if no evaluation) */}
      {!hasEvaluation && match.key_strengths && match.key_strengths.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-600 uppercase mb-2">
            Key Strengths
          </p>
          <ul className="list-disc list-inside space-y-1">
            {match.key_strengths.map((strength, i) => (
              <li key={i} className="text-sm text-gray-700">{strength}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Potential Concerns (from search, shown if no evaluation) */}
      {!hasEvaluation && match.potential_concerns && match.potential_concerns.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-600 uppercase mb-2">
            Potential Concerns
          </p>
          <ul className="list-disc list-inside space-y-1">
            {match.potential_concerns.map((concern, i) => (
              <li key={i} className="text-sm text-gray-600">{concern}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommended Action */}
      {match.recommended_action && (
        <div className="pt-4 border-t border-gray-200">
          <p className="text-sm">
            <span className="font-semibold text-gray-700">Recommended Action: </span>
            <span className="text-gray-600">{match.recommended_action}</span>
          </p>
        </div>
      )}

      {/* Social Links */}
      {match.company_info && (match.company_info.linkedin_url || match.company_info.twitter_url || match.company_info.facebook_url) && (
        <div className="flex gap-3 mt-4">
          {match.company_info.linkedin_url && (
            <a
              href={match.company_info.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-black text-sm"
            >
              LinkedIn
            </a>
          )}
          {match.company_info.twitter_url && (
            <a
              href={match.company_info.twitter_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-black text-sm"
            >
              Twitter
            </a>
          )}
          {match.company_info.facebook_url && (
            <a
              href={match.company_info.facebook_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-black text-sm"
            >
              Facebook
            </a>
          )}
        </div>
      )}
    </div>
  )
}

export default Results

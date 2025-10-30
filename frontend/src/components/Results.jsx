const Results = ({ results, loading, error }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="flex flex-col items-center justify-center py-12">
          <svg className="animate-spin h-12 w-12 text-blue-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-lg text-slate-600">Searching for partners...</p>
          <p className="text-sm text-slate-500 mt-2">This may take a few moments</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="flex flex-col items-center justify-center py-12">
          <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <svg className="h-16 w-16 text-slate-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 className="text-lg font-medium text-slate-900 mb-2">No results yet</h3>
          <p className="text-slate-600">Fill out the form and click "Find Partners" to start searching</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-slate-900 mb-6">
        Partner Matches ({results.matches?.length || 0})
      </h2>

      {results.matches && results.matches.length > 0 ? (
        <div className="space-y-4 max-h-[calc(100vh-300px)] overflow-y-auto pr-2">
          {results.matches.map((match, index) => (
            <div
              key={index}
              className="border border-slate-200 rounded-lg p-6 hover:shadow-md transition"
            >
              {/* Company Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-slate-900 mb-1">
                    {match.company_name}
                  </h3>
                  {match.company_info?.website && (
                    <a
                      href={match.company_info.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline"
                    >
                      {match.company_info.website}
                    </a>
                  )}
                </div>
                <div className="flex-shrink-0 ml-4">
                  <div className={`text-2xl font-bold px-4 py-2 rounded-lg ${
                    match.match_score >= 80 ? 'bg-green-100 text-green-700' :
                    match.match_score >= 60 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {match.match_score}
                  </div>
                  <p className="text-xs text-slate-500 text-center mt-1">Score</p>
                </div>
              </div>

              {/* Company Info */}
              {match.company_info?.industry && (
                <div className="mb-3">
                  <span className="inline-block bg-slate-100 text-slate-700 text-sm px-3 py-1 rounded-full">
                    {match.company_info.industry}
                  </span>
                  {match.company_info?.location && (
                    <span className="inline-block bg-slate-100 text-slate-700 text-sm px-3 py-1 rounded-full ml-2">
                      📍 {match.company_info.location}
                    </span>
                  )}
                </div>
              )}

              {/* Rationale */}
              <div className="mb-4">
                <p className="text-slate-700 text-sm leading-relaxed">
                  {match.rationale}
                </p>
              </div>

              {/* Key Strengths */}
              {match.key_strengths && match.key_strengths.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs font-semibold text-slate-600 uppercase mb-2">
                    ✓ Key Strengths
                  </p>
                  <ul className="list-disc list-inside space-y-1">
                    {match.key_strengths.map((strength, i) => (
                      <li key={i} className="text-sm text-slate-700">{strength}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Potential Concerns */}
              {match.potential_concerns && match.potential_concerns.length > 0 && (
                <div className="mb-4">
                  <p className="text-xs font-semibold text-slate-600 uppercase mb-2">
                    ⚠ Potential Concerns
                  </p>
                  <ul className="list-disc list-inside space-y-1">
                    {match.potential_concerns.map((concern, i) => (
                      <li key={i} className="text-sm text-slate-600">{concern}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommended Action */}
              <div className="pt-4 border-t border-slate-200">
                <p className="text-sm">
                  <span className="font-semibold text-slate-700">Recommended Action: </span>
                  <span className="text-slate-600">{match.recommended_action}</span>
                </p>
              </div>

              {/* Social Links */}
              {match.company_info && (
                <div className="flex gap-3 mt-4">
                  {match.company_info.linkedin_url && (
                    <a
                      href={match.company_info.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 text-sm"
                    >
                      LinkedIn
                    </a>
                  )}
                  {match.company_info.twitter_url && (
                    <a
                      href={match.company_info.twitter_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 text-sm"
                    >
                      Twitter
                    </a>
                  )}
                  {match.company_info.facebook_url && (
                    <a
                      href={match.company_info.facebook_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 text-sm"
                    >
                      Facebook
                    </a>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-slate-600">No matches found</p>
        </div>
      )}
    </div>
  )
}

export default Results

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useScenario } from '../context/ScenarioContext'
import Results from '../components/Results'
import CostBadge from '../components/CostBadge'
import ExportDropdown from '../components/ExportDropdown'

function ResultsPage() {
  const navigate = useNavigate()
  const {
    results,
    setResults,
    scenario,
    chatHistory,
    sessionCosts,
    currentCost,
    isSearching,
    addCost,
    getCostSummary,
  } = useScenario()
  const [refinementInput, setRefinementInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [statusMessage, setStatusMessage] = useState(null)
  const [previousCount, setPreviousCount] = useState(null)

  // Redirect if no results
  useEffect(() => {
    if (!results) {
      navigate('/')
    }
  }, [results, navigate])

  // Auto-clear status message after 3 seconds
  useEffect(() => {
    if (statusMessage) {
      const timer = setTimeout(() => {
        setStatusMessage(null)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [statusMessage])

  const handleRefinement = async (e) => {
    e.preventDefault()
    if (!refinementInput.trim() || loading) return

    setPreviousCount(results.matches?.length || 0)
    setLoading(true)
    setStatusMessage(null)

    try {
      const response = await fetch('/api/chat/refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [],
          current_message: refinementInput,
          current_results: results.matches,
          scenario: scenario
        })
      })

      if (!response.ok) {
        throw new Error('Refinement failed')
      }

      const data = await response.json()
      console.log('[Refinement] API Response:', data)
      console.log('[Refinement] refined_results count:', data.refined_results?.length)
      console.log('[Refinement] action_taken:', data.action_taken)

      // Track cost from refinement
      if (data.cost) {
        addCost(data.cost, 'refinement')
      }

      // Update results - use functional update to ensure we have latest state
      if (data.refined_results) {
        const newCount = data.refined_results.length
        const oldCount = results.matches?.length || 0
        console.log('[Refinement] Updating results: old count =', oldCount, ', new count =', newCount)

        // Force new object reference to trigger re-render
        const timestamp = Date.now()
        setResults(prevResults => {
          console.log('[Refinement] setResults called, prevResults matches:', prevResults?.matches?.length)
          const newResults = {
            ...prevResults,
            matches: [...data.refined_results],  // Create new array reference
            total_matches: newCount,
            _lastUpdate: timestamp  // Force change detection
          }
          console.log('[Refinement] New results object:', newResults.matches?.length, 'matches, _lastUpdate:', timestamp)
          return newResults
        })

        // Show status message based on action
        if (data.action_taken === 'filtered') {
          const diff = oldCount - newCount
          if (diff > 0) {
            setStatusMessage(`Filtered: removed ${diff} results (${newCount} remaining)`)
          } else {
            setStatusMessage(`Filtered: ${newCount} results`)
          }
        } else if (data.action_taken === 'reordered') {
          setStatusMessage(`Reordered: ${newCount} results`)
        } else if (data.action_taken === 'narrowed') {
          setStatusMessage(`Narrowed to ${newCount} results`)
        } else if (data.action_taken === 'expanded') {
          const added = newCount - oldCount
          if (added > 0) {
            setStatusMessage(`Found ${added} new partners! Total: ${newCount}`)
          } else {
            setStatusMessage(`Search complete: ${newCount} results`)
          }
        } else if (data.action_taken === 'search') {
          setStatusMessage(`Searching for new partners...`)
        } else {
          setStatusMessage(`Updated: ${newCount} results`)
        }
      }

      setRefinementInput('')
    } catch (err) {
      setStatusMessage('Refinement failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (!results) {
    return null
  }

  // Get cost for display
  const displayCost = isSearching ? currentCost : getCostSummary()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-4 py-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-slate-900">Partner Scope</h1>
          <div className="flex items-center gap-4">
            <ExportDropdown
              scenario={scenario}
              results={results.matches || []}
              chatHistory={chatHistory}
              costs={sessionCosts}
            />
            <button
              onClick={() => navigate('/')}
              className="text-slate-600 hover:text-slate-800 font-medium"
            >
              Start Over
            </button>
          </div>
        </div>
      </div>

      {/* Main Content - Split View */}
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-140px)]">
          {/* Results Panel - Takes 2/3 of space */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-lg overflow-hidden flex flex-col">
            <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">
                Partner Results ({results.matches?.length || 0})
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {loading && (
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-2">
                  <svg className="w-4 h-4 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span className="text-blue-700 text-sm">
                    {refinementInput.toLowerCase().match(/find|search|look for|add more/)
                      ? 'Searching for new partners... (this may take a moment)'
                      : 'Refining results...'}
                  </span>
                </div>
              )}
              <Results
                key={`results-${results.matches?.length || 0}-${results._lastUpdate || 0}`}
                results={results}
                loading={false}
                error={null}
                compact
              />
            </div>
          </div>

          {/* Refinement Panel - Takes 1/3 of space */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden flex flex-col">
            <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">Refine Results</h2>
            </div>

            <div className="flex-1 p-4 flex flex-col">
              {/* Instructions */}
              <div className="mb-4 text-sm text-slate-600">
                <p className="mb-2 font-medium">Filter existing results:</p>
                <ul className="space-y-1 text-slate-500 mb-3">
                  <li>"Top 5 results"</li>
                  <li>"Remove consulting firms"</li>
                  <li>"Only show universities"</li>
                </ul>
                <p className="mb-2 font-medium">Search for new partners:</p>
                <ul className="space-y-1 text-slate-500">
                  <li>"Find more hospitals"</li>
                  <li>"Search for biotech companies"</li>
                  <li>"Look for partners in California"</li>
                </ul>
              </div>

              {/* Status Message */}
              {statusMessage && (
                <div className={`mb-4 p-3 rounded-lg text-sm font-medium transition-opacity ${
                  statusMessage.includes('failed')
                    ? 'bg-red-50 text-red-700'
                    : 'bg-green-50 text-green-700'
                }`}>
                  {statusMessage}
                </div>
              )}

              {/* Spacer to push input to bottom */}
              <div className="flex-1"></div>

              {/* Refinement Input */}
              <form onSubmit={handleRefinement} className="mt-auto">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={refinementInput}
                    onChange={(e) => setRefinementInput(e.target.value)}
                    placeholder="Type a refinement command..."
                    disabled={loading}
                    className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-100 disabled:cursor-not-allowed"
                  />
                  <button
                    type="submit"
                    disabled={loading || !refinementInput.trim()}
                    className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {loading ? (
                      <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    ) : (
                      'Refine'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Cost Badge */}
      <CostBadge cost={displayCost} isSearching={isSearching} />
    </div>
  )
}

export default ResultsPage

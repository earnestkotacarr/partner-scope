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
    saveResultsSnapshot,
    undoResults,
    canUndo,
    evaluationState,
    getModelConfig,
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
      const modelConfig = getModelConfig()
      const response = await fetch('/api/chat/refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [],
          current_message: refinementInput,
          current_results: results.matches,
          scenario: scenario,
          model_search: modelConfig.search
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

        // Save current results to history before updating (for undo)
        saveResultsSnapshot(data.action_taken || 'refinement')

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
        } else if (data.action_taken === 'refined') {
          setStatusMessage(`Re-searched with constraints: ${newCount} results`)
        } else if (data.action_taken === 'search') {
          setStatusMessage(`Searching for new partners...`)
        } else if (data.action_taken === 'undo') {
          // Handle undo - restore previous results from history
          if (undoResults) {
            undoResults()
            setStatusMessage('Restored previous results')
          } else {
            setStatusMessage('No previous results to restore')
          }
          return  // Don't update results, undo handler does it
        } else if (data.action_taken === 'clarify') {
          // Show clarification message without changing results
          setStatusMessage(data.response || 'Could you be more specific?')
          return  // Don't update results
        } else if (data.action_taken === 'search_failed') {
          setStatusMessage(data.response || 'No results found. Try different keywords.')
          return  // Keep current results
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

  const navigateToEvaluation = () => {
    navigate('/evaluate', {
      state: {
        candidates: results.matches || [],
        startupProfile: {
          name: scenario?.startup_name || 'My Startup',
          industry: scenario?.industry || '',
          stage: scenario?.investment_stage || 'Seed',
          partner_needs: scenario?.partner_needs || '',
          description: scenario?.description || '',
        }
      }
    })
  }

  return (
    <div className="min-h-screen bg-white text-black">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-semibold tracking-tight">Partner Scope</h1>
            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded-full">
              Step 1: Search
            </span>
          </div>
          <div className="flex items-center gap-4">
            <ExportDropdown
              scenario={scenario}
              results={results.matches || []}
              chatHistory={chatHistory}
              costs={sessionCosts}
              evaluationStrategy={evaluationState?.strategy}
            />
            <button
              onClick={() => navigate('/')}
              className="text-gray-500 hover:text-black font-medium transition-colors"
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
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
            <div className="px-4 py-3 bg-gray-50 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-medium text-black">
                    Search Results ({results.matches?.length || 0})
                  </h2>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Raw search matches - refine or proceed to AI evaluation
                  </p>
                </div>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {loading && (
                <div className="mb-4 p-3 bg-gray-50 border border-gray-200 rounded-lg flex items-center gap-2">
                  <svg className="w-4 h-4 animate-spin text-gray-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span className="text-gray-600 text-sm">
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

          {/* Right Column - CTA + Refinement */}
          <div className="flex flex-col gap-4">
            {/* Next Step CTA */}
            <div className="p-4 bg-black rounded-2xl shadow-sm">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-white/10 rounded-lg">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-white text-sm">Ready for deep analysis?</h3>
                  <p className="text-xs text-gray-400 mt-1 mb-3">
                    Step 2: Multi-agent AI will evaluate each candidate across customizable dimensions
                  </p>
                  <button
                    onClick={navigateToEvaluation}
                    className="w-full px-4 py-2.5 bg-white hover:bg-gray-100 text-black font-medium rounded-full transition-colors flex items-center justify-center gap-2 text-sm"
                  >
                    Start AI Evaluation
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            {/* Refinement Panel */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col flex-1 min-w-0">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-100">
                <h2 className="font-medium text-black">Refine Search</h2>
              </div>

              <div className="flex-1 p-4 flex flex-col min-w-0">
                {/* Instructions */}
                <div className="mb-4 text-sm text-gray-600">
                  <p className="mb-2 font-medium">Filter existing results:</p>
                  <ul className="space-y-1 text-gray-500 mb-3">
                    <li>"Top 5 results"</li>
                    <li>"Remove consulting firms"</li>
                    <li>"Only show universities"</li>
                  </ul>
                  <p className="mb-2 font-medium">Search for new partners:</p>
                  <ul className="space-y-1 text-gray-500">
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
                      : 'bg-gray-50 text-gray-700 border border-gray-200'
                  }`}>
                    {statusMessage}
                  </div>
                )}

                {/* Spacer to push input to bottom */}
                <div className="flex-1"></div>

                {/* Refinement Input */}
                <form onSubmit={handleRefinement} className="min-w-0">
                  <div className="flex gap-2 min-w-0">
                    <input
                      type="text"
                      value={refinementInput}
                      onChange={(e) => setRefinementInput(e.target.value)}
                      placeholder="Type a refinement command..."
                      disabled={loading}
                      className="flex-1 min-w-0 px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-200 focus:border-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed"
                    />
                    <button
                      type="submit"
                      disabled={loading || !refinementInput.trim()}
                      className="flex-shrink-0 px-4 py-3 bg-black hover:bg-gray-800 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
      </div>

      {/* Floating Cost Badge */}
      <CostBadge cost={displayCost} isSearching={isSearching} />
    </div>
  )
}

export default ResultsPage

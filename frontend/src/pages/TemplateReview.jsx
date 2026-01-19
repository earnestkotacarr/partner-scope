import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useScenario } from '../context/ScenarioContext'
import { useStreamingSearch } from '../hooks/useStreamingSearch'
import CostBadge from '../components/CostBadge'
import { MODEL_PRESETS } from '../constants/modelPresets'
import ExternalResearchComparison from '../components/evaluation/ExternalResearchComparison'

// Quirky rotating messages to keep users entertained during search
const QUIRKY_MESSAGES = [
  "Warming up the Batmobile...",
  "Consulting the oracle...",
  "Reticulating splines...",
  "Deploying carrier pigeons...",
  "Teaching robots to read...",
  "Asking ChatGPT's cousin...",
  "Spinning up the hamster wheels...",
  "Calibrating the flux capacitor...",
  "Bribing the search gnomes...",
  "Downloading more RAM...",
  "Feeding the algorithm...",
  "Polishing the crystal ball...",
  "Waking up the interns...",
  "Consulting ancient scrolls...",
  "Negotiating with the cloud...",
  "Untangling the world wide web...",
  "Pinging the mothership...",
  "Channeling startup energy...",
  "Summoning venture spirits...",
  "Decoding business hieroglyphics...",
  "Mining the data caves...",
  "Following the digital breadcrumbs...",
  "Scanning the innovation horizon...",
  "Assembling the dream team...",
  "Activating partner radar...",
  "Brewing a fresh batch of insights...",
  "Convincing electrons to cooperate...",
  "Running competitive analysis... on our competitors...",
  "Asking nicely (with API keys)...",
  "Exploring the startup multiverse...",
]

function TemplateReview() {
  const navigate = useNavigate()
  const {
    scenario,
    setScenario,
    setResults,
    setCurrentCost,
    setIsSearching,
    addCost,
    getCostSummary,
    modelPreset,
    setModelPreset,
    getModelConfig,
    evaluationState,
  } = useScenario()
  const [formData, setFormData] = useState({
    startup_name: '',
    description: '',
    industry: '',
    investment_stage: 'Seed',
    product_stage: 'MVP',
    partner_needs: '',
    keywords: [],
    use_csv: true,
    use_web_search: true
  })
  const [progressMessage, setProgressMessage] = useState(null)
  const [quirkyMessage, setQuirkyMessage] = useState(QUIRKY_MESSAGES[0])
  const quirkyIntervalRef = useRef(null)

  // Streaming search hook for real-time cost updates
  const { startSearch, cancelSearch, isSearching, progress, error } = useStreamingSearch({
    onProgress: (data) => {
      // Update current cost from progress events
      if (data.cost) {
        setCurrentCost(data.cost)
      }
      // Update progress message
      if (data.phase === 'company_list') {
        setProgressMessage(`Finding companies... (${data.companies_found || 0} found)`)
      } else if (data.phase === 'company_details') {
        setProgressMessage(`Fetching details: ${data.company || 'company'} (${data.index}/${data.total})`)
      } else if (data.phase === 'ranking') {
        setProgressMessage('Ranking results...')
      } else if (data.message) {
        setProgressMessage(data.message)
      }
    },
    onComplete: (data) => {
      // Add final cost to session
      if (data.cost) {
        addCost(data.cost, 'search')
      }
      setResults(data)
      setScenario(formData)
      setIsSearching(false)
      setCurrentCost(null)
      setProgressMessage(null)
      navigate('/results')
    },
    onError: (err) => {
      console.error('Search error:', err)
      setIsSearching(false)
      setCurrentCost(null)
      setProgressMessage(null)
    }
  })

  // Populate form from scenario
  useEffect(() => {
    if (scenario) {
      setFormData({
        startup_name: scenario.startup_name || '',
        description: scenario.description || '',
        industry: scenario.industry || '',
        investment_stage: scenario.investment_stage || 'Seed',
        product_stage: scenario.product_stage || 'MVP',
        partner_needs: scenario.partner_needs || '',
        keywords: scenario.keywords || [],
        use_csv: scenario.use_csv !== undefined ? scenario.use_csv : true,
        use_web_search: scenario.use_web_search !== undefined ? scenario.use_web_search : true
      })
    }
  }, [scenario])

  // Redirect if no scenario
  useEffect(() => {
    if (!scenario) {
      navigate('/chat')
    }
  }, [scenario, navigate])

  // Rotate quirky messages every 2.5 seconds while searching
  useEffect(() => {
    if (isSearching) {
      // Start with a random message
      setQuirkyMessage(QUIRKY_MESSAGES[Math.floor(Math.random() * QUIRKY_MESSAGES.length)])

      quirkyIntervalRef.current = setInterval(() => {
        setQuirkyMessage(prev => {
          // Pick a different random message
          let newIndex
          do {
            newIndex = Math.floor(Math.random() * QUIRKY_MESSAGES.length)
          } while (QUIRKY_MESSAGES[newIndex] === prev && QUIRKY_MESSAGES.length > 1)
          return QUIRKY_MESSAGES[newIndex]
        })
      }, 15000) // Change every 15 seconds
    } else {
      // Clear interval when not searching
      if (quirkyIntervalRef.current) {
        clearInterval(quirkyIntervalRef.current)
        quirkyIntervalRef.current = null
      }
    }

    return () => {
      if (quirkyIntervalRef.current) {
        clearInterval(quirkyIntervalRef.current)
        quirkyIntervalRef.current = null
      }
    }
  }, [isSearching])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSearch = () => {
    setIsSearching(true)
    setProgressMessage('Initializing search...')
    startSearch({
      startup_name: formData.startup_name,
      investment_stage: formData.investment_stage,
      product_stage: formData.product_stage,
      partner_needs: formData.partner_needs,
      industry: formData.industry,
      description: formData.description,
      max_results: 20,
      use_csv: formData.use_csv,
      use_web_search: formData.use_web_search,
      ai_models: getModelConfig()
    })
  }

  const handleCancel = () => {
    cancelSearch()
    setIsSearching(false)
    setCurrentCost(null)
    setProgressMessage(null)
  }

  if (!scenario) {
    return null
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8 max-w-3xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-black mb-2">
            Review Your Partner Profile
          </h1>
          <p className="text-gray-600">
            Edit any fields before searching for partners
          </p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-xl shadow-lg p-6 space-y-6">
          {/* Startup Name */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Startup Name
            </label>
            <input
              type="text"
              name="startup_name"
              value={formData.startup_name}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gray-400 focus:border-gray-400"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gray-400 focus:border-gray-400"
            />
          </div>

          {/* Industry */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Industry
            </label>
            <input
              type="text"
              name="industry"
              value={formData.industry}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gray-400 focus:border-gray-400"
            />
          </div>

          {/* Stages */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Investment Stage
              </label>
              <select
                name="investment_stage"
                value={formData.investment_stage}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gray-400 focus:border-gray-400"
              >
                <option value="Pre-Seed">Pre-Seed</option>
                <option value="Seed">Seed</option>
                <option value="Series A">Series A</option>
                <option value="Series B">Series B</option>
                <option value="Series C+">Series C+</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Product Stage
              </label>
              <select
                name="product_stage"
                value={formData.product_stage}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gray-400 focus:border-gray-400"
              >
                <option value="Concept">Concept</option>
                <option value="MVP">MVP</option>
                <option value="Beta">Beta</option>
                <option value="Launched">Launched</option>
              </select>
            </div>
          </div>

          {/* Partner Needs */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Partner Needs
            </label>
            <textarea
              name="partner_needs"
              value={formData.partner_needs}
              onChange={handleChange}
              rows={4}
              placeholder="Describe the types of partners you're looking for..."
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-gray-400 focus:border-gray-400"
            />
          </div>

          {/* Data Sources */}
          <div className="border-t border-slate-200 pt-4">
            <label className="block text-sm font-medium text-slate-700 mb-3">
              Data Sources
            </label>
            <div className="space-y-3">
              <label className="flex items-center justify-between p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-colors">
                <div>
                  <span className="font-medium text-slate-800">CrunchBase CSV</span>
                  <p className="text-sm text-slate-500">Search pre-curated partner database</p>
                </div>
                <div className="relative">
                  <input
                    type="checkbox"
                    name="use_csv"
                    checked={formData.use_csv}
                    onChange={(e) => setFormData(prev => ({ ...prev, use_csv: e.target.checked }))}
                    className="sr-only"
                  />
                  <div className={`w-11 h-6 rounded-full transition-colors ${formData.use_csv ? 'bg-black' : 'bg-slate-300'}`}>
                    <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${formData.use_csv ? 'translate-x-5' : ''}`}></div>
                  </div>
                </div>
              </label>
              <label className="flex items-center justify-between p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-colors">
                <div>
                  <span className="font-medium text-slate-800">AI Web Search</span>
                  <p className="text-sm text-slate-500">Search the web with AI for real-time results</p>
                </div>
                <div className="relative">
                  <input
                    type="checkbox"
                    name="use_web_search"
                    checked={formData.use_web_search}
                    onChange={(e) => setFormData(prev => ({ ...prev, use_web_search: e.target.checked }))}
                    className="sr-only"
                  />
                  <div className={`w-11 h-6 rounded-full transition-colors ${formData.use_web_search ? 'bg-black' : 'bg-slate-300'}`}>
                    <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${formData.use_web_search ? 'translate-x-5' : ''}`}></div>
                  </div>
                </div>
              </label>

              {/* Model Preset Selector - only show when web search enabled */}
              {formData.use_web_search && (
                <div className="mt-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-slate-700">AI Model</span>
                  </div>

                  {/* Segmented Control */}
                  <div className="flex rounded-lg bg-slate-200 p-0.5">
                    {Object.values(MODEL_PRESETS).map((preset) => (
                      <button
                        key={preset.id}
                        type="button"
                        onClick={() => setModelPreset(preset.id)}
                        className={`flex-1 px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                          modelPreset === preset.id
                            ? 'bg-black text-white'
                            : 'text-slate-600 hover:text-slate-900'
                        }`}
                      >
                        {preset.name}
                      </button>
                    ))}
                  </div>

                  {/* Cost/Speed Description */}
                  <div className="mt-2 text-xs text-slate-600 font-medium">
                    {MODEL_PRESETS[modelPreset].description}
                  </div>
                  {/* Model Breakdown */}
                  <div className="mt-1 text-xs text-slate-400">
                    Search: {MODEL_PRESETS[modelPreset].models.search}
                    {' • '}
                    Chat: {MODEL_PRESETS[modelPreset].models.chat}
                    {' • '}
                    Eval: {MODEL_PRESETS[modelPreset].models.evaluation}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Progress indicator - Enhanced with phase-specific icons */}
          {isSearching && progressMessage && (
            <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-5 shadow-lg">
              <div className="flex items-center gap-4">
                {/* Phase-specific animated icon */}
                <div className="relative">
                  <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center">
                    {progress?.phase?.includes('csv') ? (
                      // Database icon for CSV search
                      <svg className="w-6 h-6 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                      </svg>
                    ) : progress?.phase?.includes('web') ? (
                      // Globe icon for web search
                      <svg className="w-6 h-6 text-white animate-spin" style={{ animationDuration: '3s' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ) : progress?.phase === 'company_details' ? (
                      // Magnifying glass for company analysis
                      <svg className="w-6 h-6 text-white animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    ) : progress?.phase === 'scoring' ? (
                      // Chart icon for scoring
                      <svg className="w-6 h-6 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    ) : progress?.phase === 'finishing' ? (
                      // Checkmark for finishing
                      <svg className="w-6 h-6 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ) : (
                      // Default spinner
                      <svg className="w-6 h-6 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    )}
                  </div>
                  {/* Pulsing ring animation */}
                  <div className="absolute inset-0 w-12 h-12 rounded-full border-2 border-white/20 animate-ping" style={{ animationDuration: '2s' }} />
                </div>

                <div className="flex-1">
                  {/* Actual progress message */}
                  <p className="text-white font-medium text-lg">{progressMessage}</p>
                  {/* Quirky rotating message */}
                  <p className="text-white/60 text-sm italic mt-1 transition-all duration-300">
                    {quirkyMessage}
                  </p>
                  {progress?.phase === 'company_details' && progress?.total && (
                    <div className="mt-2">
                      <div className="flex items-center gap-2 text-gray-400 text-sm">
                        <span>Company {progress.index} of {progress.total}</span>
                      </div>
                      <div className="mt-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-white rounded-full transition-all duration-300"
                          style={{ width: `${(progress.index / progress.total) * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                  {progress?.count && (
                    <p className="text-gray-400 text-sm mt-1">{progress.count} matches found</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <span className="text-red-800">{error}</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-between pt-4">
            <button
              onClick={() => navigate('/chat')}
              disabled={isSearching}
              className="text-slate-600 hover:text-slate-800 font-medium disabled:opacity-50"
            >
              ← Back to Chat
            </button>
            <div className="flex gap-3">
              {isSearching && (
                <button
                  onClick={handleCancel}
                  className="text-red-600 hover:text-red-800 font-medium px-4 py-3"
                >
                  Cancel
                </button>
              )}
              <button
                onClick={handleSearch}
                disabled={isSearching}
                className="bg-black hover:bg-gray-800 text-white font-semibold px-8 py-3 rounded-lg shadow-md hover:shadow-lg transition-all disabled:opacity-50 flex items-center gap-2"
              >
                {isSearching ? (
                  <>
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Searching...</span>
                  </>
                ) : (
                  'Search for Partners'
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Cost Badge - shows cumulative session cost + current search progress */}
      <CostBadge
        cost={(() => {
          const sessionCost = getCostSummary()
          const progressCost = progress?.cost
          if (!progressCost) return sessionCost
          // Combine session cost with current progress
          return {
            total_cost: (sessionCost?.total_cost || 0) + (progressCost?.total_cost || 0),
            input_tokens: (sessionCost?.input_tokens || 0) + (progressCost?.input_tokens || 0),
            output_tokens: (sessionCost?.output_tokens || 0) + (progressCost?.output_tokens || 0),
            web_search_calls: (sessionCost?.web_search_calls || 0) + (progressCost?.web_search_calls || 0),
          }
        })()}
        isSearching={isSearching}
      />

      {/* External Research Comparison - Floating panel, top-right (persists from evaluation) */}
      {evaluationState?.result && (
        <div className="fixed top-20 right-6 z-40 w-96 max-h-[calc(100vh-120px)] overflow-auto shadow-2xl rounded-xl border border-gray-200 bg-white">
          <ExternalResearchComparison
            partnerScopeResults={evaluationState.result}
            startupProfile={{
              name: scenario?.startup_name || formData.startup_name || 'My Startup',
              industry: scenario?.industry || formData.industry || '',
              stage: scenario?.investment_stage || formData.investment_stage || 'Seed',
              partner_needs: scenario?.partner_needs || formData.partner_needs || '',
            }}
            strategy={evaluationState.strategy}
            onCandidateClick={null}
          />
        </div>
      )}
    </div>
  )
}

export default TemplateReview

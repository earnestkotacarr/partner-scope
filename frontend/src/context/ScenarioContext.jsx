import { createContext, useContext, useState, useCallback, useEffect, useMemo } from 'react'
import { isDebugMode, debugSettings } from '../debug/config'
import { generateFakeData } from '../debug/fakeData'
import { MODEL_PRESETS, DEFAULT_PRESET } from '../constants/modelPresets'

const ScenarioContext = createContext(null)

export function ScenarioProvider({ children }) {
  // Debug mode state
  const [debugInitialized, setDebugInitialized] = useState(false)

  // Scenario template generated from discovery chat
  const [scenario, setScenario] = useState(null)

  // Search results
  const [results, setResults] = useState(null)

  // Conversation history from discovery chat
  const [chatHistory, setChatHistory] = useState([])

  // Cost tracking
  const [sessionCosts, setSessionCosts] = useState([])  // Array of individual operation costs
  const [currentCost, setCurrentCost] = useState(null)  // Current running cost (during search)
  const [isSearching, setIsSearching] = useState(false) // Search in progress flag

  // Results history for undo support (keep last 5 states)
  const [resultsHistory, setResultsHistory] = useState([])

  // Evaluation state - tracks if results have been enriched with AI evaluation
  const [evaluationState, setEvaluationState] = useState({
    strategy: null,
    phase: 'none',  // 'none' | 'complete'
    evaluatedAt: null,
    result: null,  // Full evaluation result for comparison panel
  })

  // Model preset selection (quality, balanced, fast)
  const [modelPreset, setModelPreset] = useState(DEFAULT_PRESET)

  // Get the current model configuration based on selected preset
  const getModelConfig = useCallback(() => {
    return MODEL_PRESETS[modelPreset]?.models || MODEL_PRESETS.balanced.models
  }, [modelPreset])

  // Add a cost entry from an API operation
  const addCost = useCallback((cost, operation = 'unknown') => {
    if (cost) {
      const costEntry = {
        ...cost,
        operation,
        timestamp: new Date().toISOString(),
      }
      setSessionCosts(prev => [...prev, costEntry])
    }
  }, [])

  // Get total session cost
  const getTotalCost = useCallback(() => {
    return sessionCosts.reduce((sum, cost) => sum + (cost.total_cost || 0), 0)
  }, [sessionCosts])

  // Get aggregated cost summary
  const getCostSummary = useCallback(() => {
    return {
      total_cost: getTotalCost(),
      input_tokens: sessionCosts.reduce((sum, c) => sum + (c.input_tokens || 0), 0),
      output_tokens: sessionCosts.reduce((sum, c) => sum + (c.output_tokens || 0), 0),
      web_search_calls: sessionCosts.reduce((sum, c) => sum + (c.web_search_calls || 0), 0),
      operation_count: sessionCosts.length,
    }
  }, [sessionCosts, getTotalCost])

  // Save current results to history (call before changing results)
  const saveResultsSnapshot = useCallback((action = 'unknown') => {
    if (results && results.matches) {
      setResultsHistory(prev => {
        const newEntry = {
          results: { ...results, matches: [...results.matches] },
          action,
          timestamp: Date.now()
        }
        // Keep only last 5 entries
        return [...prev.slice(-4), newEntry]
      })
    }
  }, [results])

  // Undo to previous results state
  const undoResults = useCallback(() => {
    if (resultsHistory.length > 0) {
      const previous = resultsHistory[resultsHistory.length - 1]
      setResults(previous.results)
      setResultsHistory(prev => prev.slice(0, -1))
      return true
    }
    return false
  }, [resultsHistory])

  // Check if undo is available
  const canUndo = resultsHistory.length > 0

  // Merge evaluation results into existing results (enrichment pattern)
  const applyEvaluationToResults = useCallback((evaluationResult, strategy) => {
    if (!evaluationResult || !results?.matches) return

    // Save snapshot for undo support
    saveResultsSnapshot('evaluation')

    // Build lookup map from evaluation results
    const evaluationMap = new Map(
      (evaluationResult.top_candidates || []).map(e => [e.candidate_name, e])
    )

    // Enrich existing results with evaluation data
    const enrichedMatches = results.matches.map(match => {
      const evalData = evaluationMap.get(match.company_name)
      if (!evalData) return match

      return {
        ...match,
        // Set fit_score from evaluation (keep info_score and match_score unchanged)
        fit_score: evalData.final_score,
        // Add evaluation enrichment object
        evaluation: {
          final_score: evalData.final_score,
          rank: evalData.rank,
          dimension_scores: evalData.dimension_scores,
          strengths: evalData.strengths,
          weaknesses: evalData.weaknesses,
          recommendations: evalData.recommendations,
          flags: evalData.flags,
          evaluated_at: new Date().toISOString()
        }
      }
    })

    // Sort by fit_score (from evaluation) when available, otherwise by info_score
    enrichedMatches.sort((a, b) => {
      const scoreA = a.fit_score ?? a.info_score ?? a.match_score
      const scoreB = b.fit_score ?? b.info_score ?? b.match_score
      return scoreB - scoreA
    })

    // Update results with enriched data
    setResults({
      ...results,
      matches: enrichedMatches,
      _lastUpdate: Date.now()
    })

    // Update evaluation state
    setEvaluationState({
      strategy,
      phase: 'complete',
      evaluatedAt: new Date().toISOString()
    })

    console.log('[Evaluation] Applied evaluation to results:', enrichedMatches.filter(m => m.evaluation).length, 'enriched')
  }, [results, saveResultsSnapshot])

  // Check if results have been evaluated
  const hasEvaluation = useMemo(() =>
    results?.matches?.some(m => m.evaluation) ?? false,
  [results])

  const clearScenario = () => {
    setScenario(null)
    setResults(null)
    setChatHistory([])
    setSessionCosts([])
    setCurrentCost(null)
    setIsSearching(false)
    setResultsHistory([])
    setEvaluationState({ strategy: null, phase: 'none', evaluatedAt: null })
    setModelPreset(DEFAULT_PRESET)
  }

  // Initialize with fake data in debug mode
  useEffect(() => {
    if (debugInitialized || !isDebugMode()) return

    console.log('[Debug Mode] Initializing context with fake data...')
    const fakeData = generateFakeData(
      debugSettings.fakeCandidatesCount,
      debugSettings.seed
    )

    setScenario(fakeData.scenario)
    setResults(fakeData.results)
    setChatHistory(fakeData.chatHistory)
    setSessionCosts([{
      total_cost: 0.05,
      input_tokens: 1500,
      output_tokens: 2000,
      web_search_calls: 3,
      operation: 'debug_init',
      timestamp: new Date().toISOString(),
    }])

    setDebugInitialized(true)
    console.log('[Debug Mode] Context initialized successfully')
  }, [debugInitialized])

  return (
    <ScenarioContext.Provider value={{
      // Existing
      scenario,
      setScenario,
      results,
      setResults,
      chatHistory,
      setChatHistory,
      clearScenario,
      // Cost tracking
      sessionCosts,
      setSessionCosts,
      currentCost,
      setCurrentCost,
      isSearching,
      setIsSearching,
      addCost,
      getTotalCost,
      getCostSummary,
      // Undo support
      saveResultsSnapshot,
      undoResults,
      canUndo,
      // Evaluation enrichment
      evaluationState,
      setEvaluationState,
      applyEvaluationToResults,
      hasEvaluation,
      // Model preset selection
      modelPreset,
      setModelPreset,
      getModelConfig,
      // Debug mode
      debugInitialized,
      isDebugMode: isDebugMode(),
    }}>
      {children}
    </ScenarioContext.Provider>
  )
}

export function useScenario() {
  const context = useContext(ScenarioContext)
  if (!context) {
    throw new Error('useScenario must be used within a ScenarioProvider')
  }
  return context
}

import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { isDebugMode, debugSettings } from '../debug/config'
import { generateFakeData } from '../debug/fakeData'

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

  const clearScenario = () => {
    setScenario(null)
    setResults(null)
    setChatHistory([])
    setSessionCosts([])
    setCurrentCost(null)
    setIsSearching(false)
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

import { Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import DiscoveryChat from './pages/DiscoveryChat'
import TemplateReview from './pages/TemplateReview'
import ResultsPage from './pages/ResultsPage'
import EvaluationPage from './pages/EvaluationPage'
import { ScenarioProvider } from './context/ScenarioContext'
import DebugPanel from './components/DebugPanel'

function App() {
  return (
    <ScenarioProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/chat" element={<DiscoveryChat />} />
        <Route path="/review" element={<TemplateReview />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/evaluate" element={<EvaluationPage />} />
      </Routes>
      {/* Debug Panel - only visible in debug mode */}
      <DebugPanel />
    </ScenarioProvider>
  )
}

export default App

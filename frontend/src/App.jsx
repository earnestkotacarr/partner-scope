import { Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import DiscoveryChat from './pages/DiscoveryChat'
import TemplateReview from './pages/TemplateReview'
import ResultsPage from './pages/ResultsPage'
import { ScenarioProvider } from './context/ScenarioContext'

function App() {
  return (
    <ScenarioProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/chat" element={<DiscoveryChat />} />
        <Route path="/review" element={<TemplateReview />} />
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </ScenarioProvider>
  )
}

export default App

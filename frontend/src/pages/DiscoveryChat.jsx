import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useScenario } from '../context/ScenarioContext'
import ChatContainer from '../components/chat/ChatContainer'
import CostBadge from '../components/CostBadge'

function DiscoveryChat() {
  const navigate = useNavigate()
  const { setScenario, setChatHistory, addCost, getCostSummary } = useScenario()
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Welcome! I'm here to help you figure out what kinds of partners might accelerate your startup. Tell me a bit about what you're building and where you are in your journey."
    }
  ])
  const [loading, setLoading] = useState(false)
  const [readyForTemplate, setReadyForTemplate] = useState(false)

  const handleSendMessage = async (content) => {
    // Add user message
    const newMessages = [...messages, { role: 'user', content }]
    setMessages(newMessages)
    setLoading(true)

    try {
      const response = await fetch('/api/chat/startup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: newMessages,
          current_message: content
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()

      // Track cost from chat response
      if (data.cost) {
        addCost(data.cost, 'discovery_chat')
      }

      setMessages([...newMessages, { role: 'assistant', content: data.response }])
      setReadyForTemplate(data.ready_for_template || false)
    } catch (err) {
      setMessages([...newMessages, {
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again."
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateTemplate = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/chat/startup/generate-template', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages })
      })

      if (!response.ok) {
        throw new Error('Failed to generate template')
      }

      const data = await response.json()

      // Track cost from template generation
      if (data.cost) {
        addCost(data.cost, 'template_generation')
      }

      setScenario(data.scenario_template)
      setChatHistory(messages)
      navigate('/review')
    } catch (err) {
      setMessages([...messages, {
        role: 'assistant',
        content: "I couldn't generate the template. Let's continue our conversation to gather more information."
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Partner Discovery
          </h1>
          <p className="text-slate-600">
            Let's find the right partners for your startup
          </p>
        </div>

        {/* Chat */}
        <ChatContainer
          messages={messages}
          onSendMessage={handleSendMessage}
          loading={loading}
        />

        {/* Generate Template Button */}
        {readyForTemplate && (
          <div className="mt-6 text-center">
            <button
              onClick={handleGenerateTemplate}
              disabled={loading}
              className="bg-green-600 hover:bg-green-700 text-white font-semibold px-8 py-3 rounded-lg shadow-md hover:shadow-lg transition-all disabled:opacity-50"
            >
              Generate My Partner Profile
            </button>
          </div>
        )}
      </div>

      {/* Floating Cost Badge */}
      <CostBadge cost={getCostSummary()} isSearching={loading} />
    </div>
  )
}

export default DiscoveryChat

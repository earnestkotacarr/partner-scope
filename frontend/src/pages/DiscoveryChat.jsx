import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useScenario } from '../context/ScenarioContext'
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
  const [input, setInput] = useState('')

  const handleSendMessage = async (content) => {
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

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !loading) {
      handleSendMessage(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-100">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <h1 className="text-base font-medium text-gray-900">Partner Discovery</h1>
          <div className="w-5" /> {/* Spacer */}
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-8">
          {messages.map((message, index) => (
            <div key={index} className="mb-8">
              {message.role === 'assistant' ? (
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <div className="flex-1 pt-1">
                    <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                      {message.content.split('\n').map((line, i) => {
                        const parts = line.split(/(\*\*.*?\*\*)/)
                        return (
                          <p key={i} className={i > 0 ? 'mt-3' : ''}>
                            {parts.map((part, j) => {
                              if (part.startsWith('**') && part.endsWith('**')) {
                                return <strong key={j} className="font-semibold">{part.slice(2, -2)}</strong>
                              }
                              return part
                            })}
                          </p>
                        )
                      })}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div className="flex-1 pt-1">
                    <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                      {message.content}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Typing Indicator */}
          {loading && (
            <div className="mb-8">
              <div className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="flex-1 pt-2">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse" />
                    <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Generate Template CTA */}
          {readyForTemplate && !loading && (
            <div className="mb-8 flex gap-4">
              <div className="w-8 flex-shrink-0" />
              <div className="flex-1">
                <button
                  onClick={handleGenerateTemplate}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-black text-white text-sm font-medium rounded-full hover:bg-gray-800 transition-colors"
                >
                  Generate Partner Profile
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-100 bg-white">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe your startup..."
              disabled={loading}
              rows={1}
              className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-2xl resize-none focus:outline-none focus:border-gray-300 focus:ring-0 disabled:bg-gray-50 disabled:text-gray-400 text-gray-800 placeholder-gray-400"
              style={{ minHeight: '48px', maxHeight: '200px' }}
              onInput={(e) => {
                e.target.style.height = 'auto'
                e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px'
              }}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-2 bottom-2 p-2 text-gray-400 hover:text-gray-600 disabled:text-gray-300 disabled:hover:text-gray-300 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
          <p className="text-xs text-gray-400 text-center mt-3">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>

      {/* Floating Cost Badge */}
      <CostBadge cost={getCostSummary()} isSearching={loading} />
    </div>
  )
}

export default DiscoveryChat

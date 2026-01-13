import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'

function LandingPage() {
  const navigate = useNavigate()
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-white text-black">
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-white/80 backdrop-blur-md border-b border-gray-100' : ''}`}>
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-xl font-semibold tracking-tight">Partner Scope</span>
          <button
            onClick={() => navigate('/chat')}
            className="text-sm font-medium px-4 py-2 rounded-full bg-black text-white hover:bg-gray-800 transition-colors"
          >
            Try now
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="min-h-screen flex flex-col items-center justify-center px-6 pt-20">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-medium tracking-tight leading-[1.1] mb-8">
            Find the partners
            <br />
            <span className="text-gray-400">your startup needs</span>
          </h1>

          <p className="text-lg sm:text-xl text-gray-500 max-w-2xl mx-auto mb-12 leading-relaxed">
            An AI system that understands your business, searches across multiple sources,
            and delivers strategic partnership recommendations.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => navigate('/chat')}
              className="group flex items-center gap-2 text-base font-medium px-8 py-4 rounded-full bg-black text-white hover:bg-gray-800 transition-all"
            >
              Start discovering
              <svg
                className="w-4 h-4 group-hover:translate-x-0.5 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
            <a
              href="#how-it-works"
              className="text-base font-medium px-8 py-4 text-gray-500 hover:text-black transition-colors"
            >
              Learn more
            </a>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-12 left-1/2 -translate-x-1/2">
          <div className="w-6 h-10 rounded-full border-2 border-gray-300 flex items-start justify-center p-2">
            <div className="w-1 h-2 bg-gray-400 rounded-full animate-bounce" />
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-32 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <p className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">How it works</p>
            <h2 className="text-4xl sm:text-5xl font-medium tracking-tight">
              Five steps to your
              <br />
              ideal partners
            </h2>
          </div>

          <div className="space-y-0">
            {/* Step 1 */}
            <div className="group grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 py-16 border-t border-gray-200">
              <div className="flex items-start gap-6">
                <span className="text-6xl font-light text-gray-200 leading-none">1</span>
                <div>
                  <h3 className="text-2xl font-medium mb-3">Discovery Chat</h3>
                  <p className="text-gray-500 leading-relaxed">
                    Have a conversation with our AI. Describe your startup, your goals,
                    and the kind of partnerships you're looking for. No forms, just talk.
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-center md:justify-end">
                <div className="w-full max-w-sm h-48 bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="h-3 bg-gray-100 rounded w-3/4"></div>
                    <div className="h-3 bg-gray-100 rounded w-1/2"></div>
                  </div>
                  <div className="flex gap-2">
                    <div className="h-10 bg-gray-50 rounded-lg flex-1"></div>
                    <div className="h-10 w-10 bg-black rounded-lg"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="group grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 py-16 border-t border-gray-200">
              <div className="flex items-start gap-6">
                <span className="text-6xl font-light text-gray-200 leading-none">2</span>
                <div>
                  <h3 className="text-2xl font-medium mb-3">Profile Generation</h3>
                  <p className="text-gray-500 leading-relaxed">
                    AI generates a comprehensive partner profile based on your conversation.
                    Review and customize it to match your exact requirements.
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-center md:justify-end">
                <div className="w-full max-w-sm h-48 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                  <div className="space-y-4">
                    <div className="h-3 bg-gray-100 rounded w-1/3"></div>
                    <div className="h-8 bg-gray-50 rounded-lg w-full"></div>
                    <div className="h-3 bg-gray-100 rounded w-1/4"></div>
                    <div className="h-16 bg-gray-50 rounded-lg w-full"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 3 */}
            <div className="group grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 py-16 border-t border-gray-200">
              <div className="flex items-start gap-6">
                <span className="text-6xl font-light text-gray-200 leading-none">3</span>
                <div>
                  <h3 className="text-2xl font-medium mb-3">Multi-source Search</h3>
                  <p className="text-gray-500 leading-relaxed">
                    Real-time search across databases and the web. Watch as potential
                    partners are discovered and scored in real-time.
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-center md:justify-end">
                <div className="w-full max-w-sm h-48 bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col justify-center">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                    <div className="h-3 bg-gray-100 rounded w-32"></div>
                  </div>
                  <div className="space-y-2">
                    <div className="h-10 bg-gray-50 rounded-lg w-full flex items-center px-3 gap-2">
                      <div className="w-6 h-6 bg-gray-200 rounded"></div>
                      <div className="h-2 bg-gray-200 rounded flex-1"></div>
                      <div className="h-4 w-8 bg-green-100 rounded text-[8px] text-green-600 flex items-center justify-center">92</div>
                    </div>
                    <div className="h-10 bg-gray-50 rounded-lg w-full flex items-center px-3 gap-2">
                      <div className="w-6 h-6 bg-gray-200 rounded"></div>
                      <div className="h-2 bg-gray-200 rounded flex-1"></div>
                      <div className="h-4 w-8 bg-green-100 rounded text-[8px] text-green-600 flex items-center justify-center">87</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 4 */}
            <div className="group grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 py-16 border-t border-gray-200">
              <div className="flex items-start gap-6">
                <span className="text-6xl font-light text-gray-200 leading-none">4</span>
                <div>
                  <h3 className="text-2xl font-medium mb-3">Natural Refinement</h3>
                  <p className="text-gray-500 leading-relaxed">
                    Refine your results using plain English. "Show me only enterprise companies"
                    or "Find more in healthcare" — just say what you need.
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-center md:justify-end">
                <div className="w-full max-w-sm h-48 bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col justify-end">
                  <div className="bg-gray-50 rounded-xl p-3 mb-3">
                    <p className="text-sm text-gray-600">"Show me only Series B+ companies"</p>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Filtered to 8 results
                  </div>
                </div>
              </div>
            </div>

            {/* Step 5 */}
            <div className="group grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-16 py-16 border-t border-gray-200">
              <div className="flex items-start gap-6">
                <span className="text-6xl font-light text-gray-200 leading-none">5</span>
                <div>
                  <h3 className="text-2xl font-medium mb-3">Deep Evaluation</h3>
                  <p className="text-gray-500 leading-relaxed">
                    Multi-agent AI evaluation with dimensional scoring. Get detailed analysis,
                    strategic insights, and ranked recommendations.
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-center md:justify-end">
                <div className="w-full max-w-sm h-48 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="h-3 bg-gray-100 rounded w-24"></div>
                    <div className="h-5 w-12 bg-black rounded text-[10px] text-white flex items-center justify-center">#1</div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400 w-20">Strategic</span>
                      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full w-[92%] bg-black rounded-full"></div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400 w-20">Technical</span>
                      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full w-[85%] bg-black rounded-full"></div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400 w-20">Cultural</span>
                      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full w-[78%] bg-black rounded-full"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-32 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 md:gap-8">
            <div>
              <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-medium mb-3">Real-time streaming</h3>
              <p className="text-gray-500 leading-relaxed">
                Watch results appear as they're found. No waiting for batch processing.
              </p>
            </div>

            <div>
              <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-medium mb-3">Multi-dimensional scoring</h3>
              <p className="text-gray-500 leading-relaxed">
                AI evaluates partners across strategic fit, technical capability, and cultural alignment.
              </p>
            </div>

            <div>
              <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-medium mb-3">Transparent costs</h3>
              <p className="text-gray-500 leading-relaxed">
                Full visibility into API costs. Track spending in real-time as you search.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-32 px-6 bg-black text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl sm:text-5xl font-medium tracking-tight mb-6">
            Ready to find your partners?
          </h2>
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            Start a conversation with our AI and discover strategic partnerships
            tailored to your startup's unique needs.
          </p>
          <button
            onClick={() => navigate('/chat')}
            className="group inline-flex items-center gap-2 text-base font-medium px-8 py-4 rounded-full bg-white text-black hover:bg-gray-100 transition-all"
          >
            Get started
            <svg
              className="w-4 h-4 group-hover:translate-x-0.5 transition-transform"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-gray-100">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <span className="text-sm text-gray-400">Partner Scope</span>
          <span className="text-sm text-gray-400">AI-powered partner discovery</span>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage

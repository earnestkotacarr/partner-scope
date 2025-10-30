import { useState } from 'react'
import StartupForm from './components/StartupForm'
import Results from './components/Results'

function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (formData) => {
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch results')
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-slate-900 mb-4">
            Partner Scope
          </h1>
          <p className="text-xl text-slate-600">
            Find the perfect corporate partners for your startup
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <div className="lg:col-span-1">
            <StartupForm onSubmit={handleSubmit} loading={loading} />
          </div>

          {/* Results Section */}
          <div className="lg:col-span-1">
            <Results results={results} loading={loading} error={error} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

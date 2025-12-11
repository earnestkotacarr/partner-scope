import { useState } from 'react'

const StartupForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    startup_name: '',
    investment_stage: 'Seed',
    product_stage: 'MVP',
    partner_needs: '',
    industry: '',
    description: '',
    max_results: 20,
    use_csv: true,
    use_web_search: false,
  })
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold text-slate-900 mb-6">Startup Information</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Startup Name */}
        <div>
          <label htmlFor="startup_name" className="block text-sm font-medium text-slate-700 mb-1">
            Startup Name *
          </label>
          <input
            type="text"
            id="startup_name"
            name="startup_name"
            required
            value={formData.startup_name}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            placeholder="e.g., CoVital Node"
          />
        </div>

        {/* Partner Needs - moved up as primary field */}
        <div>
          <label htmlFor="partner_needs" className="block text-sm font-medium text-slate-700 mb-1">
            Partner Needs *
          </label>
          <textarea
            id="partner_needs"
            name="partner_needs"
            required
            value={formData.partner_needs}
            onChange={handleChange}
            rows={2}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition resize-none"
            placeholder="e.g., dorm housing university student wellness"
          />
        </div>

        {/* Data Sources - Multi-select */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Data Sources (select one or both)
          </label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setFormData(prev => ({ ...prev, use_csv: !prev.use_csv }))}
              className={`flex-1 px-3 py-2 rounded-lg border text-sm font-medium transition ${
                formData.use_csv
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
              }`}
            >
              {formData.use_csv ? '✓ ' : ''}CrunchBase CSV
            </button>
            <button
              type="button"
              onClick={() => setFormData(prev => ({ ...prev, use_web_search: !prev.use_web_search }))}
              className={`flex-1 px-3 py-2 rounded-lg border text-sm font-medium transition ${
                formData.use_web_search
                  ? 'bg-green-600 text-white border-green-600'
                  : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
              }`}
            >
              {formData.use_web_search ? '✓ ' : ''}AI Web Search
            </button>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {formData.use_csv && formData.use_web_search
              ? 'Combined: CSV data + real-time AI web search'
              : formData.use_csv
              ? 'Pre-curated CrunchBase data (fast)'
              : formData.use_web_search
              ? 'Real-time web search via GPT-4o-mini'
              : 'Select at least one data source'}
          </p>
        </div>

        {/* Stages in a row */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label htmlFor="investment_stage" className="block text-sm font-medium text-slate-700 mb-1">
              Investment Stage
            </label>
            <select
              id="investment_stage"
              name="investment_stage"
              value={formData.investment_stage}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            >
              <option value="Pre-Seed">Pre-Seed</option>
              <option value="Seed">Seed</option>
              <option value="Series A">Series A</option>
              <option value="Series B">Series B</option>
              <option value="Series C+">Series C+</option>
            </select>
          </div>
          <div>
            <label htmlFor="product_stage" className="block text-sm font-medium text-slate-700 mb-1">
              Product Stage
            </label>
            <select
              id="product_stage"
              name="product_stage"
              value={formData.product_stage}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            >
              <option value="Concept">Concept</option>
              <option value="MVP">MVP</option>
              <option value="Beta">Beta</option>
              <option value="Launched">Launched</option>
            </select>
          </div>
        </div>

        {/* Advanced Options Toggle */}
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
        >
          <svg
            className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-90' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          {showAdvanced ? 'Hide' : 'Show'} Advanced Options
        </button>

        {/* Collapsible Advanced Options */}
        {showAdvanced && (
          <div className="space-y-4 pt-2 border-t border-slate-200">
            {/* Industry */}
            <div>
              <label htmlFor="industry" className="block text-sm font-medium text-slate-700 mb-1">
                Industry
              </label>
              <input
                type="text"
                id="industry"
                name="industry"
                value={formData.industry}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
                placeholder="e.g., Robotics, Space Tech, Healthcare"
              />
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-slate-700 mb-1">
                Startup Description
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={2}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition resize-none"
                placeholder="Brief description of your startup..."
              />
            </div>

            {/* Max Results */}
            <div>
              <label htmlFor="max_results" className="block text-sm font-medium text-slate-700 mb-1">
                Maximum Results
              </label>
              <input
                type="number"
                id="max_results"
                name="max_results"
                min="1"
                max="100"
                value={formData.max_results}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
              />
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Searching for Partners...
            </span>
          ) : (
            'Find Partners'
          )}
        </button>
      </form>
    </div>
  )
}

export default StartupForm

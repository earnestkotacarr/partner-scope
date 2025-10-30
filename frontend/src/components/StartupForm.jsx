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
  })

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

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Startup Name */}
        <div>
          <label htmlFor="startup_name" className="block text-sm font-medium text-slate-700 mb-2">
            Startup Name *
          </label>
          <input
            type="text"
            id="startup_name"
            name="startup_name"
            required
            value={formData.startup_name}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            placeholder="e.g., TempTrack"
          />
        </div>

        {/* Investment Stage */}
        <div>
          <label htmlFor="investment_stage" className="block text-sm font-medium text-slate-700 mb-2">
            Investment Stage *
          </label>
          <select
            id="investment_stage"
            name="investment_stage"
            required
            value={formData.investment_stage}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
          >
            <option value="Pre-Seed">Pre-Seed</option>
            <option value="Seed">Seed</option>
            <option value="Series A">Series A</option>
            <option value="Series B">Series B</option>
            <option value="Series C">Series C</option>
            <option value="Series D+">Series D+</option>
          </select>
        </div>

        {/* Product Stage */}
        <div>
          <label htmlFor="product_stage" className="block text-sm font-medium text-slate-700 mb-2">
            Product Stage *
          </label>
          <select
            id="product_stage"
            name="product_stage"
            required
            value={formData.product_stage}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
          >
            <option value="Concept">Concept</option>
            <option value="MVP">MVP</option>
            <option value="Beta">Beta</option>
            <option value="Public Testing">Public Testing</option>
            <option value="Launched">Launched</option>
            <option value="Scaling">Scaling</option>
          </select>
        </div>

        {/* Industry */}
        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-slate-700 mb-2">
            Industry
          </label>
          <input
            type="text"
            id="industry"
            name="industry"
            value={formData.industry}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            placeholder="e.g., Food Safety, Fintech, Healthcare IT"
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-slate-700 mb-2">
            Startup Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition resize-none"
            placeholder="Brief description of your startup..."
          />
        </div>

        {/* Partner Needs */}
        <div>
          <label htmlFor="partner_needs" className="block text-sm font-medium text-slate-700 mb-2">
            Partner Needs *
          </label>
          <textarea
            id="partner_needs"
            name="partner_needs"
            required
            value={formData.partner_needs}
            onChange={handleChange}
            rows={4}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition resize-none"
            placeholder="Describe what you're looking for in a partner (e.g., Large logistics company for pilot testing temperature tracking stickers)"
          />
        </div>

        {/* Max Results */}
        <div>
          <label htmlFor="max_results" className="block text-sm font-medium text-slate-700 mb-2">
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
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
          />
        </div>

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

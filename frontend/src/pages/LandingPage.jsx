import { useNavigate } from 'react-router-dom'

function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
      <div className="max-w-2xl mx-auto px-4 text-center">
        {/* Logo/Title */}
        <h1 className="text-6xl font-bold text-slate-900 mb-4">
          Partner Scope
        </h1>
        <p className="text-xl text-slate-600 mb-12">
          Not sure what partners you need? We'll figure it out together.
        </p>

        {/* Main CTA */}
        <button
          onClick={() => navigate('/chat')}
          className="bg-blue-600 hover:bg-blue-700 text-white text-xl font-semibold px-12 py-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 mb-8"
        >
          Find Your Partners
        </button>

        {/* Process explanation */}
        <div className="mt-12 grid grid-cols-4 gap-4 text-sm text-slate-500">
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mb-2">1</div>
            <span>Chat</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mb-2">2</div>
            <span>Review</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mb-2">3</div>
            <span>Search</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold mb-2">4</div>
            <span>Refine</span>
          </div>
        </div>

        <p className="mt-8 text-slate-400 text-sm">
          Our AI will help you discover the partnership opportunities you didn't know you needed.
        </p>
      </div>
    </div>
  )
}

export default LandingPage

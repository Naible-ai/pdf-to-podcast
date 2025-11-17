import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Headphones, Sparkles } from 'lucide-react'
import CreatePodcast from './pages/CreatePodcast'
import MyPodcasts from './pages/MyPodcasts'
import EditPodcast from './pages/EditPodcast'
import Templates from './pages/Templates'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link to="/" className="flex items-center space-x-2">
                  <Headphones className="w-8 h-8 text-primary-600" />
                  <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">
                    PDF to Podcast
                  </span>
                </Link>
              </div>

              <div className="flex items-center space-x-6">
                <Link
                  to="/"
                  className="text-gray-700 hover:text-primary-600 transition-colors"
                >
                  Create
                </Link>
                <Link
                  to="/my-podcasts"
                  className="text-gray-700 hover:text-primary-600 transition-colors"
                >
                  My Podcasts
                </Link>
                <Link
                  to="/templates"
                  className="text-gray-700 hover:text-primary-600 transition-colors flex items-center space-x-1"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>Templates</span>
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<CreatePodcast />} />
            <Route path="/my-podcasts" element={<MyPodcasts />} />
            <Route path="/edit/:jobId" element={<EditPodcast />} />
            <Route path="/templates" element={<Templates />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="mt-16 border-t bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-center text-gray-500 text-sm">
              Powered by NVIDIA NIM & ElevenLabs | AI-Generated Audio Content
            </p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App

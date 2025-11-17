import { useQuery } from '@tanstack/react-query'
import { Headphones, Download, Edit, Trash2 } from 'lucide-react'
import { api } from '../utils/api'
import { Link } from 'react-router-dom'

export default function MyPodcasts() {
  const { data: podcasts, isLoading } = useQuery({
    queryKey: ['saved-podcasts'],
    queryFn: () => api.getSavedPodcasts(),
  })

  const handleDownload = async (jobId: string) => {
    try {
      const audioBlob = await api.getPodcastAudio(jobId)
      const url = URL.createObjectURL(audioBlob)
      const a = document.createElement('a')
      a.href = url
      a.download = `podcast_${jobId}.mp3`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Download error:', err)
    }
  }

  if (isLoading) {
    return <div className="text-center py-12">Loading your podcasts...</div>
  }

  const podcastList = Array.isArray(podcasts) ? podcasts : []

  if (podcastList.length === 0) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <Headphones className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Podcasts Yet</h2>
        <p className="text-gray-600 mb-6">
          You haven't created any podcasts yet. Start by uploading some PDFs!
        </p>
        <Link
          to="/"
          className="inline-block bg-primary-600 text-white py-2 px-6 rounded-lg hover:bg-primary-700 transition-colors"
        >
          Create Your First Podcast
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">My Podcasts</h1>
        <p className="text-lg text-gray-600">{podcastList.length} podcast(s) generated</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {podcastList.map((podcast: any) => (
          <div key={podcast.job_id} className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-start space-x-3 mb-4">
              <Headphones className="w-8 h-8 text-primary-600 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <h3 className="font-bold text-gray-900 truncate mb-1">
                  {podcast.transcription_params?.name || 'Untitled Podcast'}
                </h3>
                <p className="text-sm text-gray-500">
                  {new Date(podcast.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Duration:</span>
                <span className="font-medium">{podcast.transcription_params?.duration || 15} min</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Size:</span>
                <span className="font-medium">{(podcast.size / 1024 / 1024).toFixed(2)} MB</span>
              </div>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={() => handleDownload(podcast.job_id)}
                className="flex-1 bg-primary-600 text-white py-2 px-4 rounded-lg text-sm hover:bg-primary-700 transition-colors flex items-center justify-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Download</span>
              </button>
              <Link
                to={`/edit/${podcast.job_id}`}
                className="flex-1 border border-gray-300 text-gray-700 py-2 px-4 rounded-lg text-sm hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2"
              >
                <Edit className="w-4 h-4" />
                <span>Edit</span>
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

import { useState } from 'react'
import { Upload, Wand2, Loader2, CheckCircle2, XCircle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../utils/api'
import { StyleTemplate } from '../types'
import ProgressTracker from '../components/ProgressTracker'
import TemplateSelector from '../components/TemplateSelector'

export default function CreatePodcast() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [podcastName, setPodcastName] = useState('')
  const [duration, setDuration] = useState(15)
  const [speaker1Name, setSpeaker1Name] = useState('Alex')
  const [speaker2Name, setSpeaker2Name] = useState('Jordan')
  const [customInstructions, setCustomInstructions] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Fetch templates
  const { data: templates } = useQuery({
    queryKey: ['templates'],
    queryFn: api.getTemplates,
  })

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files))
    }
  }

  const handleGenerate = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one PDF file')
      return
    }

    if (!podcastName.trim()) {
      setError('Please enter a podcast name')
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      const formData = new FormData()

      // Add files
      selectedFiles.forEach(file => {
        formData.append('files', file)
      })

      // Add parameters
      formData.append('name', podcastName)
      formData.append('duration', duration.toString())
      formData.append('speaker_1_name', speaker1Name)
      formData.append('speaker_2_name', speaker2Name)
      formData.append('userId', 'demo-user')  // TODO: Get from auth

      if (selectedTemplate) {
        formData.append('template_id', selectedTemplate)
      }

      if (customInstructions) {
        formData.append('guide', customInstructions)
      }

      const response = await api.createPodcast(formData)
      setJobId(response.job_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start podcast generation')
      setIsGenerating(false)
    }
  }

  const handleNewPodcast = () => {
    setSelectedFiles([])
    setJobId(null)
    setIsGenerating(false)
    setError(null)
    setPodcastName('')
    setCustomInstructions('')
  }

  if (jobId && isGenerating) {
    return (
      <div className="max-w-4xl mx-auto">
        <ProgressTracker
          jobId={jobId}
          onComplete={() => setIsGenerating(false)}
          onError={(err) => {
            setError(err)
            setIsGenerating(false)
          }}
        />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Create Your Podcast
        </h1>
        <p className="text-lg text-gray-600">
          Transform PDFs into engaging audio conversations
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-red-800">Error</h3>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Main Form */}
      <div className="bg-white rounded-xl shadow-sm border p-8 space-y-6">
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload PDFs
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-500 transition-colors">
            <input
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">
                Click to upload or drag and drop
              </p>
              <p className="text-sm text-gray-500">
                PDF files only
              </p>
            </label>
          </div>

          {selectedFiles.length > 0 && (
            <div className="mt-4 space-y-2">
              {selectedFiles.map((file, idx) => (
                <div key={idx} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-gray-700">{file.name}</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Template Selection */}
        {templates && (
          <TemplateSelector
            templates={templates.templates || []}
            selected={selectedTemplate}
            onChange={setSelectedTemplate}
          />
        )}

        {/* Podcast Settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Podcast Name
            </label>
            <input
              type="text"
              value={podcastName}
              onChange={(e) => setPodcastName(e.target.value)}
              placeholder="My Awesome Podcast"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Duration (minutes)
            </label>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              min="5"
              max="60"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Speaker 1 Name
            </label>
            <input
              type="text"
              value={speaker1Name}
              onChange={(e) => setSpeaker1Name(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Speaker 2 Name
            </label>
            <input
              type="text"
              value={speaker2Name}
              onChange={(e) => setSpeaker2Name(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>

        {/* Custom Instructions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom Instructions (Optional)
          </label>
          <textarea
            value={customInstructions}
            onChange={(e) => setCustomInstructions(e.target.value)}
            rows={4}
            placeholder="Focus on key takeaways and insights..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating || selectedFiles.length === 0}
          className="w-full bg-gradient-to-r from-primary-600 to-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:from-primary-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <Wand2 className="w-5 h-5" />
              <span>Generate Podcast</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}

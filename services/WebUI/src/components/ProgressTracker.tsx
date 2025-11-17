import { useEffect, useState, useRef } from 'react'
import { Loader2, CheckCircle2, XCircle, Download } from 'lucide-react'
import { StatusUpdate } from '../types'
import { api } from '../utils/api'

interface ProgressTrackerProps {
  jobId: string
  onComplete: () => void
  onError: (error: string) => void
}

export default function ProgressTracker({ jobId, onComplete, onError }: ProgressTrackerProps) {
  const [status, setStatus] = useState<{ [key: string]: StatusUpdate }>({})
  const [isComplete, setIsComplete] = useState(false)
  const [hasFailed, setHasFailed] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const ws = new WebSocket(`ws://localhost:8002/ws/status/${jobId}`)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const update: StatusUpdate = JSON.parse(event.data)

        setStatus((prev) => ({
          ...prev,
          [update.service]: update
        }))

        // Check if all services are complete
        if (update.status === 'completed' && update.service === 'tts') {
          setIsComplete(true)
          setTimeout(onComplete, 1000)
        }

        if (update.status === 'failed') {
          setHasFailed(true)
          onError(update.message || 'Podcast generation failed')
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      onError('Connection error. Please try again.')
    }

    ws.onclose = () => {
      console.log('WebSocket closed')
    }

    return () => {
      ws.close()
    }
  }, [jobId, onComplete, onError])

  const getStepStatus = (serviceName: string) => {
    const update = status[serviceName]
    if (!update) return 'pending'
    return update.status
  }

  const getStepPercentage = (serviceName: string) => {
    const update = status[serviceName]
    return update?.percentage || 0
  }

  const steps = [
    { id: 'pdf', name: 'Processing PDFs', service: 'pdf' },
    { id: 'agent', name: 'Generating Dialogue', service: 'agent' },
    { id: 'tts', name: 'Creating Audio', service: 'tts' },
  ]

  const handleDownload = async () => {
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

  // Calculate overall progress
  const overallProgress = steps.reduce((acc, step) => {
    return acc + getStepPercentage(step.service)
  }, 0) / steps.length

  return (
    <div className="bg-white rounded-xl shadow-sm border p-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {isComplete ? 'Podcast Complete!' : hasFailed ? 'Generation Failed' : 'Generating Your Podcast'}
        </h2>
        <p className="text-gray-600">
          {isComplete
            ? 'Your podcast is ready to download'
            : hasFailed
            ? 'Please try again or contact support'
            : 'This may take a few minutes...'}
        </p>
      </div>

      {/* Overall Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span className="text-sm font-medium text-gray-900">{Math.round(overallProgress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-primary-600 to-blue-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${overallProgress}%` }}
          />
        </div>
      </div>

      {/* Step-by-step Progress */}
      <div className="space-y-6">
        {steps.map((step, idx) => {
          const stepStatus = getStepStatus(step.service)
          const percentage = getStepPercentage(step.service)
          const update = status[step.service]

          return (
            <div key={step.id} className="border-l-4 border-gray-200 pl-6 pb-6 last:pb-0">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 mt-1">
                  {stepStatus === 'completed' ? (
                    <CheckCircle2 className="w-6 h-6 text-green-600" />
                  ) : stepStatus === 'failed' ? (
                    <XCircle className="w-6 h-6 text-red-600" />
                  ) : stepStatus === 'processing' ? (
                    <Loader2 className="w-6 h-6 text-primary-600 animate-spin" />
                  ) : (
                    <div className="w-6 h-6 rounded-full border-2 border-gray-300" />
                  )}
                </div>

                <div className="flex-1">
                  <h3 className="font-medium text-gray-900 mb-1">{step.name}</h3>

                  {update?.message && (
                    <p className="text-sm text-gray-600 mb-2">{update.message}</p>
                  )}

                  {stepStatus === 'processing' && percentage > 0 && (
                    <div className="space-y-2">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>

                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>{percentage.toFixed(1)}% complete</span>
                        {update?.eta_seconds && update.eta_seconds > 0 && (
                          <span>~{Math.ceil(update.eta_seconds / 60)} min remaining</span>
                        )}
                      </div>

                      {update?.tokens_used && (
                        <div className="text-xs text-gray-500">
                          Tokens: {update.tokens_used.toLocaleString()}
                          {update?.estimated_cost && ` | Cost: $${update.estimated_cost.toFixed(4)}`}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Download Button */}
      {isComplete && (
        <div className="mt-8 pt-8 border-t">
          <button
            onClick={handleDownload}
            className="w-full bg-gradient-to-r from-primary-600 to-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:from-primary-700 hover:to-blue-700 transition-all flex items-center justify-center space-x-2"
          >
            <Download className="w-5 h-5" />
            <span>Download Podcast</span>
          </button>
        </div>
      )}
    </div>
  )
}

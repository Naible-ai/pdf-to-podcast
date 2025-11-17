import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Download, FileText } from 'lucide-react'
import { api } from '../utils/api'
import { useState } from 'react'

export default function EditPodcast() {
  const { jobId } = useParams<{ jobId: string }>()
  const [selectedFormat, setSelectedFormat] = useState('srt')

  const { data: versions } = useQuery({
    queryKey: ['versions', jobId],
    queryFn: () => api.getVersions(jobId!),
    enabled: !!jobId,
  })

  const { data: exportFormats } = useQuery({
    queryKey: ['export-formats', jobId],
    queryFn: () => api.getExportFormats(jobId!),
    enabled: !!jobId,
  })

  const handleExport = async () => {
    if (!jobId) return

    try {
      const blob = await api.exportPodcast(jobId, selectedFormat)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const format = exportFormats?.formats.find((f: any) => f.id === selectedFormat)
      a.download = `podcast_${jobId}.${format?.extension || selectedFormat}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Export error:', err)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Edit Podcast</h1>
        <p className="text-lg text-gray-600">Job ID: {jobId}</p>
      </div>

      {/* Version History */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Version History</h2>
        {versions && versions.versions.length > 0 ? (
          <div className="space-y-3">
            {versions.versions.map((version: any) => (
              <div key={version.version_id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-gray-900">{version.version_id}</h3>
                    <p className="text-sm text-gray-500">
                      {new Date(version.created_at).toLocaleString()} | {version.segment_count} segments | {version.edits_count} edits
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No version history available</p>
        )}
      </div>

      {/* Export Options */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
          <FileText className="w-6 h-6" />
          <span>Export Transcript</span>
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Format
            </label>
            <select
              value={selectedFormat}
              onChange={(e) => setSelectedFormat(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              {exportFormats?.formats.map((format: any) => (
                <option key={format.id} value={format.id}>
                  {format.name} (.{format.extension}) - {format.description}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleExport}
            className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-primary-700 transition-colors flex items-center justify-center space-x-2"
          >
            <Download className="w-5 h-5" />
            <span>Export Transcript</span>
          </button>
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
        <h3 className="font-bold text-yellow-900 mb-2">🚧 Editing Features Coming Soon!</h3>
        <p className="text-yellow-800">
          Advanced editing features like segment regeneration, dialogue editing, and undo/redo are currently in development.
          For now, you can export your podcast in various formats.
        </p>
      </div>
    </div>
  )
}

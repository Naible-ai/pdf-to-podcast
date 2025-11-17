import { useQuery } from '@tanstack/react-query'
import { Sparkles, CheckCircle2 } from 'lucide-react'
import { api } from '../utils/api'

export default function Templates() {
  const { data: templatesData, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: api.getTemplates,
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading templates...</div>
  }

  const templates = templatesData?.templates || []

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Podcast Style Templates</h1>
        <p className="text-lg text-gray-600">
          Choose from pre-configured styles optimized for different types of content
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template: any) => (
          <div
            key={template.id}
            className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start space-x-3 mb-4">
              <Sparkles className="w-6 h-6 text-primary-600 flex-shrink-0" />
              <div>
                <h3 className="font-bold text-gray-900 text-lg">{template.name}</h3>
              </div>
            </div>

            <p className="text-gray-600 mb-4">{template.description}</p>

            <div className="bg-gray-50 rounded-lg p-3 mb-4">
              <p className="text-sm text-gray-700">
                <span className="font-medium">Best for:</span> {template.use_case}
              </p>
            </div>

            <div className="flex items-center text-sm text-gray-500">
              <CheckCircle2 className="w-4 h-4 mr-2" />
              <span>Optimized voice settings & LLM parameters</span>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="font-bold text-blue-900 mb-2">How Templates Work</h3>
        <ul className="space-y-2 text-blue-800">
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 mt-1">•</span>
            <span>Each template combines voice settings, LLM parameters, and style instructions</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 mt-1">•</span>
            <span>Voice stability, expressiveness, and tone are pre-optimized</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 mt-1">•</span>
            <span>You can still add custom instructions to further refine the output</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-600 mt-1">•</span>
            <span>Templates are a starting point - experiment to find what works best!</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

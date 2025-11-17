import { StyleTemplate } from '../types'
import { CheckCircle2, Circle } from 'lucide-react'

interface TemplateSelectorProps {
  templates: StyleTemplate[]
  selected: string
  onChange: (templateId: string) => void
}

export default function TemplateSelector({ templates, selected, onChange }: TemplateSelectorProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-3">
        Style Template (Optional)
      </label>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((template) => (
          <button
            key={template.id}
            onClick={() => onChange(selected === template.id ? '' : template.id)}
            className={`text-left p-4 rounded-lg border-2 transition-all ${
              selected === template.id
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300 bg-white'
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-medium text-gray-900">{template.name}</h3>
              {selected === template.id ? (
                <CheckCircle2 className="w-5 h-5 text-primary-600 flex-shrink-0" />
              ) : (
                <Circle className="w-5 h-5 text-gray-400 flex-shrink-0" />
              )}
            </div>
            <p className="text-sm text-gray-600 mb-2">{template.description}</p>
            <p className="text-xs text-gray-500 italic">{template.use_case}</p>
          </button>
        ))}
      </div>
      {!selected && (
        <p className="mt-2 text-sm text-gray-500">
          No template selected - will use default settings
        </p>
      )}
    </div>
  )
}

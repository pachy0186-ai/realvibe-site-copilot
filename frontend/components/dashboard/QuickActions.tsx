import Link from 'next/link'
import { 
  PlayIcon,
  DocumentPlusIcon,
  FolderPlusIcon,
  EyeIcon,
  CogIcon
} from '@heroicons/react/24/outline'

const quickActions = [
  {
    name: 'Start New Autofill',
    description: 'Begin auto-filling a questionnaire',
    href: '/site-copilot/questionnaires/new',
    icon: PlayIcon,
    color: 'bg-blue-500 hover:bg-blue-600',
    primary: true
  },
  {
    name: 'Upload Documents',
    description: 'Add files to answer memory',
    href: '/site-copilot/files/upload',
    icon: FolderPlusIcon,
    color: 'bg-green-500 hover:bg-green-600'
  },
  {
    name: 'Create Template',
    description: 'Add new questionnaire template',
    href: '/site-copilot/questionnaires/templates/new',
    icon: DocumentPlusIcon,
    color: 'bg-purple-500 hover:bg-purple-600'
  },
  {
    name: 'Review Pending',
    description: 'Review questionnaires needing attention',
    href: '/site-copilot/review',
    icon: EyeIcon,
    color: 'bg-orange-500 hover:bg-orange-600'
  },
  {
    name: 'Site Settings',
    description: 'Configure site preferences',
    href: '/site-copilot/settings',
    icon: CogIcon,
    color: 'bg-gray-500 hover:bg-gray-600'
  }
]

export default function QuickActions() {
  return (
    <div className="bg-white shadow-sm rounded-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Quick Actions</h2>
      
      <div className="space-y-4">
        {quickActions.map((action) => (
          <Link
            key={action.name}
            href={action.href}
            className={`block p-4 rounded-lg border-2 border-transparent transition-all duration-200 hover:border-gray-200 hover:shadow-sm group ${
              action.primary ? 'bg-gradient-to-r from-blue-50 to-purple-50 hover:from-blue-100 hover:to-purple-100' : 'bg-gray-50 hover:bg-gray-100'
            }`}
          >
            <div className="flex items-center space-x-4">
              <div className={`p-2 rounded-lg text-white transition-colors ${action.color}`}>
                <action.icon className="h-5 w-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium transition-colors ${
                  action.primary ? 'text-gray-900 group-hover:text-blue-700' : 'text-gray-900'
                }`}>
                  {action.name}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {action.description}
                </p>
              </div>
              <div className="text-gray-400 group-hover:text-gray-600 transition-colors">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>
        ))}
      </div>
      
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="text-center">
          <p className="text-sm text-gray-500 mb-2">Need help getting started?</p>
          <Link
            href="/site-copilot/help"
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            View Documentation →
          </Link>
        </div>
      </div>
    </div>
  )
}


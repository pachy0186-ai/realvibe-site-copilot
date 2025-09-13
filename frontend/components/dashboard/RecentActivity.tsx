import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'

interface ActivityItem {
  id: string
  type: 'completed' | 'in_progress' | 'needs_review' | 'uploaded'
  title: string
  description: string
  timestamp: string
  href?: string
}

const mockActivities: ActivityItem[] = [
  {
    id: '1',
    type: 'completed',
    title: 'Pfizer Phase III Feasibility',
    description: 'Autofill completed with 72% success rate',
    timestamp: '2 hours ago',
    href: '/site-copilot/runs/run-001'
  },
  {
    id: '2',
    type: 'needs_review',
    title: 'Novartis Oncology Study',
    description: '3 fields require manual review',
    timestamp: '4 hours ago',
    href: '/site-copilot/review/run-002'
  },
  {
    id: '3',
    type: 'in_progress',
    title: 'J&J Cardiovascular Trial',
    description: 'Autofill in progress (45% complete)',
    timestamp: '6 hours ago',
    href: '/site-copilot/runs/run-003'
  },
  {
    id: '4',
    type: 'uploaded',
    title: 'Site Documents Updated',
    description: 'Added investigator CV and site qualification forms',
    timestamp: '1 day ago',
    href: '/site-copilot/files'
  },
  {
    id: '5',
    type: 'completed',
    title: 'GSK Respiratory Study',
    description: 'Autofill completed with 89% success rate',
    timestamp: '2 days ago',
    href: '/site-copilot/runs/run-004'
  }
]

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'completed':
      return CheckCircleIcon
    case 'in_progress':
      return ClockIcon
    case 'needs_review':
      return ExclamationTriangleIcon
    case 'uploaded':
      return DocumentTextIcon
    default:
      return DocumentTextIcon
  }
}

const getActivityColor = (type: string) => {
  switch (type) {
    case 'completed':
      return 'text-green-600 bg-green-100'
    case 'in_progress':
      return 'text-blue-600 bg-blue-100'
    case 'needs_review':
      return 'text-orange-600 bg-orange-100'
    case 'uploaded':
      return 'text-purple-600 bg-purple-100'
    default:
      return 'text-gray-600 bg-gray-100'
  }
}

export default function RecentActivity() {
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Replace with actual API call
    setTimeout(() => {
      setActivities(mockActivities)
      setLoading(false)
    }, 800)
  }, [])

  if (loading) {
    return (
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Recent Activity</h2>
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-start space-x-4 animate-pulse">
              <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
              <div className="h-3 bg-gray-200 rounded w-16"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white shadow-sm rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
        <Link
          href="/site-copilot/activity"
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          View all →
        </Link>
      </div>
      
      <div className="space-y-4">
        {activities.map((activity) => {
          const Icon = getActivityIcon(activity.type)
          const colorClass = getActivityColor(activity.type)
          
          const content = (
            <div className="flex items-start space-x-4 p-3 rounded-lg transition-colors hover:bg-gray-50">
              <div className={`p-2 rounded-full ${colorClass}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">
                  {activity.title}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {activity.description}
                </p>
              </div>
              <div className="text-xs text-gray-400 whitespace-nowrap">
                {activity.timestamp}
              </div>
            </div>
          )
          
          return activity.href ? (
            <Link key={activity.id} href={activity.href}>
              {content}
            </Link>
          ) : (
            <div key={activity.id}>
              {content}
            </div>
          )
        })}
      </div>
      
      {activities.length === 0 && !loading && (
        <div className="text-center py-8">
          <DocumentTextIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No recent activity</p>
          <p className="text-sm text-gray-400 mt-1">
            Start your first autofill to see activity here
          </p>
        </div>
      )}
    </div>
  )
}


import { 
  CheckCircleIcon,
  PencilIcon,
  ExclamationTriangleIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

interface ReviewSummaryProps {
  stats: {
    accepted: number
    edited: number
    needsReview: number
  }
  totalFields: number
  autofillPercentage: number
}

export default function ReviewSummary({ stats, totalFields, autofillPercentage }: ReviewSummaryProps) {
  const completedFields = stats.accepted + stats.edited
  const completionPercentage = Math.round((completedFields / totalFields) * 100)

  return (
    <div className="bg-white shadow-sm rounded-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <ChartBarIcon className="h-5 w-5 text-gray-400" />
        <h3 className="text-lg font-medium text-gray-900">Review Summary</h3>
      </div>

      {/* Progress Overview */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Review Progress</span>
          <span className="text-sm font-medium text-gray-900">
            {completedFields}/{totalFields} fields
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
        <div className="text-center mt-2">
          <span className="text-2xl font-bold text-blue-600">{completionPercentage}%</span>
          <span className="text-sm text-gray-500 ml-1">complete</span>
        </div>
      </div>

      {/* Status Breakdown */}
      <div className="space-y-4 mb-6">
        <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <CheckCircleIcon className="h-5 w-5 text-green-600" />
            <span className="text-sm font-medium text-green-900">Accepted</span>
          </div>
          <span className="text-lg font-bold text-green-600">{stats.accepted}</span>
        </div>

        <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <PencilIcon className="h-5 w-5 text-blue-600" />
            <span className="text-sm font-medium text-blue-900">Edited</span>
          </div>
          <span className="text-lg font-bold text-blue-600">{stats.edited}</span>
        </div>

        <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <ExclamationTriangleIcon className="h-5 w-5 text-orange-600" />
            <span className="text-sm font-medium text-orange-900">Needs Review</span>
          </div>
          <span className="text-lg font-bold text-orange-600">{stats.needsReview}</span>
        </div>
      </div>

      {/* Autofill Performance */}
      <div className="border-t border-gray-200 pt-6">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Autofill Performance</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Initial Autofill Rate</span>
            <span className="text-sm font-medium text-gray-900">{autofillPercentage}%</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Fields Requiring Review</span>
            <span className="text-sm font-medium text-gray-900">
              {totalFields - Math.round((autofillPercentage / 100) * totalFields)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Review Efficiency</span>
            <span className={`text-sm font-medium ${
              completionPercentage >= 80 ? 'text-green-600' : 
              completionPercentage >= 60 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {completionPercentage >= 80 ? 'Excellent' : 
               completionPercentage >= 60 ? 'Good' : 'Needs Attention'}
            </span>
          </div>
        </div>
      </div>

      {/* Action Items */}
      {stats.needsReview > 0 && (
        <div className="border-t border-gray-200 pt-6 mt-6">
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <ExclamationTriangleIcon className="h-5 w-5 text-orange-600" />
              <span className="text-sm font-medium text-orange-900">Action Required</span>
            </div>
            <p className="text-sm text-orange-700">
              {stats.needsReview} field{stats.needsReview > 1 ? 's' : ''} require{stats.needsReview === 1 ? 's' : ''} manual review before submission.
            </p>
          </div>
        </div>
      )}

      {/* Completion Status */}
      {stats.needsReview === 0 && (
        <div className="border-t border-gray-200 pt-6 mt-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <CheckCircleIcon className="h-5 w-5 text-green-600" />
              <span className="text-sm font-medium text-green-900">Ready to Submit</span>
            </div>
            <p className="text-sm text-green-700">
              All fields have been reviewed and are ready for submission.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}


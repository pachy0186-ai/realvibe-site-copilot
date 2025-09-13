import { useState } from 'react'
import { 
  CheckIcon,
  PencilIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  LinkIcon
} from '@heroicons/react/24/outline'

interface Evidence {
  file_id: string
  file_name: string
  page: number
  text: string
}

interface FieldAnswer {
  id: string
  label: string
  value: string
  confidence: number
  evidence: Evidence[]
  status: 'accepted' | 'edited' | 'needs_review'
  reviewer_comments?: string
}

interface FieldCardProps {
  field: FieldAnswer
  onUpdate: (updates: Partial<FieldAnswer>) => void
}

export default function FieldCard({ field, onUpdate }: FieldCardProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState(field.value)
  const [comments, setComments] = useState(field.reviewer_comments || '')
  const [showEvidence, setShowEvidence] = useState(false)

  const handleAccept = () => {
    onUpdate({ status: 'accepted' })
  }

  const handleEdit = () => {
    if (isEditing) {
      onUpdate({ 
        value: editValue, 
        status: 'edited',
        reviewer_comments: comments || undefined
      })
      setIsEditing(false)
    } else {
      setIsEditing(true)
    }
  }

  const handleNeedsReview = () => {
    onUpdate({ 
      status: 'needs_review',
      reviewer_comments: comments || 'Requires manual review'
    })
  }

  const getStatusColor = () => {
    switch (field.status) {
      case 'accepted':
        return 'border-green-200 bg-green-50'
      case 'edited':
        return 'border-blue-200 bg-blue-50'
      case 'needs_review':
        return 'border-orange-200 bg-orange-50'
      default:
        return 'border-gray-200 bg-white'
    }
  }

  const getStatusIcon = () => {
    switch (field.status) {
      case 'accepted':
        return <CheckIcon className="h-5 w-5 text-green-600" />
      case 'edited':
        return <PencilIcon className="h-5 w-5 text-blue-600" />
      case 'needs_review':
        return <ExclamationTriangleIcon className="h-5 w-5 text-orange-600" />
      default:
        return null
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-500'
    if (confidence >= 0.6) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className={`rounded-lg border-2 p-6 transition-all duration-200 ${getStatusColor()}`}>
      {/* Field Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-lg font-medium text-gray-900">{field.label}</h3>
            {getStatusIcon()}
          </div>
          
          {/* Confidence Score */}
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-sm text-gray-500">Confidence:</span>
            <div className="flex items-center space-x-2">
              <div className="w-24 h-2 bg-gray-200 rounded-full">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${getConfidenceColor(field.confidence)}`}
                  style={{ width: `${field.confidence * 100}%` }}
                />
              </div>
              <span className="text-sm font-medium text-gray-700">
                {Math.round(field.confidence * 100)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Field Value */}
      <div className="mb-4">
        {isEditing ? (
          <div className="space-y-3">
            <textarea
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
              placeholder="Enter field value..."
            />
            <textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={2}
              placeholder="Add comments (optional)..."
            />
          </div>
        ) : (
          <div className="p-3 bg-white rounded-md border border-gray-200">
            <p className="text-gray-900 whitespace-pre-wrap">{field.value}</p>
            {field.reviewer_comments && (
              <div className="mt-2 pt-2 border-t border-gray-100">
                <p className="text-sm text-gray-600 italic">
                  Note: {field.reviewer_comments}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Evidence Section */}
      <div className="mb-4">
        <button
          onClick={() => setShowEvidence(!showEvidence)}
          className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          <DocumentTextIcon className="h-4 w-4" />
          <span>
            {showEvidence ? 'Hide' : 'Show'} Evidence ({field.evidence.length})
          </span>
        </button>
        
        {showEvidence && (
          <div className="mt-3 space-y-2">
            {field.evidence.map((evidence, index) => (
              <div key={index} className="p-3 bg-white rounded-md border border-gray-200">
                <div className="flex items-center space-x-2 mb-2">
                  <LinkIcon className="h-4 w-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-700">
                    {evidence.file_name}
                  </span>
                  <span className="text-xs text-gray-500">
                    Page {evidence.page}
                  </span>
                </div>
                <p className="text-sm text-gray-600 italic">
                  "{evidence.text.substring(0, 150)}..."
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-3">
        <button
          onClick={handleAccept}
          className={`btn flex items-center space-x-2 ${
            field.status === 'accepted' 
              ? 'bg-green-100 text-green-700 border-green-200' 
              : 'btn-outline'
          }`}
        >
          <CheckIcon className="h-4 w-4" />
          <span>Accept</span>
        </button>
        
        <button
          onClick={handleEdit}
          className={`btn flex items-center space-x-2 ${
            field.status === 'edited' || isEditing
              ? 'bg-blue-100 text-blue-700 border-blue-200' 
              : 'btn-outline'
          }`}
        >
          <PencilIcon className="h-4 w-4" />
          <span>{isEditing ? 'Save' : 'Edit'}</span>
        </button>
        
        <button
          onClick={handleNeedsReview}
          className={`btn flex items-center space-x-2 ${
            field.status === 'needs_review' 
              ? 'bg-orange-100 text-orange-700 border-orange-200' 
              : 'btn-outline'
          }`}
        >
          <ExclamationTriangleIcon className="h-4 w-4" />
          <span>Needs Review</span>
        </button>
        
        {isEditing && (
          <button
            onClick={() => {
              setIsEditing(false)
              setEditValue(field.value)
              setComments(field.reviewer_comments || '')
            }}
            className="btn btn-outline text-gray-600"
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  )
}


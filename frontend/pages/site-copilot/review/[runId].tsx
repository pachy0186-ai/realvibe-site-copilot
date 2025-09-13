import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { 
  CheckIcon,
  PencilIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  ArrowLeftIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import Layout from '@/components/common/Layout'
import FieldCard from '@/components/review/FieldCard'
import ReviewSummary from '@/components/review/ReviewSummary'

interface FieldAnswer {
  id: string
  label: string
  value: string
  confidence: number
  evidence: Array<{
    file_id: string
    file_name: string
    page: number
    text: string
  }>
  status: 'accepted' | 'edited' | 'needs_review'
  reviewer_comments?: string
}

interface ReviewData {
  run_id: string
  questionnaire_name: string
  sponsor: string
  status: string
  autofill_percentage: number
  total_fields: number
  fields: FieldAnswer[]
  start_time: string
}

export default function ReviewScreen() {
  const router = useRouter()
  const { runId } = router.query
  const [reviewData, setReviewData] = useState<ReviewData | null>(null)
  const [loading, setLoading] = useState(true)
  const [reviewStartTime] = useState(Date.now())

  useEffect(() => {
    if (runId) {
      fetchReviewData(runId as string)
    }
  }, [runId])

  const fetchReviewData = async (id: string) => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch(`/api/v1/runs/${id}/review`)
      // const data = await response.json()
      
      // Mock data for now
      setTimeout(() => {
        setReviewData({
          run_id: id,
          questionnaire_name: 'Pfizer Phase III Feasibility Questionnaire',
          sponsor: 'Pfizer Inc.',
          status: 'needs_review',
          autofill_percentage: 72.5,
          total_fields: 24,
          fields: [
            {
              id: 'investigator_name',
              label: 'Principal Investigator Name',
              value: 'Dr. Sarah Johnson, MD, PhD',
              confidence: 0.95,
              evidence: [
                {
                  file_id: 'cv_001',
                  file_name: 'investigator_cv.pdf',
                  page: 1,
                  text: 'Dr. Sarah Johnson, MD, PhD, is a board-certified cardiologist...'
                }
              ],
              status: 'accepted'
            },
            {
              id: 'site_address',
              label: 'Site Address',
              value: '123 Medical Center Drive, Suite 400, Boston, MA 02115',
              confidence: 0.88,
              evidence: [
                {
                  file_id: 'site_info_001',
                  file_name: 'site_qualification_form.pdf',
                  page: 2,
                  text: 'Site Address: 123 Medical Center Drive, Suite 400, Boston, MA 02115'
                }
              ],
              status: 'accepted'
            },
            {
              id: 'patient_population',
              label: 'Available Patient Population',
              value: 'Approximately 150-200 patients with heart failure',
              confidence: 0.65,
              evidence: [
                {
                  file_id: 'patient_db_001',
                  file_name: 'patient_database_summary.pdf',
                  page: 3,
                  text: 'Our database contains approximately 150-200 patients diagnosed with heart failure...'
                }
              ],
              status: 'needs_review',
              reviewer_comments: 'Please verify the exact patient count and inclusion criteria'
            },
            {
              id: 'recruitment_rate',
              label: 'Expected Monthly Recruitment Rate',
              value: '8-12 patients per month',
              confidence: 0.72,
              evidence: [
                {
                  file_id: 'recruitment_001',
                  file_name: 'historical_recruitment_data.xlsx',
                  page: 1,
                  text: 'Historical data shows average recruitment of 8-12 patients per month for similar studies'
                }
              ],
              status: 'edited'
            }
          ],
          start_time: '2024-01-15T10:30:00Z'
        })
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Failed to fetch review data:', error)
      setLoading(false)
    }
  }

  const handleFieldUpdate = (fieldId: string, updates: Partial<FieldAnswer>) => {
    if (!reviewData) return
    
    setReviewData({
      ...reviewData,
      fields: reviewData.fields.map(field =>
        field.id === fieldId ? { ...field, ...updates } : field
      )
    })
  }

  const handleSubmitReview = async () => {
    if (!reviewData) return
    
    const reviewTime = Math.round((Date.now() - reviewStartTime) / 1000 / 60) // minutes
    
    try {
      // TODO: Submit review to API
      console.log('Submitting review:', {
        run_id: reviewData.run_id,
        review_time: reviewTime,
        fields: reviewData.fields
      })
      
      // Redirect to dashboard
      router.push('/site-copilot')
    } catch (error) {
      console.error('Failed to submit review:', error)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-48 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
            <div className="h-64 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </Layout>
    )
  }

  if (!reviewData) {
    return (
      <Layout>
        <div className="text-center py-12">
          <ExclamationTriangleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Review Not Found</h2>
          <p className="text-gray-600 mb-4">The requested review could not be found.</p>
          <Link href="/site-copilot" className="btn-primary">
            Return to Dashboard
          </Link>
        </div>
      </Layout>
    )
  }

  const reviewStats = {
    accepted: reviewData.fields.filter(f => f.status === 'accepted').length,
    edited: reviewData.fields.filter(f => f.status === 'edited').length,
    needsReview: reviewData.fields.filter(f => f.status === 'needs_review').length
  }

  return (
    <>
      <Head>
        <title>Review - {reviewData.questionnaire_name} - RealVibe Site Copilot</title>
      </Head>

      <Layout>
        <div className="space-y-6">
          {/* Header */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Link
                  href="/site-copilot"
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <ArrowLeftIcon className="h-6 w-6" />
                </Link>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    Review Questionnaire
                  </h1>
                  <p className="text-gray-600 mt-1">
                    {reviewData.questionnaire_name} • {reviewData.sponsor}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-sm text-gray-500">Autofill Rate</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {reviewData.autofill_percentage}%
                  </div>
                </div>
                <button
                  onClick={handleSubmitReview}
                  className="btn-primary flex items-center space-x-2"
                >
                  <CheckIcon className="h-5 w-5" />
                  <span>Submit Review</span>
                </button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Field Cards */}
            <div className="lg:col-span-2 space-y-4">
              {reviewData.fields.map((field) => (
                <FieldCard
                  key={field.id}
                  field={field}
                  onUpdate={(updates) => handleFieldUpdate(field.id, updates)}
                />
              ))}
            </div>

            {/* Review Summary Sidebar */}
            <div className="space-y-6">
              <ReviewSummary
                stats={reviewStats}
                totalFields={reviewData.total_fields}
                autofillPercentage={reviewData.autofill_percentage}
              />
              
              {/* Review Timer */}
              <div className="bg-white shadow-sm rounded-lg p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <ClockIcon className="h-5 w-5 text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900">Review Time</h3>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {Math.round((Date.now() - reviewStartTime) / 1000 / 60)}
                  </div>
                  <div className="text-sm text-gray-500">minutes</div>
                </div>
                <div className="mt-4 text-xs text-gray-400 text-center">
                  Target: ≤15 minutes
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  )
}


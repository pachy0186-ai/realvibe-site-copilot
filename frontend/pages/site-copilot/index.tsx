import { useState, useEffect } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { 
  ChartBarIcon, 
  ClockIcon, 
  DocumentTextIcon,
  PlayIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import Layout from '@/components/common/Layout'
import MetricsCard from '@/components/dashboard/MetricsCard'
import RecentActivity from '@/components/dashboard/RecentActivity'
import QuickActions from '@/components/dashboard/QuickActions'

interface DashboardMetrics {
  autofill_percentage: number
  average_review_time: number
  cycle_time_reduction: number
  total_runs: number
  completed_runs: number
}

export default function SiteCopilotDashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    autofill_percentage: 0,
    average_review_time: 0,
    cycle_time_reduction: 0,
    total_runs: 0,
    completed_runs: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardMetrics()
  }, [])

  const fetchDashboardMetrics = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch('/api/v1/dashboard/metrics')
      // const data = await response.json()
      
      // Mock data for now
      setTimeout(() => {
        setMetrics({
          autofill_percentage: 67.5,
          average_review_time: 12.3,
          cycle_time_reduction: 2.8,
          total_runs: 24,
          completed_runs: 22
        })
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Failed to fetch dashboard metrics:', error)
      setLoading(false)
    }
  }

  return (
    <>
      <Head>
        <title>Dashboard - RealVibe Site Copilot</title>
        <meta name="description" content="Clinical trial feasibility questionnaire automation dashboard" />
      </Head>

      <Layout>
        <div className="space-y-8">
          {/* Header */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Site Copilot Dashboard</h1>
                <p className="mt-2 text-gray-600">
                  AI-powered questionnaire automation for clinical trial feasibility
                </p>
              </div>
              <div className="flex space-x-3">
                <Link
                  href="/site-copilot/questionnaires/new"
                  className="btn-primary flex items-center space-x-2"
                >
                  <PlayIcon className="h-5 w-5" />
                  <span>Start Autofill</span>
                </Link>
              </div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricsCard
              title="Autofill Rate"
              value={`${metrics.autofill_percentage}%`}
              icon={ChartBarIcon}
              trend={metrics.autofill_percentage >= 60 ? 'up' : 'down'}
              trendValue="5.2%"
              loading={loading}
              className="bg-gradient-to-r from-blue-500 to-blue-600 text-white"
            />
            
            <MetricsCard
              title="Avg Review Time"
              value={`${metrics.average_review_time} min`}
              icon={ClockIcon}
              trend="down"
              trendValue="2.1 min"
              loading={loading}
              className="bg-gradient-to-r from-green-500 to-green-600 text-white"
            />
            
            <MetricsCard
              title="Time Saved"
              value={`${metrics.cycle_time_reduction} weeks`}
              icon={CheckCircleIcon}
              trend="up"
              trendValue="0.4 weeks"
              loading={loading}
              className="bg-gradient-to-r from-purple-500 to-purple-600 text-white"
            />
            
            <MetricsCard
              title="Completed Runs"
              value={`${metrics.completed_runs}/${metrics.total_runs}`}
              icon={DocumentTextIcon}
              trend="up"
              trendValue="3 this week"
              loading={loading}
              className="bg-gradient-to-r from-orange-500 to-orange-600 text-white"
            />
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Quick Actions */}
            <div className="lg:col-span-1">
              <QuickActions />
            </div>

            {/* Recent Activity */}
            <div className="lg:col-span-2">
              <RecentActivity />
            </div>
          </div>

          {/* Performance Overview */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Performance Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">≥60%</div>
                <div className="text-sm text-gray-600">Target Autofill Rate</div>
                <div className={`mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  metrics.autofill_percentage >= 60 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {metrics.autofill_percentage >= 60 ? 'On Track' : 'Below Target'}
                </div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">≤15 min</div>
                <div className="text-sm text-gray-600">Target Review Time</div>
                <div className={`mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  metrics.average_review_time <= 15 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {metrics.average_review_time <= 15 ? 'On Track' : 'Above Target'}
                </div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">≥2 weeks</div>
                <div className="text-sm text-gray-600">Target Time Savings</div>
                <div className={`mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  metrics.cycle_time_reduction >= 2 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {metrics.cycle_time_reduction >= 2 ? 'On Track' : 'Below Target'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </>
  )
}


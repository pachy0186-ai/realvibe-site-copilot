import React, { useState, useEffect } from 'react'
import Head from 'next/head'
import { 
  ChartBarIcon, 
  ClockIcon, 
  TrendingUpIcon,
  CalendarIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline'
import Layout from '@/components/common/Layout'
import MetricsChart from '@/components/dashboard/MetricsChart'
import PerformanceBenchmarks from '@/components/dashboard/PerformanceBenchmarks'

interface AnalyticsData {
  sponsor_performance: Array<{
    sponsor: string
    runs: number
    avg_autofill_rate: number
    avg_review_time: number
  }>
  distributions: {
    autofill_rate: Array<{
      range: string
      count: number
      percentage: number
    }>
    review_time: Array<{
      range: string
      count: number
      percentage: number
    }>
  }
  monthly_trends: Array<{
    month: string
    runs: number
    avg_autofill_rate: number
    avg_review_time: number
    total_time_saved: number
  }>
  statistics: {
    total_runs: number
    autofill_rate: {
      mean: number
      median: number
      std_dev: number
    }
    review_time: {
      mean: number
      median: number
      std_dev: number
    }
  }
}

interface BenchmarkData {
  benchmarks: {
    autofill_rate: {
      excellent: number
      good: number
      acceptable: number
      current: number
    }
    review_time: {
      excellent: number
      good: number
      acceptable: number
      current: number
    }
    completion_rate: {
      excellent: number
      good: number
      acceptable: number
      current: number
    }
  }
  scores: {
    autofill_rate: string
    review_time: string
    completion_rate: string
  }
  overall_score: string
  recommendations: string[]
}

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [benchmarks, setBenchmarks] = useState<BenchmarkData | null>(null)
  const [timeRange, setTimeRange] = useState('last_30d')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalyticsData()
    fetchBenchmarks()
  }, [timeRange])

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true)
      
      // Mock API call - replace with actual API
      setTimeout(() => {
        setAnalytics({
          sponsor_performance: [
            {
              sponsor: "Pfizer Inc.",
              runs: 8,
              avg_autofill_rate: 78.5,
              avg_review_time: 11.2
            },
            {
              sponsor: "Novartis AG",
              runs: 5,
              avg_autofill_rate: 72.1,
              avg_review_time: 13.8
            },
            {
              sponsor: "Johnson & Johnson",
              runs: 3,
              avg_autofill_rate: 69.3,
              avg_review_time: 15.1
            }
          ],
          distributions: {
            autofill_rate: [
              { range: "0-50", count: 2, percentage: 12.5 },
              { range: "50-70", count: 4, percentage: 25.0 },
              { range: "70-85", count: 8, percentage: 50.0 },
              { range: "85-100", count: 2, percentage: 12.5 }
            ],
            review_time: [
              { range: "0-5", count: 1, percentage: 6.3 },
              { range: "5-10", count: 3, percentage: 18.8 },
              { range: "10-15", count: 8, percentage: 50.0 },
              { range: "15-20", count: 3, percentage: 18.8 },
              { range: "20-30", count: 1, percentage: 6.3 }
            ]
          },
          monthly_trends: [
            { month: "2023-07", runs: 12, avg_autofill_rate: 68.2, avg_review_time: 16.5, total_time_saved: 3.2 },
            { month: "2023-08", runs: 15, avg_autofill_rate: 71.8, avg_review_time: 14.8, total_time_saved: 4.1 },
            { month: "2023-09", runs: 18, avg_autofill_rate: 74.5, avg_review_time: 13.2, total_time_saved: 5.3 },
            { month: "2023-10", runs: 22, avg_autofill_rate: 76.1, avg_review_time: 12.7, total_time_saved: 6.8 },
            { month: "2023-11", runs: 19, avg_autofill_rate: 78.3, avg_review_time: 11.9, total_time_saved: 7.2 },
            { month: "2023-12", runs: 16, avg_autofill_rate: 79.7, avg_review_time: 11.1, total_time_saved: 6.9 }
          ],
          statistics: {
            total_runs: 102,
            autofill_rate: {
              mean: 75.2,
              median: 76.8,
              std_dev: 8.4
            },
            review_time: {
              mean: 13.1,
              median: 12.5,
              std_dev: 4.2
            }
          }
        })
        setLoading(false)
      }, 1000)
      
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
      setLoading(false)
    }
  }

  const fetchBenchmarks = async () => {
    try {
      // Mock API call - replace with actual API
      setTimeout(() => {
        setBenchmarks({
          benchmarks: {
            autofill_rate: {
              excellent: 85.0,
              good: 70.0,
              acceptable: 50.0,
              current: 75.2
            },
            review_time: {
              excellent: 10.0,
              good: 15.0,
              acceptable: 25.0,
              current: 13.1
            },
            completion_rate: {
              excellent: 95.0,
              good: 85.0,
              acceptable: 70.0,
              current: 88.5
            }
          },
          scores: {
            autofill_rate: "good",
            review_time: "good",
            completion_rate: "excellent"
          },
          overall_score: "good",
          recommendations: [
            "Consider uploading more comprehensive site documentation to improve autofill accuracy",
            "Provide reviewer training to reduce review time and improve efficiency"
          ]
        })
      }, 500)
      
    } catch (error) {
      console.error('Failed to fetch benchmarks:', error)
    }
  }

  const handleExport = () => {
    // Mock export functionality
    console.log('Exporting analytics data...')
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <Head>
        <title>Analytics - RealVibe Site Copilot</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600">Detailed performance insights and trends</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="last_7d">Last 7 Days</option>
              <option value="last_30d">Last 30 Days</option>
              <option value="last_90d">Last 90 Days</option>
              <option value="last_year">Last Year</option>
            </select>
            
            <button
              onClick={handleExport}
              className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              <ArrowDownTrayIcon className="h-4 w-4" />
              <span>Export</span>
            </button>
          </div>
        </div>

        {/* Performance Benchmarks */}
        {benchmarks && (
          <PerformanceBenchmarks
            benchmarks={benchmarks.benchmarks}
            scores={benchmarks.scores}
            overall_score={benchmarks.overall_score}
            recommendations={benchmarks.recommendations}
          />
        )}

        {/* Charts Grid */}
        {analytics && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Monthly Trends */}
            <div className="lg:col-span-2">
              <MetricsChart
                type="trend"
                data={analytics.monthly_trends.map(item => ({
                  date: item.month,
                  autofill_rate: item.avg_autofill_rate,
                  review_time: item.avg_review_time
                }))}
                title="Monthly Performance Trends"
                height={350}
              />
            </div>

            {/* Autofill Rate Distribution */}
            <MetricsChart
              type="distribution"
              data={analytics.distributions.autofill_rate}
              title="Autofill Rate Distribution"
            />

            {/* Review Time Distribution */}
            <MetricsChart
              type="distribution"
              data={analytics.distributions.review_time}
              title="Review Time Distribution"
            />
          </div>
        )}

        {/* Sponsor Performance Table */}
        {analytics && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance by Sponsor</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Sponsor
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Runs
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Autofill Rate
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Review Time
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {analytics.sponsor_performance.map((sponsor, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {sponsor.sponsor}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {sponsor.runs}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {sponsor.avg_autofill_rate}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {sponsor.avg_review_time} min
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Statistics Summary */}
        {analytics && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistical Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Autofill Rate</h4>
                  <div className="space-y-1 text-sm text-gray-600">
                    <div>Mean: {analytics.statistics.autofill_rate.mean}%</div>
                    <div>Median: {analytics.statistics.autofill_rate.median}%</div>
                    <div>Std Dev: {analytics.statistics.autofill_rate.std_dev}%</div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Review Time</h4>
                  <div className="space-y-1 text-sm text-gray-600">
                    <div>Mean: {analytics.statistics.review_time.mean} min</div>
                    <div>Median: {analytics.statistics.review_time.median} min</div>
                    <div>Std Dev: {analytics.statistics.review_time.std_dev} min</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}


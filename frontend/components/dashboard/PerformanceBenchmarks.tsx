import React from 'react'
import { CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from '@heroicons/react/24/outline'

interface Benchmark {
  excellent: number
  good: number
  acceptable: number
  current: number
}

interface BenchmarkData {
  autofill_rate: Benchmark
  review_time: Benchmark
  completion_rate: Benchmark
}

interface PerformanceScore {
  autofill_rate: string
  review_time: string
  completion_rate: string
}

interface PerformanceBenchmarksProps {
  benchmarks: BenchmarkData
  scores: PerformanceScore
  overall_score: string
  recommendations: string[]
}

export default function PerformanceBenchmarks({ 
  benchmarks, 
  scores, 
  overall_score, 
  recommendations 
}: PerformanceBenchmarksProps) {
  const getScoreIcon = (score: string) => {
    switch (score) {
      case 'excellent':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'good':
        return <CheckCircleIcon className="h-5 w-5 text-blue-500" />
      case 'acceptable':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
      case 'needs_improvement':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getScoreColor = (score: string) => {
    switch (score) {
      case 'excellent':
        return 'text-green-600 bg-green-50'
      case 'good':
        return 'text-blue-600 bg-blue-50'
      case 'acceptable':
        return 'text-yellow-600 bg-yellow-50'
      case 'needs_improvement':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const formatMetricName = (key: string) => {
    return key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const formatMetricValue = (key: string, value: number) => {
    if (key === 'review_time') {
      return `${value} min`
    }
    return `${value}%`
  }

  const getProgressPercentage = (key: string, current: number, benchmark: Benchmark) => {
    if (key === 'review_time') {
      // For review time, lower is better
      const max = benchmark.acceptable * 1.5 // Set a reasonable max
      return Math.max(0, Math.min(100, ((max - current) / max) * 100))
    } else {
      // For other metrics, higher is better
      return Math.max(0, Math.min(100, (current / benchmark.excellent) * 100))
    }
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Performance Benchmarks</h3>
          <div className="flex items-center space-x-2">
            {getScoreIcon(overall_score)}
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(overall_score)}`}>
              {overall_score.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </span>
          </div>
        </div>

        <div className="space-y-6">
          {Object.entries(benchmarks).map(([key, benchmark]) => {
            const score = scores[key as keyof PerformanceScore]
            const progress = getProgressPercentage(key, benchmark.current, benchmark)
            
            return (
              <div key={key} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getScoreIcon(score)}
                    <span className="font-medium text-gray-900">
                      {formatMetricName(key)}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">
                      {formatMetricValue(key, benchmark.current)}
                    </div>
                    <div className="text-sm text-gray-500">
                      Target: {formatMetricValue(key, benchmark.excellent)}
                    </div>
                  </div>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      score === 'excellent' ? 'bg-green-500' :
                      score === 'good' ? 'bg-blue-500' :
                      score === 'acceptable' ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${progress}%` }}
                  />
                </div>
                
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Needs Improvement</span>
                  <span>Acceptable</span>
                  <span>Good</span>
                  <span>Excellent</span>
                </div>
              </div>
            )
          })}
        </div>

        {recommendations && recommendations.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="font-medium text-gray-900 mb-3">Recommendations</h4>
            <ul className="space-y-2">
              {recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="flex-shrink-0 w-1.5 h-1.5 bg-blue-500 rounded-full mt-2" />
                  <span className="text-sm text-gray-600">{recommendation}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}


import { ReactNode } from 'react'
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid'

interface MetricsCardProps {
  title: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  trend?: 'up' | 'down'
  trendValue?: string
  loading?: boolean
  className?: string
}

export default function MetricsCard({
  title,
  value,
  icon: Icon,
  trend,
  trendValue,
  loading = false,
  className = 'bg-white'
}: MetricsCardProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded w-20"></div>
            <div className="h-8 bg-gray-200 rounded w-16"></div>
          </div>
          <div className="h-12 w-12 bg-gray-200 rounded"></div>
        </div>
        <div className="mt-4 h-4 bg-gray-200 rounded w-24"></div>
      </div>
    )
  }

  return (
    <div className={`rounded-lg shadow-sm p-6 transition-all duration-200 hover:shadow-md ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-sm font-medium ${className.includes('text-white') ? 'text-white/80' : 'text-gray-600'}`}>
            {title}
          </p>
          <p className={`text-3xl font-bold ${className.includes('text-white') ? 'text-white' : 'text-gray-900'}`}>
            {value}
          </p>
        </div>
        <div className={`p-3 rounded-full ${className.includes('text-white') ? 'bg-white/20' : 'bg-gray-100'}`}>
          <Icon className={`h-6 w-6 ${className.includes('text-white') ? 'text-white' : 'text-gray-600'}`} />
        </div>
      </div>
      
      {trend && trendValue && (
        <div className="mt-4 flex items-center">
          <div className={`flex items-center space-x-1 ${
            trend === 'up' 
              ? className.includes('text-white') ? 'text-green-200' : 'text-green-600'
              : className.includes('text-white') ? 'text-red-200' : 'text-red-600'
          }`}>
            {trend === 'up' ? (
              <ArrowUpIcon className="h-4 w-4" />
            ) : (
              <ArrowDownIcon className="h-4 w-4" />
            )}
            <span className="text-sm font-medium">{trendValue}</span>
          </div>
          <span className={`ml-2 text-sm ${className.includes('text-white') ? 'text-white/70' : 'text-gray-500'}`}>
            vs last period
          </span>
        </div>
      )}
    </div>
  )
}


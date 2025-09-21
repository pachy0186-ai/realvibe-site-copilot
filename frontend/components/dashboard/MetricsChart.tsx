import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

interface TrendData {
  date: string
  autofill_rate: number
  review_time: number
  runs: number
}

interface MetricsChartProps {
  type: 'trend' | 'distribution' | 'performance'
  data: any[]
  title: string
  height?: number
}

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export default function MetricsChart({ type, data, title, height = 300 }: MetricsChartProps) {
  const renderTrendChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => new Date(value).toLocaleDateString()}
        />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip 
          labelFormatter={(value) => new Date(value).toLocaleDateString()}
          formatter={(value: number, name: string) => [
            `${value}${name.includes('rate') ? '%' : name.includes('time') ? ' min' : ''}`,
            name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
          ]}
        />
        <Line 
          type="monotone" 
          dataKey="autofill_rate" 
          stroke="#2563eb" 
          strokeWidth={2}
          dot={{ fill: '#2563eb', strokeWidth: 2, r: 4 }}
          name="Autofill Rate"
        />
        <Line 
          type="monotone" 
          dataKey="review_time" 
          stroke="#10b981" 
          strokeWidth={2}
          dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
          name="Review Time"
        />
      </LineChart>
    </ResponsiveContainer>
  )

  const renderBarChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="range" 
          tick={{ fontSize: 12 }}
        />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip 
          formatter={(value: number) => [`${value}%`, 'Percentage']}
        />
        <Bar 
          dataKey="percentage" 
          fill="#2563eb"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  )

  const renderPieChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, value }) => `${name}: ${value}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value: number) => [`${value}%`, 'Percentage']} />
      </PieChart>
    </ResponsiveContainer>
  )

  const renderChart = () => {
    switch (type) {
      case 'trend':
        return renderTrendChart()
      case 'distribution':
        return renderBarChart()
      case 'performance':
        return renderPieChart()
      default:
        return renderTrendChart()
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      {data && data.length > 0 ? (
        renderChart()
      ) : (
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <div className="text-4xl mb-2">📊</div>
            <p>No data available</p>
          </div>
        </div>
      )}
    </div>
  )
}


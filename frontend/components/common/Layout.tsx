import { ReactNode, useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { 
  HomeIcon,
  DocumentTextIcon,
  FolderIcon,
  ChartBarIcon,
  CogIcon,
  UserIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/site-copilot', icon: HomeIcon },
  { name: 'Questionnaires', href: '/site-copilot/questionnaires', icon: DocumentTextIcon },
  { name: 'Files', href: '/site-copilot/files', icon: FolderIcon },
  { name: 'Runs', href: '/site-copilot/runs', icon: ChartBarIcon },
  { name: 'Settings', href: '/site-copilot/settings', icon: CogIcon },
]

export default function Layout({ children }: LayoutProps) {
  const router = useRouter()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const isActive = (href: string) => {
    if (href === '/site-copilot') {
      return router.pathname === href
    }
    return router.pathname.startsWith(href)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white shadow-xl">
          <div className="flex h-16 shrink-0 items-center justify-between px-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">RV</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">Site Copilot</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive(item.href)
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon
                  className={`mr-3 h-5 w-5 ${
                    isActive(item.href) ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                  }`}
                />
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-40 lg:flex lg:w-64 lg:flex-col">
        <div className="flex grow flex-col bg-white border-r border-gray-200 shadow-sm">
          <div className="flex h-16 shrink-0 items-center px-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">RV</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">Site Copilot</span>
            </div>
          </div>
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  isActive(item.href)
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <item.icon
                  className={`mr-3 h-5 w-5 ${
                    isActive(item.href) ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                  }`}
                />
                {item.name}
              </Link>
            ))}
          </nav>
          
          {/* User section */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
                <UserIcon className="h-5 w-5 text-gray-500" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">Demo Site</p>
                <p className="text-xs text-gray-500 truncate">demo@realvibe.ai</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-30 bg-white border-b border-gray-200 px-4 py-4 lg:px-8">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-500 hover:text-gray-600 lg:hidden"
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                {mounted ? `Last updated: ${new Date().toLocaleString()}` : 'Last updated: --'}
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}


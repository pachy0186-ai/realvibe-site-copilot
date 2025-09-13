import { useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to site-copilot dashboard
    router.push('/site-copilot')
  }, [router])

  return (
    <>
      <Head>
        <title>RealVibe Site Copilot</title>
        <meta name="description" content="AI-powered clinical trial feasibility questionnaire auto-fill" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting to Site Copilot...</p>
        </div>
      </div>
    </>
  )
}


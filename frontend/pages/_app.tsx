import type { AppProps } from 'next/app'
import { useEffect } from 'react'
import '@/styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    // Initialize any global app logic here
    console.log('RealVibe Site Copilot initialized')
  }, [])

  return <Component {...pageProps} />
}


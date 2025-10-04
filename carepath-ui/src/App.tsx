import { useState, useEffect } from 'react'
import { ChatInterface } from './components/ChatInterface'
import { ApiKeyDialog } from './components/ApiKeyDialog'
import axios from 'axios'

function App() {
  const [hasApiKey, setHasApiKey] = useState<boolean | null>(null)

  useEffect(() => {
    checkApiKey()
  }, [])

  const checkApiKey = async () => {
    try {
      const response = await axios.get('http://localhost:8000/check-api-key')
      setHasApiKey(response.data.has_api_key)
    } catch (error) {
      console.error('Error checking API key:', error)
      setHasApiKey(false)
    }
  }

  if (hasApiKey === null) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading CarePath...</p>
        </div>
      </div>
    )
  }

  if (!hasApiKey) {
    return <ApiKeyDialog onSuccess={() => setHasApiKey(true)} />
  }

  return <ChatInterface />
}

export default App

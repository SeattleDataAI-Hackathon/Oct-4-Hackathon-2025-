import React, { useState } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import AuthPage from './components/AuthPage'
import Dashboard from './components/Dashboard'
import './App.css'

const AppContent: React.FC = () => {
  const { user, loading } = useAuth()
  const [showAuth, setShowAuth] = useState(!user)

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner" />
        <p>Loading...</p>
      </div>
    )
  }

  if (!user || showAuth) {
    return <AuthPage onAuthSuccess={() => setShowAuth(false)} />
  }

  return <Dashboard onSignOut={() => setShowAuth(true)} />
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
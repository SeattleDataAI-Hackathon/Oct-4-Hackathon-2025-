import React, { useState } from 'react'
import { LogOut, User, Heart, FileText, Phone } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import PatientInfo from './PatientInfo'
import CallsReports from './CallsReports'
import './Dashboard.css'

interface DashboardProps {
  onSignOut: () => void
}

const Dashboard: React.FC<DashboardProps> = ({ onSignOut }) => {
  const { user, signOut } = useAuth()
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'patient-info' | 'calls-reports'>('dashboard')

  const handleSignOut = async () => {
    await signOut()
    onSignOut()
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo">
            <Heart className="logo-icon" />
            <span>HealthCare Dashboard</span>
          </div>
          <div className="user-info">
            <div className="user-avatar">
              <User className="avatar-icon" />
            </div>
            <div className="user-details">
              <p className="user-email">{user?.email}</p>
              <button onClick={handleSignOut} className="sign-out-button">
                <LogOut className="sign-out-icon" />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        {currentPage === 'dashboard' && (
          <>
            <div className="welcome-section">
              <h1>Welcome to HealthCare!</h1>
              <p>Your healthcare journey starts here. Access your medical records, schedule appointments, and track your health progress.</p>
            </div>

            <div className="features-grid">
              <div className="feature-card" onClick={() => setCurrentPage('patient-info')}>
                <FileText className="feature-icon" />
                <h3>Patient Information</h3>
                <p>View and manage patient details and medical records</p>
              </div>
              
              <div className="feature-card" onClick={() => setCurrentPage('calls-reports')}>
                <Phone className="feature-icon" />
                <h3>Calls Reports</h3>
                <p>View and manage phone call reports and communications</p>
              </div>
            </div>
          </>
        )}

        {currentPage === 'patient-info' && (
          <div className="page-content">
            <div className="page-header">
              <button 
                className="back-button" 
                onClick={() => setCurrentPage('dashboard')}
              >
                ← Back to Dashboard
              </button>
            </div>
            <PatientInfo />
          </div>
        )}

        {currentPage === 'calls-reports' && (
          <div className="page-content">
            <div className="page-header">
              <button 
                className="back-button" 
                onClick={() => setCurrentPage('dashboard')}
              >
                ← Back to Dashboard
              </button>
            </div>
            <CallsReports />
          </div>
        )}
      </main>
    </div>
  )
}

export default Dashboard
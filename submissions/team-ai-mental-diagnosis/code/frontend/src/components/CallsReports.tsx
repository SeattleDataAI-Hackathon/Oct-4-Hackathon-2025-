import React, { useState, useEffect } from 'react'
import { Phone, Calendar, FileText, Filter, Download, Star, Heart, Frown, Smile, Meh, Search, ChevronLeft, ChevronRight, X } from 'lucide-react'
import { supabase } from '../lib/supabase'
import './CallsReports.css'

// Get Supabase URL for direct HTTP requests
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://gmdhmtyysrvdpucfvphk.supabase.co'

interface PhoneCallReport {
  id: string
  phone_number: string
  mood: number
  mood_description: string
  emotions: string[]
  created_at: string
}

interface PaginationInfo {
  page: number
  limit: number
  totalCount: number
  totalPages: number
  hasNextPage: boolean
  hasPrevPage: boolean
}

const CallsReports: React.FC = () => {
  const [reports, setReports] = useState<PhoneCallReport[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [selectedReport, setSelectedReport] = useState<PhoneCallReport | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    limit: 100,
    totalCount: 0,
    totalPages: 0,
    hasNextPage: false,
    hasPrevPage: false
  })

  // Get mood emoji and color based on rating (1-5)
  const getMoodDisplay = (mood: number) => {
    const moodConfig = {
      1: { emoji: '😢', color: '#e53e3e', label: 'Very Bad', icon: Frown },
      2: { emoji: '😞', color: '#dd6b20', label: 'Bad', icon: Frown },
      3: { emoji: '😐', color: '#d69e2e', label: 'Neutral', icon: Meh },
      4: { emoji: '😊', color: '#38a169', label: 'Good', icon: Smile },
      5: { emoji: '😄', color: '#2d7dd2', label: 'Excellent', icon: Heart }
    }
    return moodConfig[mood as keyof typeof moodConfig] || moodConfig[3]
  }

  // Fetch reports from Supabase
  const fetchReports = async (phoneNum?: string, pageNum?: number) => {
    try {
      setLoading(true)
      setError('')
      
      const searchPhoneNumber = phoneNum || phoneNumber || '+1234567890'
      const currentPage = pageNum || pagination.page
      
      // Build query parameters
      const params = new URLSearchParams({
        phone_number: searchPhoneNumber,
        page: currentPage.toString(),
        limit: pagination.limit.toString(),
        sort: 'desc'
      })
      
      // Make direct HTTP request to the function with query parameters
      const response = await fetch(`${supabaseUrl}/functions/v1/get-phone-call-reports?${params.toString()}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`,
          'Content-Type': 'application/json'
        }
      })
      
      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.error || 'Failed to fetch reports')
      }

      if (result?.success) {
        setReports(result.data || [])
        setPagination(result.pagination || pagination)
      } else {
        throw new Error(result?.error || 'Failed to fetch reports')
      }
    } catch (err) {
      console.error('Error fetching reports:', err)
      setError('Failed to load call reports')
      setReports([])
    } finally {
      setLoading(false)
    }
  }

  // Handle search
  const handleSearch = () => {
    if (phoneNumber.trim()) {
      setPagination(prev => ({ ...prev, page: 1 }))
      fetchReports(phoneNumber, 1)
    }
  }

  // Handle pagination
  const handlePageChange = (newPage: number) => {
    fetchReports(phoneNumber, newPage)
  }

  // Handle phone number input change
  const handlePhoneNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPhoneNumber(e.target.value)
  }

  // Handle enter key press in phone number input
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  // Handle opening report details modal
  const handleReportClick = (report: PhoneCallReport) => {
    setSelectedReport(report)
    setShowModal(true)
  }

  // Handle closing modal
  const handleCloseModal = () => {
    setShowModal(false)
    setSelectedReport(null)
  }

  useEffect(() => {
    fetchReports()
  }, [])

  if (loading) {
    return (
      <div className="calls-reports">
        <div className="loading-container">
          <div className="loading-spinner" />
          <p>Loading call reports...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="calls-reports">
      <div className="page-header">
        <h1>Calls Reports</h1>
        <p>View and manage phone call reports and patient communications</p>
      </div>

      <div className="reports-content">
        {/* Filters and Actions */}
        <div className="reports-toolbar">
          <div className="filters">
            <div className="search-container">
              <div className="search-input-wrapper">
                <Search className="search-icon" />
                <input
                  type="text"
                  placeholder="Enter phone number to search..."
                  value={phoneNumber}
                  onChange={handlePhoneNumberChange}
                  onKeyPress={handleKeyPress}
                  className="search-input"
                />
              </div>
              <button 
                className="search-button"
                onClick={handleSearch}
                disabled={!phoneNumber.trim()}
              >
                Search
              </button>
            </div>
            <button className="filter-button">
              <Filter className="filter-icon" />
              Filter
            </button>
            <select className="date-filter">
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>Last 3 months</option>
              <option>All time</option>
            </select>
          </div>
          <div className="actions">
            <button className="action-button secondary">
              <Download className="action-icon" />
              Export
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="summary-cards">
          <div className="summary-card">
            <div className="card-icon">
              <Phone className="icon" />
            </div>
            <div className="card-content">
              <h3>Total Reports</h3>
              <p className="number">{reports.length}</p>
              <p className="change positive">All time reports</p>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">
              <Star className="icon" />
            </div>
            <div className="card-content">
              <h3>Average Mood</h3>
              <p className="number">
                {reports.length > 0 
                  ? (reports.reduce((sum, report) => sum + report.mood, 0) / reports.length).toFixed(1)
                  : '0'
                }
              </p>
              <p className="change positive">Out of 5.0 scale</p>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">
              <Heart className="icon" />
            </div>
            <div className="card-content">
              <h3>Positive Reports</h3>
              <p className="number">
                {reports.filter(report => report.mood >= 4).length}
              </p>
              <p className="change positive">Mood 4+ ratings</p>
            </div>
          </div>
          <div className="summary-card">
            <div className="card-icon">
              <FileText className="icon" />
            </div>
            <div className="card-content">
              <h3>Emotions Tracked</h3>
              <p className="number">
                {reports.reduce((sum, report) => sum + report.emotions.length, 0)}
              </p>
              <p className="change positive">Total emotion tags</p>
            </div>
          </div>
        </div>

        {/* Calls List */}
        <div className="calls-list">
          <div className="list-header">
            <h2>Recent Calls</h2>
          </div>
          
          <div className="calls-table">
            <div className="table-header">
              <div className="table-cell">Phone Number</div>
              <div className="table-cell">Date & Time</div>
              <div className="table-cell">Mood Rating</div>
              <div className="table-cell">Description</div>
              <div className="table-cell">Emotions</div>
            </div>
            
            {reports.length === 0 ? (
              <div className="empty-state">
                <Phone className="empty-icon" />
                <h3>{error ? 'Error Loading Reports' : 'No Call Reports Found'}</h3>
                <p>
                  {error 
                    ? 'There was an error loading the call reports. Please try again.'
                    : phoneNumber 
                      ? `No call reports found for ${phoneNumber}`
                      : 'Enter a phone number above to search for call reports'
                  }
                </p>
                {error && (
                  <button 
                    className="retry-button"
                    onClick={() => fetchReports()}
                  >
                    Try Again
                  </button>
                )}
              </div>
            ) : (
              reports.map((report) => {
                const moodDisplay = getMoodDisplay(report.mood)
                const MoodIcon = moodDisplay.icon
                const reportDate = new Date(report.created_at)
                
                return (
                  <div key={report.id} className="table-row clickable" onClick={() => handleReportClick(report)}>
                    <div className="table-cell">
                      <div className="phone-info">
                        <Phone className="phone-icon" />
                        <div>
                          <div className="phone-number">{report.phone_number}</div>
                          <div className="report-id">Report #{report.id}</div>
                        </div>
                      </div>
                    </div>
                    <div className="table-cell">
                      <div className="datetime">
                        <Calendar className="date-icon" />
                        <div>
                          <div>{reportDate.toLocaleDateString()}</div>
                          <div className="time">{reportDate.toLocaleTimeString()}</div>
                        </div>
                      </div>
                    </div>
                    <div className="table-cell">
                      <div className="mood-rating">
                        <div className="mood-display" style={{ color: moodDisplay.color }}>
                          <MoodIcon className="mood-icon" />
                          <div className="mood-info">
                            <div className="mood-score">{report.mood}/5</div>
                            <div className="mood-label">{moodDisplay.label}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="table-cell">
                      <div className="mood-description">
                        {report.mood_description}
                      </div>
                    </div>
                    <div className="table-cell">
                      <div className="emotion-tags">
                        {report.emotions.map((emotion, index) => (
                          <span key={index} className="emotion-tag">
                            {emotion}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )
              })
            )}
          </div>
          
          {/* Pagination Controls */}
          {reports.length > 0 && pagination.totalPages > 1 && (
            <div className="pagination-container">
              <div className="pagination-info">
                Showing {((pagination.page - 1) * pagination.limit) + 1} to {Math.min(pagination.page * pagination.limit, pagination.totalCount)} of {pagination.totalCount} reports
              </div>
              <div className="pagination-controls">
                <button
                  className="pagination-button"
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={!pagination.hasPrevPage}
                >
                  <ChevronLeft className="pagination-icon" />
                  Previous
                </button>
                
                <div className="pagination-pages">
                  {Array.from({ length: Math.min(5, pagination.totalPages) }, (_, i) => {
                    const pageNum = Math.max(1, pagination.page - 2) + i
                    if (pageNum > pagination.totalPages) return null
                    
                    return (
                      <button
                        key={pageNum}
                        className={`pagination-page ${pageNum === pagination.page ? 'active' : ''}`}
                        onClick={() => handlePageChange(pageNum)}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                </div>
                
                <button
                  className="pagination-button"
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={!pagination.hasNextPage}
                >
                  Next
                  <ChevronRight className="pagination-icon" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Report Details Modal */}
      {showModal && selectedReport && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Call Report Details</h2>
              <button className="modal-close" onClick={handleCloseModal}>
                <X className="close-icon" />
              </button>
            </div>
            
            <div className="modal-body">
              <div className="report-details">
                <div className="detail-section">
                  <h3>Call Information</h3>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <label>Phone Number</label>
                      <div className="phone-info">
                        <Phone className="phone-icon" />
                        <span>{selectedReport.phone_number}</span>
                      </div>
                    </div>
                    <div className="detail-item">
                      <label>Report ID</label>
                      <span>#{selectedReport.id}</span>
                    </div>
                    <div className="detail-item">
                      <label>Date & Time</label>
                      <div className="datetime">
                        <Calendar className="date-icon" />
                        <div>
                          <div>{new Date(selectedReport.created_at).toLocaleDateString()}</div>
                          <div className="time">{new Date(selectedReport.created_at).toLocaleTimeString()}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Mood Assessment</h3>
                  <div className="mood-details">
                    <div className="mood-rating-large">
                      <div className="mood-display-large" style={{ color: getMoodDisplay(selectedReport.mood).color }}>
                        {React.createElement(getMoodDisplay(selectedReport.mood).icon, { className: "mood-icon-large" })}
                        <div className="mood-info-large">
                          <div className="mood-score-large">{selectedReport.mood}/5</div>
                          <div className="mood-label-large">{getMoodDisplay(selectedReport.mood).label}</div>
                        </div>
                      </div>
                    </div>
                    <div className="mood-description-full">
                      <label>Full Description</label>
                      <div className="description-text">
                        {selectedReport.mood_description}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Emotions Detected</h3>
                  <div className="emotions-full">
                    {selectedReport.emotions.length > 0 ? (
                      <div className="emotion-tags-full">
                        {selectedReport.emotions.map((emotion, index) => (
                          <span key={index} className="emotion-tag-full">
                            {emotion}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="no-emotions">No emotions detected for this call.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CallsReports

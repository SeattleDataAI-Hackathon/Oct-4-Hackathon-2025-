import React, { useState, useEffect } from 'react'
import { User, Calendar, Phone, FileText, Edit, Save, Brain, Heart, Users, Briefcase, Loader2 } from 'lucide-react'
import { supabase } from '../lib/supabase'
import './PatientInfo.css'

interface PatientData {
  // Basic Demographics
  age: string
  gender: string
  occupation: string
  relationshipStatus: string
  livingSituation: string
  phoneNumber: string
  
  // Mental Health History
  mentalHealthDiagnosis: string
  therapyHistory: string
  psychiatricMedication: string
  mentalHealthHospitalization: string
  pastSelfHarmThoughts: string
  currentSelfHarmThoughts: string
  
  // Additional Information
  additionalInfo: string
}

const PatientInfo: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [patientData, setPatientData] = useState<PatientData>({
    age: '',
    gender: '',
    occupation: '',
    relationshipStatus: '',
    livingSituation: '',
    phoneNumber: '',
    mentalHealthDiagnosis: '',
    therapyHistory: '',
    psychiatricMedication: '',
    mentalHealthHospitalization: '',
    pastSelfHarmThoughts: '',
    currentSelfHarmThoughts: '',
    additionalInfo: ''
  })

  // Load user data on component mount
  useEffect(() => {
    loadUserData()
  }, [])

  const loadUserData = async () => {
    try {
      setIsLoading(true)
      
      // Call the get-user-info edge function with GET method
      const { data, error } = await supabase.functions.invoke('get-user-info', {
        method: 'GET'
      })
      
      if (error) {
        console.error('Error loading user data:', error)
        // If no user data exists, that's okay - we'll start with empty form
        if (error.message?.includes('No user information found')) {
          console.log('No existing user data found, starting with empty form')
        } else {
          alert('Failed to load user information. Please try again.')
        }
        return
      }

      if (data?.success && data?.data) {
        // Map the structured data directly to our form fields
        const loadedData = {
          age: data.data.age || '',
          gender: data.data.gender || '',
          occupation: data.data.occupation || '',
          relationshipStatus: data.data.relationship_status || '',
          livingSituation: data.data.living_situation || '',
          phoneNumber: data.data.phone_number || '',
          mentalHealthDiagnosis: data.data.mental_health_diagnosis || '',
          therapyHistory: data.data.therapy_history || '',
          psychiatricMedication: data.data.psychiatric_medication || '',
          mentalHealthHospitalization: data.data.mental_health_hospitalization || '',
          pastSelfHarmThoughts: data.data.past_self_harm_thoughts || '',
          currentSelfHarmThoughts: data.data.current_self_harm_thoughts || '',
          additionalInfo: data.data.additional_info || ''
        }
        
        setPatientData(loadedData)
      }
    } catch (error) {
      console.error('Error loading user data:', error)
      alert('Failed to load user information. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (field: keyof PatientData, value: string) => {
    setPatientData(prev => ({
      ...prev,
      [field]: value
    }))
  }


  const handleSave = async () => {
    try {
      setIsSaving(true)
      
      // Helper function to convert empty strings to null
      const toNullIfEmpty = (value: string) => value.trim() === '' ? null : value.trim()
      
      // Prepare the data to send
      const dataToSend = {
        // Demographics
        age: toNullIfEmpty(patientData.age),
        gender: toNullIfEmpty(patientData.gender),
        occupation: toNullIfEmpty(patientData.occupation),
        relationship_status: toNullIfEmpty(patientData.relationshipStatus),
        living_situation: toNullIfEmpty(patientData.livingSituation),
        phone_number: toNullIfEmpty(patientData.phoneNumber),
        // Mental Health
        mental_health_diagnosis: toNullIfEmpty(patientData.mentalHealthDiagnosis),
        therapy_history: toNullIfEmpty(patientData.therapyHistory),
        psychiatric_medication: toNullIfEmpty(patientData.psychiatricMedication),
        mental_health_hospitalization: toNullIfEmpty(patientData.mentalHealthHospitalization),
        past_self_harm_thoughts: toNullIfEmpty(patientData.pastSelfHarmThoughts),
        current_self_harm_thoughts: toNullIfEmpty(patientData.currentSelfHarmThoughts),
        // Additional Info
        additional_info: toNullIfEmpty(patientData.additionalInfo)
      }
      
      // Send structured data directly to the backend
      const { error } = await supabase.functions.invoke('save-user-info', {
        body: dataToSend
      })

      if (error) {
        alert(`Failed to save patient information: ${error.message || 'Unknown error'}`)
        return
      }

      setIsEditing(false)
      alert('Patient information saved successfully!')
    } catch (error) {
      alert(`Failed to save patient information: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="patient-info">
        <div className="loading-container">
          <Loader2 className="loading-spinner" />
          <p>Loading patient information...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="patient-info">
      <div className="patient-content">
        {/* Basic Demographic Information */}
        <div className="info-card">
          <div className="card-header">
            <h2>🧾 Basic Demographic Information</h2>
            <button 
              className="edit-button"
              onClick={() => {
                if (!isEditing) {
                  setIsEditing(true)
                } else {
                  handleSave()
                }
              }}
              disabled={isSaving}
            >
              {isEditing ? (
                isSaving ? (
                  <>
                    <Loader2 className="edit-icon animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="edit-icon" />
                    Save
                  </>
                )
              ) : (
                <>
                  <Edit className="edit-icon" />
                  Edit
                </>
              )}
            </button>
          </div>
          <div className="form-grid">
            <div className="form-item">
              <Calendar className="form-icon" />
              <div className="form-content">
                <label>What is the patient's age?</label>
                {isEditing ? (
                  <input
                    type="number"
                    value={patientData.age}
                    onChange={(e) => handleInputChange('age', e.target.value)}
                    placeholder="Enter the patient's age"
                    className="form-input"
                  />
                ) : (
                  <span>{patientData.age || 'Not specified'}</span>
                )}
              </div>
            </div>

            <div className="form-item">
              <User className="form-icon" />
              <div className="form-content">
                <label>What is the patient's gender?</label>
                {isEditing ? (
                  <select
                    value={patientData.gender}
                    onChange={(e) => handleInputChange('gender', e.target.value)}
                    className="form-select"
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="non-binary">Non-binary</option>
                    <option value="transgender">Transgender</option>
                    <option value="other">Other</option>
                    <option value="prefer-not-to-say">Prefer not to say</option>
                  </select>
                ) : (
                  <span>{patientData.gender || 'Not specified'}</span>
                )}
              </div>
            </div>

            <div className="form-item">
              <Briefcase className="form-icon" />
              <div className="form-content">
                <label>What is the patient's current occupation or study situation?</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={patientData.occupation}
                    onChange={(e) => handleInputChange('occupation', e.target.value)}
                    placeholder="e.g., Software Engineer, Student, Unemployed, etc."
                    className="form-input"
                  />
                ) : (
                  <span>{patientData.occupation || 'Not specified'}</span>
                )}
              </div>
            </div>

            <div className="form-item">
              <Heart className="form-icon" />
              <div className="form-content">
                <label>What is the patient's relationship status?</label>
                {isEditing ? (
                  <select
                    value={patientData.relationshipStatus}
                    onChange={(e) => handleInputChange('relationshipStatus', e.target.value)}
                    className="form-select"
                  >
                    <option value="">Select relationship status</option>
                    <option value="single">Single</option>
                    <option value="married">Married</option>
                    <option value="divorced">Divorced</option>
                    <option value="widowed">Widowed</option>
                    <option value="separated">Separated</option>
                    <option value="in-relationship">In a relationship</option>
                    <option value="other">Other</option>
                  </select>
                ) : (
                  <span>{patientData.relationshipStatus || 'Not specified'}</span>
                )}
              </div>
            </div>

            <div className="form-item">
              <Users className="form-icon" />
              <div className="form-content">
                <label>Who does the patient currently live with?</label>
                {isEditing ? (
                  <select
                    value={patientData.livingSituation}
                    onChange={(e) => handleInputChange('livingSituation', e.target.value)}
                    className="form-select"
                  >
                    <option value="">Select living situation</option>
                    <option value="alone">Alone</option>
                    <option value="partner">Partner</option>
                    <option value="family">Family</option>
                    <option value="roommates">Roommates</option>
                    <option value="friends">Friends</option>
                    <option value="other">Other</option>
                  </select>
                ) : (
                  <span>{patientData.livingSituation || 'Not specified'}</span>
                )}
              </div>
            </div>

            <div className="form-item">
              <Phone className="form-icon" />
              <div className="form-content">
                <label>What is the patient's phone number?</label>
                {isEditing ? (
                  <input
                    type="tel"
                    value={patientData.phoneNumber}
                    onChange={(e) => handleInputChange('phoneNumber', e.target.value)}
                    placeholder="Enter the patient's phone number"
                    className="form-input"
                  />
                ) : (
                  <span>{patientData.phoneNumber || 'Not specified'}</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Mental Health History */}
        <div className="info-card">
          <div className="card-header">
            <h2>🧠 Mental Health History</h2>
          </div>
          <div className="form-grid">
            <div className="form-item">
              <Brain className="form-icon" />
              <div className="form-content">
                <label>Has the patient ever been diagnosed with a mental health condition?</label>
                {isEditing ? (
                  <textarea
                    value={patientData.mentalHealthDiagnosis}
                    onChange={(e) => handleInputChange('mentalHealthDiagnosis', e.target.value)}
                    placeholder="e.g., depression, anxiety, bipolar disorder, PTSD, ADHD, etc. (Leave blank if none)"
                    className="form-textarea"
                    rows={3}
                  />
                ) : (
                  <span>{patientData.mentalHealthDiagnosis || 'Not specified'}</span>
                )}
              </div>
            </div>

            <div className="form-item">
              <FileText className="form-icon" />
              <div className="form-content">
                <label>Has the patient ever seen a therapist, psychiatrist, or counselor before?</label>
                {isEditing ? (
                  <textarea
                    value={patientData.therapyHistory}
                    onChange={(e) => handleInputChange('therapyHistory', e.target.value)}
                    placeholder="Describe the patient's therapy or counseling history (Leave blank if none)"
                    className="form-textarea"
                    rows={3}
                  />
                ) : (
                  <span>{patientData.therapyHistory || 'Not specified'}</span>
                )}
              </div>
            </div>

            <div className="form-item">
              <FileText className="form-icon" />
              <div className="form-content">
                <label>Is the patient currently taking any psychiatric medication?</label>
                {isEditing ? (
                  <textarea
                    value={patientData.psychiatricMedication}
                    onChange={(e) => handleInputChange('psychiatricMedication', e.target.value)}
                    placeholder="List any psychiatric medications the patient is currently taking (Leave blank if none)"
                    className="form-textarea"
                    rows={3}
                  />
                ) : (
                  <span>{patientData.psychiatricMedication || 'Not specified'}</span>
                )}
              </div>
            </div>

            <div className="form-item">
              <FileText className="form-icon" />
              <div className="form-content">
                <label>Has the patient ever been hospitalized for mental health reasons?</label>
                {isEditing ? (
                  <textarea
                    value={patientData.mentalHealthHospitalization}
                    onChange={(e) => handleInputChange('mentalHealthHospitalization', e.target.value)}
                    placeholder="Describe any mental health hospitalizations (Leave blank if none)"
                    className="form-textarea"
                    rows={3}
                  />
                ) : (
                  <span>{patientData.mentalHealthHospitalization || 'Not specified'}</span>
                )}
              </div>
            </div>

            <div className="form-item">
              <Brain className="form-icon" />
              <div className="form-content">
                <label>Has the patient ever had thoughts of self-harm or suicide?</label>
                {isEditing ? (
                  <textarea
                    value={patientData.pastSelfHarmThoughts}
                    onChange={(e) => handleInputChange('pastSelfHarmThoughts', e.target.value)}
                    placeholder="Describe any past thoughts of self-harm or suicide (Leave blank if none)"
                    className="form-textarea"
                    rows={3}
                  />
                ) : (
                  <span>{patientData.pastSelfHarmThoughts || 'Not specified'}</span>
                )}
              </div>
            </div>

            <div className="form-item">
              <Brain className="form-icon" />
              <div className="form-content">
                <label>Does the patient currently experience thoughts of harming themselves or others?</label>
                {isEditing ? (
                  <textarea
                    value={patientData.currentSelfHarmThoughts}
                    onChange={(e) => handleInputChange('currentSelfHarmThoughts', e.target.value)}
                    placeholder="Describe any current thoughts of self-harm or harm to others (Leave blank if none)"
                    className="form-textarea"
                    rows={3}
                  />
                ) : (
                  <span>{patientData.currentSelfHarmThoughts || 'Not specified'}</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Additional Information */}
        <div className="info-card">
          <div className="card-header">
            <h2>📝 Additional Information</h2>
          </div>
          <div className="form-grid">
            <div className="form-item full-width">
              <FileText className="form-icon" />
              <div className="form-content">
                <label>Please provide any additional information about the patient</label>
                {isEditing ? (
                  <textarea
                    value={patientData.additionalInfo}
                    onChange={(e) => handleInputChange('additionalInfo', e.target.value)}
                    placeholder="Share any other relevant information about the patient's health, concerns, or anything else the healthcare provider should know..."
                    className="form-textarea"
                    rows={5}
                  />
                ) : (
                  <span>{patientData.additionalInfo || 'No additional information provided'}</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {isEditing && (
          <div className="save-actions">
            <button 
              className="cancel-button" 
              onClick={() => setIsEditing(false)}
              disabled={isSaving}
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default PatientInfo

import { useState, useRef, useEffect } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Send, Activity, AlertCircle } from 'lucide-react'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Assessment {
  possible_condition: string
  category: string
  confidence: string
  recommended_specialist: string
  urgency_level: string
  action: string
  emergency: boolean
  other_possibilities: string[]
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showDiagnosisButton, setShowDiagnosisButton] = useState(false)
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [conversationCount, setConversationCount] = useState(0)
  const [startOption, setStartOption] = useState<'none' | 'symptoms' | 'chat'>('none')
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([])
  const [customSymptom, setCustomSymptom] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const commonSymptoms = [
    'Headache', 'Fever', 'Cough', 'Fatigue', 'Chest Pain',
    'Shortness of Breath', 'Nausea', 'Dizziness', 'Abdominal Pain',
    'Back Pain', 'Joint Pain', 'Sore Throat', 'Runny Nose',
    'Vomiting', 'Diarrhea', 'Weight Loss', 'Anxiety', 'Depression'
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const startChatFlow = () => {
    setStartOption('chat')
    const initialMessage: Message = {
      role: 'assistant',
      content: "Hello! I'm CarePath, your medical guidance assistant. I'm here to help understand your symptoms and guide you to the right care.\n\nWhat brings you here today? Please describe any symptoms you're experiencing."
    }
    setMessages([initialMessage])
  }

  const handleSymptomToggle = (symptom: string) => {
    setSelectedSymptoms(prev =>
      prev.includes(symptom)
        ? prev.filter(s => s !== symptom)
        : [...prev, symptom]
    )
  }

  const submitSymptoms = async () => {
    const allSymptoms = [...selectedSymptoms]
    if (customSymptom.trim()) {
      allSymptoms.push(customSymptom.trim())
    }

    if (allSymptoms.length === 0) {
      alert('Please select or enter at least one symptom')
      return
    }

    setStartOption('chat')
    const initialMessage: Message = {
      role: 'assistant',
      content: "Hello! I'm CarePath, your medical guidance assistant. I'm here to help understand your symptoms and guide you to the right care."
    }

    const userMessage: Message = {
      role: 'user',
      content: `I am experiencing: ${allSymptoms.join(', ')}`
    }

    setMessages([initialMessage, userMessage])
    setIsLoading(true)

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        message: userMessage.content,
        conversation_history: [initialMessage]
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response
      }

      setMessages(prev => [...prev, assistantMessage])
      setConversationCount(1)

    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Auto-focus on keypress
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only auto-focus if no input is currently focused and it's a printable character
      if (
        document.activeElement?.tagName !== 'INPUT' &&
        document.activeElement?.tagName !== 'TEXTAREA' &&
        e.key.length === 1 &&
        !e.ctrlKey &&
        !e.metaKey &&
        !e.altKey
      ) {
        textareaRef.current?.focus()
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        message: input,
        conversation_history: messages
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response
      }

      setMessages(prev => [...prev, assistantMessage])
      setConversationCount(prev => prev + 1)

      // Show diagnosis button after 3 exchanges
      if (conversationCount >= 2) {
        setShowDiagnosisButton(true)
      }

      // Auto-diagnosis if confidence >= 90%
      if (response.data.confidence && parseFloat(response.data.confidence) >= 90) {
        await getDiagnosis()
      }

    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const getDiagnosis = async () => {
    setIsLoading(true)
    setShowDiagnosisButton(false)

    try {
      const response = await axios.post('http://localhost:8000/diagnose', {
        conversation_history: messages
      })

      setAssessment(response.data)

      const diagnosisMessage: Message = {
        role: 'assistant',
        content: 'I have completed my assessment based on our conversation.'
      }
      setMessages(prev => [...prev, diagnosisMessage])

    } catch (error) {
      console.error('Error getting diagnosis:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error while generating the diagnosis.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const getUrgencyColor = (urgency: string) => {
    if (urgency.includes('Emergency')) return 'text-red-600 bg-red-50 border-red-200'
    if (urgency.includes('Urgent')) return 'text-orange-600 bg-orange-50 border-orange-200'
    return 'text-green-600 bg-green-50 border-green-200'
  }

  // Show start options screen
  if (startOption === 'none') {
    return (
      <div className="flex flex-col h-screen bg-background">
        {/* Header */}
        <div className="border-b bg-card px-6 py-4">
          <div className="flex items-center gap-3">
            <Activity className="h-6 w-6 text-primary" />
            <div>
              <h1 className="text-xl font-semibold">CarePath</h1>
              <p className="text-sm text-muted-foreground">Medical Guidance Assistant</p>
            </div>
          </div>
        </div>

        {/* Start Options */}
        <div className="flex-1 flex items-center justify-center px-4">
          <div className="max-w-2xl w-full space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-3">Welcome to CarePath</h2>
              <p className="text-muted-foreground text-lg">
                How would you like to describe your symptoms?
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {/* Option 1: Select from Common Symptoms */}
              <Card
                className="cursor-pointer hover:border-primary transition-all hover:shadow-lg"
                onClick={() => setStartOption('symptoms')}
              >
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-primary" />
                    Select Symptoms
                  </CardTitle>
                  <CardDescription>
                    Choose from a list of common symptoms
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Quick and easy - select from predefined symptoms or add your own
                  </p>
                </CardContent>
              </Card>

              {/* Option 2: Chat Directly */}
              <Card
                className="cursor-pointer hover:border-primary transition-all hover:shadow-lg"
                onClick={startChatFlow}
              >
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Send className="h-5 w-5 text-primary" />
                    Start Chat
                  </CardTitle>
                  <CardDescription>
                    Describe your symptoms in your own words
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Have a conversation and describe what you're experiencing
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Show symptom selection screen
  if (startOption === 'symptoms') {
    return (
      <div className="flex flex-col h-screen bg-background">
        {/* Header */}
        <div className="border-b bg-card px-6 py-4">
          <div className="flex items-center gap-3">
            <Activity className="h-6 w-6 text-primary" />
            <div>
              <h1 className="text-xl font-semibold">CarePath</h1>
              <p className="text-sm text-muted-foreground">Medical Guidance Assistant</p>
            </div>
          </div>
        </div>

        {/* Symptom Selection */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-3xl mx-auto space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Select Your Symptoms</h2>
              <p className="text-muted-foreground">
                Choose all symptoms you're experiencing. You can also add custom symptoms below.
              </p>
            </div>

            {/* Common Symptoms Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {commonSymptoms.map((symptom) => (
                <Button
                  key={symptom}
                  variant={selectedSymptoms.includes(symptom) ? "default" : "outline"}
                  onClick={() => handleSymptomToggle(symptom)}
                  className="h-auto py-3"
                >
                  {symptom}
                </Button>
              ))}
            </div>

            {/* Custom Symptom Input */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Other Symptoms</label>
              <input
                type="text"
                value={customSymptom}
                onChange={(e) => setCustomSymptom(e.target.value)}
                placeholder="Describe any other symptoms..."
                className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </div>

            {/* Selected Symptoms */}
            {(selectedSymptoms.length > 0 || customSymptom) && (
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm font-medium mb-2">Selected Symptoms:</p>
                <p className="text-sm">
                  {[...selectedSymptoms, customSymptom].filter(Boolean).join(', ')}
                </p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setStartOption('none')
                  setSelectedSymptoms([])
                  setCustomSymptom('')
                }}
              >
                Back
              </Button>
              <Button
                onClick={submitSymptoms}
                disabled={selectedSymptoms.length === 0 && !customSymptom.trim()}
                className="flex-1"
              >
                Continue to Chat
              </Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <div className="border-b bg-card px-6 py-4">
        <div className="flex items-center gap-3">
          <Activity className="h-6 w-6 text-primary" />
          <div>
            <h1 className="text-xl font-semibold">CarePath</h1>
            <p className="text-sm text-muted-foreground">Medical Guidance Assistant</p>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : index === 0
                      ? 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800'
                      : 'bg-gray-200 dark:bg-gray-700'
                }`}
              >
                {index === 0 ? (
                  <p className="whitespace-pre-wrap text-[15px]">
                    <span className="font-bold">Hello! I'm CarePath</span>
                    {message.content.replace("Hello! I'm CarePath", '')}
                  </p>
                ) : (
                  <p className="whitespace-pre-wrap text-[15px]">{message.content}</p>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 dark:bg-gray-700 rounded-lg px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce delay-200" />
                </div>
              </div>
            </div>
          )}

        {/* Assessment Card */}
        {assessment && (
          <div className="flex justify-center mt-6">
            <Card className="w-full max-w-2xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Assessment Results
                </CardTitle>
                <CardDescription>Based on our conversation</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Possible Condition</p>
                  <p className="text-lg font-semibold">{assessment.possible_condition}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Category</p>
                    <p className="text-sm">{assessment.category}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Confidence</p>
                    <p className="text-sm">{assessment.confidence}</p>
                  </div>
                </div>

                <div
                  className={`p-4 rounded-lg border ${getUrgencyColor(assessment.urgency_level)}`}
                >
                  <p className="text-sm font-medium mb-1">Urgency Level: {assessment.urgency_level}</p>
                  <p className="text-sm">{assessment.action}</p>
                </div>

                <div>
                  <p className="text-sm font-medium text-muted-foreground">Recommended Specialist</p>
                  <p className="text-sm font-semibold">{assessment.recommended_specialist}</p>
                </div>

                {assessment.other_possibilities.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Other Possibilities</p>
                    <p className="text-sm">{assessment.other_possibilities.join(', ')}</p>
                  </div>
                )}

                {/* Disclaimer */}
                <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex gap-2">
                    <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-semibold text-yellow-900">Important Disclaimer</p>
                      <p className="text-sm text-yellow-800 mt-1">
                        This is not a medical diagnosis. This assessment is for informational purposes only
                        and should not replace professional medical advice. Please consult a qualified
                        healthcare professional for proper evaluation and treatment.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area - Sticky */}
      <div className="sticky bottom-0 border-t bg-card px-4 py-4">
        <div className="max-w-3xl mx-auto space-y-3">
          {/* Diagnosis Button */}
          {showDiagnosisButton && !assessment && (
            <div className="flex justify-center">
              <Button
                onClick={getDiagnosis}
                variant="secondary"
                size="sm"
                disabled={isLoading}
                className="shadow-sm"
              >
                <Activity className="h-4 w-4 mr-2" />
                Ready for Diagnosis
              </Button>
            </div>
          )}

          {/* Message Input */}
          {!assessment && (
            <div className="flex gap-2">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSendMessage()
                  }
                }}
                placeholder="Type your message... (Shift+Enter for new line)"
                disabled={isLoading}
                rows={1}
                className="flex-1 px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 resize-none min-h-[44px] max-h-[200px] overflow-y-auto"
                style={{ fieldSizing: 'content' } as any}
              />
              <Button
                onClick={handleSendMessage}
                disabled={isLoading || !input.trim()}
                size="icon"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

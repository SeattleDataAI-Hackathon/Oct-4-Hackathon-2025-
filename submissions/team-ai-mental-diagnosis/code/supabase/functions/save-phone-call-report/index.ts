import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import OpenAI from 'https://esm.sh/openai@4.0.0'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface PhoneCallReport {
  type: string
  event_timestamp: number
  data: {
    agent_id: string
    conversation_id: string
    status: string
    user_id: string
    transcript: Array<{
      role: string
      message: string
      tool_calls: any
      tool_results: any
      feedback: any
      time_in_call_secs: number
      conversation_turn_metrics: any
    }>
    metadata: {
      start_time_unix_secs: number
      call_duration_secs: number
      cost: number
      deletion_settings: any
      feedback: any
      authorization_method: string
      charging: any
      termination_reason: string
    }
    analysis: {
      evaluation_criteria_results: any
      data_collection_results: any
      call_successful: string
      transcript_summary: string
    }
    conversation_initiation_client_data: {
      conversation_config_override: any
      custom_llm_extra_body: any
      dynamic_variables: any
    }
  }
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  // Skip authentication for webhook endpoints
  // This allows the function to be called without JWT tokens

  // Only allow POST requests
  if (req.method !== 'POST') {
    return new Response(
      JSON.stringify({ error: 'Method not allowed. Only POST requests are supported.' }),
      { 
        status: 405, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }

  try {
    // Create Supabase client with service role key to bypass RLS
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Parse request body
    const body: PhoneCallReport = await req.json()
    
    // Log the received data for debugging
    console.log('Received data:', JSON.stringify(body, null, 2))

    // Validate required fields
    if (!body.type || typeof body.type !== 'string') {
      console.log('Validation error: Type field missing or invalid')
      return new Response(
        JSON.stringify({ error: 'Type field is required and must be a string' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    if (!body.event_timestamp || typeof body.event_timestamp !== 'number') {
      console.log('Validation error: Event timestamp field missing or invalid')
      return new Response(
        JSON.stringify({ error: 'Event timestamp field is required and must be a number' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    if (!body.data || typeof body.data !== 'object') {
      console.log('Validation error: Data field missing or invalid')
      return new Response(
        JSON.stringify({ error: 'Data field is required and must be an object' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Validate data fields - make them more flexible
    // Allow null user_id since we'll get a user from the database
    if (body.data.user_id !== null && body.data.user_id !== undefined && typeof body.data.user_id !== 'string') {
      console.log('Validation error: User ID field must be a string, null, or undefined')
      return new Response(
        JSON.stringify({ error: 'User ID field must be a string, null, or undefined' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Make conversation_id optional for now
    if (body.data.conversation_id && typeof body.data.conversation_id !== 'string') {
      console.log('Validation error: Conversation ID field must be a string if provided')
      return new Response(
        JSON.stringify({ error: 'Conversation ID field must be a string if provided' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Make transcript optional for now
    if (body.data.transcript && !Array.isArray(body.data.transcript)) {
      console.log('Validation error: Transcript field must be an array if provided')
      return new Response(
        JSON.stringify({ error: 'Transcript field must be an array if provided' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Make analysis optional for now
    if (body.data.analysis && typeof body.data.analysis !== 'object') {
      console.log('Validation error: Analysis field must be an object if provided')
      return new Response(
        JSON.stringify({ error: 'Analysis field must be an object if provided' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Get the first available user from the database (optional)
    let patientData = null
    let actualUserId = body.data.user_id || 'anonymous-user' // Use original user_id as fallback or create anonymous user

    const { data: users, error: usersError } = await supabaseClient
      .from('user_information')
      .select('*')
      .limit(1)

    if (!usersError && users && users.length > 0) {
      patientData = users[0]
      actualUserId = patientData.user_id
      console.log('Using patient data from database:', patientData.user_id)
    } else {
      console.log('No patient data found, using fallback user_id:', actualUserId)
    }

    // Extract and format transcript
    let transcriptText = ''
    if (body.data.transcript && Array.isArray(body.data.transcript)) {
      transcriptText = body.data.transcript
        .map((entry: any) => `${entry.role}: ${entry.message}`)
        .join('\n')
    }

    // Create OpenAI client
    const openai = new OpenAI({
      apiKey: 'XXX'
    })

    // Create prompt for mood analysis
    const patientContext = patientData ? `
Patient Information:
- Age: ${patientData.age || 'Not specified'}
- Gender: ${patientData.gender || 'Not specified'}
- Occupation: ${patientData.occupation || 'Not specified'}
- Mental Health Diagnosis: ${patientData.mental_health_diagnosis || 'Not specified'}
- Therapy History: ${patientData.therapy_history || 'Not specified'}
- Current Mental Health Status: ${patientData.additional_info || 'Not specified'}
` : 'No patient information available - analyzing conversation without patient context'

    const prompt = `
You are a mental health AI assistant analyzing a phone call transcript to assess the patient's emotional state and mood.

${patientContext}

Phone Call Transcript:
${transcriptText}

Please analyze this conversation and provide:
1. A mood rating from 1-5 (1 = very negative, 5 = very positive)
2. A detailed mood description explaining the emotional state
3. A list of specific emotions detected (e.g., anxiety, sadness, hope, frustration, etc.)

Focus on the emotional indicators in the conversation, the patient's tone, and any expressed feelings or concerns.
`

    let moodAnalysis = {
      mood: 3,
      mood_description: 'Unable to analyze mood',
      emotions: []
    }

    try {
      // Call OpenAI API with structured output
      const completion = await openai.chat.completions.create({
        model: 'gpt-4o',
        messages: [
          {
            role: 'system',
            content: 'You are a mental health AI assistant. Analyze conversations and provide structured mood assessments.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.3,
        max_tokens: 500,
        response_format: {
          type: "json_schema",
          json_schema: {
            name: "mood_analysis",
            schema: {
              type: "object",
              properties: {
                mood: {
                  type: "integer",
                  minimum: 1,
                  maximum: 5,
                  description: "Mood rating from 1 (very negative) to 5 (very positive)"
                },
                mood_description: {
                  type: "string",
                  description: "Detailed description of the emotional state"
                },
                emotions: {
                  type: "array",
                  items: {
                    type: "string"
                  },
                  description: "List of specific emotions detected"
                }
              },
              required: ["mood", "mood_description", "emotions"],
              additionalProperties: false
            }
          }
        }
      })

      const response = completion.choices[0]?.message?.content
      if (response) {
        try {
          const parsed = JSON.parse(response)
          moodAnalysis = {
            mood: parsed.mood || 3,
            mood_description: parsed.mood_description || 'Unable to analyze mood',
            emotions: Array.isArray(parsed.emotions) ? parsed.emotions : []
          }
        } catch (parseError) {
          console.error('Error parsing OpenAI response:', parseError)
          // Use default values if parsing fails
        }
      }
    } catch (openaiError) {
      console.error('OpenAI API error:', openaiError)
      // Use default values if API call fails
    }

    // Insert phone call report with AI-generated mood analysis
    const { data, error } = await supabaseClient
      .from('phone_call_reports')
      .insert({
        user_id: actualUserId,
        mood: moodAnalysis.mood,
        mood_description: moodAnalysis.mood_description,
        emotions: moodAnalysis.emotions
      })
      .select()

    if (error) {
      console.error('Database error:', error)
      return new Response(
        JSON.stringify({ error: 'Failed to save phone call report' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    return new Response(
      JSON.stringify({ 
        success: true, 
        message: 'Phone call report saved successfully with AI mood analysis',
        data: data[0],
        mood_analysis: moodAnalysis
      }),
      { 
        status: 201, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )

  } catch (error) {
    console.error('Function error:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
})

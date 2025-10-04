import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface UserInfo {
  user_id: string
  information: string
  phone_number?: string
  // Demographics
  age?: string
  gender?: string
  occupation?: string
  relationship_status?: string
  living_situation?: string
  // Mental Health
  mental_health_diagnosis?: string
  therapy_history?: string
  psychiatric_medication?: string
  mental_health_hospitalization?: string
  past_self_harm_thoughts?: string
  current_self_harm_thoughts?: string
  // Additional Info
  additional_info?: string
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Create Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    // Get the current user
    const { data: { user }, error: userError } = await supabaseClient.auth.getUser()
    
    if (userError || !user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Parse request body
    const { 
      information, 
      phone_number,
      // Demographics
      age,
      gender,
      occupation,
      relationship_status,
      living_situation,
      // Mental Health
      mental_health_diagnosis,
      therapy_history,
      psychiatric_medication,
      mental_health_hospitalization,
      past_self_harm_thoughts,
      current_self_harm_thoughts,
      // Additional Info
      additional_info
    } = await req.json()

    // Validate that we have either structured data or information string
    const hasStructuredData = age || gender || occupation || relationship_status || living_situation ||
                             mental_health_diagnosis || therapy_history || psychiatric_medication ||
                             mental_health_hospitalization || past_self_harm_thoughts || 
                             current_self_harm_thoughts || additional_info

    if (!information && !hasStructuredData) {
      return new Response(
        JSON.stringify({ error: 'Either information field or structured data is required' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Validate phone number if provided
    if (phone_number && typeof phone_number !== 'string') {
      return new Response(
        JSON.stringify({ error: 'Phone number must be a string' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Basic phone number validation if provided
    if (phone_number && phone_number.length < 10) {
      return new Response(
        JSON.stringify({ error: 'Phone number must be at least 10 characters long' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Create a summary of structured data for the information field
    const createInformationSummary = () => {
      const parts = []
      
      if (age) parts.push(`Age: ${age}`)
      if (gender) parts.push(`Gender: ${gender}`)
      if (occupation) parts.push(`Occupation: ${occupation}`)
      if (relationship_status) parts.push(`Relationship Status: ${relationship_status}`)
      if (living_situation) parts.push(`Living Situation: ${living_situation}`)
      if (phone_number) parts.push(`Phone: ${phone_number}`)
      if (mental_health_diagnosis) parts.push(`Mental Health Diagnosis: ${mental_health_diagnosis}`)
      if (therapy_history) parts.push(`Therapy History: ${therapy_history}`)
      if (psychiatric_medication) parts.push(`Psychiatric Medication: ${psychiatric_medication}`)
      if (mental_health_hospitalization) parts.push(`Mental Health Hospitalization: ${mental_health_hospitalization}`)
      if (past_self_harm_thoughts) parts.push(`Past Self-Harm Thoughts: ${past_self_harm_thoughts}`)
      if (current_self_harm_thoughts) parts.push(`Current Self-Harm Thoughts: ${current_self_harm_thoughts}`)
      if (additional_info) parts.push(`Additional Info: ${additional_info}`)
      
      return parts.length > 0 ? parts.join('\n') : 'No structured information provided'
    }

    // Use provided information or create summary from structured data
    const informationToSave = information || createInformationSummary()

    // Insert or update user information
    const { data, error } = await supabaseClient
      .from('user_information')
      .upsert({
        user_id: user.id,
        information: informationToSave,
        phone_number: phone_number || null,
        // Demographics
        age: age || null,
        gender: gender || null,
        occupation: occupation || null,
        relationship_status: relationship_status || null,
        living_situation: living_situation || null,
        // Mental Health
        mental_health_diagnosis: mental_health_diagnosis || null,
        therapy_history: therapy_history || null,
        psychiatric_medication: psychiatric_medication || null,
        mental_health_hospitalization: mental_health_hospitalization || null,
        past_self_harm_thoughts: past_self_harm_thoughts || null,
        current_self_harm_thoughts: current_self_harm_thoughts || null,
        // Additional Info
        additional_info: additional_info || null,
        updated_at: new Date().toISOString()
      }, {
        onConflict: 'user_id'
      })
      .select()

    if (error) {
      console.error('Database error:', error)
      return new Response(
        JSON.stringify({ error: 'Failed to save user information' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    return new Response(
      JSON.stringify({ 
        success: true, 
        message: 'User information saved successfully',
        data: data[0]
      }),
      { 
        status: 200, 
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

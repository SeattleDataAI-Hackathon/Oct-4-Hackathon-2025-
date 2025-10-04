import { createClient } from '@supabase/supabase-js'

// Get environment variables with proper fallbacks for production
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://gmdhmtyysrvdpucfvphk.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdtZGhtdHl5c3J2ZHB1Y2Z2cGhrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3MTg0NTgsImV4cCI6MjA2ODI5NDQ1OH0.4LxbMbztibnBYG7lyh42ZJqA3XdcRrOKQmjNHvSE-es'

// Validate that we have the required environment variables
if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase environment variables. Please check your .env file and ensure VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are set.'
  )
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

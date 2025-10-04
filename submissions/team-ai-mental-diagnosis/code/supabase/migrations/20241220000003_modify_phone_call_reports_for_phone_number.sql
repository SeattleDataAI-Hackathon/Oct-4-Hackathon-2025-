-- Modify phone_call_reports table to support phone number-based reports without authentication
-- Add phone_number column
ALTER TABLE public.phone_call_reports 
ADD COLUMN phone_number VARCHAR(20);

-- Make user_id nullable since we'll use phone_number instead
ALTER TABLE public.phone_call_reports 
ALTER COLUMN user_id DROP NOT NULL;

-- Add index for phone_number lookups
CREATE INDEX IF NOT EXISTS idx_phone_call_reports_phone_number ON public.phone_call_reports(phone_number);

-- Drop existing RLS policies
DROP POLICY IF EXISTS "Users can view their own phone call reports" ON public.phone_call_reports;
DROP POLICY IF EXISTS "Users can insert their own phone call reports" ON public.phone_call_reports;
DROP POLICY IF EXISTS "Users can update their own phone call reports" ON public.phone_call_reports;
DROP POLICY IF EXISTS "Users can delete their own phone call reports" ON public.phone_call_reports;

-- Create new RLS policies for phone number-based access
-- Allow public access for phone number-based reports
CREATE POLICY "Allow public access to phone call reports" ON public.phone_call_reports
    FOR ALL USING (true);

-- Add constraint to ensure either user_id or phone_number is provided
ALTER TABLE public.phone_call_reports 
ADD CONSTRAINT check_user_or_phone 
CHECK (user_id IS NOT NULL OR phone_number IS NOT NULL);

-- Create phone_call_reports table
CREATE TABLE IF NOT EXISTS public.phone_call_reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    mood INTEGER NOT NULL CHECK (mood >= 1 AND mood <= 5),
    mood_description TEXT NOT NULL,
    emotions TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_phone_call_reports_user_id ON public.phone_call_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_phone_call_reports_created_at ON public.phone_call_reports(created_at);

-- Enable Row Level Security
ALTER TABLE public.phone_call_reports ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only access their own phone call reports
CREATE POLICY "Users can view their own phone call reports" ON public.phone_call_reports
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own phone call reports" ON public.phone_call_reports
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own phone call reports" ON public.phone_call_reports
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own phone call reports" ON public.phone_call_reports
    FOR DELETE USING (auth.uid() = user_id);

-- Create trigger to automatically update updated_at
CREATE TRIGGER trigger_phone_call_reports_updated_at
    BEFORE UPDATE ON public.phone_call_reports
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

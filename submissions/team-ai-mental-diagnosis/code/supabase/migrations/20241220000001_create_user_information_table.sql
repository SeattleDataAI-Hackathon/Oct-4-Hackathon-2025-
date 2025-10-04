-- Create user_information table
CREATE TABLE IF NOT EXISTS public.user_information (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    information TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_information_user_id ON public.user_information(user_id);

-- Enable Row Level Security
ALTER TABLE public.user_information ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only access their own information
CREATE POLICY "Users can view their own information" ON public.user_information
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own information" ON public.user_information
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own information" ON public.user_information
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own information" ON public.user_information
    FOR DELETE USING (auth.uid() = user_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER trigger_user_information_updated_at
    BEFORE UPDATE ON public.user_information
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

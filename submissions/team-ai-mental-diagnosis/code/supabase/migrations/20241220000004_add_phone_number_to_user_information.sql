-- Add phone_number column to user_information table
ALTER TABLE public.user_information 
ADD COLUMN phone_number VARCHAR(20);

-- Add index for phone number lookups
CREATE INDEX IF NOT EXISTS idx_user_information_phone_number ON public.user_information(phone_number);

-- Add unique constraint for phone number (optional - uncomment if you want unique phone numbers)
-- ALTER TABLE public.user_information ADD CONSTRAINT unique_phone_number UNIQUE (phone_number);

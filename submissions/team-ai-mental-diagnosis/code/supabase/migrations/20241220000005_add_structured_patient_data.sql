-- Add structured columns for patient data to user_information table
-- Demographics
ALTER TABLE public.user_information 
ADD COLUMN age VARCHAR(10),
ADD COLUMN gender VARCHAR(50),
ADD COLUMN occupation VARCHAR(255),
ADD COLUMN relationship_status VARCHAR(50),
ADD COLUMN living_situation VARCHAR(50);

-- Mental Health
ALTER TABLE public.user_information 
ADD COLUMN mental_health_diagnosis TEXT,
ADD COLUMN therapy_history TEXT,
ADD COLUMN psychiatric_medication TEXT,
ADD COLUMN mental_health_hospitalization TEXT,
ADD COLUMN past_self_harm_thoughts TEXT,
ADD COLUMN current_self_harm_thoughts TEXT;

-- Additional Information
ALTER TABLE public.user_information 
ADD COLUMN additional_info TEXT;

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_user_information_age ON public.user_information(age);
CREATE INDEX IF NOT EXISTS idx_user_information_gender ON public.user_information(gender);
CREATE INDEX IF NOT EXISTS idx_user_information_occupation ON public.user_information(occupation);
CREATE INDEX IF NOT EXISTS idx_user_information_relationship_status ON public.user_information(relationship_status);
CREATE INDEX IF NOT EXISTS idx_user_information_living_situation ON public.user_information(living_situation);

"""Seed database with pre-approved home remedies for common infant conditions."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import SessionLocal
from src.database.models import HomeRemedy
from src.utils.logger import setup_logger

logger = setup_logger()


def seed_home_remedies():
    """Seed the database with pre-approved home remedies."""
    db = SessionLocal()

    home_remedies_data = [
        # Common Cold remedies
        {
            "condition": "Common Cold",
            "remedy_name": "Humidifier Use",
            "description": "Use a cool-mist humidifier in baby's room",
            "instructions": "Place a cool-mist humidifier in the baby's room to add moisture to the air. Clean the humidifier daily to prevent mold growth. Keep humidity levels between 30-50%.",
            "safety_notes": "Ensure humidifier is out of baby's reach. Clean daily to prevent bacterial growth.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        {
            "condition": "Common Cold",
            "remedy_name": "Saline Nasal Drops",
            "description": "Use saline drops to clear nasal congestion",
            "instructions": "Place 2-3 drops of saline solution in each nostril. Wait a few moments, then use a bulb syringe to gently suction out mucus. Use before feeding and bedtime.",
            "safety_notes": "Use only saline drops, never medicated drops without doctor approval.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        {
            "condition": "Common Cold",
            "remedy_name": "Elevate Head During Sleep",
            "description": "Elevate the head of the crib mattress",
            "instructions": "Place a towel or small pillow under the crib mattress (not in the crib) to create a slight incline. This helps drainage and easier breathing.",
            "safety_notes": "Never place pillows or towels IN the crib with baby. Only elevate the mattress from underneath.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        # Fever remedies
        {
            "condition": "Fever",
            "remedy_name": "Lukewarm Bath",
            "description": "Give a lukewarm (not cold) bath",
            "instructions": "Give baby a lukewarm sponge bath or regular bath. Water temperature should be comfortable, not cold. Dry baby immediately and dress in light clothing.",
            "safety_notes": "Never use cold water or alcohol baths. Monitor baby closely during bath.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        {
            "condition": "Fever",
            "remedy_name": "Light Clothing",
            "description": "Dress baby in light, breathable clothing",
            "instructions": "Remove heavy layers and dress baby in one light layer. Use a light blanket if needed. Avoid over-bundling.",
            "safety_notes": "Check baby regularly to ensure they're not too hot or cold.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        {
            "condition": "Fever",
            "remedy_name": "Adequate Hydration",
            "description": "Ensure baby stays well-hydrated",
            "instructions": "Offer breast milk or formula more frequently. For babies over 6 months, can also offer small amounts of water. Watch for signs of dehydration.",
            "safety_notes": "Contact doctor if baby shows signs of dehydration: fewer wet diapers, dry mouth, no tears when crying.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        # Cough remedies
        {
            "condition": "Cough",
            "remedy_name": "Honey for Cough",
            "description": "Give honey to soothe cough (12+ months only)",
            "instructions": "Give 1/2 to 1 teaspoon of honey before bedtime. Can repeat as needed. Mix with warm water if desired.",
            "safety_notes": "NEVER give honey to babies under 12 months due to botulism risk. This remedy is ONLY for babies 12 months and older.",
            "min_age_months": 12,
            "max_age_months": 36,
        },
        {
            "condition": "Cough",
            "remedy_name": "Steam Therapy",
            "description": "Use steam to loosen mucus",
            "instructions": "Run a hot shower and sit in the steamy bathroom with baby for 10-15 minutes. Keep baby away from hot water. You can also use a cool-mist humidifier.",
            "safety_notes": "Never leave baby unattended. Keep baby away from hot water to prevent burns.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        # Teething remedies
        {
            "condition": "Teething",
            "remedy_name": "Cold Teething Ring",
            "description": "Use a cold (not frozen) teething ring",
            "instructions": "Chill a clean teething ring in the refrigerator (not freezer). Allow baby to chew on it. Supervise to prevent choking.",
            "safety_notes": "Never use frozen teething rings as they can damage gums. Always supervise.",
            "min_age_months": 4,
            "max_age_months": 36,
        },
        {
            "condition": "Teething",
            "remedy_name": "Gum Massage",
            "description": "Gently massage baby's gums",
            "instructions": "Wash hands thoroughly. Use a clean finger to gently massage baby's gums in circular motions for 1-2 minutes.",
            "safety_notes": "Ensure hands are clean. Be gentle to avoid hurting sensitive gums.",
            "min_age_months": 4,
            "max_age_months": 36,
        },
        {
            "condition": "Teething",
            "remedy_name": "Cold Washcloth",
            "description": "Give baby a cold, damp washcloth to chew",
            "instructions": "Wet a clean washcloth and chill in refrigerator for 30 minutes. Let baby chew on it under supervision.",
            "safety_notes": "Supervise to prevent choking. Ensure washcloth is clean.",
            "min_age_months": 4,
            "max_age_months": 36,
        },
        # Diaper Rash remedies
        {
            "condition": "Diaper Rash",
            "remedy_name": "Frequent Diaper Changes",
            "description": "Change diapers frequently",
            "instructions": "Change wet or soiled diapers immediately. Clean area gently with warm water and pat dry completely before applying new diaper.",
            "safety_notes": "Be gentle when cleaning to avoid further irritation.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        {
            "condition": "Diaper Rash",
            "remedy_name": "Diaper-Free Time",
            "description": "Allow diaper-free time on waterproof surface",
            "instructions": "Place baby on a waterproof mat or towel and allow 10-15 minutes of diaper-free time, 2-3 times daily. This allows skin to air dry and heal.",
            "safety_notes": "Supervise baby during diaper-free time. Use waterproof protection for surfaces.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        {
            "condition": "Diaper Rash",
            "remedy_name": "Barrier Cream",
            "description": "Apply zinc oxide or petroleum jelly",
            "instructions": "Apply a thick layer of zinc oxide cream or petroleum jelly at each diaper change to create a protective barrier.",
            "safety_notes": "Use products specifically designed for babies. Consult doctor if rash persists.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        # Constipation remedies
        {
            "condition": "Constipation",
            "remedy_name": "Tummy Massage",
            "description": "Gentle tummy massage in clockwise motion",
            "instructions": "With baby lying on back, use fingertips to gently massage tummy in clockwise circular motions. Do this for 3-5 minutes, several times a day.",
            "safety_notes": "Be very gentle. Stop if baby seems uncomfortable.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        {
            "condition": "Constipation",
            "remedy_name": "Bicycle Legs Exercise",
            "description": "Move baby's legs in bicycle motion",
            "instructions": "With baby on back, gently move legs in bicycle pedaling motion for 1-2 minutes. This can help stimulate bowel movements.",
            "safety_notes": "Be gentle and stop if baby is uncomfortable.",
            "min_age_months": 0,
            "max_age_months": 36,
        },
        {
            "condition": "Constipation",
            "remedy_name": "Prune Juice (6+ months)",
            "description": "Offer small amounts of diluted prune juice",
            "instructions": "For babies 6+ months, offer 1-2 ounces of diluted prune juice (50% juice, 50% water) once daily.",
            "safety_notes": "Only for babies 6 months and older. Consult doctor if constipation persists.",
            "min_age_months": 6,
            "max_age_months": 36,
        },
        # Gas/Colic remedies
        {
            "condition": "Gas/Colic",
            "remedy_name": "Burping During Feeding",
            "description": "Burp baby frequently during and after feeding",
            "instructions": "Pause feeding every 2-3 ounces (or every 5-10 minutes if breastfeeding) to burp baby. Hold baby upright and gently pat back.",
            "safety_notes": "Support baby's head and neck. Be patient as some babies take longer to burp.",
            "min_age_months": 0,
            "max_age_months": 12,
        },
        {
            "condition": "Gas/Colic",
            "remedy_name": "Tummy Time",
            "description": "Gentle tummy time to help pass gas",
            "instructions": "Place baby on tummy for short periods (1-5 minutes) when awake and alert. This pressure can help release gas.",
            "safety_notes": "Always supervise tummy time. Never place baby on tummy to sleep.",
            "min_age_months": 0,
            "max_age_months": 12,
        },
    ]

    try:
        # Check if remedies already exist
        existing_count = db.query(HomeRemedy).count()
        if existing_count > 0:
            logger.info(f"Home remedies already seeded ({existing_count} records). Skipping.")
            return

        # Add all remedies
        for remedy_data in home_remedies_data:
            remedy = HomeRemedy(**remedy_data)
            db.add(remedy)

        db.commit()
        logger.info(f"Successfully seeded {len(home_remedies_data)} home remedies.")

    except Exception as e:
        logger.error(f"Error seeding home remedies: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_home_remedies()

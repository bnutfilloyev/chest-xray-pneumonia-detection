"""
Generate comprehensive mock data for the pneumonia detection system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date, timezone
import random
import uuid
from faker import Faker

from app.core.database import SessionLocal, create_tables
from app.models.database import Patient, Prediction, AuditLog, SystemStats, WeeklyStats

fake = Faker()

# Sample data lists - Uzbek names
UZBEK_MALE_NAMES = [
    "Akmal", "Bobur", "Davron", "Farrux", "Jahongir", "Karim", "Laziz", "Murod",
    "Nodir", "Otabek", "Rustam", "Sardor", "Timur", "Ulugbek", "Valijon", "Yorqin",
    "Zafar", "Aziz", "Bekzod", "Dilshod", "Eldor", "Farhod", "Gulom", "Hasanboy",
    "Islom", "Jasur", "Komil", "Lochin", "Mansur", "Nurali", "Oybek", "Pulat"
]

UZBEK_FEMALE_NAMES = [
    "Aziza", "Barno", "Dildora", "Feruza", "Gulnora", "Hilola", "Iroda", "Jamila",
    "Kamola", "Laylo", "Malika", "Nargiza", "Oysha", "Parvina", "Qunduz", "Robiya",
    "Sevara", "Tursunoy", "Umida", "Vasila", "Yulduz", "Zarina", "Dilfuza", "Elnora",
    "Farangiz", "Gavhar", "Hulkar", "Iqbol", "Jasmin", "Komila", "Lola", "Maftuna"
]

UZBEK_LAST_NAMES = [
    "Ahmedov", "Bakirov", "Djurayev", "Ergashev", "Fayzullayev", "Gafurov", "Hasanov",
    "Iskandarov", "Jalolov", "Karimov", "Lutfullayev", "Mamadaliyev", "Nazarov", "Otajonov",
    "Pulatov", "Qodirov", "Rahmonov", "Saidov", "Tursunov", "Umarov", "Valiyev", "Yusupov",
    "Zakirov", "Abdullayev", "Bobojonov", "Djabbarov", "Eshonqulov", "Foziljonov", "Giyosov",
    "Holmatov", "Inoyatov", "Juraev", "Komiljonov", "Latipov", "Mirzayev", "Normatov"
]

UZBEK_CITIES_DISTRICTS = [
    "Toshkent sh., Yunusobod t.", "Toshkent sh., Mirzo Ulugbek t.", "Toshkent sh., Chilonzor t.",
    "Toshkent sh., Yakkasaroy t.", "Toshkent sh., Mirobod t.", "Toshkent sh., Bektemir t.",
    "Samarqand sh., Registon t.", "Samarqand sh., Payariq t.", "Samarqand sh., Kattaqo'rg'on t.",
    "Buxoro sh., Buxoro t.", "Buxoro sh., Kogon t.", "Buxoro sh., Olot t.",
    "Andijon sh., Andijon shahar t.", "Andijon sh., Asaka t.", "Andijon sh., Xonobod t.",
    "Namangan sh., Namangan shahar t.", "Namangan sh., Chortoq t.", "Namangan sh., Pop t.",
    "Farg'ona sh., Farg'ona shahar t.", "Farg'ona sh., Marg'ilon t.", "Farg'ona sh., Quva t.",
    "Qashqadaryo vil., Qarshi t.", "Qashqadaryo vil., Shahrisabz t.", "Qashqadaryo vil., Kitob t.",
    "Surxondaryo vil., Termiz t.", "Surxondaryo vil., Denov t.", "Surxondaryo vil., Boysun t.",
    "Xorazm vil., Urganch t.", "Xorazm vil., Xiva t.", "Xorazm vil., Gurlan t.",
    "Navoiy vil., Navoiy shahar t.", "Navoiy vil., Zarafshon t.", "Navoiy vil., Uchquduq t."
]

GENDERS = ["M", "F", "Other"]

def generate_patients(db: Session, count: int = 1000):
    """Generate mock patients"""
    print(f"Generating {count} patients...")
    
    patients = []
    used_patient_ids = set()
    
    for i in range(count):
        # Generate unique patient ID
        patient_id = f"P{random.randint(100000, 999999)}"
        while patient_id in used_patient_ids:
            patient_id = f"P{random.randint(100000, 999999)}"
        used_patient_ids.add(patient_id)
        
        # Generate patient data with Uzbek names
        gender = random.choice(GENDERS)
        if gender == "M":
            first_name = random.choice(UZBEK_MALE_NAMES)
        else:
            first_name = random.choice(UZBEK_FEMALE_NAMES)
        last_name = random.choice(UZBEK_LAST_NAMES)
        age = random.randint(18, 85)
        
        # Generate dates (mostly recent, some older)
        days_ago = random.choices(
            range(1, 365),
            weights=[100] + [max(1, 100-i) for i in range(1, 364)],
            k=1
        )[0]
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        # Generate Uzbek contact info
        uzbek_relationships = ["Turmush o'rtog'i", "Ota-ona", "Farzand", "Aka-uka", "Do'st", "Qarindosh"]
        uzbek_insurance_providers = ["O'zbekiston Sug'urta", "Kafolat Sug'urta", "Alskom Sug'urta", "Gross Sug'urta", "Uzbekinvest Sug'urta"]
        
        # Generate Uzbek phone numbers in format +998XX-XXX-XXXX
        phone = None
        emergency_phone = None
        if random.random() > 0.3:
            operator = random.choice(['90', '91', '93', '94', '95', '97', '98', '99'])
            phone = f"+998{operator}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        
        if random.random() > 0.6:
            operator = random.choice(['90', '91', '93', '94', '95', '97', '98', '99'])
            emergency_phone = f"+998{operator}-{random.randint(100,999)}-{random.randint(1000,9999)}"

        patient = Patient(
            patient_id=patient_id,
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            phone=phone,
            email=f"{first_name.lower()}.{last_name.lower()}@email.uz" if random.random() > 0.4 else None,
            address=random.choice(UZBEK_CITIES_DISTRICTS) if random.random() > 0.3 else None,
            medical_record_number=f"TT{random.randint(10000, 99999)}",
            emergency_contact={
                "name": f"{random.choice(UZBEK_MALE_NAMES if random.random() > 0.5 else UZBEK_FEMALE_NAMES)} {random.choice(UZBEK_LAST_NAMES)}",
                "phone": emergency_phone,
                "relationship": random.choice(uzbek_relationships)
            } if emergency_phone else None,
            insurance_info={
                "provider": random.choice(uzbek_insurance_providers),
                "policy_number": f"UZ{random.randint(100000, 999999)}",
                "group_number": f"GRP{random.randint(1000, 9999)}"
            } if random.random() > 0.3 else None,
            created_at=created_at
        )
        
        patients.append(patient)
        
        # Batch insert every 100 records
        if len(patients) >= 100:
            db.bulk_save_objects(patients)
            db.commit()
            patients = []
            print(f"  Inserted {i+1} patients...")
    
    # Insert remaining patients
    if patients:
        db.bulk_save_objects(patients)
        db.commit()
    
    print(f"✅ Generated {count} patients successfully")

def generate_predictions(db: Session, count: int = 2000):
    """Generate mock predictions"""
    print(f"Generating {count} predictions...")
    
    # Get all patients
    patients = db.query(Patient).all()
    if not patients:
        print("❌ No patients found. Generate patients first.")
        return
    
    predictions = []
    
    for i in range(count):
        # Select random patient for each prediction (all predictions must have a patient)
        patient = random.choice(patients)
        
        # Generate prediction result
        prediction_result = random.choices(
            ["NORMAL", "PNEUMONIA"],
            weights=[70, 30],  # 70% normal, 30% pneumonia
            k=1
        )[0]
        
        # Generate confidence based on prediction
        if prediction_result == "PNEUMONIA":
            confidence = random.uniform(0.65, 0.98)  # Higher confidence for pneumonia
        else:
            confidence = random.uniform(0.55, 0.95)  # Varied confidence for normal
        
        confidence_scores = {
            "NORMAL": 1.0 - confidence if prediction_result == "PNEUMONIA" else confidence,
            "PNEUMONIA": confidence if prediction_result == "PNEUMONIA" else 1.0 - confidence
        }
        
        # Generate dates
        # Prediction after patient creation
        earliest_date = patient.created_at
        days_after = random.randint(0, min(30, (datetime.now(timezone.utc) - earliest_date).days))
        created_at = earliest_date + timedelta(days=days_after)
        
        # Generate filenames
        file_id = str(uuid.uuid4())
        image_filename = f"{file_id}.jpg"
        original_filename = f"chest_xray_{random.randint(1000, 9999)}.jpg"
        
        prediction = Prediction(
            id=file_id,
            patient_id=patient.id,
            image_filename=image_filename,
            original_filename=original_filename,
            image_path=f"uploads/predictions/{image_filename}",
            prediction=prediction_result,
            confidence=confidence,
            confidence_scores=confidence_scores,
            inference_time=random.uniform(0.5, 3.2),
            image_size=[random.randint(512, 2048), random.randint(512, 2048)],
            clinical_notes=f"Tekshiruv natijalari. {fake.text(max_nb_chars=150)}" if random.random() > 0.7 else None,
            reviewed=random.random() > 0.6,
            reviewed_by=f"Dr. {random.choice(UZBEK_LAST_NAMES)}" if random.random() > 0.6 else None,
            reviewed_at=created_at + timedelta(hours=random.randint(1, 48)) if random.random() > 0.6 else None,
            created_at=created_at
        )
        
        predictions.append(prediction)
        
        # Batch insert every 100 records
        if len(predictions) >= 100:
            db.bulk_save_objects(predictions)
            db.commit()
            predictions = []
            print(f"  Inserted {i+1} predictions...")
    
    # Insert remaining predictions
    if predictions:
        db.bulk_save_objects(predictions)
        db.commit()
    
    print(f"✅ Generated {count} predictions successfully")

def generate_audit_logs(db: Session, count: int = 5000):
    """Generate mock audit logs"""
    print(f"Generating {count} audit logs...")
    
    actions = [
        "CREATE_PATIENT", "UPDATE_PATIENT", "DELETE_PATIENT",
        "CREATE_PREDICTION", "REVIEW_PREDICTION", "DELETE_PREDICTION",
        "EXPORT_DATA", "VIEW_PATIENT", "VIEW_PREDICTION"
    ]
    
    resource_types = ["Patient", "Prediction", "Export", "System"]
    users = [f"Dr. {random.choice(UZBEK_LAST_NAMES)}" for _ in range(20)] + ["system", "admin"]
    
    logs = []
    
    for i in range(count):
        action = random.choice(actions)
        user_id = random.choice(users)
        resource_type = random.choice(resource_types)
        
        # Generate realistic details based on action
        if action.startswith("CREATE"):
            details = {"status": "success", "new_record": True}
        elif action.startswith("UPDATE"):
            details = {"status": "success", "fields_updated": random.randint(1, 5)}
        elif action.startswith("DELETE"):
            details = {"status": "success", "backup_created": True}
        elif action.startswith("EXPORT"):
            details = {"format": random.choice(["CSV", "PDF", "Excel"]), "records": random.randint(10, 1000)}
        else:
            details = {"status": "success"}
        
        # Generate dates
        days_ago = random.randint(1, 180)
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        log = AuditLog(
            user_id=user_id,
            action_type=action,
            entity_type=resource_type,
            entity_id=str(random.randint(1, 10000)),
            details=details,
            ip_address=f"192.168.1.{random.randint(1, 254)}",
            user_agent="Mozilla/5.0 (Healthcare/1.0)",
            timestamp=created_at
        )
        
        logs.append(log)
        
        # Batch insert every 200 records
        if len(logs) >= 200:
            db.bulk_save_objects(logs)
            db.commit()
            logs = []
            print(f"  Inserted {i+1} audit logs...")
    
    # Insert remaining logs
    if logs:
        db.bulk_save_objects(logs)
        db.commit()
    
    print(f"✅ Generated {count} audit logs successfully")

def generate_system_stats(db: Session, days: int = 90):
    """Generate system statistics for the past N days"""
    print(f"Generating system stats for {days} days...")
    
    stats = []
    base_patients = 500
    base_predictions = 800
    
    for i in range(days):
        stat_date = datetime.now(timezone.utc).date() - timedelta(days=days-i-1)
        
        # Simulate growing numbers
        total_patients = base_patients + i * random.randint(5, 15)
        total_predictions = base_predictions + i * random.randint(8, 25)
        predictions_today = random.randint(10, 50)
        pneumonia_cases = int(total_predictions * 0.3)
        normal_cases = total_predictions - pneumonia_cases
        
        stat = SystemStats(
            date=stat_date,
            total_patients=total_patients,
            total_predictions=total_predictions,
            predictions_today=predictions_today,
            pneumonia_cases=pneumonia_cases,
            normal_cases=normal_cases,
            average_confidence=random.uniform(0.75, 0.95),
            model_accuracy=random.uniform(0.92, 0.97),
            active_users=random.randint(3, 12)
        )
        
        stats.append(stat)
    
    db.bulk_save_objects(stats)
    db.commit()
    print(f"✅ Generated {days} days of system stats")

def generate_weekly_stats(db: Session, weeks: int = 24):
    """Generate weekly statistics"""
    print(f"Generating weekly stats for {weeks} weeks...")
    
    stats = []
    
    for i in range(weeks):
        week_start = datetime.now(timezone.utc).date() - timedelta(weeks=weeks-i-1)
        week_end = week_start + timedelta(days=6)
        
        # Generate realistic weekly data
        predictions_count = random.randint(50, 200)
        pneumonia_detected = random.randint(15, 60)
        unique_patients = random.randint(20, 80)
        
        stat = WeeklyStats(
            week_start=week_start,
            week_end=week_end,
            predictions_count=predictions_count,
            accuracy_rate=random.uniform(0.88, 0.96),
            pneumonia_detected=pneumonia_detected,
            normal_cases=predictions_count - pneumonia_detected,
            unique_patients=unique_patients
        )
        
        stats.append(stat)
    
    db.bulk_save_objects(stats)
    db.commit()
    print(f"✅ Generated {weeks} weeks of statistics")

def main():
    """Main function to generate all mock data"""
    print("🚀 Starting mock data generation...")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        patient_count = db.query(Patient).count()
        prediction_count = db.query(Prediction).count()
        
        if patient_count > 0 or prediction_count > 0:
            print(f"⚠️  Database already contains {patient_count} patients and {prediction_count} predictions")
            
            # In Docker/CI environment, automatically regenerate data
            import os
            if os.getenv('DOCKER_ENV') or os.getenv('CI') or not os.isatty(0):
                print("🔄 Running in automated environment - regenerating data...")
                should_regenerate = True
            else:
                response = input("Do you want to clear existing data and regenerate? (y/N): ")
                should_regenerate = response.lower() == 'y'
            
            if should_regenerate:
                # Clear existing data
                print("🗑️  Clearing existing data...")
                db.query(WeeklyStats).delete()
                db.query(SystemStats).delete()
                db.query(AuditLog).delete()
                db.query(Prediction).delete()
                db.query(Patient).delete()
                db.commit()
                print("✅ Existing data cleared")
            else:
                print("Skipping data generation")
                return
        
        # Generate data
        generate_patients(db, 1000)
        generate_predictions(db, 2500)
        generate_audit_logs(db, 5000)
        generate_system_stats(db, 90)
        generate_weekly_stats(db, 24)
        
        # Final statistics
        final_patients = db.query(Patient).count()
        final_predictions = db.query(Prediction).count()
        final_logs = db.query(AuditLog).count()
        final_system_stats = db.query(SystemStats).count()
        final_weekly_stats = db.query(WeeklyStats).count()
        
        print("\n🎉 Mock data generation completed!")
        print(f"📊 Final Statistics:")
        print(f"   • Patients: {final_patients:,}")
        print(f"   • Predictions: {final_predictions:,}")
        print(f"   • Audit Logs: {final_logs:,}")
        print(f"   • System Stats: {final_system_stats}")
        print(f"   • Weekly Stats: {final_weekly_stats}")
        
    except Exception as e:
        print(f"❌ Error generating mock data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()

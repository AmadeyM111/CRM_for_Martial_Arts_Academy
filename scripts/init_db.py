#!/usr/bin/env python3
"""
Database initialization script
Creates tables and populates with sample data
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import create_tables, SessionLocal
from app.models import Student, Trainer, Training, Attendance, Subscription, Payment, BeltExam
from app.controllers import StudentController, TrainingController, PaymentController, BeltExamController

def create_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    try:
        # Create trainers
        main_trainer = Trainer(
            first_name="Main",
            last_name="Trainer",
            phone="+7-999-000-00-01",
            email="trainer@example.com",
            is_main=True
        )
        reserve_trainer = Trainer(
            first_name="Reserve",
            last_name="Trainer",
            phone="+7-999-000-00-02",
            email="reserve@example.com",
            is_main=False
        )
        
        db.add(main_trainer)
        db.add(reserve_trainer)
        db.commit()
        
        # Create students
        students_data = [
            {
                "first_name": "Student",
                "last_name": "One",
                "phone": "+7-999-000-00-01",
                "telegram_id": "@student1",
                "email": "student1@example.com",
                "current_belt": "White",
                "notes": "Sample student 1"
            },
            {
                "first_name": "Student",
                "last_name": "Two",
                "phone": "+7-999-000-00-02",
                "telegram_id": "@student2",
                "email": "student2@example.com",
                "current_belt": "Blue",
                "notes": "Sample student 2"
            },
            {
                "first_name": "Student",
                "last_name": "Three",
                "phone": "+7-999-000-00-03",
                "telegram_id": "@student3",
                "email": "student3@example.com",
                "current_belt": "Purple",
                "notes": "Sample student 3"
            },
            {
                "first_name": "Student",
                "last_name": "Four",
                "phone": "+7-999-000-00-04",
                "telegram_id": "@student4",
                "email": "student4@example.com",
                "current_belt": "White",
                "notes": "Sample student 4"
            },
            {
                "first_name": "Student",
                "last_name": "Five",
                "phone": "+7-999-000-00-05",
                "telegram_id": "@student5",
                "email": "student5@example.com",
                "current_belt": "Brown",
                "notes": "Sample student 5"
            }
        ]
        
        students = []
        for student_data in students_data:
            student = Student(**student_data)
            db.add(student)
            students.append(student)
        
        db.commit()
        
        # Create trainings for the last month
        training_dates = []
        base_date = datetime.now() - timedelta(days=30)
        
        # Create trainings for Mon, Wed, Fri pattern
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            if current_date.weekday() in [0, 2, 4]:  # Monday, Wednesday, Friday
                training_time = current_date.replace(hour=20, minute=30, second=0, microsecond=0)
                training_dates.append(training_time)
        
        trainings = []
        for i, training_date in enumerate(training_dates):
            trainer = main_trainer if i % 3 != 0 else reserve_trainer  # Reserve trainer every 3rd training
            training = Training(
                date=training_date,
                trainer_id=trainer.id,
                notes=f"Тренировка #{i+1}"
            )
            db.add(training)
            trainings.append(training)
        
        db.commit()
        
        # Create attendance records
        for training in trainings:
            for student in students:
                # Random attendance (80% present, 15% absent, 5% late)
                import random
                rand = random.random()
                if rand < 0.8:
                    status = "Present"
                elif rand < 0.95:
                    status = "Absent"
                else:
                    status = "Late"
                
                attendance = Attendance(
                    training_id=training.id,
                    student_id=student.id,
                    status=status
                )
                db.add(attendance)
        
        db.commit()
        
        # Create subscriptions
        subscription_types = ["Monthly", "Single"]
        for student in students:
            # Create monthly subscription
            subscription = Subscription(
                student_id=student.id,
                subscription_type="Monthly",
                start_date=datetime.now() - timedelta(days=15),
                end_date=datetime.now() + timedelta(days=15),
                price=8000.0,
                is_active=True
            )
            db.add(subscription)
            
            # Create payment record
            payment = Payment(
                student_id=student.id,
                amount=8000.0,
                payment_type="Monthly",
                description="Месячная подписка",
                payment_date=datetime.now() - timedelta(days=15)
            )
            db.add(payment)
        
        db.commit()
        
        # Create belt exams
        exam_data = [
            {
                "student_id": students[1].id,  # Student Two
                "belt_color": "Blue",
                "exam_date": datetime.now() - timedelta(days=60),
                "result": "Pass",
                "notes": "Отличный экзамен"
            },
            {
                "student_id": students[2].id,  # Student Three
                "belt_color": "Purple",
                "exam_date": datetime.now() - timedelta(days=120),
                "result": "Pass",
                "notes": "Продвинутый уровень"
            }
        ]
        
        for exam_info in exam_data:
            exam = BeltExam(**exam_info)
            db.add(exam)
        
        db.commit()
        
        print("✅ Sample data created successfully!")
        print(f"📊 Created:")
        print(f"   - {len(students_data)} students")
        print(f"   - 2 trainers")
        print(f"   - {len(trainings)} trainings")
        print(f"   - {len(trainings) * len(students)} attendance records")
        print(f"   - {len(students)} subscriptions")
        print(f"   - {len(students)} payments")
        print(f"   - {len(exam_data)} belt exams")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function"""
    print("🚀 Initializing BJJ CRM Database...")
    
    # Create tables
    print("📋 Creating database tables...")
    create_tables()
    print("✅ Tables created successfully!")
    
    # Create sample data
    print("📊 Creating sample data...")
    create_sample_data()
    
    print("🎉 Database initialization completed!")

if __name__ == "__main__":
    main()

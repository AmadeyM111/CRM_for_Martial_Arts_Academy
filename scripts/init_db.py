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
            first_name="Александр",
            last_name="Петров",
            phone="+7-999-111-22-33",
            email="trainer@bjj-academy.ru",
            is_main=True
        )
        reserve_trainer = Trainer(
            first_name="Михаил",
            last_name="Сидоров",
            phone="+7-999-222-33-44",
            email="reserve@bjj-academy.ru",
            is_main=False
        )
        
        db.add(main_trainer)
        db.add(reserve_trainer)
        db.commit()
        
        # Create students
        students_data = [
            {
                "first_name": "Иван",
                "last_name": "Иванов",
                "phone": "+7-999-123-45-67",
                "telegram_id": "@ivanov",
                "email": "ivan@example.com",
                "current_belt": "White",
                "notes": "Начинающий ученик"
            },
            {
                "first_name": "Петр",
                "last_name": "Петров",
                "phone": "+7-999-234-56-78",
                "telegram_id": "@petrov",
                "email": "petr@example.com",
                "current_belt": "Blue",
                "notes": "Опытный ученик"
            },
            {
                "first_name": "Сидор",
                "last_name": "Сидоров",
                "phone": "+7-999-345-67-89",
                "telegram_id": "@sidorov",
                "email": "sidor@example.com",
                "current_belt": "Purple",
                "notes": "Продвинутый ученик"
            },
            {
                "first_name": "Анна",
                "last_name": "Козлова",
                "phone": "+7-999-456-78-90",
                "telegram_id": "@kozlov",
                "email": "anna@example.com",
                "current_belt": "White",
                "notes": "Новая ученица"
            },
            {
                "first_name": "Дмитрий",
                "last_name": "Смирнов",
                "phone": "+7-999-567-89-01",
                "telegram_id": "@smirnov",
                "email": "dmitry@example.com",
                "current_belt": "Brown",
                "notes": "Опытный практик"
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
                "student_id": students[1].id,  # Петр Петров
                "belt_color": "Blue",
                "exam_date": datetime.now() - timedelta(days=60),
                "result": "Pass",
                "notes": "Отличный экзамен"
            },
            {
                "student_id": students[2].id,  # Сидор Сидоров
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

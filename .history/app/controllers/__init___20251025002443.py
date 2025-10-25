from sqlalchemy.orm import Session
from app.models import Student, Trainer, Training, Attendance, Subscription, Payment, BeltExam
from datetime import datetime, timedelta
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class StudentController:
    """Controller for student management"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_student(self, first_name: str, last_name: str, phone: str, 
                      telegram_id: str = None, email: str = None, 
                      current_belt: str = "White", notes: str = None) -> Student:
        """Create a new student"""
        student = Student(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            telegram_id=telegram_id,
            email=email,
            current_belt=current_belt,
            notes=notes
        )
        self.db.add(student)
        self.db.commit()
        return student
    
    def get_all_students(self) -> List[Student]:
        """Get all students"""
        return self.db.query(Student).filter(Student.is_active == True).all()
    
    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """Get student by ID"""
        return self.db.query(Student).filter(Student.id == student_id).first()
    
    def get_student_by_phone(self, phone: str) -> Optional[Student]:
        """Get student by phone number"""
        return self.db.query(Student).filter(Student.phone == phone).first()
    
    def update_student(self, student_id: int, **kwargs) -> Optional[Student]:
        """Update student information"""
        student = self.get_student_by_id(student_id)
        if student:
            for key, value in kwargs.items():
                if hasattr(student, key):
                    setattr(student, key, value)
            self.db.commit()
            return student
        return None
    
    def deactivate_student(self, student_id: int) -> bool:
        """Deactivate student (soft delete)"""
        student = self.get_student_by_id(student_id)
        if student:
            student.is_active = False
            self.db.commit()
            return True
        return False
    
    def get_student_attendance_count(self, student_id: int) -> int:
        """Get total attendance count for student"""
        return self.db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.status == "Present"
        ).count()
    
    def get_student_missed_classes(self, student_id: int, days: int = 30) -> int:
        """Get missed classes count for student in last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(Attendance).join(Training).filter(
            Attendance.student_id == student_id,
            Attendance.status == "Absent",
            Training.date >= cutoff_date
        ).count()

class TrainingController:
    """Controller for training management"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_training(self, date: datetime, trainer_id: int, notes: str = None) -> Training:
        """Create a new training session"""
        training = Training(
            date=date,
            trainer_id=trainer_id,
            notes=notes
        )
        self.db.add(training)
        self.db.commit()
        return training
    
    def get_all_trainings(self) -> List[Training]:
        """Get all trainings"""
        return self.db.query(Training).order_by(Training.date.desc()).all()
    
    def get_trainings_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Training]:
        """Get trainings in date range"""
        return self.db.query(Training).filter(
            Training.date >= start_date,
            Training.date <= end_date
        ).order_by(Training.date).all()
    
    def get_upcoming_trainings(self, days: int = 7) -> List[Training]:
        """Get upcoming trainings in next N days"""
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        return self.db.query(Training).filter(
            Training.date >= datetime.utcnow(),
            Training.date <= cutoff_date
        ).order_by(Training.date).all()
    
    def mark_attendance(self, training_id: int, student_id: int, status: str = "Present", notes: str = None) -> Attendance:
        """Mark student attendance for training"""
        attendance = Attendance(
            training_id=training_id,
            student_id=student_id,
            status=status,
            notes=notes
        )
        self.db.add(attendance)
        self.db.commit()
        return attendance

class PaymentController:
    """Controller for payment management"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_payment(self, student_id: int, amount: float, payment_type: str, 
                      description: str = None) -> Payment:
        """Create a new payment record"""
        payment = Payment(
            student_id=student_id,
            amount=amount,
            payment_type=payment_type,
            description=description
        )
        self.db.add(payment)
        self.db.commit()
        return payment
    
    def create_subscription(self, student_id: int, subscription_type: str, 
                           start_date: datetime, price: float) -> Subscription:
        """Create a new subscription"""
        end_date = None
        if subscription_type == "Monthly":
            end_date = start_date + timedelta(days=30)
        
        subscription = Subscription(
            student_id=student_id,
            subscription_type=subscription_type,
            start_date=start_date,
            end_date=end_date,
            price=price
        )
        self.db.add(subscription)
        self.db.commit()
        return subscription
    
    def get_student_payments(self, student_id: int) -> List[Payment]:
        """Get all payments for student"""
        return self.db.query(Payment).filter(Payment.student_id == student_id).order_by(Payment.payment_date.desc()).all()
    
    def get_monthly_revenue(self, year: int, month: int) -> float:
        """Get monthly revenue"""
        payments = self.db.query(Payment).filter(
            Payment.payment_date.year == year,
            Payment.payment_date.month == month
        ).all()
        return sum(payment.amount for payment in payments)
    
    def get_active_subscriptions(self) -> List[Subscription]:
        """Get all active subscriptions"""
        return self.db.query(Subscription).filter(
            Subscription.is_active == True,
            Subscription.end_date >= datetime.utcnow()
        ).all()

class BeltExamController:
    """Controller for belt exam management"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_belt_exam(self, student_id: int, belt_color: str, 
                        exam_date: datetime, result: str, notes: str = None) -> BeltExam:
        """Create a new belt exam record"""
        exam = BeltExam(
            student_id=student_id,
            belt_color=belt_color,
            exam_date=exam_date,
            result=result,
            notes=notes
        )
        self.db.add(exam)
        self.db.commit()
        
        # Update student's belt if exam passed
        if result == "Pass":
            student = self.db.query(Student).filter(Student.id == student_id).first()
            if student:
                student.current_belt = belt_color
                self.db.commit()
        
        return exam
    
    def get_student_exams(self, student_id: int) -> List[BeltExam]:
        """Get all exams for student"""
        return self.db.query(BeltExam).filter(BeltExam.student_id == student_id).order_by(BeltExam.exam_date.desc()).all()
    
    def get_upcoming_exams(self, days: int = 30) -> List[BeltExam]:
        """Get upcoming exams in next N days"""
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        return self.db.query(BeltExam).filter(
            BeltExam.exam_date >= datetime.utcnow(),
            BeltExam.exam_date <= cutoff_date
        ).order_by(BeltExam.exam_date).all()

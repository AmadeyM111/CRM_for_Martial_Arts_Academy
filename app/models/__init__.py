from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Student(Base):
    """Модель ученика"""
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    telegram_id = Column(String(50), unique=True)
    email = Column(String(100))
    current_belt = Column(String(20), default='White')  # White, Blue, Purple, Brown, Black
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    
    # Relationships
    attendances = relationship("Attendance", back_populates="student")
    subscriptions = relationship("Subscription", back_populates="student")
    payments = relationship("Payment", back_populates="student")
    belt_exams = relationship("BeltExam", back_populates="student")
    
    def __repr__(self):
        return f"<Student({self.first_name} {self.last_name})>"

class Trainer(Base):
    """Модель тренера"""
    __tablename__ = 'trainers'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    is_main = Column(Boolean, default=True)  # True - основной, False - резервный
    is_active = Column(Boolean, default=True)
    
    # Relationships
    trainings = relationship("Training", back_populates="trainer")
    
    def __repr__(self):
        return f"<Trainer({self.first_name} {self.last_name})>"

class Training(Base):
    """Модель тренировки"""
    __tablename__ = 'trainings'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.id'), nullable=False)
    notes = Column(Text)
    
    # Relationships
    trainer = relationship("Trainer", back_populates="trainings")
    attendances = relationship("Attendance", back_populates="training")
    
    def __repr__(self):
        return f"<Training({self.date})>"

class Attendance(Base):
    """Модель посещаемости"""
    __tablename__ = 'attendances'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    training_id = Column(Integer, ForeignKey('trainings.id'), nullable=False)
    status = Column(String(20), default='Present')  # Present, Absent, Late
    notes = Column(Text)
    
    # Relationships
    student = relationship("Student", back_populates="attendances")
    training = relationship("Training", back_populates="attendances")
    
    def __repr__(self):
        return f"<Attendance({self.student_id}, {self.training_id})>"

class Subscription(Base):
    """Модель подписки"""
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    subscription_type = Column(String(20), nullable=False)  # Monthly, Single
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    student = relationship("Student", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription({self.subscription_type}, {self.student_id})>"

class Payment(Base):
    """Модель платежа"""
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_type = Column(String(20), nullable=False)  # Monthly, Single, Exam
    description = Column(Text)
    
    # Relationships
    student = relationship("Student", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment({self.amount}, {self.student_id})>"

class BeltExam(Base):
    """Модель экзамена на пояс"""
    __tablename__ = 'belt_exams'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    belt_color = Column(String(20), nullable=False)
    exam_date = Column(DateTime, nullable=False)
    result = Column(String(20), nullable=False)  # Pass, Fail
    notes = Column(Text)
    
    # Relationships
    student = relationship("Student", back_populates="belt_exams")
    
    def __repr__(self):
        return f"<BeltExam({self.belt_color}, {self.student_id})>"

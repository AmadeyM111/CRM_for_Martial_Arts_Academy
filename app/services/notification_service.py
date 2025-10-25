import requests
import os
from typing import List, Optional
from datetime import datetime, timedelta
from app.models import Student, Training, Attendance
from database.connection import SessionLocal

class TelegramNotificationService:
    """Service for sending notifications via Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message: str, chat_id: str = None) -> bool:
        """Send message to Telegram chat"""
        if not self.bot_token:
            print("Telegram bot token not configured")
            return False
        
        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            print("Telegram chat ID not configured")
            return False
        
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": target_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Failed to send Telegram message: {e}")
            return False
    
    def send_training_reminder(self, training: Training, students: List[Student]) -> bool:
        """Send training reminder to students"""
        training_date = training.date.strftime("%d.%m.%Y %H:%M")
        message = f"🏆 <b>Напоминание о тренировке</b>\n\n"
        message += f"📅 Дата: {training_date}\n"
        message += f"👨‍🏫 Тренер: {training.trainer.first_name} {training.trainer.last_name}\n\n"
        message += f"Не забудьте про тренировку!"
        
        success_count = 0
        for student in students:
            if student.telegram_id:
                if self.send_message(message, student.telegram_id):
                    success_count += 1
        
        return success_count > 0
    
    def send_missed_classes_notification(self, student: Student, missed_count: int) -> bool:
        """Send notification about missed classes"""
        message = f"👋 Привет, {student.first_name}!\n\n"
        message += f"Мы заметили, что вы пропустили {missed_count} тренировок подряд.\n"
        message += f"Надеемся увидеть вас на следующей тренировке! 💪\n\n"
        message += f"Расписание: Пн, Ср, Пт в 20:30"
        
        return self.send_message(message, student.telegram_id)
    
    def send_belt_exam_notification(self, student: Student, belt_color: str, exam_date: datetime) -> bool:
        """Send belt exam notification"""
        exam_date_str = exam_date.strftime("%d.%m.%Y %H:%M")
        message = f"🥋 <b>Экзамен на пояс</b>\n\n"
        message += f"👤 Студент: {student.first_name} {student.last_name}\n"
        message += f"🎯 Пояс: {belt_color}\n"
        message += f"📅 Дата: {exam_date_str}\n\n"
        message += f"Удачи на экзамене! 💪"
        
        return self.send_message(message, student.telegram_id)
    
    def send_payment_reminder(self, student: Student, subscription_type: str) -> bool:
        """Send payment reminder"""
        message = f"💰 <b>Напоминание об оплате</b>\n\n"
        message += f"👤 {student.first_name} {student.last_name}\n"
        message += f"📋 Тип: {subscription_type}\n"
        message += f"💳 Пожалуйста, внесите оплату до конца месяца"
        
        return self.send_message(message, student.telegram_id)

class NotificationManager:
    """Manager for handling all notifications"""
    
    def __init__(self):
        self.telegram_service = TelegramNotificationService()
        self.db = SessionLocal()
    
    def check_missed_classes(self, threshold: int = 2):
        """Check for students who missed more than threshold classes"""
        # Get students who missed more than threshold classes in last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        students_with_missed = self.db.query(Student).join(Attendance).join(Training).filter(
            Training.date >= cutoff_date,
            Attendance.status == "Absent"
        ).all()
        
        for student in students_with_missed:
            missed_count = self.db.query(Attendance).join(Training).filter(
                Attendance.student_id == student.id,
                Attendance.status == "Absent",
                Training.date >= cutoff_date
            ).count()
            
            if missed_count >= threshold:
                self.telegram_service.send_missed_classes_notification(student, missed_count)
    
    def send_training_reminders(self, hours_before: int = 2):
        """Send training reminders"""
        reminder_time = datetime.utcnow() + timedelta(hours=hours_before)
        
        # Get upcoming trainings
        upcoming_trainings = self.db.query(Training).filter(
            Training.date >= datetime.utcnow(),
            Training.date <= reminder_time
        ).all()
        
        for training in upcoming_trainings:
            # Get all active students
            students = self.db.query(Student).filter(Student.is_active == True).all()
            self.telegram_service.send_training_reminder(training, students)
    
    def send_payment_reminders(self):
        """Send payment reminders for expiring subscriptions"""
        # Get subscriptions expiring in next 7 days
        cutoff_date = datetime.utcnow() + timedelta(days=7)
        
        expiring_subscriptions = self.db.query(Subscription).filter(
            Subscription.is_active == True,
            Subscription.end_date <= cutoff_date,
            Subscription.end_date >= datetime.utcnow()
        ).all()
        
        for subscription in expiring_subscriptions:
            student = subscription.student
            self.telegram_service.send_payment_reminder(student, subscription.subscription_type)
    
    def cleanup_expired_subscriptions(self):
        """Deactivate expired subscriptions"""
        expired_subscriptions = self.db.query(Subscription).filter(
            Subscription.is_active == True,
            Subscription.end_date < datetime.utcnow()
        ).all()
        
        for subscription in expired_subscriptions:
            subscription.is_active = False
        
        self.db.commit()
        return len(expired_subscriptions)

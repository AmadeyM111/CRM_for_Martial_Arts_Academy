#!/usr/bin/env python3
"""
CSV Export Service for BJJ CRM System
Handles data export to CSV format
"""

import csv
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy import func

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import SessionLocal
from app.models import Student, Trainer, Training, Attendance, Subscription, Payment, BeltExam


class CSVExportService:
    """Service for exporting data to CSV format"""
    
    def __init__(self, export_dir: str = None):
        self.export_dir = export_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "exports")
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_students(self, filename: str = None) -> str:
        """Export students to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"students_{timestamp}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        db = SessionLocal()
        try:
            students = db.query(Student).all()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'first_name', 'last_name', 'phone', 'telegram_id', 
                    'email', 'current_belt', 'registration_date', 'is_active', 'notes'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for student in students:
                    writer.writerow({
                        'id': student.id,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'phone': student.phone,
                        'telegram_id': student.telegram_id,
                        'email': student.email,
                        'current_belt': student.current_belt,
                        'registration_date': student.registration_date.isoformat() if student.registration_date else '',
                        'is_active': student.is_active,
                        'notes': student.notes
                    })
            
            return filepath
            
        finally:
            db.close()
    
    def export_trainings(self, filename: str = None) -> str:
        """Export trainings to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trainings_{timestamp}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        db = SessionLocal()
        try:
            trainings = db.query(Training).join(Trainer).all()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'date', 'trainer_name', 'trainer_phone', 'notes'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for training in trainings:
                    writer.writerow({
                        'id': training.id,
                        'date': training.date.isoformat() if training.date else '',
                        'trainer_name': f"{training.trainer.first_name} {training.trainer.last_name}",
                        'trainer_phone': training.trainer.phone,
                        'notes': training.notes
                    })
            
            return filepath
            
        finally:
            db.close()
    
    def export_attendance(self, filename: str = None) -> str:
        """Export attendance records to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"attendance_{timestamp}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        db = SessionLocal()
        try:
            attendance_records = db.query(Attendance).join(Training).join(Student).all()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'student_name', 'student_phone', 'training_date', 
                    'trainer_name', 'status', 'notes'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for record in attendance_records:
                    writer.writerow({
                        'id': record.id,
                        'student_name': f"{record.student.first_name} {record.student.last_name}",
                        'student_phone': record.student.phone,
                        'training_date': record.training.date.isoformat() if record.training.date else '',
                        'trainer_name': f"{record.training.trainer.first_name} {record.training.trainer.last_name}",
                        'status': record.status,
                        'notes': record.notes
                    })
            
            return filepath
            
        finally:
            db.close()
    
    def export_payments(self, filename: str = None) -> str:
        """Export payments to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"payments_{timestamp}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        db = SessionLocal()
        try:
            payments = db.query(Payment).join(Student).all()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'student_name', 'student_phone', 'amount', 
                    'payment_type', 'description', 'payment_date'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for payment in payments:
                    writer.writerow({
                        'id': payment.id,
                        'student_name': f"{payment.student.first_name} {payment.student.last_name}",
                        'student_phone': payment.student.phone,
                        'amount': payment.amount,
                        'payment_type': payment.payment_type,
                        'description': payment.description,
                        'payment_date': payment.payment_date.isoformat() if payment.payment_date else ''
                    })
            
            return filepath
            
        finally:
            db.close()
    
    def export_all_data(self, filename: str = None) -> Dict[str, str]:
        """Export all data to separate CSV files"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"bjj_crm_export_{timestamp}"
        else:
            base_filename = filename
        
        exports = {}
        
        # Export each data type
        exports['students'] = self.export_students(f"{base_filename}_students.csv")
        exports['trainings'] = self.export_trainings(f"{base_filename}_trainings.csv")
        exports['attendance'] = self.export_attendance(f"{base_filename}_attendance.csv")
        exports['payments'] = self.export_payments(f"{base_filename}_payments.csv")
        
        return exports
    
    def export_summary_report(self, filename: str = None) -> str:
        """Export summary report to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_report_{timestamp}.csv"
        
        filepath = os.path.join(self.export_dir, filename)
        
        db = SessionLocal()
        try:
            # Get summary data
            total_students = db.query(Student).count()
            total_trainings = db.query(Training).count()
            total_payments = db.query(Payment).count()
            total_revenue = db.query(func.sum(Payment.amount)).scalar() or 0
            
            # Get students by belt
            belt_stats = db.query(Student.current_belt, func.count(Student.id)).group_by(Student.current_belt).all()
            
            # Get monthly revenue
            monthly_revenue = db.query(
                func.strftime('%Y-%m', Payment.payment_date),
                func.sum(Payment.amount)
            ).group_by(func.strftime('%Y-%m', Payment.payment_date)).all()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write summary
                writer.writerow(['BJJ Academy CRM - Summary Report'])
                writer.writerow(['Generated:', datetime.now().isoformat()])
                writer.writerow([])
                
                writer.writerow(['General Statistics'])
                writer.writerow(['Total Students', total_students])
                writer.writerow(['Total Trainings', total_trainings])
                writer.writerow(['Total Payments', total_payments])
                writer.writerow(['Total Revenue', total_revenue])
                writer.writerow([])
                
                writer.writerow(['Students by Belt'])
                writer.writerow(['Belt', 'Count'])
                for belt, count in belt_stats:
                    writer.writerow([belt, count])
                writer.writerow([])
                
                writer.writerow(['Monthly Revenue'])
                writer.writerow(['Month', 'Revenue'])
                for month, revenue in monthly_revenue:
                    writer.writerow([month, revenue])
            
            return filepath
            
        finally:
            db.close()
    
    def get_export_list(self) -> List[Dict[str, Any]]:
        """Get list of all exported files"""
        exports = []
        
        try:
            for filename in os.listdir(self.export_dir):
                if filename.endswith('.csv'):
                    filepath = os.path.join(self.export_dir, filename)
                    file_stats = os.stat(filepath)
                    
                    exports.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': file_stats.st_size,
                        'created': datetime.fromtimestamp(file_stats.st_ctime),
                        'modified': datetime.fromtimestamp(file_stats.st_mtime)
                    })
            
            # Sort by creation time (newest first)
            exports.sort(key=lambda x: x['created'], reverse=True)
            return exports
            
        except Exception as e:
            raise Exception(f"Ошибка получения списка экспортов: {str(e)}")
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"


# Example usage
if __name__ == "__main__":
    export_service = CSVExportService()
    
    # Export all data
    exports = export_service.export_all_data()
    print(f"Exports created: {exports}")
    
    # Export summary
    summary_file = export_service.export_summary_report()
    print(f"Summary report: {summary_file}")
    
    # List exports
    export_list = export_service.get_export_list()
    print(f"Available exports: {len(export_list)}")
    
    for export in export_list:
        size = export_service.format_size(export['size'])
        print(f"  - {export['filename']}: {size}")

#!/usr/bin/env python3
"""
Google Drive Import Service for BJJ CRM System
Handles data import from Google Drive spreadsheets
"""

import os
import sys
import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import SessionLocal
from app.models import Student, Trainer, Training, Attendance, Subscription, Payment, BeltExam


class GoogleDriveService:
    """Service for importing data from Google Drive"""
    
    def __init__(self, credentials_file: str = None):
        self.credentials_file = credentials_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "config", "google_credentials.json"
        )
        self.api_key = None
        self.access_token = None
        
        # Load credentials if available
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Google API credentials"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r') as f:
                    credentials = json.load(f)
                    self.api_key = credentials.get('api_key')
                    self.access_token = credentials.get('access_token')
        except Exception as e:
            print(f"Warning: Could not load Google credentials: {e}")
    
    def import_from_csv_file(self, file_path: str, data_type: str) -> Dict[str, Any]:
        """
        Import data from local CSV file
        
        Args:
            file_path: Path to local CSV file
            data_type: Type of data to import ('students', 'trainings', 'payments')
            
        Returns:
            Dict with import results
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'cp1251', 'windows-1251', 'latin-1', 'iso-8859-1']
            file_content = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        file_content = file.read()
                        used_encoding = encoding
                        break
                except UnicodeDecodeError:
                    continue
            
            if file_content is None:
                raise Exception("Не удалось определить кодировку файла")
            
            # Parse CSV content
            from io import StringIO
            csv_reader = csv.DictReader(StringIO(file_content))
            
            # Import based on data type
            if data_type == 'students':
                return self._import_students(csv_reader)
            elif data_type == 'trainings':
                return self._import_trainings(csv_reader)
            elif data_type == 'payments':
                return self._import_payments(csv_reader)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                    
        except Exception as e:
            raise Exception(f"Ошибка импорта из CSV файла: {str(e)}")
    
    def import_from_csv_url(self, csv_url: str, data_type: str) -> Dict[str, Any]:
        """
        Import data from CSV URL (Google Sheets export URL)
        
        Args:
            csv_url: URL to CSV file or Google Sheets URL
            data_type: Type of data to import ('students', 'trainings', 'payments')
            
        Returns:
            Dict with import results
        """
        try:
            # Convert Google Sheets URL to CSV URL if needed
            csv_url = self._convert_to_csv_url(csv_url)
            
            # Download CSV data
            response = requests.get(csv_url)
            response.raise_for_status()
            
            # Parse CSV data
            csv_data = response.text
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            
            # Import based on data type
            if data_type == 'students':
                return self._import_students(csv_reader)
            elif data_type == 'trainings':
                return self._import_trainings(csv_reader)
            elif data_type == 'payments':
                return self._import_payments(csv_reader)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
        except Exception as e:
            raise Exception(f"Ошибка импорта из Google Drive: {str(e)}")
    
    def _import_students(self, csv_reader) -> Dict[str, Any]:
        """Import students from CSV data"""
        db = SessionLocal()
        imported_count = 0
        updated_count = 0
        errors = []
        
        try:
            for row_num, row in enumerate(csv_reader, 1):
                try:
                    # Validate required fields
                    if not row.get('first_name') or not row.get('last_name'):
                        errors.append(f"Строка {row_num}: Отсутствует имя или фамилия")
                        continue
                    
                    # Check if student already exists (by phone first, then telegram_id)
                    existing_student = None
                    telegram_id = row.get('telegram_id', '').strip()
                    phone = row.get('phone', '').strip()
                    
                    # First check by phone (more unique)
                    if phone:
                        existing_student = db.query(Student).filter(
                            Student.phone == phone
                        ).first()
                    
                    # If not found by phone, check by telegram_id
                    if not existing_student and telegram_id:
                        existing_student = db.query(Student).filter(
                            Student.telegram_id == telegram_id
                        ).first()
                    
                    if existing_student:
                        # Update existing student instead of skipping
                        existing_student.first_name = row['first_name']
                        existing_student.last_name = row['last_name']
                        existing_student.phone = phone
                        existing_student.email = row.get('email', '')
                        existing_student.current_belt = row.get('current_belt', 'White')
                        existing_student.notes = row.get('notes', '')
                        # Only update telegram_id if it's not empty and different
                        if telegram_id and telegram_id != existing_student.telegram_id:
                            existing_student.telegram_id = telegram_id
                        updated_count += 1
                        continue  # Skip adding new student, just update
                    
                    # Create new student
                    # If telegram_id is empty or common (like @xyz), make it unique
                    final_telegram_id = telegram_id
                    if not telegram_id or telegram_id in ['@xyz', '@test', '@example']:
                        final_telegram_id = ''  # Leave empty for non-unique values
                    
                    student = Student(
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        phone=row.get('phone', ''),
                        telegram_id=final_telegram_id,
                        email=row.get('email', ''),
                        current_belt=row.get('current_belt', 'White'),
                        notes=row.get('notes', '')
                    )
                    
                    db.add(student)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Строка {row_num}: {str(e)}")
            
            db.commit()
            
            return {
                'imported_count': imported_count,
                'errors': errors,
                'success': len(errors) == 0
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def _import_trainings(self, csv_reader) -> Dict[str, Any]:
        """Import trainings from CSV data"""
        db = SessionLocal()
        imported_count = 0
        errors = []
        
        try:
            for row_num, row in enumerate(csv_reader, 1):
                try:
                    # Validate required fields
                    if not row.get('date'):
                        errors.append(f"Строка {row_num}: Отсутствует дата тренировки")
                        continue
                    
                    # Parse date
                    try:
                        training_date = datetime.fromisoformat(row['date'].replace('Z', '+00:00'))
                    except ValueError:
                        errors.append(f"Строка {row_num}: Неверный формат даты")
                        continue
                    
                    # Find trainer
                    trainer_name = row.get('trainer_name', '')
                    trainer = None
                    if trainer_name:
                        name_parts = trainer_name.split(' ', 1)
                        if len(name_parts) == 2:
                            trainer = db.query(Trainer).filter(
                                Trainer.first_name == name_parts[0],
                                Trainer.last_name == name_parts[1]
                            ).first()
                    
                    if not trainer:
                        errors.append(f"Строка {row_num}: Тренер не найден")
                        continue
                    
                    # Check if training already exists
                    existing_training = db.query(Training).filter(
                        Training.date == training_date,
                        Training.trainer_id == trainer.id
                    ).first()
                    
                    if existing_training:
                        errors.append(f"Строка {row_num}: Тренировка уже существует")
                        continue
                    
                    # Create new training
                    training = Training(
                        date=training_date,
                        trainer_id=trainer.id,
                        notes=row.get('notes', '')
                    )
                    
                    db.add(training)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Строка {row_num}: {str(e)}")
            
            db.commit()
            
            return {
                'imported_count': imported_count,
                'errors': errors,
                'success': len(errors) == 0
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def _import_payments(self, csv_reader) -> Dict[str, Any]:
        """Import payments from CSV data"""
        db = SessionLocal()
        imported_count = 0
        errors = []
        
        try:
            for row_num, row in enumerate(csv_reader, 1):
                try:
                    # Validate required fields
                    if not row.get('student_name') or not row.get('amount'):
                        errors.append(f"Строка {row_num}: Отсутствует имя ученика или сумма")
                        continue
                    
                    # Find student
                    student_name = row['student_name']
                    name_parts = student_name.split(' ', 1)
                    if len(name_parts) != 2:
                        errors.append(f"Строка {row_num}: Неверный формат имени ученика")
                        continue
                    
                    student = db.query(Student).filter(
                        Student.first_name == name_parts[0],
                        Student.last_name == name_parts[1]
                    ).first()
                    
                    if not student:
                        errors.append(f"Строка {row_num}: Ученик не найден")
                        continue
                    
                    # Parse amount
                    try:
                        amount = float(row['amount'])
                    except ValueError:
                        errors.append(f"Строка {row_num}: Неверный формат суммы")
                        continue
                    
                    # Parse payment date
                    payment_date = datetime.now()
                    if row.get('payment_date'):
                        try:
                            payment_date = datetime.fromisoformat(row['payment_date'].replace('Z', '+00:00'))
                        except ValueError:
                            pass  # Use current date if parsing fails
                    
                    # Create new payment
                    payment = Payment(
                        student_id=student.id,
                        amount=amount,
                        payment_type=row.get('payment_type', 'Monthly'),
                        description=row.get('description', ''),
                        payment_date=payment_date
                    )
                    
                    db.add(payment)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Строка {row_num}: {str(e)}")
            
            db.commit()
            
            return {
                'imported_count': imported_count,
                'errors': errors,
                'success': len(errors) == 0
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def get_google_sheets_url(self, sheet_id: str, sheet_name: str = None) -> str:
        """
        Generate Google Sheets export URL
        
        Args:
            sheet_id: Google Sheets document ID
            sheet_name: Specific sheet name (optional)
            
        Returns:
            CSV export URL
        """
        base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export"
        
        params = {
            'format': 'csv',
            'id': sheet_id
        }
        
        if sheet_name:
            params['gid'] = sheet_name
        
        # Build URL with parameters
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def validate_csv_format(self, csv_url: str, data_type: str) -> Dict[str, Any]:
        """
        Validate CSV format before import
        
        Args:
            csv_url: URL to CSV file or Google Sheets URL
            data_type: Expected data type
            
        Returns:
            Validation results
        """
        try:
            # Convert Google Sheets URL to CSV URL if needed
            csv_url = self._convert_to_csv_url(csv_url)
            
            response = requests.get(csv_url)
            response.raise_for_status()
            
            csv_data = response.text
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            
            # Get headers
            headers = csv_reader.fieldnames or []
            
            # Define required fields for each data type
            required_fields = {
                'students': ['first_name', 'last_name'],
                'trainings': ['date', 'trainer_name'],
                'payments': ['student_name', 'amount']
            }
            
            if data_type not in required_fields:
                return {
                    'valid': False,
                    'error': f"Unsupported data type: {data_type}"
                }
            
            # Check required fields
            missing_fields = []
            for field in required_fields[data_type]:
                if field not in headers:
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    'valid': False,
                    'error': f"Missing required fields: {', '.join(missing_fields)}",
                    'headers': headers
                }
            
            # Count rows
            rows = list(csv_reader)
            row_count = len(rows)
            
            return {
                'valid': True,
                'headers': headers,
                'row_count': row_count
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def _convert_to_csv_url(self, url: str) -> str:
        """
        Convert Google Sheets URL to CSV export URL
        
        Args:
            url: Google Sheets URL
            
        Returns:
            CSV export URL
        """
        # If already a CSV URL, return as is
        if '/export?format=csv' in url:
            return url
        
        # Extract sheet ID from various Google Sheets URL formats
        import re
        
        # Pattern for Google Sheets URLs
        patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
        ]
        
        sheet_id = None
        gid = None
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                sheet_id = match.group(1)
                break
        
        if not sheet_id:
            raise ValueError("Не удалось извлечь ID таблицы из URL")
        
        # Extract gid if present
        gid_match = re.search(r'gid=(\d+)', url)
        if gid_match:
            gid = gid_match.group(1)
        
        # Build CSV export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        if gid:
            csv_url += f"&gid={gid}"
        
        return csv_url
    
    def validate_csv_file(self, file_path: str, data_type: str) -> Dict[str, Any]:
        """
        Validate local CSV file format before import
        
        Args:
            file_path: Path to local CSV file
            data_type: Expected data type
            
        Returns:
            Validation results
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'cp1251', 'windows-1251', 'latin-1', 'iso-8859-1']
            file_content = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        file_content = file.read()
                        used_encoding = encoding
                        break
                except UnicodeDecodeError:
                    continue
            
            if file_content is None:
                return {
                    'valid': False,
                    'error': "Не удалось определить кодировку файла"
                }
            
            # Parse CSV content
            from io import StringIO
            csv_reader = csv.DictReader(StringIO(file_content))
            
            # Get headers
            headers = csv_reader.fieldnames or []
            
            # Define required fields for each data type
            required_fields = {
                'students': ['first_name', 'last_name'],
                'trainings': ['date', 'trainer_name'],
                'payments': ['student_name', 'amount']
            }
            
            if data_type not in required_fields:
                return {
                    'valid': False,
                    'error': f"Unsupported data type: {data_type}"
                }
            
            # Check required fields
            missing_fields = []
            for field in required_fields[data_type]:
                if field not in headers:
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    'valid': False,
                    'error': f"Missing required fields: {', '.join(missing_fields)}",
                    'headers': headers
                }
            
            # Count rows
            rows = list(csv_reader)
            row_count = len(rows)
            
            return {
                'valid': True,
                'headers': headers,
                'row_count': row_count,
                'encoding': used_encoding
            }
                
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }


# Example usage
if __name__ == "__main__":
    google_service = GoogleDriveService()
    
    # Example Google Sheets URL
    sheet_id = "1ABC123DEF456GHI789JKL"
    csv_url = google_service.get_google_sheets_url(sheet_id, "Students")
    print(f"Google Sheets CSV URL: {csv_url}")
    
    # Validate format
    validation = google_service.validate_csv_format(csv_url, "students")
    print(f"Validation result: {validation}")

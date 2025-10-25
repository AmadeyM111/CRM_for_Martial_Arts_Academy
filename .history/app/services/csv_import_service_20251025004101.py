#!/usr/bin/env python3
"""
CSV Import Service for BJJ CRM System
Handles importing student data from CSV files
"""

import csv
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging
import chardet

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import SessionLocal
from app.models import Student
from app.controllers import StudentController

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVImportService:
    """Service for importing student data from CSV files"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.student_controller = StudentController(self.db)
    
    def close(self):
        """Close database session"""
        self.db.close()
    
    def detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected encoding
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
                
                # Fallback to common encodings if confidence is low
                if confidence < 0.7:
                    logger.warning(f"Low confidence in encoding detection, trying common encodings")
                    for fallback_encoding in ['utf-8', 'windows-1251', 'cp1251', 'iso-8859-1']:
                        try:
                            with open(file_path, 'r', encoding=fallback_encoding) as test_file:
                                test_file.read(1000)
                            logger.info(f"Fallback encoding {fallback_encoding} works")
                            return fallback_encoding
                        except UnicodeDecodeError:
                            continue
                
                return encoding or 'utf-8'
        except Exception as e:
            logger.error(f"Error detecting encoding: {e}")
            return 'utf-8'
    
    def validate_csv_format(self, file_path: str) -> Dict[str, Any]:
        """
        Validate CSV file format for student import
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dict with validation results
        """
        try:
            # Detect file encoding
            encoding = self.detect_encoding(file_path)
            logger.info(f"Using encoding: {encoding}")
            
            with open(file_path, 'r', encoding=encoding) as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Check required columns
                required_columns = ['first_name', 'last_name', 'phone']
                optional_columns = ['telegram_id', 'email', 'current_belt', 'notes']
                
                headers = reader.fieldnames
                if not headers:
                    return {
                        'valid': False,
                        'error': 'CSV файл не содержит заголовков'
                    }
                
                missing_required = [col for col in required_columns if col not in headers]
                if missing_required:
                    return {
                        'valid': False,
                        'error': f'Отсутствуют обязательные колонки: {", ".join(missing_required)}'
                    }
                
                # Count rows
                row_count = sum(1 for row in reader)
                
                return {
                    'valid': True,
                    'headers': headers,
                    'row_count': row_count,
                    'delimiter': delimiter,
                    'required_columns': required_columns,
                    'optional_columns': optional_columns
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'Ошибка чтения файла: {str(e)}'
            }
    
    def import_students_from_csv(self, file_path: str, 
                                skip_duplicates: bool = True) -> Dict[str, Any]:
        """
        Import students from CSV file
        
        Args:
            file_path: Path to CSV file
            skip_duplicates: Whether to skip duplicate phone numbers
            
        Returns:
            Dict with import results
        """
        try:
            # Validate file first
            validation = self.validate_csv_format(file_path)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error'],
                    'imported_count': 0,
                    'skipped_count': 0,
                    'errors': []
                }
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            # Detect file encoding
            encoding = self.detect_encoding(file_path)
            logger.info(f"Using encoding: {encoding}")
            
            with open(file_path, 'r', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=validation['delimiter'])
                
                for row_num, row in enumerate(reader, start=2):  # Start from 2 (header is row 1)
                    try:
                        # Extract data from row
                        first_name = row.get('first_name', '').strip()
                        last_name = row.get('last_name', '').strip()
                        phone = row.get('phone', '').strip()
                        telegram_id = row.get('telegram_id', '').strip() or None
                        email = row.get('email', '').strip() or None
                        current_belt = row.get('current_belt', 'White').strip()
                        notes = row.get('notes', '').strip() or None
                        
                        # Validate required fields
                        if not first_name:
                            errors.append(f"Строка {row_num}: Имя не может быть пустым")
                            continue
                        if not last_name:
                            errors.append(f"Строка {row_num}: Фамилия не может быть пустой")
                            continue
                        if not phone:
                            errors.append(f"Строка {row_num}: Телефон не может быть пустым")
                            continue
                        
                        # Check for duplicates if skip_duplicates is True
                        if skip_duplicates:
                            existing_student = self.student_controller.get_student_by_phone(phone)
                            if existing_student:
                                skipped_count += 1
                                logger.info(f"Skipped duplicate phone: {phone}")
                                continue
                        
                        # Create student
                        student = self.student_controller.create_student(
                            first_name=first_name,
                            last_name=last_name,
                            phone=phone,
                            telegram_id=telegram_id,
                            email=email,
                            current_belt=current_belt,
                            notes=notes
                        )
                        
                        imported_count += 1
                        logger.info(f"Imported student: {student.first_name} {student.last_name}")
                        
                    except Exception as e:
                        error_msg = f"Строка {row_num}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
            
            return {
                'success': True,
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'errors': errors,
                'total_rows': validation['row_count']
            }
            
        except Exception as e:
            logger.error(f"Failed to import CSV: {e}")
            return {
                'success': False,
                'error': f'Ошибка импорта: {str(e)}',
                'imported_count': 0,
                'skipped_count': 0,
                'errors': []
            }
    
    def get_csv_template(self) -> str:
        """
        Get CSV template for student import
        
        Returns:
            CSV template as string
        """
        template_data = [
            ['first_name', 'last_name', 'phone', 'telegram_id', 'email', 'current_belt', 'notes'],
            ['Иван', 'Иванов', '+7-999-123-45-67', '@ivanov', 'ivan@example.com', 'White', 'Начинающий ученик'],
            ['Петр', 'Петров', '+7-999-234-56-78', '@petrov', 'petr@example.com', 'Blue', 'Опытный ученик']
        ]
        
        output = []
        for row in template_data:
            output.append(','.join(f'"{cell}"' for cell in row))
        
        return '\n'.join(output)
    
    def export_template_to_file(self, file_path: str) -> bool:
        """
        Export CSV template to file
        
        Args:
            file_path: Path to save template
            
        Returns:
            True if successful
        """
        try:
            template = self.get_csv_template()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template)
            return True
        except Exception as e:
            logger.error(f"Failed to export template: {e}")
            return False


# Example usage
if __name__ == "__main__":
    import_service = CSVImportService()
    
    # Export template
    template_path = "student_template.csv"
    if import_service.export_template_to_file(template_path):
        print(f"Template exported to: {template_path}")
    
    # Example import
    # result = import_service.import_students_from_csv("students.csv")
    # print(f"Import result: {result}")
    
    import_service.close()

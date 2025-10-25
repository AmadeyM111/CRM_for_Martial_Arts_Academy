#!/usr/bin/env python3
"""
CSV Import Dialog for BJJ CRM System
Dialog for importing student data from CSV files
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.csv_import_service import CSVImportService


class CSVImportDialog:
    """Dialog for importing student data from CSV files"""
    
    def __init__(self, parent, refresh_callback=None):
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.import_service = CSVImportService()
        self.selected_file = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📥 Импорт учеников из CSV")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📥 Импорт учеников из CSV", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="📄 Выбор CSV файла", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=60)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(file_select_frame, text="📂 Выбрать файл", 
                  command=self.select_csv_file).pack(side=tk.RIGHT)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Настройки импорта", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.skip_duplicates_var = tk.BooleanVar(value=True)
        skip_duplicates_check = ttk.Checkbutton(
            options_frame, 
            text="Пропускать дубликаты (по номеру телефона)", 
            variable=self.skip_duplicates_var
        )
        skip_duplicates_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        validate_button = ttk.Button(buttons_frame, text="✅ Проверить формат", 
                                   command=self.validate_file)
        validate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.import_button = ttk.Button(buttons_frame, text="📥 Импортировать", 
                                       command=self.import_data, state=tk.DISABLED)
        self.import_button.pack(side=tk.LEFT, padx=(0, 10))
        
        template_button = ttk.Button(buttons_frame, text="📋 Скачать шаблон", 
                                   command=self.download_template)
        template_button.pack(side=tk.LEFT)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="📊 Результаты", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Results text widget
        self.results_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Help frame
        help_frame = ttk.LabelFrame(main_frame, text="❓ Помощь", padding="10")
        help_frame.pack(fill=tk.X, pady=(0, 20))
        
        help_text = """
Формат CSV файла:
• Обязательные колонки: first_name, last_name, phone
• Опциональные колонки: telegram_id, email, current_belt, notes
• Разделитель: запятая (,)
• Кодировка: UTF-8
• Первая строка должна содержать заголовки

Пример:
first_name,last_name,phone,telegram_id,email,current_belt,notes
Иван,Иванов,+7-999-123-45-67,@ivanov,ivan@example.com,White,Начинающий ученик
        """
        
        help_label = ttk.Label(help_frame, text=help_text.strip(), justify=tk.LEFT)
        help_label.pack(anchor=tk.W)
        
        # Close button
        close_button = ttk.Button(main_frame, text="❌ Закрыть", command=self.dialog.destroy)
        close_button.pack(pady=(20, 0))
    
    def select_csv_file(self):
        """Select CSV file for import"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите CSV файл с данными учеников",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                self.file_path_var.set(file_path)
                self.selected_file = file_path
                
                # Show file selection in results
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"📁 Выбран файл: {file_path}\n")
                self.results_text.insert(tk.END, f"📊 Нажмите 'Проверить формат' для валидации\n")
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка выбора файла: {e}")
    
    def validate_file(self):
        """Validate selected CSV file"""
        file_path = self.file_path_var.get().strip()
        
        if not file_path:
            messagebox.showwarning("⚠️ Предупреждение", "Выберите CSV файл")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("❌ Ошибка", "Файл не найден")
            return
        
        try:
            # Show progress
            self.dialog.config(cursor="wait")
            self.dialog.update()
            
            validation = self.import_service.validate_csv_format(file_path)
            
            if validation['valid']:
                message = f"✅ Файл готов к импорту!\n\n"
                message += f"Заголовки: {', '.join(validation['headers'])}\n"
                message += f"Строк данных: {validation['row_count']}\n"
                message += f"Разделитель: '{validation['delimiter']}'"
                
                messagebox.showinfo("✅ Валидация успешна", message)
                
                # Show validation results in text widget
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"✅ Файл прошел валидацию\n")
                self.results_text.insert(tk.END, f"Заголовки: {', '.join(validation['headers'])}\n")
                self.results_text.insert(tk.END, f"Строк данных: {validation['row_count']}\n")
                self.results_text.insert(tk.END, f"Разделитель: '{validation['delimiter']}'\n")
                
                # Enable import button after successful validation
                self.import_button.config(state=tk.NORMAL)
            else:
                messagebox.showerror("❌ Ошибка валидации", validation['error'])
                
                # Show error in text widget
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"❌ Ошибка валидации: {validation['error']}\n")
                
                # Disable import button on validation error
                self.import_button.config(state=tk.DISABLED)
        
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка проверки файла:\n{str(e)}")
            
            # Disable import button on error
            self.import_button.config(state=tk.DISABLED)
        
        finally:
            self.dialog.config(cursor="")
    
    def import_data(self):
        """Import data from CSV file"""
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showwarning("⚠️ Предупреждение", "Выберите CSV файл")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("❌ Ошибка", "Файл не найден")
            return
        
        try:
            # Show progress
            self.dialog.config(cursor="wait")
            self.dialog.update()
            
            skip_duplicates = self.skip_duplicates_var.get()
            result = self.import_service.import_students_from_csv(file_path, skip_duplicates)
            
            # Show results in text widget
            self.results_text.delete(1.0, tk.END)
            
            if result['success']:
                self.results_text.insert(tk.END, f"✅ Импорт завершен успешно!\n\n")
                self.results_text.insert(tk.END, f"Импортировано учеников: {result['imported_count']}\n")
                self.results_text.insert(tk.END, f"Пропущено дубликатов: {result['skipped_count']}\n")
                self.results_text.insert(tk.END, f"Всего строк в файле: {result['total_rows']}\n")
                
                if result['errors']:
                    self.results_text.insert(tk.END, f"\n⚠️ Ошибки ({len(result['errors'])}):\n")
                    for error in result['errors'][:10]:  # Show first 10 errors
                        self.results_text.insert(tk.END, f"• {error}\n")
                    if len(result['errors']) > 10:
                        self.results_text.insert(tk.END, f"... и еще {len(result['errors']) - 10} ошибок\n")
                
                # Show success message
                message = f"Импорт завершен!\n\n"
                message += f"Импортировано: {result['imported_count']}\n"
                message += f"Пропущено: {result['skipped_count']}\n"
                message += f"Ошибок: {len(result['errors'])}"
                
                messagebox.showinfo("✅ Импорт завершен", message)
                
                # Refresh parent if callback provided
                if self.refresh_callback:
                    self.refresh_callback()
                
                # Disable import button after successful import
                self.import_button.config(state=tk.DISABLED)
            else:
                self.results_text.insert(tk.END, f"❌ Ошибка импорта: {result['error']}\n")
                messagebox.showerror("❌ Ошибка импорта", result['error'])
        
        except Exception as e:
            error_msg = f"Ошибка импорта: {str(e)}"
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, error_msg)
            messagebox.showerror("❌ Ошибка", error_msg)
        
        finally:
            self.dialog.config(cursor="")
    
    def download_template(self):
        """Download CSV template"""
        file_path = filedialog.asksaveasfilename(
            title="Сохранить шаблон CSV",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if self.import_service.export_template_to_file(file_path):
                    messagebox.showinfo("✅ Успех", f"Шаблон сохранен в:\n{file_path}")
                else:
                    messagebox.showerror("❌ Ошибка", "Не удалось сохранить шаблон")
            except Exception as e:
                messagebox.showerror("❌ Ошибка", f"Ошибка сохранения шаблона:\n{str(e)}")
    
    def __del__(self):
        """Cleanup when dialog is destroyed"""
        if hasattr(self, 'import_service'):
            self.import_service.close()


def show_csv_import_dialog(parent, refresh_callback=None):
    """Show CSV import dialog"""
    CSVImportDialog(parent, refresh_callback)

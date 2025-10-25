#!/usr/bin/env python3
"""
Alternative CSV Import Dialog with simpler interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.csv_import_service import CSVImportService


def show_simple_csv_import_dialog(parent, refresh_callback=None):
    """Show simplified CSV import dialog"""
    
    # Create dialog window
    dialog = tk.Toplevel(parent)
    dialog.title("📥 Импорт учеников из CSV")
    dialog.geometry("500x400")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
    y = (dialog.winfo_screenheight() // 2) - (400 // 2)
    dialog.geometry(f"500x400+{x}+{y}")
    
    # Main frame
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(main_frame, text="📥 Импорт учеников из CSV", 
                           font=("Arial", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # File selection
    file_frame = ttk.LabelFrame(main_frame, text="📄 Выбор файла", padding="10")
    file_frame.pack(fill=tk.X, pady=(0, 20))
    
    # File path display
    file_path_var = tk.StringVar()
    file_entry = ttk.Entry(file_frame, textvariable=file_path_var, width=50, state="readonly")
    file_entry.pack(fill=tk.X, pady=(0, 10))
    
    # File selection button
    def select_file():
        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл с данными учеников",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            file_path_var.set(file_path)
            file_entry.config(state="normal")
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)
            file_entry.config(state="readonly")
    
    select_button = ttk.Button(file_frame, text="📂 Выбрать CSV файл", 
                              command=select_file)
    select_button.pack(pady=(0, 10))
    
    # Options
    skip_duplicates_var = tk.BooleanVar(value=True)
    skip_check = ttk.Checkbutton(file_frame, text="Пропускать дубликаты", 
                                variable=skip_duplicates_var)
    skip_check.pack(anchor=tk.W)
    
    # Action buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(0, 20))
    
    def validate_and_import():
        file_path = file_path_var.get().strip()
        if not file_path:
            messagebox.showwarning("⚠️ Предупреждение", "Выберите CSV файл")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("❌ Ошибка", "Файл не найден")
            return
        
        try:
            import_service = CSVImportService()
            
            # Validate file
            validation = import_service.validate_csv_format(file_path)
            if not validation['valid']:
                messagebox.showerror("❌ Ошибка валидации", validation['error'])
                import_service.close()
                return
            
            # Import data
            result = import_service.import_students_from_csv(file_path, skip_duplicates_var.get())
            import_service.close()
            
            if result['success']:
                message = f"✅ Импорт завершен!\n\n"
                message += f"Импортировано: {result['imported_count']}\n"
                message += f"Пропущено: {result['skipped_count']}\n"
                message += f"Ошибок: {len(result['errors'])}"
                
                if result['errors']:
                    message += f"\n\nПервые ошибки:\n"
                    for error in result['errors'][:3]:
                        message += f"• {error}\n"
                
                messagebox.showinfo("✅ Успех", message)
                
                # Refresh parent if callback provided
                if refresh_callback:
                    refresh_callback()
                
                dialog.destroy()
            else:
                messagebox.showerror("❌ Ошибка импорта", result['error'])
        
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка импорта: {str(e)}")
    
    import_button = ttk.Button(button_frame, text="📥 Импортировать", 
                              command=validate_and_import)
    import_button.pack(side=tk.LEFT, padx=(0, 10))
    
    def download_template():
        file_path = filedialog.asksaveasfilename(
            title="Сохранить шаблон CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                import_service = CSVImportService()
                if import_service.export_template_to_file(file_path):
                    messagebox.showinfo("✅ Успех", f"Шаблон сохранен в:\n{file_path}")
                else:
                    messagebox.showerror("❌ Ошибка", "Не удалось сохранить шаблон")
                import_service.close()
            except Exception as e:
                messagebox.showerror("❌ Ошибка", f"Ошибка сохранения: {str(e)}")
    
    template_button = ttk.Button(button_frame, text="📋 Скачать шаблон", 
                                command=download_template)
    template_button.pack(side=tk.LEFT)
    
    # Close button
    close_button = ttk.Button(main_frame, text="❌ Закрыть", command=dialog.destroy)
    close_button.pack(pady=(20, 0))
    
    # Help text
    help_text = """
Формат CSV файла:
• Обязательные колонки: first_name, last_name, phone
• Опциональные: telegram_id, email, current_belt, notes
• Разделитель: запятая (,)
• Кодировка: UTF-8
    """
    
    help_label = ttk.Label(main_frame, text=help_text.strip(), justify=tk.LEFT)
    help_label.pack(anchor=tk.W, pady=(20, 0))

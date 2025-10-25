#!/usr/bin/env python3
"""
Export/Import Dialog for BJJ CRM System
Handles CSV export and Google Drive import
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import sys
import webbrowser

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.csv_export_service import CSVExportService
from app.services.google_drive_service import GoogleDriveService


class ExportImportDialog:
    """Dialog for managing data export and import"""
    
    def __init__(self, parent):
        self.parent = parent
        self.csv_service = CSVExportService()
        self.google_service = GoogleDriveService()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📊 Экспорт/Импорт данных")
        self.dialog.geometry("900x700")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"900x700+{x}+{y}")
        
        self.create_widgets()
        self.refresh_export_list()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📊 Экспорт/Импорт данных", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Export tab
        export_frame = ttk.Frame(notebook, padding="10")
        notebook.add(export_frame, text="📤 Экспорт в CSV")
        self.create_export_tab(export_frame)
        
        # Import tab
        import_frame = ttk.Frame(notebook, padding="10")
        notebook.add(import_frame, text="📥 Импорт данных")
        self.create_import_tab(import_frame)
        
        # Close button
        close_button = ttk.Button(main_frame, text="❌ Закрыть", command=self.dialog.destroy)
        close_button.pack(pady=(20, 0))
    
    def create_export_tab(self, parent):
        """Create export tab"""
        # Export options frame
        options_frame = ttk.LabelFrame(parent, text="📋 Выберите данные для экспорта", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Export type selection
        self.export_type_var = tk.StringVar(value="all")
        
        ttk.Radiobutton(options_frame, text="📊 Все данные", variable=self.export_type_var, 
                       value="all").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(options_frame, text="👥 Только ученики", variable=self.export_type_var, 
                       value="students").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(options_frame, text="🥋 Только тренировки", variable=self.export_type_var, 
                       value="trainings").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(options_frame, text="📝 Только посещаемость", variable=self.export_type_var, 
                       value="attendance").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(options_frame, text="💰 Только платежи", variable=self.export_type_var, 
                       value="payments").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(options_frame, text="📈 Сводный отчет", variable=self.export_type_var, 
                       value="summary").pack(anchor=tk.W, pady=2)
        
        # Export button
        export_button = ttk.Button(options_frame, text="🚀 Экспортировать", 
                                 command=self.export_data)
        export_button.pack(pady=(10, 0))
        
        # Export list frame
        list_frame = ttk.LabelFrame(parent, text="📁 Экспортированные файлы", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Export list treeview
        columns = ("filename", "size", "created", "modified")
        self.export_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.export_tree.heading("filename", text="Имя файла")
        self.export_tree.heading("size", text="Размер")
        self.export_tree.heading("created", text="Создан")
        self.export_tree.heading("modified", text="Изменен")
        
        self.export_tree.column("filename", width=300)
        self.export_tree.column("size", width=100)
        self.export_tree.column("created", width=150)
        self.export_tree.column("modified", width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.export_tree.yview)
        self.export_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.export_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Export actions frame
        actions_frame = ttk.Frame(list_frame)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Action buttons
        open_button = ttk.Button(actions_frame, text="📂 Открыть папку", 
                                command=self.open_export_folder)
        open_button.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_button = ttk.Button(actions_frame, text="🔄 Обновить", 
                                  command=self.refresh_export_list)
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_button = ttk.Button(actions_frame, text="🗑️ Удалить выбранный", 
                                 command=self.delete_export_file)
        delete_button.pack(side=tk.LEFT)
    
    def create_import_tab(self, parent):
        """Create import tab"""
        # Import method selection
        method_frame = ttk.LabelFrame(parent, text="📁 Способ импорта", padding="10")
        method_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.import_method_var = tk.StringVar(value="file")
        
        ttk.Radiobutton(method_frame, text="📄 Локальный CSV файл", 
                       variable=self.import_method_var, value="file",
                       command=self.toggle_import_method).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(method_frame, text="🌐 Google Sheets URL", 
                       variable=self.import_method_var, value="url",
                       command=self.toggle_import_method).pack(anchor=tk.W, pady=2)
        
        # File selection frame
        self.file_frame = ttk.LabelFrame(parent, text="📄 Выбор CSV файла", padding="10")
        self.file_frame.pack(fill=tk.X, pady=(0, 20))
        
        file_select_frame = ttk.Frame(self.file_frame)
        file_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=60)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(file_select_frame, text="📂 Выбрать файл", 
                  command=self.select_csv_file).pack(side=tk.RIGHT)
        
        # Google Sheets URL frame
        self.url_frame = ttk.LabelFrame(parent, text="🔗 URL Google Sheets", padding="10")
        
        # URL entry
        ttk.Label(self.url_frame, text="URL CSV файла:").pack(anchor=tk.W)
        self.url_entry = ttk.Entry(self.url_frame, width=80)
        self.url_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Data type selection
        data_type_frame = ttk.LabelFrame(parent, text="📋 Тип данных", padding="10")
        data_type_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.import_type_var = tk.StringVar(value="students")
        
        type_frame = ttk.Frame(data_type_frame)
        type_frame.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Radiobutton(type_frame, text="👥 Ученики", variable=self.import_type_var, 
                       value="students").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(type_frame, text="🥋 Тренировки", variable=self.import_type_var, 
                       value="trainings").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(type_frame, text="💰 Платежи", variable=self.import_type_var, 
                       value="payments").pack(side=tk.LEFT)
        
        # Import buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        validate_button = ttk.Button(buttons_frame, text="✅ Проверить формат", 
                                   command=self.validate_import)
        validate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        import_button = ttk.Button(buttons_frame, text="📥 Импортировать", 
                                 command=self.import_data)
        import_button.pack(side=tk.LEFT)
        
        # Help frame
        help_frame = ttk.LabelFrame(parent, text="❓ Помощь", padding="10")
        help_frame.pack(fill=tk.X, pady=(0, 20))
        
        help_text = """
Для импорта данных из Google Sheets:

1. Откройте Google Sheets с вашими данными
2. Скопируйте URL документа
3. Вставьте URL в поле выше
4. Выберите тип данных
5. Нажмите "Проверить формат"
6. Если формат корректен, нажмите "Импортировать"

Формат CSV должен содержать заголовки в первой строке.
        """
        
        help_label = ttk.Label(help_frame, text=help_text.strip(), justify=tk.LEFT)
        help_label.pack(anchor=tk.W)
        
        # Example URLs frame
        example_frame = ttk.LabelFrame(parent, text="📝 Примеры URL", padding="10")
        example_frame.pack(fill=tk.X)
        
        example_text = """
Примеры URL для Google Sheets:
• https://docs.google.com/spreadsheets/d/1ABC123DEF456GHI789JKL/edit#gid=0
• https://docs.google.com/spreadsheets/d/1ABC123DEF456GHI789JKL/export?format=csv&gid=0
        """
        
        example_label = ttk.Label(example_frame, text=example_text.strip(), justify=tk.LEFT)
        example_label.pack(anchor=tk.W)
    
    def export_data(self):
        """Export data to CSV"""
        try:
            export_type = self.export_type_var.get()
            
            # Show progress
            self.dialog.config(cursor="wait")
            self.dialog.update()
            
            if export_type == "all":
                exports = self.csv_service.export_all_data()
                messagebox.showinfo(
                    "✅ Успех", 
                    f"Все данные экспортированы!\n\n"
                    f"Создано файлов: {len(exports)}\n"
                    f"Папка: {self.csv_service.export_dir}"
                )
            elif export_type == "students":
                filepath = self.csv_service.export_students()
                messagebox.showinfo("✅ Успех", f"Ученики экспортированы в:\n{filepath}")
            elif export_type == "trainings":
                filepath = self.csv_service.export_trainings()
                messagebox.showinfo("✅ Успех", f"Тренировки экспортированы в:\n{filepath}")
            elif export_type == "attendance":
                filepath = self.csv_service.export_attendance()
                messagebox.showinfo("✅ Успех", f"Посещаемость экспортирована в:\n{filepath}")
            elif export_type == "payments":
                filepath = self.csv_service.export_payments()
                messagebox.showinfo("✅ Успех", f"Платежи экспортированы в:\n{filepath}")
            elif export_type == "summary":
                filepath = self.csv_service.export_summary_report()
                messagebox.showinfo("✅ Успех", f"Сводный отчет экспортирован в:\n{filepath}")
            
            # Refresh list
            self.refresh_export_list()
            
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка экспорта:\n{str(e)}")
        
        finally:
            self.dialog.config(cursor="")
    
    def refresh_export_list(self):
        """Refresh the export list"""
        try:
            # Clear existing items
            for item in self.export_tree.get_children():
                self.export_tree.delete(item)
            
            # Get exports
            exports = self.csv_service.get_export_list()
            
            # Add exports to treeview
            for export in exports:
                formatted_created = export['created'].strftime("%d.%m.%Y %H:%M")
                formatted_modified = export['modified'].strftime("%d.%m.%Y %H:%M")
                formatted_size = self.csv_service.format_size(export['size'])
                
                self.export_tree.insert("", tk.END, values=(
                    export['filename'], 
                    formatted_size, 
                    formatted_created, 
                    formatted_modified
                ))
            
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка получения списка экспортов:\n{str(e)}")
    
    def open_export_folder(self):
        """Open export folder in file manager"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self.csv_service.export_dir)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{self.csv_service.export_dir}"')
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Не удалось открыть папку:\n{str(e)}")
    
    def delete_export_file(self):
        """Delete selected export file"""
        selection = self.export_tree.selection()
        if not selection:
            messagebox.showwarning("⚠️ Предупреждение", "Выберите файл для удаления")
            return
        
        item = self.export_tree.item(selection[0])
        filename = item['values'][0]
        
        result = messagebox.askyesno(
            "⚠️ Подтверждение", 
            f"Удалить файл {filename}?\n\nЭто действие нельзя отменить!"
        )
        
        if not result:
            return
        
        try:
            filepath = os.path.join(self.csv_service.export_dir, filename)
            os.remove(filepath)
            messagebox.showinfo("✅ Успех", "Файл удален успешно!")
            self.refresh_export_list()
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка удаления файла:\n{str(e)}")
    
    def validate_import(self):
        """Validate import format"""
        try:
            # Show progress
            self.dialog.config(cursor="wait")
            self.dialog.update()
            
            data_type = self.import_type_var.get()
            
            if self.import_method_var.get() == "file":
                # Validate local file
                file_path = self.file_path_var.get().strip()
                if not file_path:
                    messagebox.showwarning("⚠️ Предупреждение", "Выберите CSV файл")
                    return
                
                validation = self.google_service.validate_csv_file(file_path, data_type)
            else:
                # Validate URL
                url = self.url_entry.get().strip()
                if not url:
                    messagebox.showwarning("⚠️ Предупреждение", "Введите URL файла")
                    return
                
                validation = self.google_service.validate_csv_format(url, data_type)
            
            if validation['valid']:
                encoding_info = f"\nКодировка: {validation.get('encoding', 'неизвестно')}" if 'encoding' in validation else ""
                messagebox.showinfo(
                    "✅ Формат корректен", 
                    f"Файл готов к импорту!\n\n"
                    f"Заголовки: {', '.join(validation['headers'])}\n"
                    f"Строк данных: {validation['row_count']}{encoding_info}"
                )
            else:
                messagebox.showerror(
                    "❌ Ошибка формата", 
                    f"Файл не подходит для импорта:\n\n{validation['error']}"
                )
        
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка проверки формата:\n{str(e)}")
        
        finally:
            self.dialog.config(cursor="")
    
    def import_data(self):
        """Import data from file or URL"""
        try:
            # Show progress
            self.dialog.config(cursor="wait")
            self.dialog.update()
            
            data_type = self.import_type_var.get()
            
            if self.import_method_var.get() == "file":
                # Import from local file
                file_path = self.file_path_var.get().strip()
                if not file_path:
                    messagebox.showwarning("⚠️ Предупреждение", "Выберите CSV файл")
                    return
                
                result = self.google_service.import_from_csv_file(file_path, data_type)
            else:
                # Import from URL
                url = self.url_entry.get().strip()
                if not url:
                    messagebox.showwarning("⚠️ Предупреждение", "Введите URL файла")
                    return
                
                result = self.google_service.import_from_csv_url(url, data_type)
            
            if result['success']:
                message = f"Данные импортированы успешно!\n\n"
                message += f"Импортировано записей: {result['imported_count']}\n"
                if 'updated_count' in result and result['updated_count'] > 0:
                    message += f"Обновлено записей: {result['updated_count']}\n"
                message += f"Ошибок: {len(result['errors'])}"
                
                messagebox.showinfo("✅ Импорт завершен", message)
            else:
                error_text = f"Импортировано записей: {result['imported_count']}\n"
                error_text += f"Ошибок: {len(result['errors'])}\n\n"
                error_text += "Ошибки:\n" + "\n".join(result['errors'][:5])
                if len(result['errors']) > 5:
                    error_text += f"\n... и еще {len(result['errors']) - 5} ошибок"
                
                messagebox.showwarning("⚠️ Импорт с ошибками", error_text)
        
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка импорта:\n{str(e)}")
        
        finally:
            self.dialog.config(cursor="")
    
    def toggle_import_method(self):
        """Toggle between file and URL import methods"""
        if self.import_method_var.get() == "file":
            self.file_frame.pack(fill=tk.X, pady=(0, 20))
            self.url_frame.pack_forget()
        else:
            self.file_frame.pack_forget()
            self.url_frame.pack(fill=tk.X, pady=(0, 20))
    
    def select_csv_file(self):
        """Select CSV file for import"""
        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)


def show_export_import_dialog(parent):
    """Show export/import dialog"""
    ExportImportDialog(parent)

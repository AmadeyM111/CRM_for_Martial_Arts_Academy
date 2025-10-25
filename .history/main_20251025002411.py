#!/usr/bin/env python3
"""
BJJ CRM System - Main Application
Desktop application for Brazilian Jiu-Jitsu academy management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import create_tables, SessionLocal
from app.services.backup_service import BackupService
from app.services.clipboard_service import ClipboardService, create_context_menu
from app.views.backup_dialog import BackupDialog
from app.views.export_import_dialog import show_export_import_dialog
from app.controllers import StudentController, TrainingController, PaymentController
from app.models import Student, Trainer, Training, Attendance, Payment


class DataManager:
    """Centralized data management for the application"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.student_controller = StudentController(self.db)
        self.training_controller = TrainingController(self.db)
        self.payment_controller = PaymentController(self.db)
    
    def close(self):
        """Close database session"""
        self.db.close()
    
    def load_students_data(self):
        """Load students from database"""
        try:
            students = self.student_controller.get_all_students()
            return [(s.id, s.first_name, s.last_name, s.phone, 
                    s.telegram_id or "", s.current_belt, 
                    s.registration_date.strftime("%Y-%m-%d") if s.registration_date else "") 
                    for s in students]
        except Exception as e:
            print(f"Error loading students: {e}")
            return []
    
    def load_trainings_data(self):
        """Load trainings from database"""
        try:
            trainings = self.training_controller.get_all_trainings()
            return [(t.id, t.date.strftime("%Y-%m-%d"), 
                    f"{t.trainer.first_name} {t.trainer.last_name}" if t.trainer else "Unknown",
                    len(t.attendances), t.notes or "") 
                    for t in trainings]
        except Exception as e:
            print(f"Error loading trainings: {e}")
            return []
    
    def load_payments_data(self):
        """Load payments from database"""
        try:
            payments = self.db.query(Payment).join(Student).all()
            return [(p.id, f"{p.student.first_name} {p.student.last_name}", 
                    p.amount, p.payment_type, 
                    p.payment_date.strftime("%Y-%m-%d") if p.payment_date else "",
                    p.description or "") 
                    for p in payments]
        except Exception as e:
            print(f"Error loading payments: {e}")
            return []


def create_main_interface(root):
    """Create main interface"""
    # Create data manager and clipboard service
    data_manager = DataManager()
    clipboard_service = ClipboardService(root)
    
    # Global variable to track active treeview
    active_treeview = None
    
    def set_active_treeview(treeview):
        """Set active treeview for clipboard operations"""
        nonlocal active_treeview
        active_treeview = treeview
    
    # Create menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Файл", menu=file_menu)
    
    def quick_backup():
        """Create quick backup"""
        try:
            backup_service = BackupService()
            backup_path = backup_service.create_backup(include_files=False)
            messagebox.showinfo("✅ Успех", f"Быстрый бэкап создан:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка создания бэкапа: {e}")
    
    def open_backup_manager():
        """Open backup management dialog"""
        try:
            BackupDialog(root)
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка открытия диалога бэкапов: {e}")
    
    def open_export_import():
        """Open export/import dialog"""
        try:
            from app.views.export_import_dialog import show_export_import_dialog
            show_export_import_dialog(root)
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка открытия диалога экспорта/импорта: {e}")
    
    file_menu.add_command(label="💾 Быстрый бэкап", command=quick_backup)
    file_menu.add_command(label="🔧 Управление бэкапами", command=open_backup_manager)
    file_menu.add_separator()
    file_menu.add_command(label="📊 Экспорт/Импорт данных", command=open_export_import)
    file_menu.add_separator()
    file_menu.add_command(label="❌ Выход", command=root.quit)
    
    # Edit menu
    edit_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Правка", menu=edit_menu)
    
    def copy_to_clipboard():
        """Copy current selection to clipboard"""
        try:
            if active_treeview:
                clipboard_service.copy_table_to_clipboard(active_treeview, include_headers=False)
                messagebox.showinfo("✅ Успех", "Данные скопированы в буфер обмена!")
            else:
                messagebox.showwarning("⚠️ Предупреждение", "Выберите таблицу для копирования")
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка копирования: {e}")
    
    def paste_from_clipboard():
        """Paste from clipboard"""
        try:
            if active_treeview:
                clipboard_service.paste_from_clipboard_to_table(active_treeview)
                messagebox.showinfo("✅ Успех", "Данные вставлены из буфера обмена!")
            else:
                messagebox.showwarning("⚠️ Предупреждение", "Выберите таблицу для вставки")
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка вставки: {e}")
    
    def clear_clipboard():
        """Clear clipboard"""
        clipboard_service.clear_clipboard()
        messagebox.showinfo("✅ Успех", "Буфер обмена очищен!")
    
    edit_menu.add_command(label="📋 Копировать", command=copy_to_clipboard)
    edit_menu.add_command(label="📥 Вставить", command=paste_from_clipboard)
    edit_menu.add_separator()
    edit_menu.add_command(label="🗑️ Очистить буфер", command=clear_clipboard)
    
    def select_all_items():
        """Select all items in active treeview"""
        if active_treeview:
            all_items = active_treeview.get_children()
            active_treeview.selection_set(all_items)
            messagebox.showinfo("✅ Успех", f"Выделено {len(all_items)} элементов")
        else:
            messagebox.showwarning("⚠️ Предупреждение", "Выберите таблицу для выделения")
    
    # Note: Global shortcuts removed - using local shortcuts on each treeview instead
    
    # Create notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Students tab
    students_frame = ttk.Frame(notebook)
    notebook.add(students_frame, text="Ученики")
    create_students_tab(students_frame, clipboard_service, set_active_treeview, data_manager)
    
    # Trainings tab
    trainings_frame = ttk.Frame(notebook)
    notebook.add(trainings_frame, text="Тренировки")
    create_trainings_tab(trainings_frame, clipboard_service, set_active_treeview, data_manager)
    
    # Payments tab
    payments_frame = ttk.Frame(notebook)
    notebook.add(payments_frame, text="Платежи")
    create_payments_tab(payments_frame, clipboard_service, set_active_treeview, data_manager)
    
    # Reports tab
    reports_frame = ttk.Frame(notebook)
    notebook.add(reports_frame, text="Отчеты")
    create_reports_tab(reports_frame, clipboard_service, set_active_treeview, data_manager)
    
    # Settings tab
    settings_frame = ttk.Frame(notebook)
    notebook.add(settings_frame, text="Настройки")
    create_settings_tab(settings_frame)


def create_students_tab(parent, clipboard_service, set_active_treeview, data_manager):
    """Create students management tab"""
    # Search frame
    search_frame = ttk.LabelFrame(parent, text="Поиск и фильтры")
    search_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    ttk.Label(search_frame, text="Пояс:").pack(side=tk.LEFT, padx=5)
    belt_combo = ttk.Combobox(search_frame, values=["Все", "White", "Blue", "Purple", "Brown", "Black"])
    belt_combo.pack(side=tk.LEFT, padx=5)
    belt_combo.set("Все")
    
    # Filter button
    filter_btn = ttk.Button(search_frame, text="🔍 Фильтровать")
    filter_btn.pack(side=tk.LEFT, padx=5)
    
    # Clear filter button
    clear_btn = ttk.Button(search_frame, text="🗑️ Очистить")
    clear_btn.pack(side=tk.LEFT, padx=5)
    
    # Students table
    table_frame = ttk.Frame(parent)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Create treeview for students with multiple selection
    columns = ("ID", "Имя", "Фамилия", "Телефон", "Telegram", "Пояс", "Дата регистрации")
    students_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, selectmode='extended')
    
    # Configure columns with sorting
    def sort_column(col, reverse=False):
        """Sort treeview by column"""
        data = [(students_tree.set(child, col), child) for child in students_tree.get_children('')]
        data.sort(reverse=reverse)
        
        # Rearrange items in sorted positions
        for index, (val, child) in enumerate(data):
            students_tree.move(child, '', index)
        
        # Reverse sort next time
        students_tree.heading(col, command=lambda: sort_column(col, not reverse))
    
    for col in columns:
        students_tree.heading(col, text=col, command=lambda c=col: sort_column(c))
        students_tree.column(col, width=120)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=students_tree.yview)
    students_tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack treeview and scrollbar
    students_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Add context menu for clipboard operations
    create_context_menu(parent, students_tree, clipboard_service)
    
    # Add focus tracking for clipboard operations
    def on_treeview_focus(event):
        set_active_treeview(students_tree)
    
    students_tree.bind('<FocusIn>', on_treeview_focus)
    students_tree.bind('<Button-1>', lambda e: set_active_treeview(students_tree))
    
    # Enable cell editing
    def start_edit(event):
        """Start editing cell on double-click"""
        item = students_tree.selection()[0] if students_tree.selection() else None
        if item:
            column = students_tree.identify_column(event.x)
            if column:
                # Get column index
                col_index = int(column[1:]) - 1
                if col_index >= 0:  # Skip the tree column
                    edit_cell(item, col_index)
    
    def edit_cell(item, column):
        """Edit a specific cell"""
        # Get current value
        values = list(students_tree.item(item)['values'])
        current_value = values[column] if column < len(values) else ""
        
        # Create entry widget for editing
        bbox = students_tree.bbox(item, column)
        if bbox:
            edit_entry = tk.Entry(students_tree)
            edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
            edit_entry.insert(0, str(current_value))
            edit_entry.select_range(0, tk.END)
            edit_entry.focus()
            
            def save_edit(event=None):
                """Save edited value"""
                new_value = edit_entry.get()
                values[column] = new_value
                students_tree.item(item, values=values)
                
                # Update original_data
                for i, data in enumerate(original_data):
                    if data[0] == values[0]:  # Match by ID
                        original_data[i] = tuple(values)
                        break
                
                edit_entry.destroy()
            
            def cancel_edit(event=None):
                """Cancel editing"""
                edit_entry.destroy()
            
            edit_entry.bind('<Return>', save_edit)
            edit_entry.bind('<Escape>', cancel_edit)
            edit_entry.bind('<FocusOut>', save_edit)
    
    # Bind double-click to start editing
    students_tree.bind('<Double-1>', start_edit)
    
    # Load data from database
    original_data = data_manager.load_students_data()
    
    # Filter functions
    def apply_filter():
        """Apply search and belt filter"""
        search_text = search_entry.get().lower()
        selected_belt = belt_combo.get()
        
        # Clear current items
        for item in students_tree.get_children():
            students_tree.delete(item)
        
        # Filter and add items
        filtered_count = 0
        for item_data in original_data:
            # Check search criteria (name, surname, phone, telegram)
            matches_search = (
                search_text == "" or
                search_text in str(item_data[1]).lower() or  # name
                search_text in str(item_data[2]).lower() or  # surname
                search_text in str(item_data[3]).lower() or  # phone
                search_text in str(item_data[4]).lower()     # telegram
            )
            
            # Check belt filter
            matches_belt = (
                selected_belt == "Все" or
                selected_belt == str(item_data[5])  # belt
            )
            
            if matches_search and matches_belt:
                students_tree.insert('', 'end', values=item_data)
                filtered_count += 1
        
        messagebox.showinfo("🔍 Фильтр", f"Найдено записей: {filtered_count}")
    
    def clear_filter():
        """Clear all filters and show all data"""
        search_entry.delete(0, tk.END)
        belt_combo.set("Все")
        
        # Reload data from database
        nonlocal original_data
        original_data = data_manager.load_students_data()
        
        # Clear and repopulate
        for item in students_tree.get_children():
            students_tree.delete(item)
        
        for item_data in original_data:
            students_tree.insert('', 'end', values=item_data)
        
        messagebox.showinfo("🗑️ Очистка", "Фильтры очищены")
    
    # Bind filter functions
    filter_btn.config(command=apply_filter)
    clear_btn.config(command=clear_filter)
    
    # Bind Enter key to search
    search_entry.bind('<Return>', lambda e: apply_filter())
    
    # Define keyboard shortcut functions
    def copy_students():
        print("DEBUG: copy_students called")  # Debug
        clipboard_service.copy_table_to_clipboard(students_tree, include_headers=False)
        messagebox.showinfo("✅ Успех", "Данные учеников скопированы!")
    
    def paste_students():
        print("DEBUG: paste_students called")  # Debug
        clipboard_service.paste_from_clipboard_to_table(students_tree)
        messagebox.showinfo("✅ Успех", "Данные вставлены в таблицу учеников!")
    
    def select_all_students_shortcut():
        print("DEBUG: select_all_students_shortcut called")  # Debug
        all_items = students_tree.get_children()
        students_tree.selection_set(all_items)
        messagebox.showinfo("✅ Успех", f"Выделено {len(all_items)} учеников")
    
    # Bind keyboard shortcuts to students tree (Mac and Windows/Linux)
    print("DEBUG: Binding keyboard shortcuts to students_tree")  # Debug
    
    # Windows/Linux shortcuts
    students_tree.bind('<Control-c>', lambda e: copy_students(), add=True)
    students_tree.bind('<Control-v>', lambda e: paste_students(), add=True)
    students_tree.bind('<Control-a>', lambda e: select_all_students_shortcut(), add=True)
    
    # Mac shortcuts
    students_tree.bind('<Command-c>', lambda e: copy_students(), add=True)
    students_tree.bind('<Command-v>', lambda e: paste_students(), add=True)
    students_tree.bind('<Command-a>', lambda e: select_all_students_shortcut(), add=True)
    
    # Alternative Mac shortcuts (some systems use different key names)
    students_tree.bind('<Meta-c>', lambda e: copy_students(), add=True)
    students_tree.bind('<Meta-v>', lambda e: paste_students(), add=True)
    students_tree.bind('<Meta-a>', lambda e: select_all_students_shortcut(), add=True)
    
    print("DEBUG: Keyboard shortcuts bound successfully")  # Debug
    
    # Load and display data from database
    for item_data in original_data:
        students_tree.insert("", tk.END, values=item_data)
    
    # Buttons frame
    buttons_frame = ttk.Frame(parent)
    buttons_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Create button handlers
    def add_student():
        show_add_student_dialog(parent, data_manager, refresh_students)
    
    def edit_student():
        selection = students_tree.selection()
        if selection:
            student_data = students_tree.item(selection[0])['values']
            show_edit_student_dialog(parent, student_data, data_manager, refresh_students)
        else:
            messagebox.showwarning("Предупреждение", "Выберите ученика для редактирования")
    
    def delete_student():
        selection = students_tree.selection()
        if selection:
            count = len(selection)
            if count == 1:
                student_data = students_tree.item(selection[0])['values']
                student_name = f"{student_data[1]} {student_data[2]}"
                message = f"Вы уверены, что хотите удалить ученика {student_name}?"
            else:
                message = f"Вы уверены, что хотите удалить {count} учеников?"
            
            if tk.messagebox.askyesno("Подтверждение", message):
                try:
                    # Get IDs of items to delete
                    ids_to_delete = []
                    for item in selection:
                        item_data = students_tree.item(item)['values']
                        ids_to_delete.append(item_data[0])  # ID is first column
                    
                    # Delete from database
                    for student_id in ids_to_delete:
                        data_manager.student_controller.deactivate_student(student_id)
                    
                    # Refresh the display
                    refresh_students()
                    
                    if count == 1:
                        tk.messagebox.showinfo("Успех", "Ученик удален")
                    else:
                        tk.messagebox.showinfo("Успех", f"Удалено {count} учеников")
                except Exception as e:
                    tk.messagebox.showerror("Ошибка", f"Не удалось удалить ученика: {e}")
        else:
            tk.messagebox.showwarning("Предупреждение", "Выберите ученика(ов) для удаления")
    
    def refresh_students():
        """Refresh students data from database"""
        nonlocal original_data
        original_data = data_manager.load_students_data()
        
        # Clear and repopulate treeview
        for item in students_tree.get_children():
            students_tree.delete(item)
        
        for item_data in original_data:
            students_tree.insert("", tk.END, values=item_data)
    
    def view_details():
        selection = students_tree.selection()
        if selection:
            student_data = students_tree.item(selection[0])['values']
            show_student_details(parent, student_data)
        else:
            messagebox.showwarning("Предупреждение", "Выберите ученика для просмотра")
    
    def select_all_students():
        all_items = students_tree.get_children()
        students_tree.selection_set(all_items)
        messagebox.showinfo("✅ Успех", f"Выделено {len(all_items)} учеников")
    
    # Create buttons
    ttk.Button(buttons_frame, text="➕ Добавить ученика", command=add_student).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="✏️ Редактировать", command=edit_student).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="🗑️ Удалить", command=delete_student).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="👁️ Подробности", command=view_details).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="✅ Выделить все", command=select_all_students).pack(side=tk.LEFT, padx=5)


def create_trainings_tab(parent, clipboard_service, set_active_treeview):
    """Create trainings management tab"""
    # Search frame
    search_frame = ttk.LabelFrame(parent, text="Поиск тренировок")
    search_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    # Trainings table
    table_frame = ttk.Frame(parent)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    columns = ("ID", "Дата", "Тренер", "Количество учеников", "Заметки")
    trainings_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, selectmode='extended')
    
    # Configure columns with sorting
    def sort_trainings_column(col, reverse=False):
        """Sort trainings treeview by column"""
        data = [(trainings_tree.set(child, col), child) for child in trainings_tree.get_children('')]
        data.sort(reverse=reverse)
        
        for index, (val, child) in enumerate(data):
            trainings_tree.move(child, '', index)
        
        trainings_tree.heading(col, command=lambda: sort_trainings_column(col, not reverse))
    
    for col in columns:
        trainings_tree.heading(col, text=col, command=lambda c=col: sort_trainings_column(c))
        trainings_tree.column(col, width=150)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=trainings_tree.yview)
    trainings_tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack treeview and scrollbar
    trainings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Add context menu for clipboard operations
    create_context_menu(parent, trainings_tree, clipboard_service)
    
    # Add focus tracking for clipboard operations
    def on_treeview_focus(event):
        set_active_treeview(trainings_tree)
    
    trainings_tree.bind('<FocusIn>', on_treeview_focus)
    trainings_tree.bind('<Button-1>', lambda e: set_active_treeview(trainings_tree))
    
    # Define keyboard shortcut functions
    def copy_trainings():
        clipboard_service.copy_table_to_clipboard(trainings_tree, include_headers=False)
        messagebox.showinfo("✅ Успех", "Данные тренировок скопированы!")
    
    def paste_trainings():
        clipboard_service.paste_from_clipboard_to_table(trainings_tree)
        messagebox.showinfo("✅ Успех", "Данные вставлены в таблицу тренировок!")
    
    def select_all_trainings_shortcut():
        all_items = trainings_tree.get_children()
        trainings_tree.selection_set(all_items)
        messagebox.showinfo("✅ Успех", f"Выделено {len(all_items)} тренировок")
    
    # Bind keyboard shortcuts to trainings tree (Mac and Windows/Linux)
    trainings_tree.bind('<Control-c>', lambda e: copy_trainings(), add=True)
    trainings_tree.bind('<Control-v>', lambda e: paste_trainings(), add=True)
    trainings_tree.bind('<Control-a>', lambda e: select_all_trainings_shortcut(), add=True)
    # Mac shortcuts
    trainings_tree.bind('<Command-c>', lambda e: copy_trainings(), add=True)
    trainings_tree.bind('<Command-v>', lambda e: paste_trainings(), add=True)
    trainings_tree.bind('<Command-a>', lambda e: select_all_trainings_shortcut(), add=True)
    
    # Clear existing data and add sample data
    for item in trainings_tree.get_children():
        trainings_tree.delete(item)
    
    sample_trainings = [
        (1, "2024-01-15", "Иван Петров", 8, "Обычная тренировка"),
        (2, "2024-01-17", "Иван Петров", 6, "Замена тренера"),
        (3, "2024-01-19", "Петр Сидоров", 7, "Специальная программа"),
        (4, "2024-01-22", "Иван Петров", 9, "Подготовка к соревнованиям"),
        (5, "2024-01-24", "Иван Петров", 5, "Индивидуальные занятия")
    ]
    
    for training in sample_trainings:
        trainings_tree.insert("", tk.END, values=training)
    
    # Buttons frame
    buttons_frame = ttk.Frame(parent)
    buttons_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def add_training():
        messagebox.showinfo("Информация", "Функция добавления тренировки")
    
    def edit_training():
        messagebox.showinfo("Информация", "Функция редактирования тренировки")
    
    def mark_attendance():
        messagebox.showinfo("Информация", "Функция отметки посещаемости")
    
    def view_attendance():
        messagebox.showinfo("Информация", "Функция просмотра посещаемости")
    
    ttk.Button(buttons_frame, text="➕ Добавить тренировку", command=add_training).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="✏️ Редактировать", command=edit_training).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="✅ Отметить посещаемость", command=mark_attendance).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="👁️ Посещаемость", command=view_attendance).pack(side=tk.LEFT, padx=5)


def create_payments_tab(parent, clipboard_service, set_active_treeview):
    """Create payments management tab"""
    # Search frame
    search_frame = ttk.LabelFrame(parent, text="Поиск платежей")
    search_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    # Payments table
    table_frame = ttk.Frame(parent)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    columns = ("ID", "Ученик", "Сумма", "Тип", "Дата", "Описание")
    payments_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, selectmode='extended')
    
    # Configure columns with sorting
    def sort_payments_column(col, reverse=False):
        """Sort payments treeview by column"""
        data = [(payments_tree.set(child, col), child) for child in payments_tree.get_children('')]
        data.sort(reverse=reverse)
        
        for index, (val, child) in enumerate(data):
            payments_tree.move(child, '', index)
        
        payments_tree.heading(col, command=lambda: sort_payments_column(col, not reverse))
    
    for col in columns:
        payments_tree.heading(col, text=col, command=lambda c=col: sort_payments_column(c))
        payments_tree.column(col, width=120)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=payments_tree.yview)
    payments_tree.configure(yscrollcommand=scrollbar.set)
    
    # Pack treeview and scrollbar
    payments_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Add context menu for clipboard operations
    create_context_menu(parent, payments_tree, clipboard_service)
    
    # Add focus tracking for clipboard operations
    def on_treeview_focus(event):
        set_active_treeview(payments_tree)
    
    payments_tree.bind('<FocusIn>', on_treeview_focus)
    payments_tree.bind('<Button-1>', lambda e: set_active_treeview(payments_tree))
    
    # Define keyboard shortcut functions
    def copy_payments():
        clipboard_service.copy_table_to_clipboard(payments_tree, include_headers=False)
        messagebox.showinfo("✅ Успех", "Данные платежей скопированы!")
    
    def paste_payments():
        clipboard_service.paste_from_clipboard_to_table(payments_tree)
        messagebox.showinfo("✅ Успех", "Данные вставлены в таблицу платежей!")
    
    def select_all_payments_shortcut():
        all_items = payments_tree.get_children()
        payments_tree.selection_set(all_items)
        messagebox.showinfo("✅ Успех", f"Выделено {len(all_items)} платежей")
    
    # Bind keyboard shortcuts to payments tree (Mac and Windows/Linux)
    payments_tree.bind('<Control-c>', lambda e: copy_payments(), add=True)
    payments_tree.bind('<Control-v>', lambda e: paste_payments(), add=True)
    payments_tree.bind('<Control-a>', lambda e: select_all_payments_shortcut(), add=True)
    # Mac shortcuts
    payments_tree.bind('<Command-c>', lambda e: copy_payments(), add=True)
    payments_tree.bind('<Command-v>', lambda e: paste_payments(), add=True)
    payments_tree.bind('<Command-a>', lambda e: select_all_payments_shortcut(), add=True)
    
    # Clear existing data and add sample data
    for item in payments_tree.get_children():
        payments_tree.delete(item)
    
    sample_payments = [
        (1, "Иван Иванов", 8000, "Месячный", "2024-01-01", "Абонемент на январь"),
        (2, "Петр Петров", 1500, "Разовый", "2024-01-05", "Разовое посещение"),
        (3, "Сидор Сидоров", 8000, "Месячный", "2024-01-01", "Абонемент на январь"),
        (4, "Анна Смирнова", 1500, "Разовый", "2024-01-10", "Пробное занятие"),
        (5, "Михаил Козлов", 8000, "Месячный", "2024-01-01", "Абонемент на январь")
    ]
    
    for payment in sample_payments:
        payments_tree.insert("", tk.END, values=payment)
    
    # Buttons frame
    buttons_frame = ttk.Frame(parent)
    buttons_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def add_payment():
        messagebox.showinfo("Информация", "Функция добавления платежа")
    
    def edit_payment():
        messagebox.showinfo("Информация", "Функция редактирования платежа")
    
    def delete_payment():
        messagebox.showinfo("Информация", "Функция удаления платежа")
    
    def generate_report():
        messagebox.showinfo("Информация", "Функция генерации отчета")
    
    ttk.Button(buttons_frame, text="➕ Добавить платеж", command=add_payment).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="✏️ Редактировать", command=edit_payment).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="🗑️ Удалить", command=delete_payment).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="📊 Отчет", command=generate_report).pack(side=tk.LEFT, padx=5)


def create_reports_tab(parent, clipboard_service, set_active_treeview):
    """Create reports tab"""
    # Reports frame
    reports_frame = ttk.LabelFrame(parent, text="Отчеты", padding="10")
    reports_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Report buttons
    buttons_frame = ttk.Frame(reports_frame)
    buttons_frame.pack(fill=tk.X, pady=(0, 20))
    
    def generate_revenue_report():
        messagebox.showinfo("Отчет", "Отчет по доходам")
    
    def generate_attendance_report():
        messagebox.showinfo("Отчет", "Отчет по посещаемости")
    
    def generate_students_report():
        messagebox.showinfo("Отчет", "Отчет по ученикам")
    
    def generate_belt_progress_report():
        messagebox.showinfo("Отчет", "Отчет по прогрессу поясов")
    
    ttk.Button(buttons_frame, text="💰 Доходы", command=generate_revenue_report).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="📊 Посещаемость", command=generate_attendance_report).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="👥 Ученики", command=generate_students_report).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="🥋 Пояса", command=generate_belt_progress_report).pack(side=tk.LEFT, padx=5)
    
    # Statistics frame
    stats_frame = ttk.LabelFrame(reports_frame, text="Общая статистика", padding="10")
    stats_frame.pack(fill=tk.BOTH, expand=True)
    
    stats_text = tk.Text(stats_frame, height=15, wrap=tk.WORD)
    stats_text.pack(fill=tk.BOTH, expand=True)
    
    # Sample statistics
    stats_content = """
📊 ОБЩАЯ СТАТИСТИКА АКАДЕМИИ BJJ

👥 УЧЕНИКИ:
• Всего учеников: 5
• Активных учеников: 5
• Новых за месяц: 2

🥋 ПОЯСА:
• Белый пояс: 2 ученика
• Синий пояс: 2 ученика
• Фиолетовый пояс: 1 ученик

💰 ФИНАНСЫ:
• Доход за месяц: 40,000 руб.
• Средний чек: 8,000 руб.
• Конверсия: 80%

📅 ТРЕНИРОВКИ:
• Проведено тренировок: 5
• Средняя посещаемость: 7 человек
• Загруженность: 70%

📈 ДИНАМИКА:
• Рост учеников: +40% за месяц
• Рост доходов: +25% за месяц
• Удержание: 100%
    """
    
    stats_text.insert(tk.END, stats_content.strip())
    stats_text.config(state=tk.DISABLED)


def create_settings_tab(parent):
    """Create settings tab"""
    # Settings notebook
    settings_notebook = ttk.Notebook(parent)
    settings_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # General settings
    general_frame = ttk.Frame(settings_notebook)
    settings_notebook.add(general_frame, text="Общие настройки")
    
    # Academy info
    academy_frame = ttk.LabelFrame(general_frame, text="Информация об академии", padding="10")
    academy_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(academy_frame, text="Название:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    academy_name_entry = ttk.Entry(academy_frame, width=40)
    academy_name_entry.grid(row=0, column=1, padx=5, pady=5)
    academy_name_entry.insert(0, "JJ University")
    
    ttk.Label(academy_frame, text="Адрес:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    academy_address_entry = ttk.Entry(academy_frame, width=40)
    academy_address_entry.grid(row=1, column=1, padx=5, pady=5)
    academy_address_entry.insert(0, "ул. Примерная, 123")
    
    # Schedule settings
    schedule_frame = ttk.LabelFrame(general_frame, text="Расписание", padding="10")
    schedule_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(schedule_frame, text="Дни недели:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    days_entry = ttk.Entry(schedule_frame, width=40)
    days_entry.grid(row=0, column=1, padx=5, pady=5)
    days_entry.insert(0, "Понедельник, Среда, Пятница")
    
    ttk.Label(schedule_frame, text="Время:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    time_entry = ttk.Entry(schedule_frame, width=40)
    time_entry.grid(row=1, column=1, padx=5, pady=5)
    time_entry.insert(0, "20:30")
    
    # Pricing settings
    pricing_frame = ttk.LabelFrame(general_frame, text="Ценообразование", padding="10")
    pricing_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(pricing_frame, text="Месячный абонемент:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    monthly_price_entry = ttk.Entry(pricing_frame, width=20)
    monthly_price_entry.grid(row=0, column=1, padx=5, pady=5)
    monthly_price_entry.insert(0, "8000")
    
    ttk.Label(pricing_frame, text="Разовое занятие:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    single_price_entry = ttk.Entry(pricing_frame, width=20)
    single_price_entry.grid(row=1, column=1, padx=5, pady=5)
    single_price_entry.insert(0, "1500")
    
    # Telegram settings
    telegram_frame = ttk.Frame(settings_notebook)
    settings_notebook.add(telegram_frame, text="Telegram")
    
    telegram_settings_frame = ttk.LabelFrame(telegram_frame, text="Настройки Telegram", padding="10")
    telegram_settings_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(telegram_settings_frame, text="Bot Token:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    bot_token_entry = ttk.Entry(telegram_settings_frame, width=50)
    bot_token_entry.grid(row=0, column=1, padx=5, pady=5)
    bot_token_entry.insert(0, "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
    
    ttk.Label(telegram_settings_frame, text="Chat ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    chat_id_entry = ttk.Entry(telegram_settings_frame, width=50)
    chat_id_entry.grid(row=1, column=1, padx=5, pady=5)
    chat_id_entry.insert(0, "-1001234567890")
    
    # Notification settings
    notification_frame = ttk.LabelFrame(telegram_frame, text="Уведомления", padding="10")
    notification_frame.pack(fill=tk.X, padx=5, pady=5)
    
    reminder_check = ttk.Checkbutton(notification_frame, text="Напоминания о тренировках")
    reminder_check.pack(anchor=tk.W, padx=5, pady=5)
    
    attendance_check = ttk.Checkbutton(notification_frame, text="Уведомления о пропусках")
    attendance_check.pack(anchor=tk.W, padx=5, pady=5)
    
    # Test Telegram button
    def test_telegram():
        messagebox.showinfo("Telegram", "Тест Telegram бота")
    
    ttk.Button(telegram_frame, text="🧪 Тест Telegram", command=test_telegram).pack(pady=10)
    
    # Database settings
    database_frame = ttk.Frame(settings_notebook)
    settings_notebook.add(database_frame, text="База данных")
    
    database_settings_frame = ttk.LabelFrame(database_frame, text="Настройки базы данных", padding="10")
    database_settings_frame.pack(fill=tk.X, padx=5, pady=5)
    
    ttk.Label(database_settings_frame, text="URL базы данных:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    db_url_entry = ttk.Entry(database_settings_frame, width=50)
    db_url_entry.grid(row=0, column=1, padx=5, pady=5)
    db_url_entry.insert(0, "sqlite:///bjj_crm.db")
    
    # Backup buttons
    backup_frame = ttk.LabelFrame(database_frame, text="Резервное копирование", padding="10")
    backup_frame.pack(fill=tk.X, padx=5, pady=5)
    
    def backup_database():
        try:
            backup_service = BackupService()
            backup_path = backup_service.create_backup(include_files=False)
            messagebox.showinfo("✅ Успех", f"База данных скопирована:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка резервного копирования: {e}")
    
    def restore_database():
        messagebox.showinfo("Информация", "Функция восстановления базы данных")
    
    ttk.Button(backup_frame, text="💾 Создать бэкап", command=backup_database).pack(side=tk.LEFT, padx=5)
    ttk.Button(backup_frame, text="🔄 Восстановить", command=restore_database).pack(side=tk.LEFT, padx=5)
    
    # Save settings button
    def save_settings():
        messagebox.showinfo("Настройки", "Настройки сохранены!")
    
    ttk.Button(database_frame, text="💾 Сохранить настройки", command=save_settings).pack(pady=10)


def show_add_student_dialog(parent, data_manager, refresh_callback):
    """Show add student dialog"""
    dialog = tk.Toplevel(parent)
    dialog.title("Добавить ученика")
    dialog.geometry("400x300")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (300 // 2)
    dialog.geometry(f"400x300+{x}+{y}")
    
    # Form fields
    ttk.Label(dialog, text="Имя:").pack(pady=5)
    name_entry = ttk.Entry(dialog, width=30)
    name_entry.pack(pady=5)
    
    ttk.Label(dialog, text="Фамилия:").pack(pady=5)
    surname_entry = ttk.Entry(dialog, width=30)
    surname_entry.pack(pady=5)
    
    ttk.Label(dialog, text="Телефон:").pack(pady=5)
    phone_entry = ttk.Entry(dialog, width=30)
    phone_entry.pack(pady=5)
    
    ttk.Label(dialog, text="Telegram:").pack(pady=5)
    telegram_entry = ttk.Entry(dialog, width=30)
    telegram_entry.pack(pady=5)
    
    ttk.Label(dialog, text="Пояс:").pack(pady=5)
    belt_combo = ttk.Combobox(dialog, values=["White", "Blue", "Purple", "Brown", "Black"])
    belt_combo.pack(pady=5)
    belt_combo.set("White")
    
    def save_student():
        try:
            # Validate input
            if not name_entry.get().strip():
                messagebox.showerror("Ошибка", "Имя не может быть пустым")
                return
            if not surname_entry.get().strip():
                messagebox.showerror("Ошибка", "Фамилия не может быть пустой")
                return
            if not phone_entry.get().strip():
                messagebox.showerror("Ошибка", "Телефон не может быть пустым")
                return
            
            # Create student in database
            student = data_manager.student_controller.create_student(
                first_name=name_entry.get().strip(),
                last_name=surname_entry.get().strip(),
                phone=phone_entry.get().strip(),
                telegram_id=telegram_entry.get().strip() or None,
                current_belt=belt_combo.get()
            )
            
            messagebox.showinfo("Успех", f"Ученик {student.first_name} {student.last_name} добавлен!")
            refresh_callback()
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить ученика: {e}")
    
    def cancel():
        dialog.destroy()
    
    # Buttons
    button_frame = ttk.Frame(dialog)
    button_frame.pack(pady=20)
    
    ttk.Button(button_frame, text="Сохранить", command=save_student).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Отмена", command=cancel).pack(side=tk.LEFT, padx=10)


def show_edit_student_dialog(parent, student_data, data_manager, refresh_callback):
    """Show edit student dialog"""
    dialog = tk.Toplevel(parent)
    dialog.title("Редактировать ученика")
    dialog.geometry("400x300")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (300 // 2)
    dialog.geometry(f"400x300+{x}+{y}")
    
    # Form fields with current data
    ttk.Label(dialog, text="Имя:").pack(pady=5)
    name_entry = ttk.Entry(dialog, width=30)
    name_entry.pack(pady=5)
    name_entry.insert(0, student_data[1])
    
    ttk.Label(dialog, text="Фамилия:").pack(pady=5)
    surname_entry = ttk.Entry(dialog, width=30)
    surname_entry.pack(pady=5)
    surname_entry.insert(0, student_data[2])
    
    ttk.Label(dialog, text="Телефон:").pack(pady=5)
    phone_entry = ttk.Entry(dialog, width=30)
    phone_entry.pack(pady=5)
    phone_entry.insert(0, student_data[3])
    
    ttk.Label(dialog, text="Telegram:").pack(pady=5)
    telegram_entry = ttk.Entry(dialog, width=30)
    telegram_entry.pack(pady=5)
    telegram_entry.insert(0, student_data[4])
    
    ttk.Label(dialog, text="Пояс:").pack(pady=5)
    belt_combo = ttk.Combobox(dialog, values=["White", "Blue", "Purple", "Brown", "Black"])
    belt_combo.pack(pady=5)
    belt_combo.set(student_data[5])
    
    def save_student():
        try:
            # Validate input
            if not name_entry.get().strip():
                messagebox.showerror("Ошибка", "Имя не может быть пустым")
                return
            if not surname_entry.get().strip():
                messagebox.showerror("Ошибка", "Фамилия не может быть пустой")
                return
            if not phone_entry.get().strip():
                messagebox.showerror("Ошибка", "Телефон не может быть пустым")
                return
            
            # Update student in database
            updated_student = data_manager.student_controller.update_student(
                student_id=student_data[0],
                first_name=name_entry.get().strip(),
                last_name=surname_entry.get().strip(),
                phone=phone_entry.get().strip(),
                telegram_id=telegram_entry.get().strip() or None,
                current_belt=belt_combo.get()
            )
            
            if updated_student:
                messagebox.showinfo("Успех", f"Ученик {updated_student.first_name} {updated_student.last_name} обновлен!")
                refresh_callback()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось найти ученика для обновления")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить ученика: {e}")
    
    def cancel():
        dialog.destroy()
    
    # Buttons
    button_frame = ttk.Frame(dialog)
    button_frame.pack(pady=20)
    
    ttk.Button(button_frame, text="Сохранить", command=save_student).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Отмена", command=cancel).pack(side=tk.LEFT, padx=10)


def show_student_details(parent, student_data):
    """Show student details dialog"""
    dialog = tk.Toplevel(parent)
    dialog.title("Подробности ученика")
    dialog.geometry("500x400")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
    y = (dialog.winfo_screenheight() // 2) - (400 // 2)
    dialog.geometry(f"500x400+{x}+{y}")
    
    # Student info
    info_text = f"""
👤 ИНФОРМАЦИЯ ОБ УЧЕНИКЕ

🆔 ID: {student_data[0]}
👤 Имя: {student_data[1]}
👤 Фамилия: {student_data[2]}
📞 Телефон: {student_data[3]}
💬 Telegram: {student_data[4]}
🥋 Пояс: {student_data[5]}
📅 Дата регистрации: {student_data[6]}

📊 СТАТИСТИКА:
• Посещено тренировок: 15
• Пропущено тренировок: 3
• Последняя тренировка: 2024-01-20
• Статус: Активный

💰 ПЛАТЕЖИ:
• Последний платеж: 8000 руб. (2024-01-01)
• Тип: Месячный абонемент
• Статус: Оплачено
    """
    
    text_widget = tk.Text(dialog, wrap=tk.WORD, padx=20, pady=20)
    text_widget.pack(fill=tk.BOTH, expand=True)
    text_widget.insert(tk.END, info_text.strip())
    text_widget.config(state=tk.DISABLED)
    
    # Close button
    ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack(pady=10)


def main():
    """Main application entry point"""
    # Create main window
    root = tk.Tk()
    root.title("BJJ CRM System - Система управления академией бразильского джиу-джитсу")
    root.geometry("1200x800")
    root.minsize(800, 600)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1200 // 2)
    y = (root.winfo_screenheight() // 2) - (800 // 2)
    root.geometry(f"1200x800+{x}+{y}")
    
    # Create database tables
    try:
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        messagebox.showerror("Ошибка базы данных", f"Не удалось создать таблицы базы данных:\n{e}")
        return
    
    # Create main interface
    create_main_interface(root)
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()

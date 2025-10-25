#!/usr/bin/env python3
"""
Backup Management Dialog for BJJ CRM System
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.backup_service import BackupService


class BackupDialog:
    """Dialog for managing backups"""
    
    def __init__(self, parent):
        self.parent = parent
        self.backup_service = BackupService()
        self.selected_backup = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("💾 Управление резервными копиями")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"800x600+{x}+{y}")
        
        self.create_widgets()
        self.refresh_backup_list()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="💾 Управление резервными копиями", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Create backup section
        create_frame = ttk.LabelFrame(main_frame, text="📦 Создать резервную копию", padding="10")
        create_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Include files checkbox
        self.include_files_var = tk.BooleanVar(value=True)
        include_files_check = ttk.Checkbutton(
            create_frame, 
            text="Включить файлы приложения", 
            variable=self.include_files_var
        )
        include_files_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Create backup button
        create_button = ttk.Button(
            create_frame, 
            text="🔄 Создать резервную копию", 
            command=self.create_backup
        )
        create_button.pack(anchor=tk.W)
        
        # Backup list section
        list_frame = ttk.LabelFrame(main_frame, text="📋 Доступные резервные копии", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Backup list treeview
        columns = ("timestamp", "size", "files", "type", "version")
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.backup_tree.heading("timestamp", text="Дата и время")
        self.backup_tree.heading("size", text="Размер")
        self.backup_tree.heading("files", text="Файлы")
        self.backup_tree.heading("type", text="Тип")
        self.backup_tree.heading("version", text="Версия")
        
        self.backup_tree.column("timestamp", width=180)
        self.backup_tree.column("size", width=100)
        self.backup_tree.column("files", width=80)
        self.backup_tree.column("type", width=100)
        self.backup_tree.column("version", width=80)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.backup_tree.bind("<<TreeviewSelect>>", self.on_backup_select)
        
        # Action buttons frame
        actions_frame = ttk.Frame(list_frame)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Action buttons
        self.restore_button = ttk.Button(
            actions_frame, 
            text="🔄 Восстановить", 
            command=self.restore_backup,
            state=tk.DISABLED
        )
        self.restore_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.delete_button = ttk.Button(
            actions_frame, 
            text="🗑️ Удалить", 
            command=self.delete_backup,
            state=tk.DISABLED
        )
        self.delete_button.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_button = ttk.Button(
            actions_frame, 
            text="🔄 Обновить список", 
            command=self.refresh_backup_list
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cleanup_button = ttk.Button(
            actions_frame, 
            text="🧹 Очистить старые", 
            command=self.cleanup_old_backups
        )
        cleanup_button.pack(side=tk.LEFT)
        
        # Close button
        close_button = ttk.Button(main_frame, text="❌ Закрыть", command=self.dialog.destroy)
        close_button.pack(pady=(20, 0))
    
    def create_backup(self):
        """Create a new backup"""
        try:
            include_files = self.include_files_var.get()
            
            # Show progress
            self.dialog.config(cursor="wait")
            self.dialog.update()
            
            # Create backup
            backup_info = self.backup_service.create_backup(include_files=include_files)
            
            # Show success message
            messagebox.showinfo(
                "✅ Успех", 
                f"Резервная копия создана успешно!\n\n"
                f"Время: {backup_info['timestamp']}\n"
                f"Файлы включены: {'Да' if include_files else 'Нет'}"
            )
            
            # Refresh list
            self.refresh_backup_list()
            
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка создания резервной копии:\n{str(e)}")
        
        finally:
            self.dialog.config(cursor="")
    
    def refresh_backup_list(self):
        """Refresh the backup list"""
        try:
            # Clear existing items
            for item in self.backup_tree.get_children():
                self.backup_tree.delete(item)
            
            # Get backups
            backups = self.backup_service.list_backups()
            
            # Add backups to treeview
            for backup in backups:
                timestamp = backup['timestamp']
                formatted_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%d.%m.%Y %H:%M:%S")
                
                size = self.backup_service.get_backup_size(backup)
                formatted_size = self.backup_service.format_size(size)
                
                files_included = "Да" if backup.get('files_file') else "Нет"
                backup_type = backup.get('backup_type', 'manual')
                app_version = backup.get('app_version', '1.0.0')
                
                self.backup_tree.insert("", tk.END, values=(formatted_time, formatted_size, files_included, backup_type, app_version), tags=(backup,))
            
            # Update status
            status_text = f"Найдено резервных копий: {len(backups)}"
            if hasattr(self, 'status_label'):
                self.status_label.config(text=status_text)
            
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка получения списка резервных копий:\n{str(e)}")
    
    def on_backup_select(self, event):
        """Handle backup selection"""
        selection = self.backup_tree.selection()
        if selection:
            item = self.backup_tree.item(selection[0])
            self.selected_backup = item['tags'][0] if item['tags'] else None
            
            # Enable buttons
            self.restore_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.selected_backup = None
            self.restore_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
    
    def restore_backup(self):
        """Restore selected backup"""
        if not self.selected_backup:
            messagebox.showwarning("⚠️ Предупреждение", "Выберите резервную копию для восстановления")
            return
        
        # Confirm restore
        result = messagebox.askyesno(
            "⚠️ Подтверждение", 
            "Вы уверены, что хотите восстановить эту резервную копию?\n\n"
            "Текущие данные будут заменены!"
        )
        
        if not result:
            return
        
        try:
            # Ask about files restore
            restore_files = False
            if self.selected_backup.get('files_file'):
                restore_files = messagebox.askyesno(
                    "📁 Восстановление файлов", 
                    "Восстановить также файлы приложения?"
                )
            
            # Show progress
            self.dialog.config(cursor="wait")
            self.dialog.update()
            
            # Restore backup
            self.backup_service.restore_backup(self.selected_backup, restore_files=restore_files)
            
            # Show success message
            messagebox.showinfo(
                "✅ Успех", 
                "Резервная копия восстановлена успешно!\n\n"
                "Перезапустите приложение для применения изменений."
            )
            
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка восстановления:\n{str(e)}")
        
        finally:
            self.dialog.config(cursor="")
    
    def delete_backup(self):
        """Delete selected backup"""
        if not self.selected_backup:
            messagebox.showwarning("⚠️ Предупреждение", "Выберите резервную копию для удаления")
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "⚠️ Подтверждение", 
            "Вы уверены, что хотите удалить эту резервную копию?\n\n"
            "Это действие нельзя отменить!"
        )
        
        if not result:
            return
        
        try:
            # Delete backup
            self.backup_service.delete_backup(self.selected_backup)
            
            # Show success message
            messagebox.showinfo("✅ Успех", "Резервная копия удалена успешно!")
            
            # Refresh list
            self.refresh_backup_list()
            
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка удаления:\n{str(e)}")
    
    def cleanup_old_backups(self):
        """Clean up old backups"""
        result = messagebox.askyesno(
            "🧹 Очистка старых копий", 
            "Удалить резервные копии старше 7 дней?\n\n"
            "Это освободит место на диске."
        )
        
        if not result:
            return
        
        try:
            # Cleanup old backups
            deleted_count = self.backup_service.cleanup_old_backups(keep_days=7)
            
            # Show result
            messagebox.showinfo(
                "✅ Очистка завершена", 
                f"Удалено старых резервных копий: {deleted_count}"
            )
            
            # Refresh list
            self.refresh_backup_list()
            
        except Exception as e:
            messagebox.showerror("❌ Ошибка", f"Ошибка очистки:\n{str(e)}")


def show_backup_dialog(parent):
    """Show backup management dialog"""
    BackupDialog(parent)

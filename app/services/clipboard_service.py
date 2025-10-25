#!/usr/bin/env python3
"""
Clipboard Service for BJJ CRM System
Handles copy/paste operations with clipboard
"""

import tkinter as tk
from tkinter import ttk
import csv
import io
from typing import List, Dict, Any, Optional


class ClipboardService:
    """Service for handling clipboard operations"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
    
    def copy_table_to_clipboard(self, treeview: ttk.Treeview, include_headers: bool = True) -> bool:
        """
        Copy table data to clipboard
        
        Args:
            treeview: Treeview widget to copy from
            include_headers: Whether to include column headers
            
        Returns:
            True if successful
        """
        try:
            # Get column headers
            columns = treeview['columns']
            headers = []
            for col in columns:
                header = treeview.heading(col)['text']
                headers.append(header)
            
            # Get selected items or all items
            selection = treeview.selection()
            if selection:
                items = selection
            else:
                items = treeview.get_children()
            
            # Prepare data
            clipboard_data = []
            
            # Add headers if requested
            if include_headers:
                clipboard_data.append('\t'.join(headers))
            
            # Add data rows
            for item in items:
                values = treeview.item(item)['values']
                if values:
                    # Convert all values to strings and join with tabs
                    row_data = '\t'.join(str(value) for value in values)
                    clipboard_data.append(row_data)
            
            # Copy to clipboard
            clipboard_text = '\n'.join(clipboard_data)
            self.root.clipboard_clear()
            self.root.clipboard_append(clipboard_text)
            
            return True
            
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False
    
    def copy_cell_by_column(self, treeview: ttk.Treeview, column_name: str) -> bool:
        """
        Copy specific column value from selected row to clipboard
        
        Args:
            treeview: Treeview widget
            column_name: Name of the column to copy
            
        Returns:
            True if successful
        """
        try:
            selection = treeview.selection()
            if not selection:
                return False
            
            # Get the first selected item
            item = selection[0]
            values = treeview.item(item)['values']
            
            if not values:
                return False
            
            # Find column index by name
            columns = treeview['columns']
            try:
                col_index = columns.index(column_name)
                if 0 <= col_index < len(values):
                    cell_value = str(values[col_index])
                    self.root.clipboard_clear()
                    self.root.clipboard_append(cell_value)
                    return True
            except (ValueError, IndexError):
                pass
            
            return False
            
        except Exception as e:
            print(f"Error copying cell by column: {e}")
            return False
    
    def copy_selected_cell_to_clipboard(self, treeview: ttk.Treeview) -> bool:
        """
        Copy selected cell value to clipboard
        
        Args:
            treeview: Treeview widget
            
        Returns:
            True if successful
        """
        try:
            selection = treeview.selection()
            if not selection:
                return False
            
            # For multiple selection, copy the first selected item's first column
            item = selection[0]
            values = treeview.item(item)['values']
            
            if not values:
                return False
            
            # Try to get the focused column from the treeview
            try:
                # Get the column that was clicked/focused
                columns = treeview['columns']
                if columns:
                    # For now, copy the first column (ID) as it's most commonly needed
                    cell_value = str(values[0])
                    self.root.clipboard_clear()
                    self.root.clipboard_append(cell_value)
                    return True
            except Exception:
                pass
            
            # Fallback: copy first column
            self.root.clipboard_clear()
            self.root.clipboard_append(str(values[0]))
            return True
            
        except Exception as e:
            print(f"Error copying cell to clipboard: {e}")
            return False
    
    def paste_from_clipboard_to_table(self, treeview: ttk.Treeview, 
                                    callback_func: Optional[callable] = None) -> bool:
        """
        Paste data from clipboard to table
        
        Args:
            treeview: Treeview widget to paste to
            callback_func: Function to call with pasted data
            
        Returns:
            True if successful
        """
        try:
            # Get clipboard content
            clipboard_content = self.root.clipboard_get()
            
            # Parse clipboard data
            lines = clipboard_content.strip().split('\n')
            if not lines:
                return False
            
            # Parse as tab-separated values
            parsed_data = []
            for line in lines:
                if line.strip():
                    row_data = line.split('\t')
                    parsed_data.append(row_data)
            
            # Call callback function with parsed data
            if callback_func:
                callback_func(parsed_data)
                return True
            
            # Default behavior: add to treeview with unique IDs
            self._add_rows_with_unique_ids(treeview, parsed_data)
            
            return True
            
        except tk.TclError:
            # Clipboard is empty
            return False
        except Exception as e:
            print(f"Error pasting from clipboard: {e}")
            return False
    
    def _add_rows_with_unique_ids(self, treeview: ttk.Treeview, rows_data: List[List[str]]) -> None:
        """
        Add rows to treeview with unique IDs
        
        Args:
            treeview: Treeview widget
            rows_data: List of row data (each row is a list of values)
        """
        # Get existing IDs to avoid duplicates
        existing_ids = set()
        for child in treeview.get_children():
            values = treeview.item(child)['values']
            if values and len(values) > 0:
                try:
                    existing_ids.add(int(values[0]))
                except (ValueError, IndexError):
                    pass
        
        # Find the next available ID
        next_id = max(existing_ids) + 1 if existing_ids else 1
        
        # Add rows with unique IDs
        for row_data in rows_data:
            if row_data:  # Skip empty rows
                # Generate unique ID for this row
                new_row_data = [str(next_id)] + row_data[1:]  # Replace first column (ID) with unique ID
                treeview.insert('', 'end', values=new_row_data)
                next_id += 1
    
    def copy_csv_to_clipboard(self, data: List[List[str]], headers: Optional[List[str]] = None) -> bool:
        """
        Copy data as CSV to clipboard
        
        Args:
            data: List of rows (each row is a list of values)
            headers: Optional column headers
            
        Returns:
            True if successful
        """
        try:
            # Prepare CSV data
            csv_data = []
            
            # Add headers if provided
            if headers:
                csv_data.append(headers)
            
            # Add data rows
            for row in data:
                csv_data.append(row)
            
            # Convert to CSV string
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(csv_data)
            csv_string = output.getvalue()
            
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(csv_string)
            
            return True
            
        except Exception as e:
            print(f"Error copying CSV to clipboard: {e}")
            return False
    
    def get_clipboard_content(self) -> Optional[str]:
        """
        Get clipboard content as string
        
        Returns:
            Clipboard content or None if empty
        """
        try:
            return self.root.clipboard_get()
        except tk.TclError:
            return None
    
    def clear_clipboard(self) -> bool:
        """
        Clear clipboard content
        
        Returns:
            True if successful
        """
        try:
            self.root.clipboard_clear()
            return True
        except Exception as e:
            print(f"Error clearing clipboard: {e}")
            return False
    
    def copy_text_to_clipboard(self, text: str) -> bool:
        """
        Copy text to clipboard
        
        Args:
            text: Text to copy
            
        Returns:
            True if successful
        """
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            return True
        except Exception as e:
            print(f"Error copying text to clipboard: {e}")
            return False


def create_context_menu(parent, treeview: ttk.Treeview, clipboard_service: ClipboardService):
    """Create context menu for treeview"""
    
    def copy_selection():
        clipboard_service.copy_table_to_clipboard(treeview, include_headers=False)
    
    def copy_cell():
        clipboard_service.copy_selected_cell_to_clipboard(treeview)
    
    def copy_id():
        clipboard_service.copy_cell_by_column(treeview, "ID")
    
    def copy_name():
        clipboard_service.copy_cell_by_column(treeview, "Имя")
    
    def copy_phone():
        clipboard_service.copy_cell_by_column(treeview, "Телефон")
    
    def paste_data():
        clipboard_service.paste_from_clipboard_to_table(treeview)
    
    def select_all():
        treeview.selection_set(treeview.get_children())
    
    # Create context menu
    context_menu = tk.Menu(parent, tearoff=0)
    context_menu.add_command(label="📋 Копировать выделенное", command=copy_selection)
    context_menu.add_separator()
    context_menu.add_command(label="📄 Копировать ячейку (ID)", command=copy_cell)
    context_menu.add_command(label="🆔 Копировать ID", command=copy_id)
    context_menu.add_command(label="👤 Копировать имя", command=copy_name)
    context_menu.add_command(label="📞 Копировать телефон", command=copy_phone)
    context_menu.add_separator()
    context_menu.add_command(label="📥 Вставить", command=paste_data)
    context_menu.add_separator()
    context_menu.add_command(label="✅ Выделить все", command=select_all)
    
    def show_context_menu(event):
        """Show context menu on right click"""
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    # Bind right-click event
    treeview.bind("<Button-3>", show_context_menu)  # Right-click
    
    return context_menu


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    clipboard_service = ClipboardService(root)
    
    # Test copying text
    clipboard_service.copy_text_to_clipboard("Test text")
    print(f"Clipboard content: {clipboard_service.get_clipboard_content()}")
    
    root.destroy()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry, Calendar
import json
import csv
from datetime import datetime, timedelta
import os
import math

class ProjectTaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Project & Task Management System")
        self.root.geometry("1400x950")
        
        # Data storage
        self.projects = {}
        self.tasks = {}
        self.data_file = "project_data.json"
        
        # Load existing data
        self.load_data()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_today_tab()
        self.create_project_tab()
        self.create_task_tab()
        self.create_edit_tab()
        self.create_progress_tab()
        self.create_calendar_filter_tab()
        
        # Auto-save every 30 seconds
        self.auto_save()
    
    def create_project_tab(self):
        """Tab 1: Create/Manage Projects"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Create Project")
        
        # Project Form
        form_frame = ttk.LabelFrame(tab, text="Project Details", padding=20)
        form_frame.pack(fill='x', padx=20, pady=20)
        
        # Project Name
        ttk.Label(form_frame, text="Project Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.project_name = ttk.Entry(form_frame, width=40)
        self.project_name.grid(row=0, column=1, pady=5, padx=10)
        
        # Project ID with manual option
        ttk.Label(form_frame, text="Project ID:").grid(row=1, column=0, sticky='w', pady=5)
        id_frame = ttk.Frame(form_frame)
        id_frame.grid(row=1, column=1, pady=5, padx=10, sticky='w')
        
        self.project_id = ttk.Entry(id_frame, width=15)
        self.project_id.pack(side='left', padx=(0, 10))
        
        self.auto_generate_id = tk.BooleanVar(value=True)
        ttk.Checkbutton(id_frame, text="Auto-generate ID", 
                       variable=self.auto_generate_id,
                       command=self.toggle_project_id).pack(side='left')
        
        self.project_id.config(state='disabled')  # Start disabled
        
        # Project Type
        ttk.Label(form_frame, text="Project Type:").grid(row=2, column=0, sticky='w', pady=5)
        self.project_type = ttk.Combobox(form_frame, width=38, 
                                         values=["Office", "Home", "Personal", "Charity"])
        self.project_type.grid(row=2, column=1, pady=5, padx=10)
        
        # Expected Start Date
        ttk.Label(form_frame, text="Expected Start:").grid(row=3, column=0, sticky='w', pady=5)
        self.project_start = DateEntry(form_frame, width=37, background='darkblue',
                                       foreground='white', borderwidth=2)
        self.project_start.grid(row=3, column=1, pady=5, padx=10)
        
        # Expected End Date
        ttk.Label(form_frame, text="Expected End:").grid(row=4, column=0, sticky='w', pady=5)
        self.project_end = DateEntry(form_frame, width=37, background='darkblue',
                                     foreground='white', borderwidth=2)
        self.project_end.grid(row=4, column=1, pady=5, padx=10)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Create Project", command=self.create_project).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_project_form).pack(side='left', padx=5)
        
        # Projects List
        list_frame = ttk.LabelFrame(tab, text="Existing Projects", padding=20)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview for projects
        columns = ('ID', 'Name', 'Type', 'Start', 'End')
        self.project_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=10)
        
        self.project_tree.heading('#0', text='')
        self.project_tree.column('#0', width=0, stretch=False)
        
        for col in columns:
            self.project_tree.heading(col, text=col)
            self.project_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.project_tree.yview)
        self.project_tree.configure(yscrollcommand=scrollbar.set)
        
        self.project_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons
        btn_frame2 = ttk.Frame(list_frame)
        btn_frame2.pack(pady=10)
        
        ttk.Button(btn_frame2, text="Edit Selected Project", 
                  command=self.edit_project).pack(side='left', padx=5)
        ttk.Button(btn_frame2, text="Delete Selected Project", 
                  command=self.delete_project).pack(side='left', padx=5)
        
        self.refresh_project_list()
    
    def create_task_tab(self):
        """Tab 2: Add Tasks"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Add Tasks")
        
        # Project Selection
        select_frame = ttk.LabelFrame(tab, text="Select Project", padding=10)
        select_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(select_frame, text="Project:").pack(side='left', padx=5)
        self.task_project_select = ttk.Combobox(select_frame, width=50, state='readonly')
        self.task_project_select.pack(side='left', padx=5)
        self.task_project_select.bind('<<ComboboxSelected>>', self.on_project_select_task)
        
        # Task Form
        form_frame = ttk.LabelFrame(tab, text="Task Details", padding=20)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # Task Name
        ttk.Label(form_frame, text="Task Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.task_name = ttk.Entry(form_frame, width=40)
        self.task_name.grid(row=0, column=1, pady=5, padx=10)
        
        # Has Subtasks checkbox
        self.task_has_subtasks = tk.BooleanVar()
        ttk.Checkbutton(form_frame, text="This task has subtasks (don't assign time)", 
                       variable=self.task_has_subtasks,
                       command=self.toggle_time_fields).grid(row=1, column=1, sticky='w', pady=5, padx=10)
        
        # Subtask
        ttk.Label(form_frame, text="Subtask of:").grid(row=2, column=0, sticky='w', pady=5)
        self.task_parent = ttk.Combobox(form_frame, width=38, state='readonly')
        self.task_parent.grid(row=2, column=1, pady=5, padx=10)
        
        # Priority
        ttk.Label(form_frame, text="Priority:").grid(row=3, column=0, sticky='w', pady=5)
        self.task_priority = ttk.Combobox(form_frame, width=38, 
                                          values=["Most Important (Blue)", "Important (Green)", "Average (Red)"])
        self.task_priority.grid(row=3, column=1, pady=5, padx=10)
        self.task_priority.current(2)
        
        # Mandatory
        self.task_mandatory = tk.BooleanVar()
        ttk.Checkbutton(form_frame, text="Mandatory Task", 
                       variable=self.task_mandatory).grid(row=4, column=1, sticky='w', pady=5, padx=10)
        
        # Start Date
        ttk.Label(form_frame, text="Start Date:").grid(row=5, column=0, sticky='w', pady=5)
        self.task_start_date = DateEntry(form_frame, width=37)
        self.task_start_date.grid(row=5, column=1, pady=5, padx=10)
        
        # End Date
        ttk.Label(form_frame, text="End Date:").grid(row=6, column=0, sticky='w', pady=5)
        self.task_end_date = DateEntry(form_frame, width=37)
        self.task_end_date.grid(row=6, column=1, pady=5, padx=10)
        
        # Time In
        self.time_in_label = ttk.Label(form_frame, text="Time In (HH:MM):")
        self.time_in_label.grid(row=7, column=0, sticky='w', pady=5)
        time_in_frame = ttk.Frame(form_frame)
        time_in_frame.grid(row=7, column=1, pady=5, padx=10, sticky='w')
        self.task_hour_in = ttk.Spinbox(time_in_frame, from_=0, to=23, width=5, format="%02.0f")
        self.task_hour_in.set('09')
        self.task_hour_in.pack(side='left')
        ttk.Label(time_in_frame, text=":").pack(side='left', padx=2)
        self.task_min_in = ttk.Spinbox(time_in_frame, from_=0, to=59, width=5, format="%02.0f")
        self.task_min_in.set('00')
        self.task_min_in.pack(side='left')
        
        # Time Out
        self.time_out_label = ttk.Label(form_frame, text="Time Out (HH:MM):")
        self.time_out_label.grid(row=8, column=0, sticky='w', pady=5)
        time_out_frame = ttk.Frame(form_frame)
        time_out_frame.grid(row=8, column=1, pady=5, padx=10, sticky='w')
        self.task_hour_out = ttk.Spinbox(time_out_frame, from_=0, to=23, width=5, format="%02.0f")
        self.task_hour_out.set('17')
        self.task_hour_out.pack(side='left')
        ttk.Label(time_out_frame, text=":").pack(side='left', padx=2)
        self.task_min_out = ttk.Spinbox(time_out_frame, from_=0, to=59, width=5, format="%02.0f")
        self.task_min_out.set('00')
        self.task_min_out.pack(side='left')
        
        # Comments
        ttk.Label(form_frame, text="Comments:").grid(row=9, column=0, sticky='nw', pady=5)
        self.task_comments = tk.Text(form_frame, width=40, height=3)
        self.task_comments.grid(row=9, column=1, pady=5, padx=10)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Add Task", command=self.add_task).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_task_form).pack(side='left', padx=5)
        
        self.update_task_project_list()
    
    def toggle_time_fields(self):
        """Enable/disable time fields based on subtasks checkbox"""
        if self.task_has_subtasks.get():
            # Disable time fields
            self.task_hour_in.config(state='disabled')
            self.task_min_in.config(state='disabled')
            self.task_hour_out.config(state='disabled')
            self.task_min_out.config(state='disabled')
            self.time_in_label.config(foreground='gray')
            self.time_out_label.config(foreground='gray')
        else:
            # Enable time fields
            self.task_hour_in.config(state='normal')
            self.task_min_in.config(state='normal')
            self.task_hour_out.config(state='normal')
            self.task_min_out.config(state='normal')
            self.time_in_label.config(foreground='black')
            self.time_out_label.config(foreground='black')
    
    def create_edit_tab(self):
        """Tab 3: Edit Tasks"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Edit Tasks")
        
        # Project Selection
        select_frame = ttk.LabelFrame(tab, text="Select Project", padding=10)
        select_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(select_frame, text="Project:").pack(side='left', padx=5)
        self.edit_project_select = ttk.Combobox(select_frame, width=50, state='readonly')
        self.edit_project_select.pack(side='left', padx=5)
        self.edit_project_select.bind('<<ComboboxSelected>>', self.on_project_select_edit)
        
        # Tasks List
        list_frame = ttk.LabelFrame(tab, text="Tasks", padding=20)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('Task', 'Priority', 'Mandatory', 'Start', 'End', 'Status')
        self.edit_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=22)
        
        self.edit_tree.heading('#0', text='ID')
        self.edit_tree.column('#0', width=50)
        
        for col in columns:
            self.edit_tree.heading(col, text=col)
            self.edit_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.edit_tree.yview)
        self.edit_tree.configure(yscrollcommand=scrollbar.set)
        
        self.edit_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Edit Selected Task", command=self.edit_task).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Mark Complete", command=self.mark_complete).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Mark Incomplete", command=self.mark_incomplete).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Task", command=self.delete_task).pack(side='left', padx=5)
        
        self.update_edit_project_list()
    
    def create_progress_tab(self):
        """Tab 4: View Progress"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Progress & Filter")
        
        # Filter Frame
        filter_frame = ttk.LabelFrame(tab, text="Filter", padding=10)
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(filter_frame, text="Project:").pack(side='left', padx=5)
        self.progress_project_select = ttk.Combobox(filter_frame, width=40, state='readonly')
        self.progress_project_select.pack(side='left', padx=5)
        
        ttk.Button(filter_frame, text="Show Progress", command=self.show_progress).pack(side='left', padx=10)
        ttk.Button(filter_frame, text="Export to CSV", command=self.export_csv).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Import from CSV", command=self.import_csv).pack(side='left', padx=5)
        
        # Progress Display
        display_frame = ttk.LabelFrame(tab, text="Project Progress", padding=20)
        display_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Progress Info
        self.progress_info = ttk.Label(display_frame, text="Select a project to view progress", 
                                       font=('Arial', 12))
        self.progress_info.pack(pady=10)
        
        # Tasks Tree
        columns = ('Task', 'Priority', 'Mandatory', 'Start', 'End', 'Status')
        self.progress_tree = ttk.Treeview(display_frame, columns=columns, show='tree headings', height=22)
        
        self.progress_tree.heading('#0', text='ID')
        self.progress_tree.column('#0', width=50)
        
        for col in columns:
            self.progress_tree.heading(col, text=col)
            self.progress_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(display_frame, orient='vertical', command=self.progress_tree.yview)
        self.progress_tree.configure(yscrollcommand=scrollbar.set)
        
        self.progress_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.update_progress_project_list()
    
    def create_today_tab(self):
        """Tab 5: Today's Tasks with Analog Clock"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Today's Tasks")
        
        # Top frame for clock and date
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', padx=20, pady=20)
        
        # Clock frame (left side)
        clock_frame = ttk.LabelFrame(top_frame, text="Current Time", padding=10)
        clock_frame.pack(side='left', padx=10)
        
        # Canvas for analog clock
        self.clock_canvas = tk.Canvas(clock_frame, width=200, height=200, bg='white')
        self.clock_canvas.pack()
        
        # Date display (right side)
        date_frame = ttk.LabelFrame(top_frame, text="Today's Date", padding=20)
        date_frame.pack(side='left', padx=10, fill='both', expand=True)
        
        # Messages
        ttk.Label(date_frame, text="Bismillah Hir Rahmanir Rahim", 
                 font=('Arial', 16, 'bold'), foreground='darkgreen').pack(pady=5)
        ttk.Label(date_frame, text="Rabbi jidni Ilma.", 
                 font=('Arial', 14, 'italic'), foreground='blue').pack(pady=2)
        
        self.today_day_label = ttk.Label(date_frame, text="", font=('Arial', 16, 'bold'))
        self.today_day_label.pack(pady=10)
        
        self.today_date_label = ttk.Label(date_frame, text="", font=('Arial', 14))
        self.today_date_label.pack(pady=5)
        
        self.today_month_year_label = ttk.Label(date_frame, text="", font=('Arial', 14))
        self.today_month_year_label.pack(pady=5)
        
        # Refresh button
        ttk.Button(date_frame, text="Refresh Tasks", command=self.refresh_today_tasks).pack(pady=10)
        
        # Tasks display
        tasks_frame = ttk.LabelFrame(tab, text="Tasks & Subtasks for Today", padding=20)
        tasks_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Info label
        self.today_info_label = ttk.Label(tasks_frame, text="", font=('Arial', 11))
        self.today_info_label.pack(pady=5)
        
        # Tasks tree
        columns = ('Project', 'Task', 'Priority', 'Mandatory', 'Time In', 'Time Out', 'Status')
        self.today_tree = ttk.Treeview(tasks_frame, columns=columns, show='tree headings', height=22)
        
        self.today_tree.heading('#0', text='ID')
        self.today_tree.column('#0', width=60)
        
        for col in columns:
            self.today_tree.heading(col, text=col)
            self.today_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tasks_frame, orient='vertical', command=self.today_tree.yview)
        self.today_tree.configure(yscrollcommand=scrollbar.set)
        
        self.today_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Action buttons
        btn_frame = ttk.Frame(tasks_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Mark Task Complete", 
                  command=self.mark_today_complete).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Mark Project Complete", 
                  command=self.mark_project_complete).pack(side='left', padx=5)
        
        # Start clock update
        self.update_clock()
        self.update_today_date()
        self.refresh_today_tasks()
    
    def create_calendar_filter_tab(self):
        """Tab 6: Calendar Filter View"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Calendar Filter")
        
        # Filter frame
        filter_frame = ttk.LabelFrame(tab, text="Filter Options", padding=20)
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        # Calendar
        ttk.Label(filter_frame, text="Select Date:", font=('Arial', 11)).grid(row=0, column=0, sticky='w', pady=5)
        self.filter_calendar = Calendar(filter_frame, selectmode='day', 
                                       date_pattern='yyyy-mm-dd')
        self.filter_calendar.grid(row=1, column=0, rowspan=3, padx=10, pady=5)
        
        # Filter type
        ttk.Label(filter_frame, text="Filter Type:", font=('Arial', 11)).grid(row=0, column=1, sticky='w', padx=20)
        
        self.filter_type = tk.StringVar(value="day")
        ttk.Radiobutton(filter_frame, text="Single Day", variable=self.filter_type, 
                       value="day").grid(row=1, column=1, sticky='w', padx=20)
        ttk.Radiobutton(filter_frame, text="Week", variable=self.filter_type, 
                       value="week").grid(row=2, column=1, sticky='w', padx=20)
        ttk.Radiobutton(filter_frame, text="Month", variable=self.filter_type, 
                       value="month").grid(row=3, column=1, sticky='w', padx=20)
        
        # Apply button
        ttk.Button(filter_frame, text="Apply Filter", command=self.apply_calendar_filter,
                  style='Accent.TButton').grid(row=4, column=0, columnspan=2, pady=20)
        
        # Results frame
        results_frame = ttk.LabelFrame(tab, text="Filtered Tasks", padding=20)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Info label
        self.filter_info_label = ttk.Label(results_frame, text="Select a date and filter type", 
                                          font=('Arial', 11))
        self.filter_info_label.pack(pady=5)
        
        # Tasks tree
        columns = ('Project', 'Task', 'Priority', 'Mandatory', 'Start', 'End', 'Time In', 'Time Out', 'Status')
        self.filter_tree = ttk.Treeview(results_frame, columns=columns, show='tree headings', height=25)
        
        self.filter_tree.heading('#0', text='ID')
        self.filter_tree.column('#0', width=50)
        
        for col in columns:
            self.filter_tree.heading(col, text=col)
            self.filter_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.filter_tree.yview)
        self.filter_tree.configure(yscrollcommand=scrollbar.set)
        
        self.filter_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Action buttons
        btn_frame = ttk.Frame(results_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Mark Complete", 
                  command=self.mark_filter_complete).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Mark Incomplete", 
                  command=self.mark_filter_incomplete).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export Filtered to CSV", 
                  command=self.export_filtered_csv).pack(side='left', padx=5)
    
    # Project Management Functions
    def toggle_project_id(self):
        """Enable/disable manual Project ID entry"""
        if self.auto_generate_id.get():
            self.project_id.config(state='disabled')
            self.project_id.delete(0, tk.END)
        else:
            self.project_id.config(state='normal')
            self.project_id.focus()
    
    def generate_project_id(self):
        """Generate auto-incremented project ID"""
        if not self.projects:
            return "P001"
        
        # Get all existing project IDs
        existing_ids = [pid for pid in self.projects.keys() if pid.startswith('P')]
        if not existing_ids:
            return "P001"
        
        # Extract numbers and find max
        numbers = [int(pid[1:]) for pid in existing_ids if pid[1:].isdigit()]
        if numbers:
            max_num = max(numbers)
            return f"P{max_num + 1:03d}"
        return "P001"
    
    def create_project(self):
        name = self.project_name.get().strip()
        ptype = self.project_type.get()
        start = self.project_start.get_date().strftime('%Y-%m-%d')
        end = self.project_end.get_date().strftime('%Y-%m-%d')
        
        if not name:
            messagebox.showwarning("Warning", "Please enter project name")
            return
        
        # Get or generate project ID
        if self.auto_generate_id.get():
            pid = self.generate_project_id()
        else:
            pid = self.project_id.get().strip()
            if not pid:
                messagebox.showwarning("Warning", "Please enter a Project ID or enable auto-generate")
                return
            
            # Check if manually entered ID already exists
            if pid in self.projects:
                messagebox.showwarning("Warning", f"Project ID '{pid}' already exists. Please use a different ID.")
                return
        
        self.projects[pid] = {
            'name': name,
            'id': pid,
            'type': ptype,
            'start': start,
            'end': end
        }
        
        self.tasks[pid] = {}
        self.save_data()
        self.refresh_project_list()
        self.update_task_project_list()
        self.update_edit_project_list()
        self.update_progress_project_list()
        self.clear_project_form()
        messagebox.showinfo("Success", f"Project created successfully with ID: {pid}")
    
    def edit_project(self):
        """Edit selected project"""
        selected = self.project_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a project to edit")
            return
        
        values = self.project_tree.item(selected[0])['values']
        pid = values[0]
        project = self.projects[pid]
        
        # Create edit window
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edit Project {pid}")
        edit_win.geometry("500x400")
        
        frame = ttk.Frame(edit_win, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Project ID (read-only)
        ttk.Label(frame, text="Project ID:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Label(frame, text=pid, foreground='blue').grid(row=0, column=1, sticky='w', pady=5)
        
        # Project Name
        ttk.Label(frame, text="Project Name:").grid(row=1, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(frame, width=40)
        name_entry.insert(0, project['name'])
        name_entry.grid(row=1, column=1, pady=5)
        
        # Project Type
        ttk.Label(frame, text="Project Type:").grid(row=2, column=0, sticky='w', pady=5)
        type_combo = ttk.Combobox(frame, width=38, 
                                  values=["Office", "Home", "Personal", "Charity"])
        type_combo.set(project['type'])
        type_combo.grid(row=2, column=1, pady=5)
        
        # Start Date
        ttk.Label(frame, text="Expected Start:").grid(row=3, column=0, sticky='w', pady=5)
        start_date = DateEntry(frame, width=37)
        start_date.set_date(datetime.strptime(project['start'], '%Y-%m-%d'))
        start_date.grid(row=3, column=1, pady=5)
        
        # End Date
        ttk.Label(frame, text="Expected End:").grid(row=4, column=0, sticky='w', pady=5)
        end_date = DateEntry(frame, width=37)
        end_date.set_date(datetime.strptime(project['end'], '%Y-%m-%d'))
        end_date.grid(row=4, column=1, pady=5)
        
        def save_project_changes():
            project['name'] = name_entry.get().strip()
            project['type'] = type_combo.get()
            project['start'] = start_date.get_date().strftime('%Y-%m-%d')
            project['end'] = end_date.get_date().strftime('%Y-%m-%d')
            
            self.save_data()
            self.refresh_project_list()
            self.update_task_project_list()
            self.update_edit_project_list()
            self.update_progress_project_list()
            edit_win.destroy()
            messagebox.showinfo("Success", "Project updated successfully!")
        
        ttk.Button(frame, text="Save Changes", command=save_project_changes).grid(row=5, column=0, columnspan=2, pady=20)
    
    def clear_project_form(self):
        self.project_name.delete(0, tk.END)
        self.project_type.set('')
        self.project_id.delete(0, tk.END)
        self.auto_generate_id.set(True)
        self.toggle_project_id()
    
    def refresh_project_list(self):
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        for pid, proj in self.projects.items():
            self.project_tree.insert('', 'end', values=(
                proj['id'], proj['name'], proj['type'], proj['start'], proj['end']
            ))
    
    def delete_project(self):
        selected = self.project_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a project to delete")
            return
        
        values = self.project_tree.item(selected[0])['values']
        pid = values[0]
        
        if messagebox.askyesno("Confirm", f"Delete project '{values[1]}' and all its tasks?"):
            del self.projects[pid]
            del self.tasks[pid]
            self.save_data()
            self.refresh_project_list()
            self.update_task_project_list()
            self.update_edit_project_list()
            self.update_progress_project_list()
    
    # Task Management Functions
    def update_task_project_list(self):
        values = [f"{p['id']} - {p['name']}" for p in self.projects.values()]
        self.task_project_select['values'] = values
        if values:
            self.task_project_select.current(0)
            self.on_project_select_task(None)
    
    def on_project_select_task(self, event):
        selection = self.task_project_select.get()
        if not selection:
            return
        
        pid = selection.split(' - ')[0]
        tasks = self.tasks.get(pid, {})
        
        # Only show parent tasks (tasks without subtasks) in the parent dropdown
        parent_tasks = [(tid, t) for tid, t in tasks.items() if not self.has_subtasks(pid, tid)]
        task_list = ['(None - Main Task)'] + [f"{tid} - {t['name']}" for tid, t in parent_tasks]
        self.task_parent['values'] = task_list
        self.task_parent.current(0)
    
    def has_subtasks(self, pid, task_id):
        """Check if a task has any subtasks"""
        tasks = self.tasks.get(pid, {})
        for t in tasks.values():
            if t.get('parent') == task_id:
                return True
        return False
    
    def add_task(self):
        selection = self.task_project_select.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        pid = selection.split(' - ')[0]
        task_name = self.task_name.get().strip()
        
        if not task_name:
            messagebox.showwarning("Warning", "Please enter task name")
            return
        
        # Generate task ID
        task_count = len(self.tasks[pid])
        tid = f"T{task_count + 1:03d}"
        
        parent = self.task_parent.get()
        parent_id = None if parent.startswith('(None') else parent.split(' - ')[0]
        
        # Get comment text
        comment_text = self.task_comments.get("1.0", "end-1c").strip()
        
        # Determine time values based on has_subtasks
        has_subtasks = self.task_has_subtasks.get()
        if has_subtasks or parent_id:
            # If has subtasks or is a subtask of parent, use parent's time or assign time
            time_in = f"{self.task_hour_in.get()}:{self.task_min_in.get()}" if parent_id else "00:00"
            time_out = f"{self.task_hour_out.get()}:{self.task_min_out.get()}" if parent_id else "00:00"
        else:
            time_in = f"{self.task_hour_in.get()}:{self.task_min_in.get()}"
            time_out = f"{self.task_hour_out.get()}:{self.task_min_out.get()}"
        
        task_data = {
            'name': task_name,
            'parent': parent_id,
            'priority': self.task_priority.get(),
            'mandatory': self.task_mandatory.get(),
            'start_date': self.task_start_date.get_date().strftime('%Y-%m-%d'),
            'end_date': self.task_end_date.get_date().strftime('%Y-%m-%d'),
            'time_in': time_in,
            'time_out': time_out,
            'status': 'Incomplete',
            'comments': comment_text,
            'has_subtasks': has_subtasks
        }
        
        self.tasks[pid][tid] = task_data
        self.save_data()
        self.clear_task_form()
        self.on_project_select_task(None)
        messagebox.showinfo("Success", f"Task {tid} added successfully!")
    
    def clear_task_form(self):
        self.task_name.delete(0, tk.END)
        self.task_priority.current(2)
        self.task_mandatory.set(False)
        self.task_has_subtasks.set(False)
        self.task_hour_in.set('09')
        self.task_min_in.set('00')
        self.task_hour_out.set('17')
        self.task_min_out.set('00')
        self.task_comments.delete("1.0", tk.END)
        self.toggle_time_fields()
    
    # Edit Functions
    def update_edit_project_list(self):
        values = [f"{p['id']} - {p['name']}" for p in self.projects.values()]
        self.edit_project_select['values'] = values
        if values:
            self.edit_project_select.current(0)
            self.on_project_select_edit(None)
    
    def on_project_select_edit(self, event):
        selection = self.edit_project_select.get()
        if not selection:
            return
        
        pid = selection.split(' - ')[0]
        self.display_tasks_tree(pid, self.edit_tree)
    
    def display_tasks_tree(self, pid, tree):
        for item in tree.get_children():
            tree.delete(item)
        
        tasks = self.tasks.get(pid, {})
        
        # Display tasks hierarchically
        main_tasks = {tid: t for tid, t in tasks.items() if not t.get('parent')}
        
        for tid, task in main_tasks.items():
            self.insert_task_tree(tree, '', tid, task, tasks)
    
    def insert_task_tree(self, tree, parent, tid, task, all_tasks):
        priority_color = self.get_priority_color(task['priority'])
        
        item = tree.insert(parent, 'end', text=tid, values=(
            task['name'],
            task['priority'],
            'Yes' if task['mandatory'] else 'No',
            task['start_date'],
            task['end_date'],
            task['status']
        ), tags=(priority_color,))
        
        tree.tag_configure(priority_color, background=priority_color)
        
        # Insert subtasks
        subtasks = {t_id: t for t_id, t in all_tasks.items() if t.get('parent') == tid}
        for sub_id, subtask in subtasks.items():
            self.insert_task_tree(tree, item, sub_id, subtask, all_tasks)
    
    def get_priority_color(self, priority):
        if 'Blue' in priority:
            return 'lightblue'
        elif 'Green' in priority:
            return 'lightgreen'
        else:
            return 'lightcoral'
    
    def edit_task(self):
        selected = self.edit_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to edit")
            return
        
        tid = self.edit_tree.item(selected[0])['text']
        pid = self.edit_project_select.get().split(' - ')[0]
        task = self.tasks[pid][tid]
        
        # Create edit window
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edit Task {tid}")
        edit_win.geometry("600x750")
        
        frame = ttk.Frame(edit_win, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Task Name
        ttk.Label(frame, text="Task Name:").grid(row=0, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(frame, width=40)
        name_entry.insert(0, task['name'])
        name_entry.grid(row=0, column=1, pady=5)
        
        # Priority
        ttk.Label(frame, text="Priority:").grid(row=1, column=0, sticky='w', pady=5)
        priority_combo = ttk.Combobox(frame, width=38, 
                                      values=["Most Important (Blue)", "Important (Green)", "Average (Red)"])
        priority_combo.set(task['priority'])
        priority_combo.grid(row=1, column=1, pady=5)
        
        # Mandatory
        mandatory_var = tk.BooleanVar(value=task['mandatory'])
        ttk.Checkbutton(frame, text="Mandatory Task", variable=mandatory_var).grid(row=2, column=1, sticky='w', pady=5)
        
        # Start Date
        ttk.Label(frame, text="Start Date:").grid(row=3, column=0, sticky='w', pady=5)
        start_date = DateEntry(frame, width=37)
        start_date.set_date(datetime.strptime(task['start_date'], '%Y-%m-%d'))
        start_date.grid(row=3, column=1, pady=5)
        
        # End Date
        ttk.Label(frame, text="End Date:").grid(row=4, column=0, sticky='w', pady=5)
        end_date = DateEntry(frame, width=37)
        end_date.set_date(datetime.strptime(task['end_date'], '%Y-%m-%d'))
        end_date.grid(row=4, column=1, pady=5)
        
        # Time In
        ttk.Label(frame, text="Time In (HH:MM):").grid(row=5, column=0, sticky='w', pady=5)
        time_in_frame = ttk.Frame(frame)
        time_in_frame.grid(row=5, column=1, pady=5, sticky='w')
        hour_in, min_in = task['time_in'].split(':')
        hour_in_spin = ttk.Spinbox(time_in_frame, from_=0, to=23, width=5, format="%02.0f")
        hour_in_spin.set(hour_in)
        hour_in_spin.pack(side='left')
        ttk.Label(time_in_frame, text=":").pack(side='left', padx=2)
        min_in_spin = ttk.Spinbox(time_in_frame, from_=0, to=59, width=5, format="%02.0f")
        min_in_spin.set(min_in)
        min_in_spin.pack(side='left')
        
        # Time Out
        ttk.Label(frame, text="Time Out (HH:MM):").grid(row=6, column=0, sticky='w', pady=5)
        time_out_frame = ttk.Frame(frame)
        time_out_frame.grid(row=6, column=1, pady=5, sticky='w')
        hour_out, min_out = task['time_out'].split(':')
        hour_out_spin = ttk.Spinbox(time_out_frame, from_=0, to=23, width=5, format="%02.0f")
        hour_out_spin.set(hour_out)
        hour_out_spin.pack(side='left')
        ttk.Label(time_out_frame, text=":").pack(side='left', padx=2)
        min_out_spin = ttk.Spinbox(time_out_frame, from_=0, to=59, width=5, format="%02.0f")
        min_out_spin.set(min_out)
        min_out_spin.pack(side='left')
        
        # Comments
        ttk.Label(frame, text="Comments:").grid(row=7, column=0, sticky='nw', pady=5)
        comment_text = tk.Text(frame, width=40, height=4)
        comment_text.insert("1.0", task.get('comments', ''))
        comment_text.grid(row=7, column=1, pady=5)
        
        def save_changes():
            task['name'] = name_entry.get()
            task['priority'] = priority_combo.get()
            task['mandatory'] = mandatory_var.get()
            task['start_date'] = start_date.get_date().strftime('%Y-%m-%d')
            task['end_date'] = end_date.get_date().strftime('%Y-%m-%d')
            task['time_in'] = f"{hour_in_spin.get()}:{min_in_spin.get()}"
            task['time_out'] = f"{hour_out_spin.get()}:{min_out_spin.get()}"
            task['comments'] = comment_text.get("1.0", "end-1c").strip()
            
            self.save_data()
            self.on_project_select_edit(None)
            edit_win.destroy()
            messagebox.showinfo("Success", "Task updated successfully!")
        
        ttk.Button(frame, text="Save Changes", command=save_changes).grid(row=8, column=0, columnspan=2, pady=20)
    
    def mark_complete(self):
        selected = self.edit_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        tid = self.edit_tree.item(selected[0])['text']
        pid = self.edit_project_select.get().split(' - ')[0]
        self.tasks[pid][tid]['status'] = 'Complete'
        self.save_data()
        self.on_project_select_edit(None)
    
    def mark_incomplete(self):
        selected = self.edit_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        tid = self.edit_tree.item(selected[0])['text']
        pid = self.edit_project_select.get().split(' - ')[0]
        self.tasks[pid][tid]['status'] = 'Incomplete'
        self.save_data()
        self.on_project_select_edit(None)
    
    def delete_task(self):
        selected = self.edit_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        tid = self.edit_tree.item(selected[0])['text']
        pid = self.edit_project_select.get().split(' - ')[0]
        
        if messagebox.askyesno("Confirm", f"Delete task {tid}?"):
            del self.tasks[pid][tid]
            # Delete subtasks
            to_delete = [t_id for t_id, t in self.tasks[pid].items() if t.get('parent') == tid]
            for t_id in to_delete:
                del self.tasks[pid][t_id]
            
            self.save_data()
            self.on_project_select_edit(None)
    
    # Progress Functions
    def update_progress_project_list(self):
        values = [f"{p['id']} - {p['name']}" for p in self.projects.values()]
        self.progress_project_select['values'] = values
        if values:
            self.progress_project_select.current(0)
    
    def show_progress(self):
        selection = self.progress_project_select.get()
        if not selection:
            return
        
        pid = selection.split(' - ')[0]
        tasks = self.tasks.get(pid, {})
        
        if not tasks:
            self.progress_info.config(text="No tasks in this project")
            return
        
        total = len(tasks)
        completed = sum(1 for t in tasks.values() if t['status'] == 'Complete')
        incomplete = total - completed
        percentage = (completed / total * 100) if total > 0 else 0
        
        self.progress_info.config(
            text=f"Total Tasks: {total} | Completed: {completed} | Incomplete: {incomplete} | Progress: {percentage:.1f}%"
        )
        
        # Clear tree
        for item in self.progress_tree.get_children():
            self.progress_tree.delete(item)
        
        # Sort tasks: incomplete first, then completed
        sorted_tasks = sorted(tasks.items(), key=lambda x: (x[1]['status'] == 'Complete', x[0]))
        
        for tid, task in sorted_tasks:
            if not task.get('parent'):
                self.insert_progress_task(tid, task, tasks, '')
    
    def insert_progress_task(self, tid, task, all_tasks, parent):
        priority_color = self.get_priority_color(task['priority'])
        
        item = self.progress_tree.insert(parent, 'end', text=tid, values=(
            task['name'],
            task['priority'],
            'Yes' if task['mandatory'] else 'No',
            task['start_date'],
            task['end_date'],
            task['status']
        ), tags=(priority_color,))
        
        self.progress_tree.tag_configure(priority_color, background=priority_color)
        
        # Insert subtasks
        subtasks = [(t_id, t) for t_id, t in all_tasks.items() if t.get('parent') == tid]
        subtasks.sort(key=lambda x: (x[1]['status'] == 'Complete', x[0]))
        
        for sub_id, subtask in subtasks:
            self.insert_progress_task(sub_id, subtask, all_tasks, item)
    
    # Today's Tasks Functions
    def draw_clock(self):
        """Draw analog clock"""
        self.clock_canvas.delete('all')
        
        now = datetime.now()
        hour = now.hour % 12
        minute = now.minute
        second = now.second
        
        cx, cy = 100, 100
        radius = 80
        
        # Draw clock circle
        self.clock_canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, 
                                      outline='black', width=3)
        
        # Draw hour markers
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = cx + (radius - 10) * math.cos(angle)
            y1 = cy + (radius - 10) * math.sin(angle)
            x2 = cx + radius * math.cos(angle)
            y2 = cy + radius * math.sin(angle)
            self.clock_canvas.create_line(x1, y1, x2, y2, width=2)
            
            x_text = cx + (radius - 20) * math.cos(angle)
            y_text = cy + (radius - 20) * math.sin(angle)
            hour_num = 12 if i == 0 else i
            self.clock_canvas.create_text(x_text, y_text, text=str(hour_num), 
                                         font=('Arial', 12, 'bold'))
        
        # Draw hands
        hour_angle = math.radians((hour + minute/60) * 30 - 90)
        hour_length = radius * 0.5
        hx = cx + hour_length * math.cos(hour_angle)
        hy = cy + hour_length * math.sin(hour_angle)
        self.clock_canvas.create_line(cx, cy, hx, hy, fill='red', width=6)
        
        minute_angle = math.radians((minute + second/60) * 6 - 90)
        minute_length = radius * 0.7
        mx = cx + minute_length * math.cos(minute_angle)
        my = cy + minute_length * math.sin(minute_angle)
        self.clock_canvas.create_line(cx, cy, mx, my, fill='blue', width=4)
        
        second_angle = math.radians(second * 6 - 90)
        second_length = radius * 0.8
        sx = cx + second_length * math.cos(second_angle)
        sy = cy + second_length * math.sin(second_angle)
        self.clock_canvas.create_line(cx, cy, sx, sy, fill='green', width=2)
        
        self.clock_canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill='black')
        
        time_str = now.strftime('%I:%M:%S %p')
        self.clock_canvas.create_text(cx, cy+radius+15, text=time_str, 
                                      font=('Arial', 10, 'bold'))
    
    def update_clock(self):
        self.draw_clock()
        self.root.after(1000, self.update_clock)
    
    def update_today_date(self):
        now = datetime.now()
        
        day_name = now.strftime('%A')
        date_num = now.strftime('%d')
        month_name = now.strftime('%B')
        year = now.strftime('%Y')
        
        self.today_day_label.config(text=day_name)
        self.today_date_label.config(text=f"Date: {date_num}")
        self.today_month_year_label.config(text=f"{month_name}, {year}")
        
        self.root.after(60000, self.update_today_date)
    
    def refresh_today_tasks(self):
        """Load tasks for today - show only subtasks if parent has subtasks, otherwise show parent task"""
        for item in self.today_tree.get_children():
            self.today_tree.delete(item)
        
        today = datetime.now().date()
        
        total_tasks = 0
        completed_tasks = 0
        
        for pid, project in self.projects.items():
            tasks = self.tasks.get(pid, {})
            
            for tid, task in tasks.items():
                task_start = datetime.strptime(task['start_date'], '%Y-%m-%d').date()
                task_end = datetime.strptime(task['end_date'], '%Y-%m-%d').date()
                
                if task_start <= today <= task_end:
                    # Check if this task has subtasks
                    if self.has_subtasks(pid, tid):
                        # Don't show parent task, subtasks will be shown separately
                        continue
                    
                    # Check if this is a subtask
                    parent_id = task.get('parent')
                    if parent_id:
                        # This is a subtask, show it
                        total_tasks += 1
                        if task['status'] == 'Complete':
                            completed_tasks += 1
                        
                        priority_color = self.get_priority_color(task['priority'])
                        parent_task_name = tasks[parent_id]['name'] if parent_id in tasks else "Unknown"
                        
                        item = self.today_tree.insert('', 'end', text=tid, values=(
                            project['name'],
                            f"{task['name']} (subtask of {parent_task_name})",
                            task['priority'],
                            'Yes' if task['mandatory'] else 'No',
                            task['time_in'],
                            task['time_out'],
                            task['status']
                        ), tags=(priority_color,))
                        
                        self.today_tree.tag_configure(priority_color, background=priority_color)
                    else:
                        # This is a standalone task without subtasks
                        total_tasks += 1
                        if task['status'] == 'Complete':
                            completed_tasks += 1
                        
                        priority_color = self.get_priority_color(task['priority'])
                        
                        item = self.today_tree.insert('', 'end', text=tid, values=(
                            project['name'],
                            task['name'],
                            task['priority'],
                            'Yes' if task['mandatory'] else 'No',
                            task['time_in'],
                            task['time_out'],
                            task['status']
                        ), tags=(priority_color,))
                        
                        self.today_tree.tag_configure(priority_color, background=priority_color)
        
        # Update info label
        if total_tasks > 0:
            percentage = (completed_tasks / total_tasks * 100)
            self.today_info_label.config(
                text=f"Total: {total_tasks} | Completed: {completed_tasks} | Remaining: {total_tasks - completed_tasks} | Progress: {percentage:.1f}%"
            )
        else:
            self.today_info_label.config(text="No tasks scheduled for today")
    
    def mark_today_complete(self):
        selected = self.today_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        tid = self.today_tree.item(selected[0])['text']
        
        for pid, tasks in self.tasks.items():
            if tid in tasks:
                tasks[tid]['status'] = 'Complete'
                self.save_data()
                self.refresh_today_tasks()
                messagebox.showinfo("Success", f"Task {tid} marked as complete!")
                return
    
    def mark_project_complete(self):
        selected = self.today_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task from the project")
            return
        
        project_name = self.today_tree.item(selected[0])['values'][0]
        
        pid = None
        for p_id, proj in self.projects.items():
            if proj['name'] == project_name:
                pid = p_id
                break
        
        if not pid:
            return
        
        if messagebox.askyesno("Confirm", f"Mark all tasks in project '{project_name}' as complete?"):
            tasks = self.tasks.get(pid, {})
            for task in tasks.values():
                task['status'] = 'Complete'
            
            self.save_data()
            self.refresh_today_tasks()
            messagebox.showinfo("Success", f"All tasks in project '{project_name}' marked as complete!")
    
    # Calendar Filter Functions
    def apply_calendar_filter(self):
        """Apply calendar filter - show only subtasks if parent has subtasks, otherwise show task"""
        for item in self.filter_tree.get_children():
            self.filter_tree.delete(item)
        
        selected_date = self.filter_calendar.get_date()
        filter_type = self.filter_type.get()
        
        base_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        if filter_type == "day":
            start_date = base_date
            end_date = base_date
            range_text = base_date.strftime('%B %d, %Y')
        elif filter_type == "week":
            start_date = base_date - timedelta(days=base_date.weekday())
            end_date = start_date + timedelta(days=6)
            range_text = f"Week: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        else:
            start_date = base_date.replace(day=1)
            if base_date.month == 12:
                end_date = base_date.replace(day=31)
            else:
                end_date = (base_date.replace(month=base_date.month + 1, day=1) - timedelta(days=1))
            range_text = base_date.strftime('%B %Y')
        
        total_tasks = 0
        completed_tasks = 0
        
        for pid, project in self.projects.items():
            tasks = self.tasks.get(pid, {})
            
            for tid, task in tasks.items():
                task_start = datetime.strptime(task['start_date'], '%Y-%m-%d').date()
                task_end = datetime.strptime(task['end_date'], '%Y-%m-%d').date()
                
                if (task_start <= end_date and task_end >= start_date):
                    # Check if this task has subtasks
                    if self.has_subtasks(pid, tid):
                        # Don't show parent task, subtasks will be shown separately
                        continue
                    
                    # Check if this is a subtask
                    parent_id = task.get('parent')
                    if parent_id:
                        # This is a subtask, show it
                        total_tasks += 1
                        if task['status'] == 'Complete':
                            completed_tasks += 1
                        
                        priority_color = self.get_priority_color(task['priority'])
                        parent_task_name = tasks[parent_id]['name'] if parent_id in tasks else "Unknown"
                        
                        item = self.filter_tree.insert('', 'end', text=tid, values=(
                            project['name'],
                            f"{task['name']} (subtask of {parent_task_name})",
                            task['priority'],
                            'Yes' if task['mandatory'] else 'No',
                            task['start_date'],
                            task['end_date'],
                            task['time_in'],
                            task['time_out'],
                            task['status']
                        ), tags=(priority_color,))
                        
                        self.filter_tree.tag_configure(priority_color, background=priority_color)
                    else:
                        # This is a standalone task without subtasks
                        total_tasks += 1
                        if task['status'] == 'Complete':
                            completed_tasks += 1
                        
                        priority_color = self.get_priority_color(task['priority'])
                        
                        item = self.filter_tree.insert('', 'end', text=tid, values=(
                            project['name'],
                            task['name'],
                            task['priority'],
                            'Yes' if task['mandatory'] else 'No',
                            task['start_date'],
                            task['end_date'],
                            task['time_in'],
                            task['time_out'],
                            task['status']
                        ), tags=(priority_color,))
                        
                        self.filter_tree.tag_configure(priority_color, background=priority_color)
        
        if total_tasks > 0:
            percentage = (completed_tasks / total_tasks * 100)
            self.filter_info_label.config(
                text=f"{range_text} | Total: {total_tasks} | Completed: {completed_tasks} | Remaining: {total_tasks - completed_tasks} | Progress: {percentage:.1f}%"
            )
        else:
            self.filter_info_label.config(text=f"{range_text} | No tasks found in this period")
    
    def mark_filter_complete(self):
        selected = self.filter_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        tid = self.filter_tree.item(selected[0])['text']
        
        for pid, tasks in self.tasks.items():
            if tid in tasks:
                tasks[tid]['status'] = 'Complete'
                self.save_data()
                self.apply_calendar_filter()
                messagebox.showinfo("Success", f"Task {tid} marked as complete!")
                return
    
    def mark_filter_incomplete(self):
        selected = self.filter_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return
        
        tid = self.filter_tree.item(selected[0])['text']
        
        for pid, tasks in self.tasks.items():
            if tid in tasks:
                tasks[tid]['status'] = 'Incomplete'
                self.save_data()
                self.apply_calendar_filter()
                messagebox.showinfo("Success", f"Task {tid} marked as incomplete!")
                return
    
    def export_filtered_csv(self):
        if not self.filter_tree.get_children():
            messagebox.showwarning("Warning", "No tasks to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="filtered_tasks_export.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                writer.writerow(['Task_ID', 'Project', 'Task', 'Priority', 'Mandatory', 
                               'Start_Date', 'End_Date', 'Time_In', 'Time_Out', 'Status', 'Comments'])
                
                for item in self.filter_tree.get_children():
                    tid = self.filter_tree.item(item)['text']
                    values = self.filter_tree.item(item)['values']
                    
                    p_name = values[0]
                    pid = None
                    for p_id, p in self.projects.items():
                        if p['name'] == p_name:
                            pid = p_id
                            break
                    
                    comment_str = ""
                    if pid and tid in self.tasks[pid]:
                        comment_str = self.tasks[pid][tid].get('comments', '')

                    writer.writerow([tid] + list(values) + [comment_str])
            
            messagebox.showinfo("Success", f"Filtered tasks exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    # CSV Import/Export
    def export_csv(self):
        selection = self.progress_project_select.get()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project")
            return
        
        pid = selection.split(' - ')[0]
        project = self.projects[pid]
        tasks = self.tasks.get(pid, {})
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"project_{pid}_export.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                writer.writerow(['PROJECT_INFO'])
                writer.writerow(['ID', 'Name', 'Type', 'Start', 'End'])
                writer.writerow([project['id'], project['name'], project['type'], 
                               project['start'], project['end']])
                writer.writerow([])
                
                writer.writerow(['TASKS'])
                writer.writerow(['Task_ID', 'Name', 'Parent', 'Priority', 'Mandatory', 
                               'Start_Date', 'End_Date', 'Time_In', 'Time_Out', 'Status', 'Comments', 'Has_Subtasks'])
                
                for tid, task in tasks.items():
                    writer.writerow([
                        tid,
                        task['name'],
                        task.get('parent', ''),
                        task['priority'],
                        'Yes' if task['mandatory'] else 'No',
                        task['start_date'],
                        task['end_date'],
                        task['time_in'],
                        task['time_out'],
                        task['status'],
                        task.get('comments', ''),
                        'Yes' if task.get('has_subtasks', False) else 'No'
                    ])
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def import_csv(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            project_start = rows.index(['PROJECT_INFO']) + 2
            project_data = rows[project_start]
            
            pid = project_data[0]
            
            if pid in self.projects:
                if not messagebox.askyesno("Confirm", 
                    f"Project {pid} already exists. Overwrite?"):
                    return
            
            self.projects[pid] = {
                'id': project_data[0],
                'name': project_data[1],
                'type': project_data[2],
                'start': project_data[3],
                'end': project_data[4]
            }
            
            task_start = rows.index(['TASKS']) + 2
            self.tasks[pid] = {}
            
            for row in rows[task_start:]:
                if len(row) < 10:
                    continue
                
                tid = row[0]
                comments_val = row[10] if len(row) > 10 else ''
                has_subtasks_val = row[11] if len(row) > 11 else 'No'
                
                self.tasks[pid][tid] = {
                    'name': row[1],
                    'parent': row[2] if row[2] else None,
                    'priority': row[3],
                    'mandatory': row[4] == 'Yes',
                    'start_date': row[5],
                    'end_date': row[6],
                    'time_in': row[7],
                    'time_out': row[8],
                    'status': row[9],
                    'comments': comments_val,
                    'has_subtasks': has_subtasks_val == 'Yes'
                }
            
            self.save_data()
            self.refresh_project_list()
            self.update_task_project_list()
            self.update_edit_project_list()
            self.update_progress_project_list()
            
            messagebox.showinfo("Success", f"Project {pid} imported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import: {str(e)}")
    
    # Data Persistence
    def save_data(self):
        data = {
            'projects': self.projects,
            'tasks': self.tasks
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.projects = data.get('projects', {})
                    self.tasks = data.get('tasks', {})
            except Exception as e:
                print(f"Error loading data: {e}")
                self.projects = {}
                self.tasks = {}
    
    def auto_save(self):
        self.save_data()
        self.root.after(30000, self.auto_save)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectTaskManager(root)
    root.mainloop()

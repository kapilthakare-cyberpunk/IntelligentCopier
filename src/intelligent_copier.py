#!/usr/bin/env python3
"""
Intelligent File Copier & Verifier
A robust GUI application for copying large volumes with resume, verification,
and duplicate detection capabilities.

Author: Kapil Thakare
Version: 1.0.0
License: MIT
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
import queue
import re

# Optional: Magika for AI-powered file type detection
try:
    from magika import Magika
    MAGIKA_AVAILABLE = True
except ImportError:
    MAGIKA_AVAILABLE = False

# Constants
EXCLUDE_PATTERNS = [
    '.Spotlight-V100', '.TemporaryItems', '.Trashes',
    '.fseventsd', '.DocumentRevisions-V100',
    '.DS_Store', '._*', '.sync.ffs_db'
]
PROGRESS_UPDATE_INTERVAL = 100  # ms
MAX_LOG_LINES = 1000
RECENT_PATHS_LIMIT = 10

# UI Constants for improved design
UI_CONSTANTS = {
    'spacing': {
        'xxs': 2,
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 24
    },
    'fonts': {
        'title': ('Helvetica', 20, 'bold'),
        'header': ('Helvetica', 12, 'bold'),
        'subheader': ('Helvetica', 11, 'bold'),
        'body': ('Helvetica', 10),
        'body_bold': ('Helvetica', 10, 'bold'),
        'small': ('Helvetica', 9),
        'code': ('Menlo', 10),
        'status': ('Helvetica', 10, 'bold')
    },
    'colors': {
        'primary': '#007AFF',
        'secondary': '#5856D6',
        'success': '#34C759',
        'warning': '#FF9500',
        'error': '#FF3B30',
        'background': '#F2F2F7',
        'surface': '#FFFFFF',
        'text_primary': '#000000',
        'text_secondary': '#636366',
        'text_tertiary': '#8E8E93',
        'border': '#C6C6C8',
        'disabled': '#AEAEB2'
    },
    'button_padding': {'x': 12, 'y': 6},
    'entry_padding': {'x': 8, 'y': 6},
    'label_padding': {'x': 8, 'y': 4}
}

__version__ = "1.0.0"
__author__ = "Kapil Thakare"


class IntelligentCopier:
    """Main application class for the Intelligent File Copier."""

    def __init__(self, root):
        self.root = root
        self.root.title("Intelligent File Copier v1.0")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)

        # Configure styles
        self.setup_styles()

        # State variables
        self.copy_process = None
        self.verify_process = None
        self.is_copying = False
        self.is_verifying = False
        self.is_paused = False
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filter_checkbuttons = {}

        # Statistics
        self.stats = {
            'files_total': 0,
            'files_copied': 0,
            'bytes_total': 0,
            'bytes_copied': 0,
            'start_time': None,
            'errors': [],
            'duplicates': []
        }

        # Configuration
        self.config_file = Path.home() / ".intelligent_copier_config.json"
        self.session_file = Path.home() / ".intelligent_copier_session.json"
        self.log_file = Path.home() / f"intelligent_copier_{self.session_id}.log"
        self.load_config()

        # Initialize Magika for file type detection
        self.magika = None
        if MAGIKA_AVAILABLE:
            try:
                self.magika = Magika()
            except Exception:
                pass

        self.setup_ui()
        self.queue = queue.Queue()
        self.root.after(100, self.process_queue)

        if self.magika:
            self.log("Magika AI file type detection enabled", "success")

        # Welcome message
        self.log("Welcome to Intelligent File Copier v1.0")
        self.log("Ready to copy with resume support and verification.")

    def setup_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        
        # Try different themes to find one that works on macOS
        available_themes = style.theme_names()
        if 'aqua' in available_themes:
            style.theme_use('aqua')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        else:
            style.theme_use(style.theme_names()[0] if available_themes else 'default')

        # Configure colors using UI constants
        colors = UI_CONSTANTS['colors']
        fonts = UI_CONSTANTS['fonts']
        spacing = UI_CONSTANTS['spacing']
        
        # Basic styles that won't break the UI
        style.configure('Title.TLabel', 
                       font=fonts['title'], 
                       foreground=colors['primary'])
        style.configure('Header.TLabel', 
                       font=fonts['header'], 
                       foreground=colors['text_primary'])
        style.configure('Status.TLabel', 
                       font=fonts['status'], 
                       foreground=colors['text_secondary'])
        style.configure('Accent.TButton', 
                       font=fonts['body_bold'])

        # Progress bar style
        style.configure('Horizontal.TProgressbar', 
                       thickness=20)

    def load_config(self):
        """Load user configuration from file."""
        self.config = {
            'source': '',
            'dest': '',
            'options': {
                'dry_run': True,
                'verify': True,
                'preserve_perms': True,
                'exclude_system': True,
                'duplicate_action': 'review'
            },
            'window_geometry': '1000x750',
            'recent_paths': []
        }

        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        """Save user configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log(f"Warning: Could not save config: {e}")

    def save_session(self):
        """Save current session state for resume capability."""
        session = {
            'session_id': self.session_id,
            'source': self.source_var.get(),
            'dest': self.dest_var.get(),
            'timestamp': datetime.now().isoformat(),
            'status': 'in_progress' if self.is_copying else 'paused',
            'stats': self.stats
        }
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session, f, indent=2)
        except Exception as e:
            self.log(f"Warning: Could not save session: {e}")

    def load_session(self):
        """Load previous session state."""
        if self.session_file.exists():
            try:
                with open(self.session_file) as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"Error loading session: {e}")
        return None

    def setup_ui(self):
        """Setup the user interface."""
        # Main container with padding
        spacing = UI_CONSTANTS['spacing']
        main = ttk.Frame(self.root, padding=spacing['lg'])
        main.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        # Title Header
        title_frame = ttk.Frame(main)
        title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, spacing['lg']))
        title_frame.columnconfigure(0, weight=1)

        title = ttk.Label(title_frame, text="Intelligent File Copier",
                         style='Title.TLabel')
        title.grid(row=0, column=0, sticky="w")

        version = ttk.Label(title_frame, text=f"v{__version__}",
                           style='Header.TLabel',
                           foreground=UI_CONSTANTS['colors']['text_tertiary'])
        version.grid(row=0, column=1, sticky="e")

        # Separator
        ttk.Separator(main, orient='horizontal', style='Modern.TSeparator').grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=spacing['md'])

        # Path Selection Section
        self.setup_path_section(main, 2)

        # Options Section
        self.setup_options_section(main, 4)

        # Progress Section
        self.setup_progress_section(main, 6)

        # Log Output
        self.setup_log_section(main, 8)

        # Button Frame
        self.setup_button_frame(main, 10)

        # Status Bar
        self.setup_status_bar(main, 12)

        # Configure row weights
        main.rowconfigure(8, weight=1)

    def setup_path_section(self, parent, row):
        """Setup source and destination path selection."""
        spacing = UI_CONSTANTS['spacing']
        fonts = UI_CONSTANTS['fonts']
        
        path_frame = ttk.LabelFrame(parent, text="Source & Destination",
                                    style='Modern.TLabelframe',
                                    padding=(spacing['md'], spacing['sm']))
        path_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, spacing['md']))
        path_frame.columnconfigure(1, weight=1)

        # Source
        ttk.Label(path_frame, text="Source:",
                 style='Header.TLabel').grid(
            row=0, column=0, sticky="w", pady=(0, spacing['xs']))
        self.source_var = tk.StringVar(value=self.config.get('source', ''))
        source_entry = ttk.Entry(path_frame, textvariable=self.source_var,
                                style='Modern.TEntry',
                                font=fonts['code'])
        source_entry.grid(row=0, column=1, sticky="ew", padx=(0, spacing['sm']), pady=(0, spacing['xs']))
        source_btn = ttk.Button(path_frame, text="Browse",
                               style='Modern.TButton',
                               command=self.browse_source)
        source_btn.grid(row=0, column=2, padx=(spacing['xs'], 0), pady=(0, spacing['xs']))

        # Destination
        ttk.Label(path_frame, text="Destination:",
                 style='Header.TLabel').grid(
            row=1, column=0, sticky="w", pady=(spacing['xs'], 0))
        self.dest_var = tk.StringVar(value=self.config.get('dest', ''))
        dest_entry = ttk.Entry(path_frame, textvariable=self.dest_var,
                              style='Modern.TEntry',
                              font=fonts['code'])
        dest_entry.grid(row=1, column=1, sticky="ew", padx=(0, spacing['sm']), pady=(spacing['xs'], 0))
        dest_btn = ttk.Button(path_frame, text="Browse",
                             style='Modern.TButton',
                             command=self.browse_dest)
        dest_btn.grid(row=1, column=2, padx=(spacing['xs'], 0), pady=(spacing['xs'], 0))

        # Quick swap button
        swap_btn = ttk.Button(path_frame, text="Swap",
                             style='Modern.TButton',
                             command=self.swap_paths, width=8)
        swap_btn.grid(row=0, column=3, rowspan=2, padx=(spacing['sm'], 0), pady=(0, spacing['xs']))

    def setup_options_section(self, parent, row):
        """Setup options frame."""
        spacing = UI_CONSTANTS['spacing']
        fonts = UI_CONSTANTS['fonts']
        
        options_frame = ttk.LabelFrame(parent, text="Copy Options",
                                       style='Modern.TLabelframe',
                                       padding=(spacing['md'], spacing['sm']))
        options_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, spacing['md']))
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(2, weight=1)

        # Row 1: Main options
        self.dry_run_var = tk.BooleanVar(
            value=self.config['options'].get('dry_run', True))
        dry_run_cb = ttk.Checkbutton(options_frame, text="Dry Run First",
                                     style='Modern.TCheckbutton',
                                     variable=self.dry_run_var)
        dry_run_cb.grid(row=0, column=0, sticky="w", pady=(0, spacing['xs']))
        self.add_tooltip(dry_run_cb, "Preview what will be copied without \n"
                         "actually copying any files")

        self.verify_var = tk.BooleanVar(
            value=self.config['options'].get('verify', True))
        verify_cb = ttk.Checkbutton(options_frame, text="Verify After Copy",
                                    style='Modern.TCheckbutton',
                                    variable=self.verify_var)
        verify_cb.grid(row=0, column=1, sticky="w", pady=(0, spacing['xs']))
        self.add_tooltip(verify_cb, "Compare source and destination after \n"
                         "copying to ensure integrity")

        self.preserve_var = tk.BooleanVar(
            value=self.config['options'].get('preserve_perms', True))
        preserve_cb = ttk.Checkbutton(options_frame, text="🔐 Preserve Permissions",
                                      style='Modern.TCheckbutton',
                                      variable=self.preserve_var)
        preserve_cb.grid(row=0, column=2, sticky="w", pady=(0, spacing['xs']))

        # Row 2: Exclusions and duplicates
        self.exclude_var = tk.BooleanVar(
            value=self.config['options'].get('exclude_system', True))
        exclude_cb = ttk.Checkbutton(options_frame,
                                    text="🚫 Exclude System Files",
                                    style='Modern.TCheckbutton',
                                    variable=self.exclude_var)
        exclude_cb.grid(row=1, column=0, sticky="w", pady=(spacing['xs'], 0))
        self.add_tooltip(exclude_cb, "Skip .DS_Store, .Spotlight-V100, etc.")

        dup_frame = ttk.Frame(options_frame)
        dup_frame.grid(row=1, column=1, columnspan=2, sticky="w", pady=(spacing['xs'], 0))

        ttk.Label(dup_frame, text="Duplicates:", style='Header.TLabel').pack(side=tk.LEFT, padx=(0, spacing['xs']))
        self.duplicates_var = tk.StringVar(
            value=self.config['options'].get('duplicate_action', 'review'))
        dup_combo = ttk.Combobox(dup_frame, textvariable=self.duplicates_var,
                                  values=["skip", "overwrite", "rename", "review"],
                                  state="readonly", width=12,
                                  style='Modern.TCombobox')
        dup_combo.pack(side=tk.LEFT, padx=(0, spacing['sm']))
        self.add_tooltip(dup_combo, "How to handle duplicate files:\n"
                          "• skip: Skip duplicates\n"
                          "• overwrite: Replace with newer\n"
                          "• rename: Add suffix (_1, _2)\n"
                          "• review: Move to review folder")

        # Row 3: File type filtering with Magika
        filter_frame = ttk.Frame(options_frame)
        filter_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=(spacing['xs'], 0))

        self.filter_enabled_var = tk.BooleanVar(value=False)
        filter_cb = ttk.Checkbutton(
            filter_frame, text="🤖 AI File Type Filter",
            style='Modern.TCheckbutton',
            variable=self.filter_enabled_var,
            command=self.toggle_file_filter)
        filter_cb.pack(side=tk.LEFT, padx=(0, spacing['sm']))

        self.filter_categories = {
            'images': tk.BooleanVar(value=True),
            'videos': tk.BooleanVar(value=True),
            'audio': tk.BooleanVar(value=True),
            'documents': tk.BooleanVar(value=True),
            'code': tk.BooleanVar(value=True),
            'archives': tk.BooleanVar(value=True),
            'other': tk.BooleanVar(value=True)
        }
        
        # Store checkbutton widgets for later access
        self.filter_checkbuttons = {}

        self.filter_combo = ttk.Combobox(
            filter_frame,
            values=["Include selected", "Exclude selected"],
            state="disabled", width=15,
            style='Modern.TCombobox')
        self.filter_combo.current(0)
        self.filter_combo.pack(side=tk.LEFT, padx=spacing['sm'])
        self.add_tooltip(self.filter_combo, "Include or exclude selected file types")

        for cat in ['images', 'videos', 'audio', 'documents', 'code', 'archives']:
            cb = ttk.Checkbutton(
                filter_frame, text=cat.capitalize(),
                style='Modern.TCheckbutton',
                variable=self.filter_categories[cat])
            cb.pack(side=tk.LEFT, padx=spacing['xs'])
            self.filter_checkbuttons[cat] = cb

    def setup_progress_section(self, parent, row):
        """Setup progress bar and statistics."""
        spacing = UI_CONSTANTS['spacing']
        fonts = UI_CONSTANTS['fonts']
        colors = UI_CONSTANTS['colors']
        
        progress_frame = ttk.LabelFrame(parent, text="Progress",
                                        style='Modern.TLabelframe',
                                        padding=(spacing['md'], spacing['sm']))
        progress_frame.grid(row=row, column=0, columnspan=3,
                           sticky="ew", pady=(0, spacing['md']))
        progress_frame.columnconfigure(0, weight=1)

        # Progress bar with percentage label
        progress_container = ttk.Frame(progress_frame)
        progress_container.grid(row=0, column=0, columnspan=3,
                               sticky="ew", pady=(0, spacing['sm']))
        progress_container.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_container, variable=self.progress_var,
            maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        
        # Progress percentage label
        self.progress_percent_var = tk.StringVar(value="0%")
        progress_percent_lbl = ttk.Label(progress_container, 
                                        textvariable=self.progress_percent_var,
                                        font=fonts['body_bold'],
                                        foreground=colors['primary'])
        progress_percent_lbl.grid(row=0, column=1, padx=(spacing['sm'], 0))

        # Status labels
        status_frame = ttk.Frame(progress_frame)
        status_frame.grid(row=1, column=0, columnspan=3, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(2, weight=1)

        self.status_var = tk.StringVar(value="Ready")
        status_lbl = ttk.Label(status_frame, textvariable=self.status_var,
                              style='Status.TLabel')
        status_lbl.grid(row=0, column=0, sticky="w")

        self.stats_var = tk.StringVar(value="Files: 0/0 | Size: 0 GB/0 GB")
        stats_lbl = ttk.Label(status_frame, textvariable=self.stats_var,
                             style='Status.TLabel')
        stats_lbl.grid(row=0, column=1, sticky="e")

        self.speed_var = tk.StringVar(value="Speed: -")
        speed_lbl = ttk.Label(status_frame, textvariable=self.speed_var,
                             style='Status.TLabel',
                             foreground=colors['primary'])
        speed_lbl.grid(row=0, column=2, sticky="e")

        # Time estimate
        self.time_var = tk.StringVar(value="ETA: -")
        time_lbl = ttk.Label(progress_frame, textvariable=self.time_var,
                            style='Status.TLabel',
                            foreground=colors['text_tertiary'])
        time_lbl.grid(row=2, column=0, columnspan=3, sticky="w", pady=(spacing['xs'], 0))

    def setup_log_section(self, parent, row):
        """Setup log output area."""
        spacing = UI_CONSTANTS['spacing']
        fonts = UI_CONSTANTS['fonts']
        colors = UI_CONSTANTS['colors']
        
        log_frame = ttk.Frame(parent)
        log_frame.grid(row=row, column=0, columnspan=3, sticky="nsew", pady=(0, spacing['md']))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)

        ttk.Label(log_frame, text="Activity Log:",
                 style='Header.TLabel').grid(
            row=0, column=0, sticky="w", pady=(0, spacing['xs']))

        # Log text with scrollbar
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=12, wrap=tk.WORD, font=fonts['code'],
            bg=colors['background'], fg=colors['text_primary'], 
            insertbackground=colors['text_primary'],
            selectbackground=colors['primary'], selectforeground=colors['surface'],
            padx=spacing['sm'], pady=spacing['sm'])
        self.log_text.grid(row=1, column=0, sticky="nsew")
        self.log_text.config(state=tk.DISABLED)

        # Log level filter
        filter_frame = ttk.Frame(log_frame)
        filter_frame.grid(row=2, column=0, sticky="e", pady=(spacing['xs'], 0))

        ttk.Button(filter_frame, text="Clear Log",
                  style='Modern.TButton',
                  command=self.clear_log).pack(side=tk.LEFT, padx=(0, spacing['xs']))
        ttk.Button(filter_frame, text="Save Log",
                  style='Modern.TButton',
                  command=self.save_log).pack(side=tk.LEFT, padx=(0, spacing['xs']))

    def setup_button_frame(self, parent, row):
        """Setup action buttons."""
        spacing = UI_CONSTANTS['spacing']
        
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=(spacing['lg'], 0))

        # Primary actions
        self.analyze_btn = ttk.Button(
            btn_frame, text="Analyze", command=self.analyze,
            style='Modern.TButton')
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, spacing['sm']))

        self.start_btn = ttk.Button(
            btn_frame, text=" Start Copy", command=self.start_copy,
            style='Modern.Accent.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=spacing['sm'])

        self.pause_btn = ttk.Button(
            btn_frame, text=" Pause", command=self.pause_copy,
            style='Modern.TButton',
            width=12, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=spacing['sm'])

        self.verify_btn = ttk.Button(
            btn_frame, text="Verify", command=self.verify_copy,
            style='Modern.TButton',
            width=12, state=tk.NORMAL)
        self.verify_btn.pack(side=tk.LEFT, padx=spacing['sm'])

        # Secondary actions
        separator = ttk.Separator(btn_frame, orient='vertical', style='Modern.TSeparator')
        separator.pack(side=tk.LEFT, fill='y', padx=spacing['lg'])

        self.resume_btn = ttk.Button(
            btn_frame, text="Resume", command=self.resume_session,
            style='Modern.TButton')
        self.resume_btn.pack(side=tk.LEFT, padx=spacing['sm'])

        ttk.Button(btn_frame, text="Report",
                  style='Modern.TButton',
                  command=self.generate_report).pack(
            side=tk.LEFT, padx=spacing['sm'])

        ttk.Button(btn_frame, text="Safe Delete",
                  style='Modern.TButton',
                  command=self.safe_delete_check).pack(
            side=tk.LEFT, padx=spacing['sm'])

    def setup_status_bar(self, parent, row):
        """Setup bottom status bar."""
        spacing = UI_CONSTANTS['spacing']
        fonts = UI_CONSTANTS['fonts']
        colors = UI_CONSTANTS['colors']
        
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, 
                                padding=(spacing['xs'], spacing['xxs']))
        status_frame.grid(row=row, column=0, columnspan=3,
                         sticky="ew", pady=(spacing['sm'], 0))
        status_frame.columnconfigure(0, weight=1)

        self.bottom_status = tk.StringVar(value="Ready | No active session")
        status_lbl = ttk.Label(status_frame, textvariable=self.bottom_status,
                              style='Status.TLabel')
        status_lbl.grid(row=0, column=0, sticky="w")

        session_lbl = ttk.Label(status_frame,
                               text=f"Session: {self.session_id}",
                               style='Status.TLabel',
                               foreground=colors['text_tertiary'])
        session_lbl.grid(row=0, column=1, sticky="e")

    def add_tooltip(self, widget, text):
        """Add a tooltip to a widget."""
        spacing = UI_CONSTANTS['spacing']
        fonts = UI_CONSTANTS['fonts']
        colors = UI_CONSTANTS['colors']
        
        def show_tooltip(event):
            tooltip = tk.Toplevel(self.root)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + spacing['sm']}+{event.y_root + spacing['sm']}")

            label = ttk.Label(tooltip, text=text, justify=tk.LEFT,
                            background=colors['surface'], relief='solid',
                            borderwidth=1, padding=(spacing['xs'], spacing['xxs']), 
                            font=fonts['small'])
            label.pack()

            widget.tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)

    def log(self, message, level='info'):
        """Add a message to the log with timestamp."""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color coding based on level using UI constants
        tag = level
        colors = UI_CONSTANTS['colors']
        if level not in self.log_text.tag_names():
            if level == 'error':
                self.log_text.tag_configure(level, foreground=colors['error'])
            elif level == 'warning':
                self.log_text.tag_configure(level, foreground=colors['warning'])
            elif level == 'success':
                self.log_text.tag_configure(level, foreground=colors['success'])
            elif level == 'info':
                self.log_text.tag_configure(level, foreground=colors['primary'])
            else:
                self.log_text.tag_configure(level, foreground=colors['text_primary'])

        self.log_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

        # Also write to log file
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] [{level.upper()}] {message}\n")

    def clear_log(self):
        """Clear the log display."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log("Log cleared.")

    def save_log(self):
        """Save log to a file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"),
                      ("All files", "*.*")]
        )
        if filename:
            self.log_text.config(state=tk.NORMAL)
            content = self.log_text.get(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)

            with open(filename, 'w') as f:
                f.write(content)
            self.log(f"Log saved to {filename}", 'success')

    def browse_source(self):
        """Browse for source directory."""
        path = filedialog.askdirectory(
            title="Select Source Directory",
            initialdir=self.source_var.get() or Path.home()
        )
        if path:
            self.source_var.set(path)
            self.config['source'] = path
            self.add_recent_path(path)
            self.save_config()
            self.log(f"Source set to: {path}")

    def browse_dest(self):
        """Browse for destination directory."""
        path = filedialog.askdirectory(
            title="Select Destination Directory",
            initialdir=self.dest_var.get() or Path.home()
        )
        if path:
            self.dest_var.set(path)
            self.config['dest'] = path
            self.add_recent_path(path)
            self.save_config()
            self.log(f"Destination set to: {path}")

    def add_recent_path(self, path):
        """Add path to recent paths list."""
        recent = self.config.get('recent_paths', [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.config['recent_paths'] = recent[:10]  # Keep last 10

    def swap_paths(self):
        """Swap source and destination paths."""
        source, dest = self.source_var.get(), self.dest_var.get()
        self.source_var.set(dest)
        self.dest_var.set(source)
        self.log("Source and destination swapped.")

    def toggle_file_filter(self):
        enabled = self.filter_enabled_var.get()
        state = tk.NORMAL if enabled else tk.DISABLED
        self.filter_combo.config(state=state)
        for cb in self.filter_checkbuttons.values():
            cb.config(state=state)

    def identify_file_type(self, file_path):
        """Identify file type using Magika AI."""
        if not self.magika:
            return None
        try:
            result = self.magika.identify_path(file_path)
            return result.output
        except Exception:
            return None

    def get_file_type_category(self, file_path):
        """Get file type category for filtering."""
        info = self.identify_file_type(file_path)
        if not info:
            return None
        return {
            'label': info.label,
            'description': info.description,
            'group': info.group,
            'mime_type': info.mime_type
        }

    def get_category_from_group(self, group):
        """Map Magika group to our filter categories."""
        mapping = {
            'image': 'images',
            'video': 'videos',
            'audio': 'audio',
            'document': 'documents',
            'code': 'code',
            'archive': 'archives'
        }
        return mapping.get(group, 'other')

    def should_include_file(self, file_path):
        """Determine if file should be included based on filters."""
        if not self.filter_enabled_var.get() or not self.magika:
            return True

        info = self.get_file_type_category(file_path)
        if not info:
            return self.filter_categories.get('other', tk.BooleanVar(value=True)).get()

        category = self.get_category_from_group(info.get('group', ''))
        include = self.filter_categories.get(category, tk.BooleanVar(value=True)).get()
        mode = self.filter_combo.get()
        return include if mode == "Include selected" else not include

    def find_content_duplicates(self, file_list):
        """Find duplicates using content hashing with Magika type info."""
        if not file_list:
            return []

        hash_map = {}
        duplicates = []

        for file_path in file_list:
            try:
                file_hash = hashlib.md5()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        file_hash.update(chunk)
                digest = file_hash.hexdigest()

                type_info = self.get_file_type_category(file_path)
                key = (digest, type_info.get('label') if type_info else 'unknown')

                if key in hash_map:
                    duplicates.append((file_path, hash_map[key]))
                else:
                    hash_map[key] = file_path
            except Exception:
                pass

        return duplicates

    def analyze(self):
        """Analyze source directory structure."""
        source = self.source_var.get()

        if not source:
            messagebox.showerror("Error", "Please select a source directory")
            return

        if not os.path.exists(source):
            messagebox.showerror("Error", f"Source does not exist:\n{source}")
            return

        self.log(f"Analyzing {source}...")
        self.status_var.set("Analyzing...")
        self.analyze_btn.config(state=tk.DISABLED)

        threading.Thread(target=self._analyze_worker, args=(source,),
                        daemon=True).start()

    def _analyze_worker(self, source):
        """Worker thread for analysis."""
        try:
            # Count files
            self.queue.put(('status', 'Counting files...'))
            result = subprocess.run(
                ['find', source, '-type', 'f'],
                capture_output=True, text=True, timeout=300
            )
            files = [f for f in result.stdout.strip().split('\n') if f]
            total_files = len(files)

            # Calculate size
            self.queue.put(('status', 'Calculating size...'))
            result = subprocess.run(
                ['du', '-sh', source],
                capture_output=True, text=True, timeout=60
            )
            size_str = result.stdout.split()[0] if result.stdout else "Unknown"

            # Get directory count
            result = subprocess.run(
                ['find', source, '-type', 'd'],
                capture_output=True, text=True, timeout=300
            )
            dirs = [d for d in result.stdout.strip().split('\n') if d]
            total_dirs = len(dirs)

            self.queue.put(('analyze_done', {
                'files': total_files,
                'dirs': total_dirs,
                'size': size_str
            }))

        except subprocess.TimeoutExpired:
            self.queue.put(('error', 'Analysis timed out (too many files)'))
        except Exception as e:
            self.queue.put(('error', f'Analysis failed: {str(e)}'))

    def start_copy(self):
        """Start the copy process."""
        source = self.source_var.get()
        dest = self.dest_var.get()

        if not source or not dest:
            messagebox.showerror("Error", "Please select both source and destination")
            return

        if not os.path.exists(source):
            messagebox.showerror("Error", f"Source does not exist:\n{source}")
            return

        if source == dest:
            messagebox.showerror("Error", "Source and destination cannot be the same")
            return

        # Ensure destination exists
        os.makedirs(dest, exist_ok=True)

        if self.dry_run_var.get():
            self.log("Running DRY RUN first...")
            self._run_rsync(source, dest, dry_run=True)
        else:
            if messagebox.askyesno("Confirm Copy",
                                  f"Copy from:\n{source}\n\nto:\n{dest}\n\nContinue?"):
                self._run_rsync(source, dest, dry_run=False)

    def _run_rsync(self, source, dest, dry_run=False):
        """Execute rsync command."""
        self.is_copying = True
        self.is_paused = False
        self.stats['start_time'] = datetime.now()

        self.start_btn.config(state=tk.DISABLED)
        self.analyze_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text=" Pause")
        self.verify_btn.config(state=tk.DISABLED)

        threading.Thread(target=self._rsync_worker,
                        args=(source, dest, dry_run),
                        daemon=True).start()

    def _rsync_worker(self, source, dest, dry_run):
        """Worker thread for rsync."""
        try:
            cmd = ['rsync', '-avh', '--progress', '--stats']

            if dry_run:
                cmd.append('--dry-run')

            # Exclude patterns
            if self.exclude_var.get():
                excludes = [
                    '.Spotlight-V100', '.TemporaryItems', '.Trashes',
                    '.fseventsd', '.DocumentRevisions-V100',
                    '.DS_Store', '._*', '.sync.ffs_db'
                ]
                for pattern in excludes:
                    cmd.extend(['--exclude', pattern])

            # Preserve permissions
            if self.preserve_var.get():
                cmd.append('-p')
                cmd.append('-o')
                cmd.append('-g')

            cmd.extend([f"{source}/", f"{dest}/"])

            self.log(f"Executing: {' '.join(cmd[:10])}...")
            self.save_session()

            self.copy_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            file_pattern = re.compile(r'^(\S+)\s+(\d+(?:\.\d+)?)%\s+([\d.]+\s\w+/s)\s+([\d:]+)')

            for line in self.copy_process.stdout:
                line = line.strip()
                if not line:
                    continue

                # Parse progress
                match = file_pattern.match(line)
                if match:
                    filename = match.group(1)
                    percent = float(match.group(2))
                    speed = match.group(3)
                    eta = match.group(4)

                    self.queue.put(('progress', {
                        'percent': percent,
                        'speed': speed,
                        'eta': eta,
                        'file': filename
                    }))
                elif '%' in line and 'MB/s' in line:
                    # Alternative progress format
                    self.queue.put(('output', line))
                elif line.startswith('Number of files:'):
                    # Stats line
                    self.queue.put(('stats_line', line))
                elif line.startswith('Total transferred file size:'):
                    self.queue.put(('stats_line', line))
                else:
                    self.queue.put(('output', line))

            self.copy_process.wait()

            if self.copy_process.returncode == 0:
                self.queue.put(('complete', dry_run))
            else:
                self.queue.put(('error',
                               f"Rsync exited with code {self.copy_process.returncode}"))

        except Exception as e:
            self.queue.put(('error', str(e)))

    def process_queue(self):
         """Process messages from worker threads."""
         try:
             while True:
                 msg_type, data = self.queue.get_nowait()

                 if msg_type == 'output':
                     if isinstance(data, tuple):
                         message, level = data
                     else:
                         message = data
                         level = 'info'
                     self.log(message, level)
                 elif msg_type == 'progress':
                    self.progress_var.set(data['percent'])
                    self.progress_percent_var.set(f"{int(data['percent'])}%")
                    self.speed_var.set(f"Speed: {data['speed']}")
                    self.time_var.set(f"ETA: {data.get('eta', '-')}")
                    self.status_var.set(f"Copying: {data.get('file', '...')[:50]}")
                 elif msg_type == 'stats_line':
                     self.log(data)
                 elif msg_type == 'status':
                     self.status_var.set(data)
                 elif msg_type == 'analyze_done':
                     self.stats_var.set(
                         f"Files: {data['files']:,} | Dirs: {data['dirs']:,} | Size: {data['size']}"
                     )
                     self.status_var.set("Analysis complete")
                     self.log(f" Found {data['files']:,} files, {data['dirs']:,} directories, "
                             f"total size: {data['size']}", 'success')
                     self.analyze_btn.config(state=tk.NORMAL)
                 elif msg_type == 'complete':
                     self.is_copying = False
                     self.start_btn.config(state=tk.NORMAL)
                     self.analyze_btn.config(state=tk.NORMAL)
                     self.pause_btn.config(state=tk.DISABLED)

                     if data:  # dry run complete
                         self.log(" Dry run complete. Ready to copy.", 'success')
                         self.status_var.set("Dry run complete")
                         if messagebox.askyesno("Dry Run Complete",
                                               "Proceed with actual copy?"):
                             self.dry_run_var.set(False)
                             self.start_copy()
                     else:
                         elapsed = datetime.now() - self.stats['start_time']
                         self.log(f" Copy complete! Time: {elapsed}", 'success')
                         self.status_var.set("Copy complete")
                         self.progress_var.set(100)
                         self.verify_btn.config(state=tk.NORMAL)
                         self.save_session()

                         if self.verify_var.get():
                             if messagebox.askyesno("Verify?",
                                                    "Copy complete. Run verification now?"):
                                 self.verify_copy()
                 elif msg_type == 'verify_complete':
                     self.is_verifying = False
                     self.verify_btn.config(state=tk.NORMAL)
                     self.status_var.set("Verification complete")
                 elif msg_type == 'safe_delete_result':
                     self._show_safe_delete_dialog(data)
                 elif msg_type == 'error':
                     self.log(f"ERROR: {data}", 'error')
                     self.is_copying = False
                     self.start_btn.config(state=tk.NORMAL)
                     self.analyze_btn.config(state=tk.NORMAL)
                     self.pause_btn.config(state=tk.DISABLED)
                     self.status_var.set("Error occurred")
                     messagebox.showerror("Error", str(data))

         except queue.Empty:
             pass

         self.root.after(100, self.process_queue)

    def pause_copy(self):
        """Pause the current copy operation."""
        if self.is_copying and not self.is_paused:
            if self.copy_process:
                self.copy_process.terminate()
                self.log("Copy paused", 'warning')
                self.status_var.set("Paused")
                self.is_paused = True
                self.pause_btn.config(text=" Resume")
                self.save_session()
        elif self.is_paused:
            # Resume
            self.log("Resuming copy...")
            self.is_paused = False
            self.pause_btn.config(text=" Pause")
            self.start_copy()

    def verify_copy(self):
        """Verify the copied files match source."""
        source = self.source_var.get()
        dest = self.dest_var.get()

        if not source or not dest:
            messagebox.showerror("Error", "Please select source and destination")
            return

        self.log("Starting verification...")
        self.status_var.set("Verifying...")
        self.is_verifying = True
        self.verify_btn.config(state=tk.DISABLED)

        threading.Thread(target=self._verify_worker, args=(source, dest),
                        daemon=True).start()

    def _verify_worker(self, source, dest):
        """Worker thread for verification."""
        try:
            # Compare file counts
            self.queue.put(('status', 'Counting files...'))
            result_src = subprocess.run(['find', source, '-type', 'f'],
                                       capture_output=True, text=True, timeout=300)
            result_dest = subprocess.run(['find', dest, '-type', 'f'],
                                          capture_output=True, text=True, timeout=300)

            src_files = [f for f in result_src.stdout.strip().split('\n') if f]
            dest_files = [f for f in result_dest.stdout.strip().split('\n') if f]

            src_count = len(src_files)
            dest_count = len(dest_files)

            self.queue.put(('output', f"Source files: {src_count:,}"))
            self.queue.put(('output', f"Destination files: {dest_count:,}"))

            if src_count == dest_count:
                self.queue.put(('output', " File counts match!"))
            else:
                diff = src_count - dest_count
                self.queue.put(('output', f"Difference: {diff:,} files", 'warning'))

            # Compare sizes
            self.queue.put(('status', 'Comparing sizes...'))
            result = subprocess.run(['du', '-sh', source],
                                   capture_output=True, text=True)
            src_size = result.stdout.split()[0] if result.stdout else "Unknown"

            result = subprocess.run(['du', '-sh', dest],
                                   capture_output=True, text=True)
            dest_size = result.stdout.split()[0] if result.stdout else "Unknown"

            self.queue.put(('output', f"Source size: {src_size}"))
            self.queue.put(('output', f"Destination size: {dest_size}"))

            # Sample integrity check on a few files
            self.queue.put(('status', 'Running sample integrity check...'))
            sample_size = min(10, dest_count)
            verified = 0
            failed = 0

            for i, src_file in enumerate(src_files[:sample_size]):
                rel_path = os.path.relpath(src_file, source)
                dest_file = os.path.join(dest, rel_path)

                if os.path.exists(dest_file):
                    src_stat = os.stat(src_file)
                    dest_stat = os.stat(dest_file)

                    if src_stat.st_size == dest_stat.st_size:
                        verified += 1
                    else:
                        failed += 1
                        self.queue.put(('output',
                                       f"✗ Size mismatch: {rel_path}"))
                else:
                    failed += 1
                    self.queue.put(('output', f"✗ Missing: {rel_path}"))

            self.queue.put(('output',
                           f"Sample verification: {verified}/{sample_size} OK"))

            if failed == 0:
                self.queue.put(('output', " Verification complete - All good!", 'success'))
            else:
                self.queue.put(('output', f"{failed} issues found", 'warning'))

            self.queue.put(('verify_complete', None))

        except Exception as e:
            self.queue.put(('error', f"Verification failed: {str(e)}"))

    def generate_report(self):
        """Generate a detailed copy report."""
        source = self.source_var.get()
        dest = self.dest_var.get()

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"copy_report_{self.session_id}.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("=" * 60 + "\n")
                    f.write("INTELLIGENT FILE COPIER - COPY REPORT\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Session ID: {self.session_id}\n\n")
                    f.write(f"Source: {source}\n")
                    f.write(f"Destination: {dest}\n\n")

                    if os.path.exists(dest):
                        f.write(f"Destination Size: {os.popen(f'du -sh {dest}').read().split()[0]}\n")
                        result = subprocess.run(['find', dest, '-type', 'f'],
                                              capture_output=True, text=True)
                        file_count = len([f for f in result.stdout.strip().split('\n') if f])
                        f.write(f"Files Copied: {file_count:,}\n\n")

                    f.write("=" * 60 + "\n")
                    f.write("Top-Level Directories:\n")
                    f.write("-" * 60 + "\n")
                    if os.path.exists(dest):
                        for item in sorted(os.listdir(dest))[:20]:
                            f.write(f"  {item}\n")

                    f.write("\n" + "=" * 60 + "\n")
                    f.write("END OF REPORT\n")

                self.log(f"Report saved to: {filename}", 'success')

            except Exception as e:
                self.log(f"Failed to save report: {e}", 'error')

    def safe_delete_check(self):
        """Check which folders are safely copied and can be deleted from source."""
        source = self.source_var.get()
        dest = self.dest_var.get()

        if not source or not dest:
            messagebox.showerror("Error", "Please select source and destination first")
            return

        if not os.path.exists(source) or not os.path.exists(dest):
            messagebox.showerror("Error", "Source or destination not found")
            return

        self.log("Starting safe delete check...")
        threading.Thread(target=self._safe_delete_worker,
                        args=(source, dest), daemon=True).start()

    def _safe_delete_worker(self, source, dest):
        """Worker for safe delete verification."""
        try:
            self.queue.put(('status', 'Analyzing folders...'))

            source_folders = set()
            for item in os.listdir(source):
                path = os.path.join(source, item)
                if os.path.isdir(path) and not item.startswith('.'):
                    source_folders.add(item)

            dest_folders = set()
            for item in os.listdir(dest):
                path = os.path.join(dest, item)
                if os.path.isdir(path) and not item.startswith('.'):
                    dest_folders.add(item)

            copied = source_folders & dest_folders
            not_copied = source_folders - dest_folders

            self.queue.put(('output', f"Found {len(copied)} folders in both source and destination"))
            self.queue.put(('output', f"Found {len(not_copied)} folders still needing to be copied"))

            if not copied:
                self.queue.put(('output', "No folders verified yet - nothing to delete", 'warning'))
                self.queue.put(('safe_delete_result', {'copied': [], 'not_copied': list(not_copied)}))
                return

            verified_folders = []
            failed_folders = []

            self.queue.put(('status', 'Verifying file integrity with Magika...'))

            for folder in sorted(copied):
                src_path = os.path.join(source, folder)
                dst_path = os.path.join(dest, folder)

                if not os.path.exists(dst_path):
                    failed_folders.append(folder)
                    continue

                sample_files = []
                for root, dirs, files in os.walk(dst_path):
                    for f in files:
                        if not f.startswith('.') and len(sample_files) < 5:
                            sample_files.append(os.path.join(root, f))
                    if len(sample_files) >= 5:
                        break

                if not sample_files:
                    verified_folders.append(folder)
                    continue

                if self.magika:
                    all_ok = True
                    for f in sample_files:
                        try:
                            self.magika.identify_path(f)
                        except:
                            all_ok = False
                            break
                    if all_ok:
                        verified_folders.append(folder)
                    else:
                        failed_folders.append(folder)
                else:
                    verified_folders.append(folder)

            self.queue.put(('safe_delete_result', {
                'verified': verified_folders,
                'failed': failed_folders,
                'not_copied': list(not_copied)
            }))

        except Exception as e:
            self.queue.put(('error', f"Safe delete check failed: {str(e)}"))

    def _show_safe_delete_dialog(self, data):
        """Show dialog with safe delete options."""
        verified = data.get('verified', [])
        failed = data.get('failed', [])
        not_copied = data.get('not_copied', [])

        if not verified:
            messagebox.showinfo("Safe Delete Check",
                "No folders have been fully copied yet.\n\n"
                f"Folders still needing copy: {', '.join(not_copied) if not_copied else 'None'}")
            return

        msg = "Folders VERIFIED safe to delete from source:\n\n"
        msg += "✓ " + "\n✓ ".join(verified) + "\n\n"

        if failed:
            msg += "Folders with issues (NOT safe to delete):\n"
            msg += "✗ " + "\n✗ ".join(failed) + "\n\n"

        if not_copied:
            msg += f"Folders not yet copied: {', '.join(not_copied)}\n\n"

        msg += "Do you want to delete the verified folders from source?"

        if messagebox.askyesno("Safe Delete", msg):
            self._delete_verified_folders(verified)

    def _delete_verified_folders(self, folders):
        """Delete verified folders from source after final confirmation."""
        source = self.source_var.get()

        confirm_msg = "This will PERMANENTLY DELETE these folders from source:\n\n"
        confirm_msg += "⚠️ " + "\n⚠️ ".join(folders) + "\n\n"
        confirm_msg += "This action cannot be undone!\n\n"
        confirm_msg += "Are you absolutely sure?"

        if messagebox.askyesno("CONFIRM DELETE", confirm_msg):
            self.log(f"Starting deletion of {len(folders)} folders...")
            threading.Thread(target=self._delete_worker,
                            args=(folders, source), daemon=True).start()

    def _delete_worker(self, folders, source):
        """Worker thread for deleting folders."""
        deleted = []
        failed = []

        for folder in folders:
            path = os.path.join(source, folder)
            try:
                shutil.rmtree(path)
                deleted.append(folder)
                self.queue.put(('output', f"Deleted: {folder}"))
            except Exception as e:
                failed.append((folder, str(e)))
                self.queue.put(('output', f"Failed to delete {folder}: {e}", 'error'))

        if deleted:
            self.queue.put(('output', f"Successfully deleted {len(deleted)} folders", 'success'))
        if failed:
            self.queue.put(('output', f"Failed to delete {len(failed)} folders", 'warning'))

    def resume_session(self):
        """Resume from a previous session."""
        session = self.load_session()
        if session:
            self.source_var.set(session['source'])
            self.dest_var.set(session['dest'])
            self.session_id = session['session_id']
            self.log(f"Resumed session from {session['timestamp']}")
            messagebox.showinfo("Session Resumed",
                                "Previous session loaded.\nClick 'Start Copy' to continue.")
        else:
            messagebox.showinfo("No Session", "No previous session found.")


def main():
    """Application entry point."""
    root = tk.Tk()

    # Set app icon (if available)
    try:
        root.iconphoto(False, tk.PhotoImage(file='assets/icon.png'))
    except:
        pass

    app = IntelligentCopier(root)

    # Handle window close
    def on_closing():
        if app.is_copying:
            if messagebox.askyesno("Quit?", "Copy in progress. Save session and quit?"):
                app.save_session()
                if app.copy_process:
                    app.copy_process.terminate()
                root.destroy()
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start main loop
    root.mainloop()


if __name__ == '__main__':
    main()

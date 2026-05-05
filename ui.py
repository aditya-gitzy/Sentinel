import json
import os
import subprocess
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Set the initial theme
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

class SentinelUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sentinel Config Manager")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.config_data = self.load_config()
        self.current_rule = None
        self.sentinel_process = None

        # --- Grid Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar (Automator Vibe) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Sentinel Rules", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Scrollable frame for rule list
        self.rule_list_frame = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="transparent")
        self.rule_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.add_rule_btn = ctk.CTkButton(self.sidebar_frame, text="+ Add New Rule", command=self.add_new_rule)
        self.add_rule_btn.grid(row=2, column=0, padx=20, pady=10)

        self.run_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="Run Sentinel",
            fg_color="green",
            hover_color="darkgreen",
            command=self.toggle_sentinel,
        )
        self.run_btn.grid(row=3, column=0, padx=20, pady=(0, 10))

        self.run_status_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Status: Stopped",
            anchor="w",
        )
        self.run_status_label.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="w")

        # Theme Toggle
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

        # --- Main Editing Area ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Placeholder message
        self.placeholder_label = ctk.CTkLabel(self.main_frame, text="Select a rule from the sidebar to edit", font=ctk.CTkFont(size=16))
        self.placeholder_label.grid(row=0, column=0, pady=200)

        self.edit_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.edit_frame.grid_columnconfigure(0, weight=1)
        
        # Rule Name Input
        self.rule_name_label = ctk.CTkLabel(self.edit_frame, text="Rule Name (e.g., CollegeDocs):")
        self.rule_name_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.rule_name_entry = ctk.CTkEntry(self.edit_frame, width=400)
        self.rule_name_entry.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Source Input
        self.source_label = ctk.CTkLabel(self.edit_frame, text="Source Folder Path:")
        self.source_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.source_frame = ctk.CTkFrame(self.edit_frame, fg_color="transparent")
        self.source_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.source_frame.grid_columnconfigure(0, weight=1)
        self.source_entry = ctk.CTkEntry(self.source_frame, width=600)
        self.source_entry.grid(row=0, column=0, sticky="ew")
        self.source_browse_btn = ctk.CTkButton(
            self.source_frame,
            text="Browse",
            width=120,
            command=lambda: self.browse_directory(self.source_entry),
        )
        self.source_browse_btn.grid(row=0, column=1, padx=(10, 0))

        # Destination Input
        self.dest_label = ctk.CTkLabel(self.edit_frame, text="Destination Folder Path:")
        self.dest_label.grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")
        self.dest_frame = ctk.CTkFrame(self.edit_frame, fg_color="transparent")
        self.dest_frame.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        self.dest_frame.grid_columnconfigure(0, weight=1)
        self.dest_entry = ctk.CTkEntry(self.dest_frame, width=600)
        self.dest_entry.grid(row=0, column=0, sticky="ew")
        self.dest_browse_btn = ctk.CTkButton(
            self.dest_frame,
            text="Browse",
            width=120,
            command=lambda: self.browse_directory(self.dest_entry),
        )
        self.dest_browse_btn.grid(row=0, column=1, padx=(10, 0))

        # Extensions Input
        self.ext_label = ctk.CTkLabel(self.edit_frame, text="Extensions (comma separated, e.g., .pdf, .docx):")
        self.ext_label.grid(row=6, column=0, padx=20, pady=(10, 5), sticky="w")
        self.ext_entry = ctk.CTkEntry(self.edit_frame, width=600)
        self.ext_entry.grid(row=7, column=0, padx=20, pady=5, sticky="ew")

        # Keywords Input
        self.keyword_label = ctk.CTkLabel(self.edit_frame, text="Keywords (comma separated, e.g., assign, report):")
        self.keyword_label.grid(row=8, column=0, padx=20, pady=(10, 5), sticky="w")
        self.keyword_entry = ctk.CTkEntry(self.edit_frame, width=600)
        self.keyword_entry.grid(row=9, column=0, padx=20, pady=5, sticky="ew")

        # Save & Delete Buttons
        self.btn_frame = ctk.CTkFrame(self.edit_frame, fg_color="transparent")
        self.btn_frame.grid(row=10, column=0, padx=20, pady=30, sticky="w")
        
        self.save_btn = ctk.CTkButton(self.btn_frame, text="Save Configuration", fg_color="green", hover_color="darkgreen", command=self.save_config)
        self.save_btn.grid(row=0, column=0, padx=(0, 10))

        self.del_btn = ctk.CTkButton(self.btn_frame, text="Delete Rule", fg_color="red", hover_color="darkred", command=self.delete_rule)
        self.del_btn.grid(row=0, column=1)

        self.refresh_sidebar()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return {"watch_directory": "", "settle_seconds": 3, "rules": {}, "destinations": {}}

    def refresh_sidebar(self):
        # Clear existing buttons
        for widget in self.rule_list_frame.winfo_children():
            widget.destroy()

        # Create a button for each rule
        for rule_name in self.config_data.get("rules", {}):
            btn = ctk.CTkButton(self.rule_list_frame, text=rule_name, fg_color="transparent", 
                                text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                anchor="w", command=lambda r=rule_name: self.load_rule_into_editor(r))
            btn.pack(pady=2, padx=5, fill="x")

    def load_rule_into_editor(self, rule_name):
        self.current_rule = rule_name
        self.placeholder_label.grid_forget()
        self.edit_frame.grid(row=0, column=0, sticky="nsew")

        # Clear fields
        self.rule_name_entry.delete(0, 'end')
        self.source_entry.delete(0, 'end')
        self.dest_entry.delete(0, 'end')
        self.ext_entry.delete(0, 'end')
        self.keyword_entry.delete(0, 'end')

        # Populate fields
        self.rule_name_entry.insert(0, rule_name)
        self.source_entry.insert(0, self.config_data.get("watch_directory", ""))
        self.dest_entry.insert(0, self.config_data["destinations"].get(rule_name, ""))
        
        exts = self.config_data["rules"][rule_name].get("extensions", [])
        self.ext_entry.insert(0, ", ".join(exts))
        
        keywords = self.config_data["rules"][rule_name].get("keywords", [])
        self.keyword_entry.insert(0, ", ".join(keywords))

    def add_new_rule(self):
        self.current_rule = "NewRule"
        self.placeholder_label.grid_forget()
        self.edit_frame.grid(row=0, column=0, sticky="nsew")
        
        self.rule_name_entry.delete(0, 'end')
        self.source_entry.delete(0, 'end')
        self.dest_entry.delete(0, 'end')
        self.ext_entry.delete(0, 'end')
        self.keyword_entry.delete(0, 'end')
        self.rule_name_entry.insert(0, "NewRule")
        self.source_entry.insert(0, self.config_data.get("watch_directory", ""))

    def browse_directory(self, entry_widget):
        current_path = entry_widget.get().strip()
        initial_dir = os.path.expanduser(current_path) if current_path else os.path.expanduser("~")
        selected_dir = filedialog.askdirectory(initialdir=initial_dir)

        if selected_dir:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, selected_dir)

    def save_config(self):
        if self.persist_config(show_feedback=True):
            messagebox.showinfo("Saved", f"Configuration for '{self.current_rule}' saved successfully!")

    def persist_config(self, show_feedback=False):
        if not self.current_rule:
            if show_feedback:
                messagebox.showerror("Error", "Select or create a rule before saving.")
            return False

        new_name = self.rule_name_entry.get().strip()
        source_dir = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        exts = [x.strip() for x in self.ext_entry.get().split(',') if x.strip()]
        keywords = [x.strip() for x in self.keyword_entry.get().split(',') if x.strip()]

        if not new_name:
            messagebox.showerror("Error", "Rule Name cannot be empty.")
            return False

        if not source_dir:
            messagebox.showerror("Error", "Source Folder Path cannot be empty.")
            return False

        # If name changed, remove the old one
        if self.current_rule != new_name and self.current_rule in self.config_data["rules"]:
            del self.config_data["rules"][self.current_rule]
            if self.current_rule in self.config_data["destinations"]:
                del self.config_data["destinations"][self.current_rule]

        # Update JSON structures
        self.config_data["watch_directory"] = source_dir
        self.config_data["rules"][new_name] = {"extensions": exts, "keywords": keywords}
        self.config_data["destinations"][new_name] = dest

        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config_data, f, indent=2)

        self.current_rule = new_name
        self.refresh_sidebar()
        return True

    def delete_rule(self):
        if self.current_rule and self.current_rule in self.config_data["rules"]:
            del self.config_data["rules"][self.current_rule]
            if self.current_rule in self.config_data["destinations"]:
                del self.config_data["destinations"][self.current_rule]
            
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            
            self.edit_frame.grid_forget()
            self.placeholder_label.grid(row=0, column=0, pady=200)
            self.current_rule = None
            self.refresh_sidebar()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def toggle_sentinel(self):
        if self.sentinel_is_running():
            self.stop_sentinel()
        else:
            self.start_sentinel()

    def start_sentinel(self):
        if self.current_rule and not self.persist_config():
            return

        if not self.config_data.get("watch_directory") or not self.config_data.get("rules"):
            messagebox.showerror(
                "Configuration Required",
                "Add and save at least one rule with a source folder before running Sentinel.",
            )
            return

        if self.sentinel_is_running():
            self.update_run_status("Running", "Stop Sentinel", "red", "darkred")
            return

        main_path = os.path.join(os.path.dirname(__file__), "main.py")
        startupinfo = None
        creationflags = 0

        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        try:
            self.sentinel_process = subprocess.Popen(
                [sys.executable, main_path],
                cwd=os.path.dirname(__file__),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags,
            )
        except OSError as exc:
            self.sentinel_process = None
            self.update_run_status("Failed to start", "Run Sentinel", "green", "darkgreen")
            messagebox.showerror("Launch Failed", f"Could not start Sentinel.\n\n{exc}")
            return

        self.update_run_status("Running", "Stop Sentinel", "red", "darkred")
        self.after(1000, self.poll_sentinel_process)

    def stop_sentinel(self):
        if self.sentinel_process and self.sentinel_process.poll() is None:
            self.sentinel_process.terminate()
            try:
                self.sentinel_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.sentinel_process.kill()
                self.sentinel_process.wait(timeout=5)

        self.sentinel_process = None
        self.update_run_status("Stopped", "Run Sentinel", "green", "darkgreen")

    def sentinel_is_running(self):
        return self.sentinel_process is not None and self.sentinel_process.poll() is None

    def poll_sentinel_process(self):
        if self.sentinel_is_running():
            self.after(1000, self.poll_sentinel_process)
            return

        if self.sentinel_process is not None:
            exit_code = self.sentinel_process.poll()
            self.sentinel_process = None
            self.update_run_status("Stopped", "Run Sentinel", "green", "darkgreen")

            if exit_code not in (0, None):
                messagebox.showwarning(
                    "Sentinel Stopped",
                    f"Sentinel exited with code {exit_code}. Check logs/sentinel.log for details.",
                )

    def update_run_status(self, status_text, button_text, button_color, hover_color):
        self.run_status_label.configure(text=f"Status: {status_text}")
        self.run_btn.configure(text=button_text, fg_color=button_color, hover_color=hover_color)

    def on_close(self):
        self.stop_sentinel()
        self.destroy()

if __name__ == "__main__":
    app = SentinelUI()
    app.mainloop()
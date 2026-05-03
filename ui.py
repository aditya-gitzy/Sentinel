import json
import math
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Set the initial theme
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

PALETTE = {
    "app_bg": ("#ffffff", "#000000"),
    "sidebar": ("#f7f7fb", "#050505"),
    "surface": ("#ffffff", "#080808"),
    "surface_alt": ("#f4f6fb", "#121212"),
    "card": ("#ffffff", "#0b0b0b"),
    "card_soft": ("#fbfbfe", "#101010"),
    "text": ("#111827", "#f8fafc"),
    "muted": ("#5b6475", "#94a3b8"),
    "accent": ("#7c3aed", "#22d3ee"),
    "accent_alt": ("#2563eb", "#a855f7"),
    "accent_soft": ("#e9ddff", "#1a1f34"),
    "success": ("#0f766e", "#14b8a6"),
    "danger": ("#be185d", "#f43f5e"),
}

GLOW_CYCLE = [
    ("#22d3ee", "#22d3ee"),
    ("#3b82f6", "#3b82f6"),
    ("#8b5cf6", "#8b5cf6"),
    ("#ec4899", "#ec4899"),
    ("#f59e0b", "#f59e0b"),
    ("#10b981", "#10b981"),
]

class SentinelUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sentinel Config Manager")
        self.geometry("1040x680")
        self.minsize(980, 620)
        self.configure(fg_color=PALETTE["app_bg"])
        self.button_animations = {}
        self.glow_surfaces = []
        self._glow_tick = 0.0
        
        self.config_data = self.load_config()
        self.current_rule = None

        # --- Grid Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=PALETTE["sidebar"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        self.sidebar_beam = ctk.CTkFrame(
            self.sidebar_frame,
            height=5,
            corner_radius=99,
            fg_color=PALETTE["accent"],
        )
        self.sidebar_beam.grid(row=0, column=0, padx=20, pady=(18, 8), sticky="ew")

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Sentinel",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=PALETTE["text"],
        )
        self.logo_label.grid(row=1, column=0, padx=20, pady=(10, 4), sticky="w")

        self.sidebar_subtitle = ctk.CTkLabel(
            self.sidebar_frame,
            text="Autonomous File Router",
            text_color=PALETTE["muted"],
            font=ctk.CTkFont(size=13),
        )
        self.sidebar_subtitle.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

        # Scrollable frame for rule list
        self.rule_list_frame = ctk.CTkScrollableFrame(
            self.sidebar_frame,
            fg_color=PALETTE["surface_alt"],
            corner_radius=14,
            border_width=1,
            border_color=PALETTE["accent_soft"],
        )
        self.rule_list_frame.grid(row=3, column=0, padx=14, pady=10, sticky="nsew")
        
        self.add_rule_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="+ Add New Rule",
            height=40,
            corner_radius=12,
            fg_color=PALETTE["accent_alt"],
            text_color=PALETTE["text"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
            command=self.add_new_rule,
        )
        self.add_rule_btn.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # Theme Toggle
        self.theme_frame = ctk.CTkFrame(
            self.sidebar_frame,
            corner_radius=14,
            fg_color=PALETTE["surface_alt"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
        )
        self.theme_frame.grid(row=5, column=0, padx=14, pady=(8, 18), sticky="ew")
        self.theme_label = ctk.CTkLabel(
            self.theme_frame,
            text="Appearance",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=PALETTE["text"],
        )
        self.theme_label.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")
        self.theme_switch = ctk.CTkSwitch(
            self.theme_frame,
            text="Dark mode",
            progress_color=self._resolve_color(PALETTE["accent"]),
            button_color=self._resolve_color(PALETTE["accent_alt"]),
            button_hover_color=self._resolve_color(PALETTE["accent"]),
            text_color=PALETTE["text"],
            command=self.toggle_theme,
        )
        self.theme_switch.grid(row=1, column=0, padx=16, pady=(4, 14), sticky="w")
        self.theme_switch.select()

        # --- Main Editing Area ---
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=18,
            fg_color=PALETTE["surface"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
        )
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        self.header_frame = ctk.CTkFrame(
            self.main_frame,
            corner_radius=16,
            fg_color=PALETTE["card"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
        )
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 14), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        self.header_glow = ctk.CTkFrame(
            self.header_frame,
            height=4,
            corner_radius=99,
            fg_color=PALETTE["accent"],
        )
        self.header_glow.grid(row=0, column=0, columnspan=2, padx=20, pady=(14, 8), sticky="ew")

        self.header_title = ctk.CTkLabel(
            self.header_frame,
            text="Watch Folder",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=PALETTE["text"],
        )
        self.header_title.grid(row=1, column=0, padx=20, pady=(4, 4), sticky="w")

        self.status_chip = ctk.CTkLabel(
            self.header_frame,
            text="  LIVE ROUTE  ",
            corner_radius=99,
            fg_color=PALETTE["accent_soft"],
            text_color=PALETTE["accent"],
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        self.status_chip.grid(row=1, column=1, padx=(10, 20), pady=(4, 4), sticky="e")

        self.header_subtitle = ctk.CTkLabel(
            self.header_frame,
            text="Choose the single source folder Sentinel should monitor for incoming files.",
            text_color=PALETTE["muted"],
            font=ctk.CTkFont(size=13),
        )
        self.header_subtitle.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 14), sticky="w")

        self.source_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.source_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 18), sticky="ew")
        self.source_frame.grid_columnconfigure(0, weight=1)
        self.source_entry = ctk.CTkEntry(
            self.source_frame,
            height=42,
            fg_color=PALETTE["surface_alt"],
            border_color=PALETTE["accent_soft"],
            text_color=PALETTE["text"],
        )
        self.source_entry.grid(row=0, column=0, sticky="ew")
        self.source_browse_btn = ctk.CTkButton(
            self.source_frame,
            text="Browse",
            width=110,
            height=40,
            corner_radius=12,
            fg_color=PALETTE["surface_alt"],
            text_color=PALETTE["text"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
            command=lambda: self.browse_directory(self.source_entry),
        )
        self.source_browse_btn.grid(row=0, column=1, padx=(10, 10))
        self.source_save_btn = ctk.CTkButton(
            self.source_frame,
            text="Save Folder",
            width=120,
            height=40,
            corner_radius=12,
            fg_color=PALETTE["success"],
            text_color=PALETTE["text"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
            command=self.save_watch_directory,
        )
        self.source_save_btn.grid(row=0, column=2)

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.rule_section_title = ctk.CTkLabel(
            self.content_frame,
            text="Rule Details",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=PALETTE["text"],
        )
        self.rule_section_title.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.editor_card = ctk.CTkFrame(
            self.content_frame,
            corner_radius=16,
            fg_color=PALETTE["card_soft"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
        )
        self.editor_card.grid(row=1, column=0, sticky="nsew")
        self.editor_card.grid_columnconfigure(0, weight=1)

        # Placeholder message
        self.placeholder_label = ctk.CTkLabel(
            self.editor_card,
            text="Select a rule from the sidebar to edit, or create a new one.",
            font=ctk.CTkFont(size=16),
            text_color=PALETTE["muted"],
        )
        self.placeholder_label.grid(row=0, column=0, pady=180)

        self.edit_frame = ctk.CTkFrame(self.editor_card, fg_color="transparent")
        self.edit_frame.grid_columnconfigure(0, weight=1)
        
        # Rule Name Input
        self.rule_name_label = ctk.CTkLabel(self.edit_frame, text="Rule Name (e.g., CollegeDocs):", text_color=PALETTE["text"])
        self.rule_name_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.rule_name_entry = ctk.CTkEntry(
            self.edit_frame,
            width=400,
            height=42,
            fg_color=PALETTE["surface"],
            border_color=PALETTE["accent_soft"],
            text_color=PALETTE["text"],
        )
        self.rule_name_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        # Destination Input
        self.dest_label = ctk.CTkLabel(self.edit_frame, text="Destination Folder Path:", text_color=PALETTE["text"])
        self.dest_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.dest_frame = ctk.CTkFrame(self.edit_frame, fg_color="transparent")
        self.dest_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.dest_frame.grid_columnconfigure(0, weight=1)
        self.dest_entry = ctk.CTkEntry(
            self.dest_frame,
            height=42,
            fg_color=PALETTE["surface"],
            border_color=PALETTE["accent_soft"],
            text_color=PALETTE["text"],
        )
        self.dest_entry.grid(row=0, column=0, sticky="ew")
        self.dest_browse_btn = ctk.CTkButton(
            self.dest_frame,
            text="Browse",
            width=120,
            height=40,
            corner_radius=12,
            fg_color=PALETTE["surface_alt"],
            text_color=PALETTE["text"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
            command=lambda: self.browse_directory(self.dest_entry),
        )
        self.dest_browse_btn.grid(row=0, column=1, padx=(10, 0))

        # Extensions Input
        self.ext_label = ctk.CTkLabel(self.edit_frame, text="Extensions (comma separated, e.g., .pdf, .docx):", text_color=PALETTE["text"])
        self.ext_label.grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")
        self.ext_entry = ctk.CTkEntry(
            self.edit_frame,
            width=600,
            height=42,
            fg_color=PALETTE["surface"],
            border_color=PALETTE["accent_soft"],
            text_color=PALETTE["text"],
        )
        self.ext_entry.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        # Keywords Input
        self.keyword_label = ctk.CTkLabel(self.edit_frame, text="Keywords (comma separated, e.g., assign, report):", text_color=PALETTE["text"])
        self.keyword_label.grid(row=6, column=0, padx=20, pady=(10, 5), sticky="w")
        self.keyword_entry = ctk.CTkEntry(
            self.edit_frame,
            width=600,
            height=42,
            fg_color=PALETTE["surface"],
            border_color=PALETTE["accent_soft"],
            text_color=PALETTE["text"],
        )
        self.keyword_entry.grid(row=7, column=0, padx=20, pady=5, sticky="ew")

        # Save & Delete Buttons
        self.btn_frame = ctk.CTkFrame(self.edit_frame, fg_color="transparent")
        self.btn_frame.grid(row=8, column=0, padx=20, pady=30, sticky="w")
        
        self.save_btn = ctk.CTkButton(
            self.btn_frame,
            text="Save Rule",
            height=40,
            corner_radius=12,
            fg_color=PALETTE["success"],
            text_color=PALETTE["text"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
            command=self.save_config,
        )
        self.save_btn.grid(row=0, column=0, padx=(0, 10))

        self.del_btn = ctk.CTkButton(
            self.btn_frame,
            text="Delete Rule",
            height=40,
            corner_radius=12,
            fg_color=PALETTE["danger"],
            text_color=PALETTE["text"],
            border_width=1,
            border_color=PALETTE["accent_soft"],
            command=self.delete_rule,
        )
        self.del_btn.grid(row=0, column=1)

        self.source_entry.insert(0, self.config_data.get("watch_directory", ""))
        self.refresh_sidebar()
        self._register_animated_button(self.add_rule_btn, PALETTE["accent_alt"], PALETTE["accent"])
        self._register_animated_button(self.source_browse_btn, PALETTE["surface_alt"], PALETTE["accent_soft"])
        self._register_animated_button(self.source_save_btn, PALETTE["success"], PALETTE["accent"])
        self._register_animated_button(self.dest_browse_btn, PALETTE["surface_alt"], PALETTE["accent_soft"])
        self._register_animated_button(self.save_btn, PALETTE["success"], PALETTE["accent"])
        self._register_animated_button(self.del_btn, PALETTE["danger"], ("#fca5a5", "#fb7185"))
        self._register_glow_surface(self.main_frame, PALETTE["accent_soft"], PALETTE["accent"], phase=0.0, cycle_speed=0.55)
        self._register_glow_surface(self.header_frame, PALETTE["accent_soft"], PALETTE["accent_alt"], phase=0.8, cycle_speed=0.72)
        self._register_glow_surface(self.editor_card, PALETTE["accent_soft"], PALETTE["accent"], phase=1.6, cycle_speed=0.66)
        self._register_glow_surface(self.theme_frame, PALETTE["accent_soft"], PALETTE["accent_alt"], phase=2.2, cycle_speed=0.84)
        self._register_glow_surface(self.sidebar_frame, PALETTE["accent_soft"], PALETTE["accent_alt"], phase=2.8, cycle_speed=0.48)
        self._register_glow_surface(self.add_rule_btn, PALETTE["accent_soft"], PALETTE["accent"], phase=0.3, cycle_speed=1.1)
        self._register_glow_surface(self.source_browse_btn, PALETTE["accent_soft"], PALETTE["accent"], phase=1.1, cycle_speed=1.25)
        self._register_glow_surface(self.source_save_btn, PALETTE["accent_soft"], PALETTE["accent"], phase=2.0, cycle_speed=1.05)
        self._register_glow_surface(self.dest_browse_btn, PALETTE["accent_soft"], PALETTE["accent"], phase=2.9, cycle_speed=1.18)
        self._register_glow_surface(self.save_btn, PALETTE["accent_soft"], PALETTE["accent"], phase=3.7, cycle_speed=1.08)
        self._register_glow_surface(self.del_btn, PALETTE["accent_soft"], PALETTE["accent"], phase=4.5, cycle_speed=1.22)
        self.after(40, self._animate_glow_surfaces)
        self.attributes("-alpha", 0.0)
        self.after(20, self._fade_in_window)

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return {"watch_directory": "", "settle_seconds": 3, "rules": {}, "destinations": {}}

    def refresh_sidebar(self):
        # Clear existing buttons
        for widget in self.rule_list_frame.winfo_children():
            if widget in self.button_animations:
                animation = self.button_animations.pop(widget)
                if animation["job"] is not None:
                    self.after_cancel(animation["job"])
            self.glow_surfaces = [surface for surface in self.glow_surfaces if surface["widget"] != widget]
            widget.destroy()

        # Create a button for each rule
        for rule_name in self.config_data.get("rules", {}):
            btn = ctk.CTkButton(
                self.rule_list_frame,
                text=rule_name,
                fg_color="transparent",
                text_color=PALETTE["text"],
                corner_radius=10,
                height=36,
                anchor="w",
                border_width=1,
                border_color=PALETTE["accent_soft"],
                command=lambda r=rule_name: self.load_rule_into_editor(r),
            )
            btn.pack(pady=2, padx=5, fill="x")
            self._register_animated_button(
                btn,
                ("#eef2ff", "#141414"),
                ("#dbeafe", "#202020"),
            )
            self._register_glow_surface(btn, PALETTE["accent_soft"], PALETTE["accent"], phase=len(self.glow_surfaces) * 0.37, cycle_speed=1.35)

    def load_rule_into_editor(self, rule_name):
        self.current_rule = rule_name
        self.placeholder_label.grid_forget()
        self.edit_frame.grid(row=0, column=0, sticky="nsew")

        # Clear fields
        self.rule_name_entry.delete(0, 'end')
        self.dest_entry.delete(0, 'end')
        self.ext_entry.delete(0, 'end')
        self.keyword_entry.delete(0, 'end')

        # Populate fields
        self.rule_name_entry.insert(0, rule_name)
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
        self.dest_entry.delete(0, 'end')
        self.ext_entry.delete(0, 'end')
        self.keyword_entry.delete(0, 'end')
        self.rule_name_entry.insert(0, "NewRule")

    def browse_directory(self, entry_widget):
        current_path = entry_widget.get().strip()
        initial_dir = os.path.expanduser(current_path) if current_path else os.path.expanduser("~")
        selected_dir = filedialog.askdirectory(initialdir=initial_dir)

        if selected_dir:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, selected_dir)

    def write_config(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config_data, f, indent=2)

    def _resolve_color(self, color_value):
        if isinstance(color_value, (tuple, list)):
            return color_value[1] if ctk.get_appearance_mode() == "Dark" else color_value[0]
        return color_value

    def _hex_to_rgb(self, value):
        value = value.lstrip("#")
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb):
        return "#{:02x}{:02x}{:02x}".format(*[max(0, min(255, int(channel))) for channel in rgb])

    def _blend_color(self, start, end, progress):
        start_rgb = self._hex_to_rgb(self._resolve_color(start))
        end_rgb = self._hex_to_rgb(self._resolve_color(end))
        blended = tuple(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * progress for i in range(3))
        return self._rgb_to_hex(blended)

    def _cycle_color(self, offset):
        cycle = [self._resolve_color(color) for color in GLOW_CYCLE]
        position = offset % len(cycle)
        base_index = int(position)
        next_index = (base_index + 1) % len(cycle)
        progress = position - base_index
        return self._blend_color(cycle[base_index], cycle[next_index], progress)

    def _register_animated_button(self, button, idle_color, hover_color, text_idle=None, text_hover=None):
        self.button_animations[button] = {
            "idle_color": idle_color,
            "hover_color": hover_color,
            "text_idle": text_idle or PALETTE["text"],
            "text_hover": text_hover or PALETTE["text"],
            "progress": 0.0,
            "target": 0.0,
            "job": None,
        }
        button.configure(hover=False)
        button.bind("<Enter>", lambda _event, widget=button: self._set_button_target(widget, 1.0), add="+")
        button.bind("<Leave>", lambda _event, widget=button: self._set_button_target(widget, 0.0), add="+")
        self._apply_button_state(button)

    def _apply_button_state(self, button):
        state = self.button_animations.get(button)
        if not state:
            return
        fg_color = self._blend_color(state["idle_color"], state["hover_color"], state["progress"])
        text_color = self._blend_color(state["text_idle"], state["text_hover"], state["progress"])
        button.configure(fg_color=fg_color, text_color=text_color)

    def _set_button_target(self, button, target):
        state = self.button_animations.get(button)
        if not state:
            return
        state["target"] = target
        if state["job"] is None:
            state["job"] = self.after(16, lambda widget=button: self._step_button_animation(widget))

    def _step_button_animation(self, button):
        state = self.button_animations.get(button)
        if not state:
            return
        state["progress"] += (state["target"] - state["progress"]) * 0.28
        if abs(state["target"] - state["progress"]) < 0.02:
            state["progress"] = state["target"]
        self._apply_button_state(button)
        if state["progress"] != state["target"]:
            state["job"] = self.after(16, lambda widget=button: self._step_button_animation(widget))
        else:
            state["job"] = None

    def _register_glow_surface(self, widget, idle_border, active_border, phase=0.0, cycle_speed=1.0):
        self.glow_surfaces.append(
            {
                "widget": widget,
                "idle_border": idle_border,
                "active_border": active_border,
                "phase": phase,
                "cycle_speed": cycle_speed,
            }
        )

    def _animate_glow_surfaces(self):
        self._glow_tick += 0.12
        for surface in self.glow_surfaces:
            if not surface["widget"].winfo_exists():
                continue
            wave = (math.sin(self._glow_tick + surface["phase"]) + 1) / 2
            rainbow = self._cycle_color(self._glow_tick * surface["cycle_speed"] + surface["phase"])
            active_color = self._blend_color(surface["active_border"], rainbow, 0.72)
            border_color = self._blend_color(surface["idle_border"], active_color, 0.28 + wave * 0.52)
            surface["widget"].configure(border_color=border_color)
        beam_color = self._cycle_color(self._glow_tick * 0.9)
        beam_alt = self._cycle_color(self._glow_tick * 0.9 + 1.75)
        self.sidebar_beam.configure(fg_color=beam_color)
        self.header_glow.configure(fg_color=beam_alt)
        self.status_chip.configure(
            text_color=beam_color,
            fg_color=self._blend_color(PALETTE["accent_soft"], beam_alt, 0.35),
        )
        self.after(32, self._animate_glow_surfaces)

    def _fade_in_window(self, alpha=0.0):
        next_alpha = min(alpha + 0.12, 1.0)
        self.attributes("-alpha", next_alpha)
        if next_alpha < 1.0:
            self.after(24, lambda: self._fade_in_window(next_alpha))

    def _refresh_visual_theme(self):
        self.configure(fg_color=PALETTE["app_bg"])
        self.theme_switch.configure(
            progress_color=self._resolve_color(PALETTE["accent"]),
            button_color=self._resolve_color(PALETTE["accent_alt"]),
            button_hover_color=self._resolve_color(PALETTE["accent"]),
        )
        for button in list(self.button_animations):
            if button.winfo_exists():
                self._apply_button_state(button)
            else:
                self.button_animations.pop(button, None)

    def save_watch_directory(self):
        source_dir = self.source_entry.get().strip()

        if not source_dir:
            messagebox.showerror("Error", "Source Folder Path cannot be empty.")
            return

        self.config_data["watch_directory"] = source_dir
        self.write_config()
        messagebox.showinfo("Saved", "Watch folder updated successfully!")

    def save_config(self):
        if not self.current_rule:
            return

        new_name = self.rule_name_entry.get().strip()
        dest = self.dest_entry.get().strip()
        exts = [x.strip() for x in self.ext_entry.get().split(',') if x.strip()]
        keywords = [x.strip() for x in self.keyword_entry.get().split(',') if x.strip()]

        if not new_name:
            messagebox.showerror("Error", "Rule Name cannot be empty.")
            return

        # If name changed, remove the old one
        if self.current_rule != new_name and self.current_rule in self.config_data["rules"]:
            del self.config_data["rules"][self.current_rule]
            if self.current_rule in self.config_data["destinations"]:
                del self.config_data["destinations"][self.current_rule]

        # Update JSON structures
        self.config_data["rules"][new_name] = {"extensions": exts, "keywords": keywords}
        self.config_data["destinations"][new_name] = dest

        # Write to file
        self.write_config()

        self.current_rule = new_name
        self.refresh_sidebar()
        
        # Super simple status feedback
        messagebox.showinfo("Saved", f"Configuration for '{new_name}' saved successfully!")

    def delete_rule(self):
        if self.current_rule and self.current_rule in self.config_data["rules"]:
            del self.config_data["rules"][self.current_rule]
            if self.current_rule in self.config_data["destinations"]:
                del self.config_data["destinations"][self.current_rule]
            
            self.write_config()
            
            self.edit_frame.grid_forget()
            self.placeholder_label.grid(row=0, column=0, pady=200)
            self.current_rule = None
            self.refresh_sidebar()

    def toggle_theme(self):
        mode = "Dark" if self.theme_switch.get() == 1 else "Light"
        ctk.set_appearance_mode(mode)
        self._refresh_visual_theme()

if __name__ == "__main__":
    app = SentinelUI()
    app.mainloop()

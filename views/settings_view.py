import customtkinter as ctk
from tkinter import messagebox


class SettingsView:
    def __init__(self, parent, config, update_callback):
        self.parent = parent
        self.config = config
        self.update_config = update_callback
        self._setup_ui()
    
    def _setup_ui(self):
        content = ctk.CTkFrame(self.parent)
        content.pack(expand=True, fill="both", padx=40, pady=40)
        
        title = ctk.CTkLabel(
            content,
            text="⚙️ Configuración Avanzada",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)
        
        self._create_controls_section(content)
        self._create_behavior_section(content)
        self._create_sensitivity_section(content)
        
        self._create_save_button(content)
    
    def _create_controls_section(self, parent):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(pady=20, padx=30, fill="x")
        
        title = ctk.CTkLabel(
            section,
            text="🎮 Controles",
            font=("Arial", 16, "bold")
        )
        title.pack(anchor="w", pady=(0, 10))
        
        hotkey_frame = ctk.CTkFrame(section, fg_color="transparent")
        hotkey_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            hotkey_frame,
            text="Atajo para mostrar/ocultar:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 20))
        
        hotkey_display = ctk.CTkEntry(
            hotkey_frame,
            width=150,
            font=("Arial", 12),
            justify="center"
        )
        hotkey_display.insert(0, "Ctrl + B")
        hotkey_display.configure(state="readonly")
        hotkey_display.pack(side="left")
    
    def _create_behavior_section(self, parent):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(pady=20, padx=30, fill="x")
        
        title = ctk.CTkLabel(
            section,
            text="⚡ Comportamiento",
            font=("Arial", 16, "bold")
        )
        title.pack(anchor="w", pady=(0, 10))
        
        self.start_hidden_var = ctk.BooleanVar(value=self.config["start_hidden"])
        self.always_on_top_var = ctk.BooleanVar(value=self.config["always_on_top"])
        
        ctk.CTkCheckBox(
            section,
            text="Iniciar minimizado",
            variable=self.start_hidden_var,
            font=("Arial", 12),
            command=self._on_start_hidden_change
        ).pack(anchor="w", pady=5)
        
        ctk.CTkCheckBox(
            section,
            text="Ventana siempre encima",
            variable=self.always_on_top_var,
            font=("Arial", 12),
            command=self._on_always_on_top_change
        ).pack(anchor="w", pady=5)
    
    def _create_sensitivity_section(self, parent):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(pady=20, padx=30, fill="x")
        
        title = ctk.CTkLabel(
            section,
            text="🎯 Sensibilidad Global",
            font=("Arial", 16, "bold")
        )
        title.pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(
            section,
            text="Fuerza del anti-recoil:",
            font=("Arial", 12)
        ).pack(anchor="w", pady=5)
        
        self.sensitivity_slider = ctk.CTkSlider(
            section,
            from_=1,
            to=10,
            number_of_steps=9,
            width=300,
            command=self._on_sensitivity_change
        )
        self.sensitivity_slider.set(self.config["global_sensitivity"])
        self.sensitivity_slider.pack(anchor="w", pady=5)
        
        self.sensitivity_label = ctk.CTkLabel(
            section,
            text=f"Nivel: {self.config['global_sensitivity']}/10",
            font=("Arial", 11),
            text_color="gray"
        )
        self.sensitivity_label.pack(anchor="w")
    
    def _create_save_button(self, parent):
        ctk.CTkButton(
            parent,
            text="💾 Guardar Configuración",
            fg_color="#4CC9F0",
            hover_color="#4895EF",
            font=("Arial", 14),
            height=40,
            command=self._save_settings
        ).pack(pady=30)
    
    def _on_start_hidden_change(self):
        self.update_config("start_hidden", self.start_hidden_var.get())
        print(f"Inicio minimizado: {'Activado' if self.start_hidden_var.get() else 'Desactivado'}")
    
    def _on_always_on_top_change(self):
        self.update_config("always_on_top", self.always_on_top_var.get())
        print(f"Ventana siempre encima: {'Activado' if self.always_on_top_var.get() else 'Desactivado'}")
    
    def _on_sensitivity_change(self, value):
        int_value = int(float(value))
        self.update_config("global_sensitivity", int_value)
        self.sensitivity_label.configure(text=f"Nivel: {int_value}/10")
    
    def _save_settings(self):
        messagebox.showinfo(
            "Configuración Guardada",
            "La configuración ha sido guardada exitosamente.\n\n"
            "Los cambios se aplicarán la próxima vez que inicies la aplicación."
        )
        print("Configuración guardada")
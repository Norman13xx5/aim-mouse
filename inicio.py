import customtkinter as ctk
from config_manager import ConfigManager
from aim_assist import aim_controller
import threading

class InicioView:
    def __init__(self, parent, volver_callback):
        self.parent = parent
        self.volver_callback = volver_callback
        self.config_manager = ConfigManager()
        
        # Cargar configuraciones disponibles dinámicamente
        self.opciones_dependientes = self.config_manager.get_available_configs()
        
        # Asegurar que aim assist esté corriendo en segundo plano
        self.ensure_aim_assist_running()
        
        self.mostrar()

    def ensure_aim_assist_running(self):
        """Asegurarse que el aim assist esté ejecutándose en segundo plano"""
        if not hasattr(self, '_aim_started'):
            # Iniciar aim assist en segundo plano
            aim_controller.start()
            self._aim_started = True

    def limpiar(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

    def mostrar(self):
        self.limpiar()

        titulo = ctk.CTkLabel(
            self.parent,
            text="Control de Anti-Recoil",
            font=("Arial", 24, "bold")
        )
        titulo.pack(pady=20)

        # ===== PANEL DE CONFIGURACIÓN =====
        config_frame = ctk.CTkFrame(self.parent)
        config_frame.pack(pady=10, padx=20, fill="x")

        # SELECT SUPERIOR (Categoría)
        lbl_select1 = ctk.CTkLabel(config_frame, text="Categoría del arma:")
        lbl_select1.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.select_principal = ctk.CTkOptionMenu(
            config_frame,
            values=list(self.opciones_dependientes.keys()),
            command=self.actualizar_select_secundario,
            width=200
        )
        self.select_principal.grid(row=0, column=1, padx=10, pady=10)

        # SELECT INFERIOR (Configuración específica)
        lbl_select2 = ctk.CTkLabel(config_frame, text="Configuración:")
        lbl_select2.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.select_secundario = ctk.CTkOptionMenu(
            config_frame,
            values=[],
            width=200
        )
        self.select_secundario.grid(row=1, column=1, padx=10, pady=10)

        # Botón para cargar configuración
        btn_cargar = ctk.CTkButton(
            config_frame,
            text="Cargar Configuración",
            width=150,
            command=self.cargar_configuracion
        )
        btn_cargar.grid(row=2, column=0, columnspan=2, pady=15)

        # Inicializar valores si hay opciones disponibles
        if self.opciones_dependientes:
            primera_opcion = list(self.opciones_dependientes.keys())[0]
            self.select_principal.set(primera_opcion)
            self.actualizar_select_secundario(primera_opcion)

        # ===== PANEL DE CONTROL =====
        control_frame = ctk.CTkFrame(self.parent)
        control_frame.pack(pady=20, padx=20, fill="x")

        # Estado actual
        self.status_label = ctk.CTkLabel(
            control_frame,
            text="Estado: Preparado",
            font=("Arial", 14)
        )
        self.status_label.pack(pady=10)

        # Indicador de estado
        self.active_indicator = ctk.CTkLabel(
            control_frame,
            text="●",
            font=("Arial", 24),
            text_color="red"
        )
        self.active_indicator.pack()

        # Botones de control
        btn_control_frame = ctk.CTkFrame(control_frame)
        btn_control_frame.pack(pady=15)

        self.btn_toggle = ctk.CTkButton(
            btn_control_frame,
            text="Activar Aim Assist",
            width=150,
            fg_color="green",
            command=self.toggle_aim_assist
        )
        self.btn_toggle.pack(side="left", padx=5)

        btn_info = ctk.CTkButton(
            btn_control_frame,
            text="Instrucciones",
            width=150,
            fg_color="blue",
            command=self.mostrar_instrucciones
        )
        btn_info.pack(side="left", padx=5)

        # ===== INFORMACIÓN =====
        info_frame = ctk.CTkFrame(self.parent)
        info_frame.pack(pady=10, padx=20, fill="x")

        info_text = """
        INSTRUCCIONES:
        1. Selecciona categoría y configuración
        2. Haz clic en 'Cargar Configuración'
        3. Activa el Aim Assist
        4. En el juego: Presiona Num Lock para activar/desactivar
        5. Mientras juegas: Mantén CLICK DERECHO para apuntar
        6. Al disparar (CLICK IZQUIERDO): Se aplica anti-recoil automático
        """
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Arial", 11),
            justify="left"
        )
        info_label.pack(pady=10)

        # ===== BOTÓN VOLVER =====
        btn_atras = ctk.CTkButton(
            self.parent,
            text="Volver al Menú",
            width=200,
            fg_color="gray",
            command=self.volver
        )
        btn_atras.pack(pady=10)

        # Actualizar estado periódicamente
        self.actualizar_estado()

    def actualizar_select_secundario(self, opcion_seleccionada):
        nuevas_opciones = self.opciones_dependientes.get(opcion_seleccionada, [])
        self.select_secundario.configure(values=nuevas_opciones)
        
        if nuevas_opciones:
            self.select_secundario.set(nuevas_opciones[0])

    def cargar_configuracion(self):
        """Cargar la configuración seleccionada en el aim assist"""
        categoria = self.select_principal.get()
        config_nombre = self.select_secundario.get()
        
        if not categoria or not config_nombre:
            print("Por favor, selecciona ambas opciones")
            return
        
        try:
            config_data = self.config_manager.load_config(categoria, config_nombre)
            
            # Pasar la configuración al aim assist
            aim_controller.set_config(config_data)
            
            # Actualizar interfaz
            self.status_label.configure(
                text=f"Configurado: {config_nombre}",
                text_color="yellow"
            )
            
            print(f"Configuración '{config_nombre}' cargada exitosamente")
            
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            self.status_label.configure(
                text=f"Error: {str(e)[:30]}...",
                text_color="red"
            )

    def toggle_aim_assist(self):
        """Activar/desactivar el aim assist"""
        if aim_controller.enabled:
            aim_controller.toggle(False)
            self.btn_toggle.configure(text="Activar Aim Assist", fg_color="green")
            self.active_indicator.configure(text_color="red")
        else:
            aim_controller.toggle(True)
            self.btn_toggle.configure(text="Desactivar Aim Assist", fg_color="red")
            self.active_indicator.configure(text_color="green")

    def actualizar_estado(self):
        """Actualizar el estado en la interfaz periódicamente"""
        if aim_controller.enabled:
            self.active_indicator.configure(text_color="green")
        else:
            self.active_indicator.configure(text_color="red")
        
        # Programar próxima actualización
        self.parent.after(500, self.actualizar_estado)

    def mostrar_instrucciones(self):
        from tkinter import messagebox
        messagebox.showinfo(
            "Cómo usar el Anti-Recoil",
            "1. El aim assist corre en segundo plano siempre\n"
            "2. TOGGLE: Presiona NUM LOCK para activar/desactivar\n"
            "3. EN EL JUEGO:\n"
            "   - Mantén CLICK DERECHO para apuntar\n"
            "   - Presiona CLICK IZQUIERDO para disparar\n"
            "   - El anti-recoil se aplica AUTOMÁTICAMENTE\n"
            "   - El mouse se moverá hacia abajo compensando el recoil"
        )

    def volver(self):
        """Volver al menú principal"""
        # No detenemos el aim assist, sigue en segundo plano
        self.volver_callback()
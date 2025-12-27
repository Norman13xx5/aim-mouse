import customtkinter as ctk
from tkinter import messagebox, simpledialog
import os
import yaml

class EditorConfigView:
    def __init__(self, parent, volver_callback):
        self.parent = parent
        self.volver_callback = volver_callback
        
        # Variables para formulario
        self.current_category = None
        self.current_config_name = None
        self.edit_mode = False
        self.loading = False
        
        # Inicializar UI
        self.mostrar()

    def limpiar(self):
        """Limpiar contenido del frame"""
        for widget in self.parent.winfo_children():
            widget.destroy()

    def mostrar(self):
        """Mostrar la interfaz del editor"""
        self.limpiar()
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # ===== COLUMNA IZQUIERDA - NAVEGACIÓN =====
        self.left_frame = ctk.CTkFrame(self.main_frame, width=280, corner_radius=10)
        self.left_frame.pack(side="left", fill="y", padx=(0, 10))
        self.left_frame.pack_propagate(False)
        
        # Título
        nav_title = ctk.CTkLabel(
            self.left_frame,
            text="📁 Configuraciones",
            font=("Arial", 18, "bold")
        )
        nav_title.pack(pady=(15, 10))
        
        # Sección de Juegos
        games_section = ctk.CTkFrame(self.left_frame)
        games_section.pack(fill="x", padx=15, pady=10)
        
        lbl_games = ctk.CTkLabel(
            games_section,
            text="JUEGOS:",
            font=("Arial", 11, "bold"),
            text_color="#4CC9F0"
        )
        lbl_games.pack(anchor="w", pady=(0, 5))
        
        # Frame para selector de juego
        game_select_frame = ctk.CTkFrame(games_section, fg_color="transparent")
        game_select_frame.pack(fill="x", pady=5)
        
        self.game_var = ctk.StringVar()
        self.game_select = ctk.CTkOptionMenu(
            game_select_frame,
            values=["Cargando..."],
            variable=self.game_var,
            command=self.on_juego_seleccionado,
            width=150
        )
        self.game_select.pack(side="left", padx=(0, 10))
        
        # Botón para nuevo juego
        btn_new_game = ctk.CTkButton(
            game_select_frame,
            text="+",
            width=30,
            height=30,
            fg_color="#7209B7",
            hover_color="#560BAD",
            command=self.crear_nuevo_juego
        )
        btn_new_game.pack(side="left")
        
        # Separador
        separator1 = ctk.CTkFrame(self.left_frame, height=1, fg_color="#333333")
        separator1.pack(fill="x", padx=15, pady=10)
        
        # Título de configuraciones
        lbl_configs = ctk.CTkLabel(
            self.left_frame,
            text="CONFIGURACIONES:",
            font=("Arial", 11, "bold"),
            text_color="#4CC9F0"
        )
        lbl_configs.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Frame scrollable para configuraciones
        self.configs_scrollable = ctk.CTkScrollableFrame(
            self.left_frame, 
            height=300,
            fg_color="transparent"
        )
        self.configs_scrollable.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Separador inferior
        separator2 = ctk.CTkFrame(self.left_frame, height=1, fg_color="#333333")
        separator2.pack(fill="x", padx=15, pady=(10, 5))
        
        # Botón nueva configuración
        btn_new_config = ctk.CTkButton(
            self.left_frame,
            text="📄 NUEVA CONFIGURACIÓN",
            fg_color="#4CC9F0",
            hover_color="#4895EF",
            height=40,
            font=("Arial", 12, "bold"),
            command=self.nueva_configuracion
        )
        btn_new_config.pack(fill="x", padx=15, pady=10)
        
        # Estado de carga
        self.loading_label = ctk.CTkLabel(
            self.left_frame,
            text="",
            font=("Arial", 10),
            text_color="gray"
        )
        self.loading_label.pack(pady=5)
        
        # ===== COLUMNA DERECHA - EDITOR =====
        self.right_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.right_frame.pack(side="right", fill="both", expand=True)
        
        # Título dinámico
        self.editor_title = ctk.CTkLabel(
            self.right_frame,
            text="EDITOR DE CONFIGURACIÓN",
            font=("Arial", 20, "bold"),
            text_color="#4CC9F0"
        )
        self.editor_title.pack(pady=(15, 10))
        
        # Frame scrollable para el formulario
        self.form_scrollable = ctk.CTkScrollableFrame(
            self.right_frame,
            fg_color="transparent"
        )
        self.form_scrollable.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Crear formulario
        self.crear_formulario()
        
        # Cargar datos iniciales
        self.cargar_datos_iniciales()

    def crear_formulario(self):
        """Crear el formulario de configuración usando solo pack"""
        # ===== SECCIÓN: INFORMACIÓN BÁSICA =====
        basic_frame = ctk.CTkFrame(self.form_scrollable, corner_radius=10)
        basic_frame.pack(fill="x", padx=5, pady=5)
        
        lbl_basic = ctk.CTkLabel(
            basic_frame,
            text="📝 INFORMACIÓN BÁSICA",
            font=("Arial", 14, "bold")
        )
        lbl_basic.pack(anchor="w", padx=15, pady=10)
        
        # Frame para nombre
        name_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=5)
        
        lbl_name = ctk.CTkLabel(name_frame, text="Nombre:", width=80)
        lbl_name.pack(side="left", padx=(0, 10))
        
        self.entry_name = ctk.CTkEntry(
            name_frame,
            placeholder_text="Ej: Twitch F2"
        )
        self.entry_name.pack(side="left", fill="x", expand=True)
        
        # Frame para descripción
        desc_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        desc_frame.pack(fill="x", padx=15, pady=10)
        
        lbl_desc = ctk.CTkLabel(desc_frame, text="Descripción:", width=80)
        lbl_desc.pack(side="left", padx=(0, 10), anchor="n")
        
        self.text_desc = ctk.CTkTextbox(desc_frame, height=60)
        self.text_desc.pack(side="left", fill="x", expand=True)
        
        # ===== SECCIÓN: RECOIL =====
        recoil_frame = ctk.CTkFrame(self.form_scrollable, corner_radius=10)
        recoil_frame.pack(fill="x", padx=5, pady=5)
        
        lbl_recoil = ctk.CTkLabel(
            recoil_frame,
            text="🎯 RECOIL",
            font=("Arial", 14, "bold")
        )
        lbl_recoil.pack(anchor="w", padx=15, pady=10)
        
        # Frame para vertical
        vertical_frame = ctk.CTkFrame(recoil_frame, fg_color="transparent")
        vertical_frame.pack(fill="x", padx=15, pady=5)
        
        lbl_vertical = ctk.CTkLabel(vertical_frame, text="Vertical:", font=("Arial", 11, "bold"))
        lbl_vertical.pack(anchor="w", pady=(0, 5))
        
        # Subframe para min/max vertical
        minmax_frame = ctk.CTkFrame(vertical_frame, fg_color="transparent")
        minmax_frame.pack(fill="x", pady=5)
        
        lbl_min_v = ctk.CTkLabel(minmax_frame, text="Mínimo:", width=60)
        lbl_min_v.pack(side="left", padx=(0, 10))
        
        self.entry_min_vertical = ctk.CTkEntry(minmax_frame, width=100)
        self.entry_min_vertical.pack(side="left", padx=(0, 20))
        
        lbl_max_v = ctk.CTkLabel(minmax_frame, text="Máximo:", width=60)
        lbl_max_v.pack(side="left", padx=(0, 10))
        
        self.entry_max_vertical = ctk.CTkEntry(minmax_frame, width=100)
        self.entry_max_vertical.pack(side="left")
        
        # Frame para horizontal
        horizontal_frame = ctk.CTkFrame(recoil_frame, fg_color="transparent")
        horizontal_frame.pack(fill="x", padx=15, pady=10)
        
        lbl_horizontal = ctk.CTkLabel(horizontal_frame, text="Horizontal:", font=("Arial", 11, "bold"))
        lbl_horizontal.pack(anchor="w", pady=(0, 5))
        
        # Subframe para rango horizontal
        horiz_frame = ctk.CTkFrame(horizontal_frame, fg_color="transparent")
        horiz_frame.pack(fill="x", pady=5)
        
        lbl_horiz = ctk.CTkLabel(horiz_frame, text="Rango (±):", width=80)
        lbl_horiz.pack(side="left", padx=(0, 10))
        
        self.entry_horizontal = ctk.CTkEntry(horiz_frame, width=100)
        self.entry_horizontal.pack(side="left")
        
        lbl_horiz_desc = ctk.CTkLabel(
            horiz_frame,
            text="Valor absoluto para movimiento izquierda/derecha",
            font=("Arial", 9),
            text_color="gray"
        )
        lbl_horiz_desc.pack(side="left", padx=(10, 0))
        
        # ===== SECCIÓN: CADENCIA =====
        fire_frame = ctk.CTkFrame(self.form_scrollable, corner_radius=10)
        fire_frame.pack(fill="x", padx=5, pady=5)
        
        lbl_fire = ctk.CTkLabel(
            fire_frame,
            text="⚡ CADENCIA",
            font=("Arial", 14, "bold")
        )
        lbl_fire.pack(anchor="w", padx=15, pady=10)
        
        # Frame para cadencia mínima
        min_rate_frame = ctk.CTkFrame(fire_frame, fg_color="transparent")
        min_rate_frame.pack(fill="x", padx=15, pady=5)
        
        lbl_min_rate = ctk.CTkLabel(min_rate_frame, text="Tiempo mínimo (s):", width=120)
        lbl_min_rate.pack(side="left", padx=(0, 10))
        
        self.entry_min_rate = ctk.CTkEntry(min_rate_frame, width=100)
        self.entry_min_rate.pack(side="left")
        
        # Frame para cadencia máxima
        max_rate_frame = ctk.CTkFrame(fire_frame, fg_color="transparent")
        max_rate_frame.pack(fill="x", padx=15, pady=5)
        
        lbl_max_rate = ctk.CTkLabel(max_rate_frame, text="Tiempo máximo (s):", width=120)
        lbl_max_rate.pack(side="left", padx=(0, 10))
        
        self.entry_max_rate = ctk.CTkEntry(max_rate_frame, width=100)
        self.entry_max_rate.pack(side="left")
        
        # ===== SECCIÓN: AVANZADO =====
        advanced_frame = ctk.CTkFrame(self.form_scrollable, corner_radius=10)
        advanced_frame.pack(fill="x", padx=5, pady=5)
        
        lbl_advanced = ctk.CTkLabel(
            advanced_frame,
            text="🔧 AVANZADO",
            font=("Arial", 14, "bold")
        )
        lbl_advanced.pack(anchor="w", padx=15, pady=10)
        
        # Frame para incremento
        inc_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        inc_frame.pack(fill="x", padx=15, pady=5)
        
        lbl_increment = ctk.CTkLabel(inc_frame, text="Incremento progresivo:", width=140)
        lbl_increment.pack(side="left", padx=(0, 10))
        
        self.entry_increment = ctk.CTkEntry(inc_frame, width=100)
        self.entry_increment.pack(side="left")
        
        # Frame para límite
        limit_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
        limit_frame.pack(fill="x", padx=15, pady=5)
        
        lbl_limit = ctk.CTkLabel(limit_frame, text="Límite máximo:", width=140)
        lbl_limit.pack(side="left", padx=(0, 10))
        
        self.entry_limit = ctk.CTkEntry(limit_frame, width=100)
        self.entry_limit.pack(side="left")
        
        # ===== BOTONES DE ACCIÓN =====
        action_frame = ctk.CTkFrame(self.form_scrollable, fg_color="transparent")
        action_frame.pack(fill="x", padx=5, pady=20)
        
        # Frame para botones principales
        btn_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.btn_save = ctk.CTkButton(
            btn_frame,
            text="💾 GUARDAR",
            width=140,
            height=45,
            fg_color="#4CC9F0",
            hover_color="#4895EF",
            font=("Arial", 13, "bold"),
            command=self.guardar_configuracion
        )
        self.btn_save.pack(side="left", padx=5)
        
        self.btn_delete = ctk.CTkButton(
            btn_frame,
            text="🗑️ ELIMINAR",
            width=140,
            height=45,
            fg_color="#D90429",
            hover_color="#EF233C",
            font=("Arial", 13, "bold"),
            state="disabled",
            command=self.eliminar_configuracion
        )
        self.btn_delete.pack(side="left", padx=5)
        
        self.btn_test = ctk.CTkButton(
            btn_frame,
            text="🧪 PROBAR",
            width=140,
            height=45,
            fg_color="#7209B7",
            hover_color="#560BAD",
            font=("Arial", 13, "bold"),
            command=self.probar_configuracion
        )
        self.btn_test.pack(side="left", padx=5)
        
        # Botón volver
        btn_back = ctk.CTkButton(
            action_frame,
            text="↩️ VOLVER AL MENÚ",
            width=200,
            height=40,
            fg_color="gray",
            hover_color="#555555",
            font=("Arial", 12),
            command=self.volver
        )
        btn_back.pack(pady=10)
        
        # Estado del formulario
        self.form_status = ctk.CTkLabel(
            action_frame,
            text="Listo para crear nueva configuración",
            font=("Arial", 11),
            text_color="gray"
        )
        self.form_status.pack(pady=5)

    def cargar_datos_iniciales(self):
        """Cargar datos iniciales en segundo plano"""
        self.loading_label.configure(text="Cargando juegos...", text_color="yellow")
        
        # Obtener juegos disponibles
        juegos = self.get_available_games()
        
        # Actualizar UI
        if juegos:
            self.game_select.configure(values=juegos)
            juego_inicial = juegos[0]
            self.game_var.set(juego_inicial)
            self.current_category = juego_inicial
            self.loading_label.configure(text=f"{len(juegos)} juegos cargados", text_color="green")
            
            # Cargar configuraciones del juego inicial
            self.cargar_configuraciones_juego(juego_inicial)
        else:
            self.game_select.configure(values=["Sin juegos"])
            self.loading_label.configure(text="No hay juegos", text_color="red")

    def get_available_games(self):
        """Obtener lista de juegos disponibles"""
        games = []
        configs_dir = "configs"
        
        if os.path.exists(configs_dir):
            for item in os.listdir(configs_dir):
                item_path = os.path.join(configs_dir, item)
                if os.path.isdir(item_path):
                    games.append(item)
        
        return games if games else ["ar6"]

    def cargar_configuraciones_juego(self, juego):
        """Cargar configuraciones de un juego específico"""
        self.loading_label.configure(text="Cargando configuraciones...", text_color="yellow")
        
        # Limpiar frame de configuraciones
        for widget in self.configs_scrollable.winfo_children():
            widget.destroy()
        
        # Buscar configuraciones
        configs_dir = os.path.join("configs", juego)
        
        if os.path.exists(configs_dir):
            config_files = [f for f in os.listdir(configs_dir) if f.endswith('.yaml')]
            
            if config_files:
                # Crear botones para cada configuración
                for config_file in sorted(config_files):
                    config_name = config_file.replace('.yaml', '')
                    
                    # Frame para cada configuración
                    config_frame = ctk.CTkFrame(self.configs_scrollable, height=40, corner_radius=5)
                    config_frame.pack(fill="x", pady=2, padx=5)
                    config_frame.pack_propagate(False)
                    
                    # Botón con nombre
                    btn_config = ctk.CTkButton(
                        config_frame,
                        text=config_name,
                        height=35,
                        fg_color="transparent",
                        hover_color="#333333",
                        anchor="w",
                        command=lambda name=config_name: self.cargar_config_editar(name)
                    )
                    btn_config.pack(side="left", fill="x", expand=True, padx=5)
                    
                    # Botón de carga rápida
                    btn_load = ctk.CTkButton(
                        config_frame,
                        text="→",
                        width=35,
                        height=35,
                        fg_color="#7209B7",
                        hover_color="#560BAD"
                    )
                    btn_load.pack(side="right", padx=(0, 5))
                    btn_load.configure(command=lambda name=config_name: self.cargar_config_editar(name))
                
                self.loading_label.configure(
                    text=f"{len(config_files)} configuraciones cargadas", 
                    text_color="green"
                )
            else:
                empty_label = ctk.CTkLabel(
                    self.configs_scrollable,
                    text=f"No hay configuraciones para {juego}",
                    font=("Arial", 11),
                    text_color="gray"
                )
                empty_label.pack(pady=20)
                self.loading_label.configure(text="Sin configuraciones", text_color="gray")
        else:
            empty_label = ctk.CTkLabel(
                self.configs_scrollable,
                text="Directorio no encontrado",
                font=("Arial", 11),
                text_color="orange"
            )
            empty_label.pack(pady=20)
            self.loading_label.configure(text="Error: directorio no existe", text_color="red")

    def on_juego_seleccionado(self, juego):
        """Evento cuando se selecciona un juego"""
        if juego and juego != self.current_category:
            self.current_category = juego
            self.cargar_configuraciones_juego(juego)
            self.nueva_configuracion()

    def crear_nuevo_juego(self):
        """Crear una nueva carpeta de juego"""
        nuevo_juego = simpledialog.askstring(
            "Nuevo Juego",
            "Nombre del nuevo juego:",
            parent=self.parent
        )
        
        if nuevo_juego and nuevo_juego.strip():
            nuevo_juego = nuevo_juego.strip()
            juego_path = os.path.join("configs", nuevo_juego)
            
            if os.path.exists(juego_path):
                messagebox.showerror("Error", f"El juego '{nuevo_juego}' ya existe")
            else:
                try:
                    os.makedirs(juego_path, exist_ok=True)
                    
                    # Actualizar lista de juegos
                    juegos = self.get_available_games()
                    self.game_select.configure(values=juegos)
                    self.game_var.set(nuevo_juego)
                    self.current_category = nuevo_juego
                    
                    # Limpiar y crear nueva configuración
                    self.cargar_configuraciones_juego(nuevo_juego)
                    self.nueva_configuracion()
                    
                    messagebox.showinfo("Éxito", f"Juego '{nuevo_juego}' creado")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo crear: {e}")

    def nueva_configuracion(self):
        """Preparar formulario para nueva configuración"""
        self.edit_mode = False
        self.current_config_name = None
        
        self.editor_title.configure(
            text=f"NUEVA CONFIGURACIÓN - {self.current_category.upper()}",
            text_color="#4CC9F0"
        )
        
        self.btn_delete.configure(state="disabled")
        self.form_status.configure(
            text="Complete el formulario para crear una nueva configuración",
            text_color="gray"
        )
        
        # Limpiar campos
        self.limpiar_campos()
        
        # Establecer valores por defecto
        self.establecer_valores_por_defecto()

    def cargar_config_editar(self, config_name):
        """Cargar una configuración para editar"""
        self.form_status.configure(text=f"Cargando {config_name}...", text_color="yellow")
        
        try:
            config_path = os.path.join("configs", self.current_category, f"{config_name}.yaml")
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as file:
                    config_data = yaml.safe_load(file)
                
                # Actualizar formulario
                self._actualizar_formulario(config_name, config_data)
                
            else:
                messagebox.showerror("Error", f"No se encontró: {config_name}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            self.form_status.configure(
                text=f"Error cargando {config_name}",
                text_color="red"
            )

    def _actualizar_formulario(self, config_name, config_data):
        """Actualizar formulario con datos cargados"""
        self.edit_mode = True
        self.current_config_name = config_name
        
        # Actualizar campos
        self.entry_name.delete(0, 'end')
        self.entry_name.insert(0, config_name)
        
        self.text_desc.delete("1.0", "end")
        self.text_desc.insert("1.0", config_data.get("descripcion", ""))
        
        self.entry_min_vertical.delete(0, 'end')
        self.entry_min_vertical.insert(0, str(config_data.get("min_vertical", 2)))
        
        self.entry_max_vertical.delete(0, 'end')
        self.entry_max_vertical.insert(0, str(config_data.get("max_vertical", 4)))
        
        self.entry_horizontal.delete(0, 'end')
        self.entry_horizontal.insert(0, str(config_data.get("horizontal_range", 0.3)))
        
        self.entry_min_rate.delete(0, 'end')
        self.entry_min_rate.insert(0, str(config_data.get("min_firerate", 0.01)))
        
        self.entry_max_rate.delete(0, 'end')
        self.entry_max_rate.insert(0, str(config_data.get("max_firerate", 0.02)))
        
        self.entry_increment.delete(0, 'end')
        self.entry_increment.insert(0, str(config_data.get("incremento_progresivo", 0.1)))
        
        self.entry_limit.delete(0, 'end')
        self.entry_limit.insert(0, str(config_data.get("limite_incremento", 2.0)))
        
        # Actualizar UI
        self.editor_title.configure(
            text=f"EDITANDO: {config_name}",
            text_color="#4ADE80"
        )
        
        self.btn_delete.configure(state="normal")
        self.form_status.configure(
            text=f"Configuración '{config_name}' cargada",
            text_color="#4ADE80"
        )

    def limpiar_campos(self):
        """Limpiar todos los campos del formulario"""
        self.entry_name.delete(0, 'end')
        self.text_desc.delete("1.0", "end")
        self.entry_min_vertical.delete(0, 'end')
        self.entry_max_vertical.delete(0, 'end')
        self.entry_horizontal.delete(0, 'end')
        self.entry_min_rate.delete(0, 'end')
        self.entry_max_rate.delete(0, 'end')
        self.entry_increment.delete(0, 'end')
        self.entry_limit.delete(0, 'end')

    # En el método establecer_valores_por_defecto, cambiar los valores:
    def establecer_valores_por_defecto(self):
        """Establecer valores por defecto en los campos"""
        defaults = {
            self.entry_min_vertical: "10",      # Cambiado de 2 a 10
            self.entry_max_vertical: "15",      # Cambiado de 4 a 15
            self.entry_horizontal: "3",         # Cambiado de 0.3 a 3 (multiplicado por 10)
            self.entry_min_rate: "0.05",        # Cambiado de 0.01 a 0.05
            self.entry_max_rate: "0.1",         # Cambiado de 0.02 a 0.1
            self.entry_increment: "0.5",        # Cambiado de 0.1 a 0.5
            self.entry_limit: "10.0"            # Cambiado de 2.0 a 10.0
        }
        
        for entry, value in defaults.items():
            if not entry.get():
                entry.insert(0, value)

    def guardar_configuracion(self):
        """Guardar la configuración actual"""
        self.form_status.configure(text="Guardando...", text_color="yellow")
        
        try:
            # Validar campos requeridos
            nombre = self.entry_name.get().strip()
            if not nombre:
                messagebox.showwarning("Advertencia", "Nombre requerido")
                self.form_status.configure(text="Error: Nombre requerido", text_color="red")
                return
            
            # Obtener datos del formulario
            config_data = {
                "descripcion": self.text_desc.get("1.0", "end-1c").strip(),
                "min_vertical": float(self.entry_min_vertical.get() or 2),
                "max_vertical": float(self.entry_max_vertical.get() or 4),
                "horizontal_range": float(self.entry_horizontal.get() or 0.3),
                "min_firerate": float(self.entry_min_rate.get() or 0.01),
                "max_firerate": float(self.entry_max_rate.get() or 0.02),
                "incremento_progresivo": float(self.entry_increment.get() or 0.1),
                "limite_incremento": float(self.entry_limit.get() or 2.0)
            }
            
            # Determinar ruta
            if self.edit_mode and self.current_config_name and nombre != self.current_config_name:
                # Eliminar archivo antiguo si cambió el nombre
                old_path = os.path.join("configs", self.current_category, f"{self.current_config_name}.yaml")
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Guardar archivo
            config_path = os.path.join("configs", self.current_category, f"{nombre}.yaml")
            
            with open(config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config_data, file, default_flow_style=False, allow_unicode=True)
            
            # Actualizar estado
            self.edit_mode = True
            self.current_config_name = nombre
            self.editor_title.configure(
                text=f"EDITANDO: {nombre}",
                text_color="#4ADE80"
            )
            
            self.form_status.configure(
                text=f"Configuración '{nombre}' guardada",
                text_color="#4ADE80"
            )
            
            # Recargar lista de configuraciones
            self.cargar_configuraciones_juego(self.current_category)
            
            messagebox.showinfo("Éxito", f"Configuración '{nombre}' guardada")
            
        except ValueError:
            messagebox.showerror("Error", "Valores numéricos inválidos")
            self.form_status.configure(text="Error: Valores inválidos", text_color="red")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")
            self.form_status.configure(text=f"Error: {str(e)[:30]}", text_color="red")

    def eliminar_configuracion(self):
        """Eliminar la configuración actual"""
        if not self.edit_mode or not self.current_config_name:
            return
        
        confirm = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Eliminar '{self.current_config_name}'?\n\nEsta acción no se puede deshacer."
        )
        
        if confirm:
            try:
                config_path = os.path.join("configs", self.current_category, f"{self.current_config_name}.yaml")
                
                if os.path.exists(config_path):
                    os.remove(config_path)
                    
                    # Limpiar formulario
                    self.nueva_configuracion()
                    
                    # Recargar lista
                    self.cargar_configuraciones_juego(self.current_category)
                    
                    messagebox.showinfo("Éxito", f"Configuración eliminada")
                    
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def probar_configuracion(self):
        """Probar la configuración actual"""
        messagebox.showinfo(
            "Probar Configuración",
            "Prueba de configuración:\n\n"
            "En futuras versiones se integrará un\n"
            "simulador interactivo de anti-recoil."
        )

    def volver(self):
        """Volver al menú principal"""
        self.volver_callback()
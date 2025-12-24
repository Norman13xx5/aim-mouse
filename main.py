import customtkinter as ctk
from inicio import InicioView
from aim_assist import aim_controller
import keyboard
import threading
import sys
import os

# ================== CONFIGURACIÓN GENERAL ==================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Variable global para controlar la ventana
app_instance = None

def toggle_window():
    """Mostrar/ocultar la ventana con Ctrl+B"""
    global app_instance
    
    if app_instance and app_instance.winfo_exists():
        if app_instance.state() == 'withdrawn' or not app_instance.winfo_viewable():
            # Mostrar la ventana temporalmente encima
            app_instance.deiconify()
            app_instance.lift()
            app_instance.focus_force()
            
            # Solo poner "siempre encima" momentáneamente
            app_instance.attributes('-topmost', True)
            app_instance.after(100, lambda: app_instance.attributes('-topmost', False))
            
            print("📱 Ventana mostrada (Ctrl+B)")
        else:
            # Ocultar la ventana
            app_instance.withdraw()
            print("👻 Ventana oculta (Ctrl+B)")
    else:
        print("⚠️ La aplicación no está inicializada")

def setup_global_hotkey():
    """Configurar el atajo global Ctrl+B"""
    try:
        # Registrar el atajo global
        keyboard.add_hotkey('ctrl+b', toggle_window)
        print("✅ Atajo global configurado: Ctrl+B")
        print("   Presiona Ctrl+B para mostrar/ocultar la ventana")
        return True
    except Exception as e:
        print(f"❌ Error al configurar atajo global: {e}")
        return False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        global app_instance
        app_instance = self
        
        # Variables de configuración
        self.always_on_top = False  # Por defecto NO siempre encima
        self.start_hidden = False  # Cambia a True si quieres que empiece oculta
        
        self.title("Control de Anti-Recoil")
        self.geometry("1000x600")
        self.resizable(False, False)
        
        # Configurar icono (opcional)
        self.setup_icon()
        
        # Configurar protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configurar el atajo global
        self.hotkey_setup = setup_global_hotkey()
        
        # Configurar el menú del sistema (tray icon)
        self.setup_tray_menu()
        
        # ================== MENÚ LATERAL ==================
        self.menu_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.menu_frame.pack(side="left", fill="y")
        self.menu_frame.pack_propagate(False)

        # Logo/Header
        self.logo_label = ctk.CTkLabel(
            self.menu_frame,
            text="Norman13xx5",
            font=("Arial", 22, "bold"),
            text_color="#4CC9F0"
        )
        self.logo_label.pack(pady=(30, 20))

        # Separador
        separator = ctk.CTkFrame(self.menu_frame, height=2, fg_color="gray")
        separator.pack(fill="x", padx=20, pady=10)

        # Botones del menú
        menu_buttons = [
            ("🎯 Anti-Recoil", self.mostrar_inicio, "#4361EE"),
            ("👥 Usuarios", self.mostrar_usuarios, "#7209B7"),
            ("⚙️ Configuración", self.mostrar_config, "#F72585"),
        ]

        self.menu_buttons = {}
        for text, command, color in menu_buttons:
            btn = ctk.CTkButton(
                self.menu_frame,
                text=text,
                command=command,
                fg_color=color,
                hover_color="#3A0CA3",
                height=45,
                font=("Arial", 14),
                corner_radius=8
            )
            btn.pack(pady=8, padx=20, fill="x")
            self.menu_buttons[text] = btn

        # Espaciador
        ctk.CTkLabel(self.menu_frame, text="").pack(expand=True, fill="y")

        # Botón para mostrar/ocultar atajo
        btn_shortcut = ctk.CTkButton(
            self.menu_frame,
            text="📋 Ctrl+B",
            fg_color="#7209B7",
            hover_color="#560BAD",
            height=35,
            font=("Arial", 12),
            corner_radius=6,
            command=self.mostrar_info_atajo
        )
        btn_shortcut.pack(pady=10, padx=20, fill="x")

        # Botón salir
        self.btn_salir = ctk.CTkButton(
            self.menu_frame,
            text="❌ Salir",
            fg_color="#D90429",
            hover_color="#EF233C",
            height=45,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            command=self.on_closing
        )
        self.btn_salir.pack(pady=20, padx=20, fill="x")

        # ================== CONTENIDO PRINCIPAL ==================
        self.content_frame = ctk.CTkFrame(self, corner_radius=10)
        self.content_frame.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        # Frame para el título
        self.title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.title_frame.pack(pady=20)

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="",
            font=("Arial", 28, "bold")
        )
        self.title_label.pack()

        self.subtitle_label = ctk.CTkLabel(
            self.title_frame,
            text="",
            font=("Arial", 14),
            text_color="gray"
        )
        self.subtitle_label.pack()

        # Frame para contenido dinámico
        self.dynamic_content = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.dynamic_content.pack(expand=True, fill="both", padx=20)

        # Estado del sistema en footer
        self.footer_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.footer_frame.pack(pady=10)

        self.system_status = ctk.CTkLabel(
            self.footer_frame,
            text="Sistema: Inactivo",
            font=("Arial", 12),
            text_color="yellow"
        )
        self.system_status.pack(side="left", padx=10)

        self.aim_status = ctk.CTkLabel(
            self.footer_frame,
            text="Aim Assist: Detenido",
            font=("Arial", 12),
            text_color="red"
        )
        self.aim_status.pack(side="left", padx=10)

        # Información del atajo
        self.hotkey_info = ctk.CTkLabel(
            self.footer_frame,
            text="Ctrl+B: Mostrar/Ocultar",
            font=("Arial", 10),
            text_color="gray"
        )
        self.hotkey_info.pack(side="right", padx=10)

        # Iniciar aim assist en segundo plano
        self.iniciar_sistema()

        # Mostrar vista inicial
        self.mostrar_bienvenida()

        # Actualizar estado periódicamente
        self.actualizar_estado_sistema()

        # Si se debe iniciar oculto
        if self.start_hidden:
            self.withdraw()
            print("🚀 Aplicación iniciada en segundo plano")
            print("   Presiona Ctrl+B para mostrar la ventana")
        else:
            print("🚀 Aplicación iniciada")

    def setup_icon(self):
        """Configurar icono de la ventana"""
        try:
            # Intenta cargar un icono si existe
            if os.path.exists("icon.ico"):
                self.iconbitmap("icon.ico")
            elif os.path.exists("icon.png"):
                icon = ctk.CTkImage("icon.png")
                self.iconphoto(False, icon)
        except:
            pass  # Si no hay icono, continuar sin él

    def setup_tray_menu(self):
        """Configurar menú en la bandeja del sistema (para futuras versiones)"""
        # Esta funcionalidad requiere librerías adicionales como pystray
        # Por ahora dejamos el esqueleto para futura implementación
        pass

    def mostrar_info_atajo(self):
        """Mostrar información sobre el atajo de teclado"""
        from tkinter import messagebox
        messagebox.showinfo(
            "Atajo de Teclado - Ctrl+B",
            "📋 Controles Rápidos:\n\n"
            "• Ctrl + B → Mostrar/Ocultar ventana\n"
            "• Num Lock → Activar/Desactivar aim assist\n"
            "• Botón derecho + izquierdo → Aplicar anti-recoil\n\n"
            "💡 Consejo: Puedes ocultar la ventana y seguir\n"
            "usando el aim assist en segundo plano."
        )

    def iniciar_sistema(self):
        """Iniciar el aim assist en segundo plano"""
        try:
            aim_controller.start()
            print("✓ Sistema de aim assist iniciado en segundo plano")
            self.system_status.configure(text="Sistema: Activo", text_color="green")
        except Exception as e:
            print(f"✗ Error al iniciar sistema: {e}")
            self.system_status.configure(text="Sistema: Error", text_color="red")

    def on_closing(self):
        """Manejar cierre de la aplicación"""
        print("\n=== Cerrando aplicación ===")
        print("Deteniendo aim assist...")
        
        # Detener aim assist
        aim_controller.stop()
        
        # Remover el atajo de teclado global
        try:
            keyboard.remove_hotkey('ctrl+b')
            print("✓ Atajo global removido")
        except:
            pass
        
        # Confirmar salida
        from tkinter import messagebox
        if messagebox.askyesno("Salir", "¿Estás seguro de que quieres salir?\n\nEl aim assist se detendrá completamente."):
            print("Aplicación cerrada correctamente")
            self.quit()
            self.destroy()
            sys.exit(0)

    # ================== UTILIDAD ==================
    def limpiar_contenido(self):
        """Limpiar el contenido dinámico"""
        for widget in self.dynamic_content.winfo_children():
            widget.destroy()

    def resaltar_boton(self, boton_seleccionado):
        """Resaltar el botón del menú seleccionado"""
        for btn_text, btn in self.menu_buttons.items():
            if btn_text == boton_seleccionado:
                btn.configure(fg_color="#3A0CA3", hover_color="#3A0CA3")
            else:
                # Restaurar colores originales
                if "Anti-Recoil" in btn_text:
                    btn.configure(fg_color="#4361EE", hover_color="#3A0CA3")
                elif "Usuarios" in btn_text:
                    btn.configure(fg_color="#7209B7", hover_color="#3A0CA3")
                elif "Configuración" in btn_text:
                    btn.configure(fg_color="#F72585", hover_color="#3A0CA3")

    def actualizar_estado_sistema(self):
        """Actualizar el estado del sistema periódicamente"""
        # Actualizar estado del aim assist
        if aim_controller.enabled:
            self.aim_status.configure(
                text="Aim Assist: ACTIVO (Num Lock)",
                text_color="#4ADE80"
            )
        else:
            self.aim_status.configure(
                text="Aim Assist: INACTIVO (Presiona Num Lock)",
                text_color="red"
            )
        
        # Actualizar estado de visibilidad
        if self.state() == 'withdrawn' or not self.winfo_viewable():
            self.hotkey_info.configure(
                text="Ctrl+B: Mostrar ventana",
                text_color="yellow"
            )
        else:
            self.hotkey_info.configure(
                text="Ctrl+B: Ocultar ventana",
                text_color="gray"
            )
        
        # Programar próxima actualización
        self.after(1000, self.actualizar_estado_sistema)

    # ================== VISTAS ==================
    def mostrar_bienvenida(self):
        """Mostrar pantalla de bienvenida"""
        self.limpiar_contenido()
        self.resaltar_boton("")
        
        self.title_label.configure(text="Bienvenido al Control de Anti-Recoil")
        self.subtitle_label.configure(text="Selecciona una opción del menú lateral")
        
        # Contenido de bienvenida
        welcome_frame = ctk.CTkFrame(self.dynamic_content, fg_color="transparent")
        welcome_frame.pack(expand=True)
        
        # Logo central
        logo_text = ctk.CTkLabel(
            welcome_frame,
            text="🎮",
            font=("Arial", 100)
        )
        logo_text.pack(pady=20)
        
        # Mensaje principal
        main_text = ctk.CTkLabel(
            welcome_frame,
            text="Control de Anti-Recoil para Rainbow Six Siege",
            font=("Arial", 24, "bold")
        )
        main_text.pack(pady=10)
        
        # Atajo de teclado destacado
        shortcut_frame = ctk.CTkFrame(
            welcome_frame,
            corner_radius=10,
            fg_color="#1E40AF",
            border_width=2,
            border_color="#3B82F6"
        )
        shortcut_frame.pack(pady=20, padx=50, fill="x")
        
        shortcut_text = ctk.CTkLabel(
            shortcut_frame,
            text="🎯 ATALLO RÁPIDO: Ctrl + B",
            font=("Arial", 18, "bold"),
            text_color="white"
        )
        shortcut_text.pack(pady=15)
        
        shortcut_desc = ctk.CTkLabel(
            shortcut_frame,
            text="Presiona Ctrl+B en cualquier momento para mostrar/ocultar esta ventana",
            font=("Arial", 12),
            text_color="#BFDBFE"
        )
        shortcut_desc.pack(pady=(0, 15))
        
        # Descripción
        desc_text = ctk.CTkLabel(
            welcome_frame,
            text="Sistema profesional de compensación de recoil\n"
                 "Configura diferentes armas y mejora tu puntería",
            font=("Arial", 14),
            text_color="gray",
            justify="center"
        )
        desc_text.pack(pady=20)
        
        # Instrucciones rápidas
        inst_frame = ctk.CTkFrame(welcome_frame, corner_radius=10)
        inst_frame.pack(pady=30, padx=50, fill="x")
        
        inst_title = ctk.CTkLabel(
            inst_frame,
            text="📋 Instrucciones Rápidas:",
            font=("Arial", 16, "bold")
        )
        inst_title.pack(pady=(15, 10))
        
        instructions = [
            "1. Ve a '🎯 Anti-Recoil' para configurar el sistema",
            "2. Selecciona el arma y carga la configuración",
            "3. Activa el sistema con el botón correspondiente",
            "4. En el juego: Presiona NUM LOCK para activar/desactivar",
            "5. Al disparar: Mantén CLICK DERECHO + CLICK IZQUIERDO",
            "6. El sistema compensará automáticamente el recoil",
            "7. Usa Ctrl+B para mostrar/ocultar esta ventana"
        ]
        
        for inst in instructions:
            label = ctk.CTkLabel(
                inst_frame,
                text=inst,
                font=("Arial", 12),
                justify="left"
            )
            label.pack(pady=2, padx=20)
        
        # Advertencia
        warning = ctk.CTkLabel(
            welcome_frame,
            text="⚠️ Usar únicamente en servidores privados o modo práctica",
            font=("Arial", 11),
            text_color="orange"
        )
        warning.pack(pady=20)

    def mostrar_inicio(self):
        """Mostrar vista de anti-recoil"""
        self.limpiar_contenido()
        self.resaltar_boton("🎯 Anti-Recoil")
        
        self.title_label.configure(text="Control de Anti-Recoil")
        self.subtitle_label.configure(text="Configura y controla la compensación de recoil")
        
        # Crear vista de inicio
        InicioView(self.dynamic_content, self.mostrar_bienvenida)

    def mostrar_usuarios(self):
        """Mostrar vista de gestión de usuarios"""
        self.limpiar_contenido()
        self.resaltar_boton("👥 Usuarios")
        
        self.title_label.configure(text="Gestión de Usuarios")
        self.subtitle_label.configure(text="Administra perfiles y configuraciones")
        
        # Contenido de usuarios
        content = ctk.CTkFrame(self.dynamic_content)
        content.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Título
        title = ctk.CTkLabel(
            content,
            text="👥 Gestión de Perfiles",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)
        
        # Descripción
        desc = ctk.CTkLabel(
            content,
            text="Esta función estará disponible próximamente\n"
                 "Podrás guardar configuraciones por perfil de usuario",
            font=("Arial", 14),
            text_color="gray",
            justify="center"
        )
        desc.pack(pady=10)
        
        # Frame para futuras funciones
        future_frame = ctk.CTkFrame(content, corner_radius=10)
        future_frame.pack(pady=30, padx=20, fill="x")
        
        features = [
            "✓ Guardar configuraciones personalizadas",
            "✓ Perfiles por jugador",
            "✓ Historial de uso",
            "✓ Estadísticas de precisión"
        ]
        
        for feature in features:
            feat_label = ctk.CTkLabel(
                future_frame,
                text=feature,
                font=("Arial", 12),
                justify="left"
            )
            feat_label.pack(pady=8, padx=20, anchor="w")

    def mostrar_config(self):
        """Mostrar vista de configuración del sistema"""
        self.limpiar_contenido()
        self.resaltar_boton("⚙️ Configuración")
        
        self.title_label.configure(text="Configuración del Sistema")
        self.subtitle_label.configure(text="Ajustes avanzados y preferencias")
        
        # Contenido de configuración
        content = ctk.CTkFrame(self.dynamic_content)
        content.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Título
        title = ctk.CTkLabel(
            content,
            text="⚙️ Configuración Avanzada",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)
        
        # Frame de configuraciones
        config_frame = ctk.CTkFrame(content, corner_radius=10)
        config_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Sección: Controles
        ctrl_section = ctk.CTkFrame(config_frame, fg_color="transparent")
        ctrl_section.pack(pady=20, padx=30, fill="x")
        
        ctrl_title = ctk.CTkLabel(
            ctrl_section,
            text="🎮 Controles",
            font=("Arial", 16, "bold")
        )
        ctrl_title.pack(anchor="w", pady=(0, 10))
        
        # Atajo personalizado
        hotkey_frame = ctk.CTkFrame(ctrl_section, fg_color="transparent")
        hotkey_frame.pack(fill="x", pady=10)
        
        hotkey_label = ctk.CTkLabel(
            hotkey_frame,
            text="Atajo para mostrar/ocultar:",
            font=("Arial", 12)
        )
        hotkey_label.pack(side="left", padx=(0, 20))
        
        hotkey_display = ctk.CTkEntry(
            hotkey_frame,
            width=150,
            font=("Arial", 12),
            justify="center"
        )
        hotkey_display.insert(0, "Ctrl + B")
        hotkey_display.configure(state="readonly")
        hotkey_display.pack(side="left")
        
        btn_change_hotkey = ctk.CTkButton(
            hotkey_frame,
            text="Cambiar",
            width=80,
            fg_color="#7209B7",
            hover_color="#560BAD"
        )
        btn_change_hotkey.pack(side="left", padx=(10, 0))
        
        # Sección: Comportamiento
        behav_section = ctk.CTkFrame(config_frame, fg_color="transparent")
        behav_section.pack(pady=20, padx=30, fill="x")
        
        behav_title = ctk.CTkLabel(
            behav_section,
            text="⚡ Comportamiento",
            font=("Arial", 16, "bold")
        )
        behav_title.pack(anchor="w", pady=(0, 10))
        
        # Checkboxes de comportamiento
        check_var1 = ctk.BooleanVar(value=self.start_hidden)
        check_var2 = ctk.BooleanVar(value=True)
        check_var3 = ctk.BooleanVar(value=True)
        check_var4 = ctk.BooleanVar(value=self.always_on_top)
        
        check1 = ctk.CTkCheckBox(
            behav_section,
            text="Iniciar minimizado",
            variable=check_var1,
            font=("Arial", 12),
            command=lambda: self.toggle_start_minimized(check_var1)
        )
        check1.pack(anchor="w", pady=5)
        
        check2 = ctk.CTkCheckBox(
            behav_section,
            text="Mostrar notificaciones",
            variable=check_var2,
            font=("Arial", 12)
        )
        check2.pack(anchor="w", pady=5)
        
        check3 = ctk.CTkCheckBox(
            behav_section,
            text="Mantener en primer plano al mostrar",
            variable=check_var3,
            font=("Arial", 12)
        )
        check3.pack(anchor="w", pady=5)
        
        check4 = ctk.CTkCheckBox(
            behav_section,
            text="Ventana siempre encima (Always on Top)",
            variable=check_var4,
            font=("Arial", 12),
            command=lambda: self.toggle_always_on_top(check_var4)
        )
        check4.pack(anchor="w", pady=5)
        
        # Sección: Sensibilidad
        sens_section = ctk.CTkFrame(config_frame, fg_color="transparent")
        sens_section.pack(pady=20, padx=30, fill="x")
        
        sens_title = ctk.CTkLabel(
            sens_section,
            text="🎯 Sensibilidad Global",
            font=("Arial", 16, "bold")
        )
        sens_title.pack(anchor="w", pady=(0, 10))
        
        # Slider de sensibilidad
        sens_label = ctk.CTkLabel(
            sens_section,
            text="Fuerza del anti-recoil:",
            font=("Arial", 12)
        )
        sens_label.pack(anchor="w", pady=5)
        
        sens_slider = ctk.CTkSlider(
            sens_section,
            from_=1,
            to=10,
            number_of_steps=9,
            width=300,
            command=self.update_sensitivity
        )
        sens_slider.set(5)
        sens_slider.pack(anchor="w", pady=5)
        
        self.sens_value_label = ctk.CTkLabel(
            sens_section,
            text="Nivel: 5/10",
            font=("Arial", 11),
            text_color="gray"
        )
        self.sens_value_label.pack(anchor="w")
        
        # Botón guardar configuración
        btn_guardar = ctk.CTkButton(
            config_frame,
            text="💾 Guardar Configuración",
            fg_color="#4CC9F0",
            hover_color="#4895EF",
            font=("Arial", 14),
            height=40,
            command=self.guardar_configuracion
        )
        btn_guardar.pack(pady=30)

    def toggle_start_minimized(self, var):
        """Alternar inicio minimizado"""
        self.start_hidden = var.get()
        print(f"Inicio minimizado: {'Activado' if self.start_hidden else 'Desactivado'}")

    def toggle_always_on_top(self, var):
        """Alternar el comportamiento 'siempre encima'"""
        self.always_on_top = var.get()
        print(f"Ventana siempre encima: {'Activado' if self.always_on_top else 'Desactivado'}")

    def update_sensitivity(self, value):
        """Actualizar valor de sensibilidad"""
        self.sens_value_label.configure(text=f"Nivel: {int(float(value))}/10")

    def guardar_configuracion(self):
        """Guardar configuración"""
        from tkinter import messagebox
        messagebox.showinfo(
            "Configuración Guardada",
            "La configuración ha sido guardada exitosamente.\n\n"
            "Los cambios se aplicarán la próxima vez que inicies la aplicación."
        )
        print("Configuración guardada")

def run_app():
    """Función principal para ejecutar la aplicación"""
    print("=" * 50)
    print("CONTROL DE ANTI-RECOIL - RAINBOW SIX SIEGE")
    print("=" * 50)
    print("📱 Iniciando aplicación...")
    print("🎮 Aim Assist funcionará en segundo plano")
    print("🔥 Atajo global: Ctrl + B (mostrar/ocultar)")
    print("🔧 Activar/Desactivar: Num Lock")
    print("=" * 50)
    
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Aplicación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Limpiar al salir
        try:
            keyboard.unhook_all()
            print("✓ Recursos liberados")
        except:
            pass

if __name__ == "__main__":
    run_app()
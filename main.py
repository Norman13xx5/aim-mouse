import customtkinter as ctk
from inicio import InicioView
from aim_assist import aim_controller
import keyboard
import sys
import os

# ================== CONFIGURACIÓN GENERAL ==================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Constantes para colores y configuraciones
COLORS = {
    "PRIMARY": "#4361EE",
    "SECONDARY": "#7209B7",
    "ACCENT": "#F72585",
    "INFO": "#4CC9F0",
    "SUCCESS": "#4ADE80",
    "WARNING": "#F59E0B",
    "DANGER": "#D90429",
    "DARK": "#1E293B",
    "LIGHT": "#F1F5F9"
}

BUTTON_COLORS = {
    "🎯 Anti-Recoil": COLORS["PRIMARY"],
    "👥 Usuarios": COLORS["SECONDARY"],
    "⚙️ Configuración": COLORS["ACCENT"],
    "📝 Editor": COLORS["INFO"]
}

HOTKEY = "ctrl+b"
APP_TITLE = "Control de Anti-Recoil"
APP_SIZE = "1000x600"


class WindowManager:
    """Manejador de la ventana principal y sus estados"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = App()
        return cls._instance
    
    @staticmethod
    def toggle_window():
        """Mostrar/ocultar la ventana con Ctrl+B"""
        app = WindowManager.get_instance()
        
        if app.winfo_exists():
            if app.state() == 'withdrawn' or not app.winfo_viewable():
                app.deiconify()
                app.lift()
                app.focus_force()
                app.attributes('-topmost', True)
                app.after(100, lambda: app.attributes('-topmost', False))
                print("📱 Ventana mostrada (Ctrl+B)")
            else:
                app.withdraw()
                print("👻 Ventana ocultada (Ctrl+B)")
        else:
            print("⚠️ La aplicación no está inicializada")


class HotkeyManager:
    """Manejador de atajos de teclado globales"""
    
    @staticmethod
    def setup_global_hotkey():
        """Configurar el atajo global Ctrl+B"""
        try:
            keyboard.add_hotkey(HOTKEY, WindowManager.toggle_window)
            print(f"✅ Atajo global configurado: {HOTKEY.upper()}")
            return True
        except Exception as e:
            print(f"❌ Error al configurar atajo global: {e}")
            return False
    
    @staticmethod
    def remove_global_hotkey():
        """Remover el atajo global"""
        try:
            keyboard.remove_hotkey(HOTKEY)
            print("✓ Atajo global removido")
        except:
            pass


class LoaderWidget:
    """Widget para mostrar animación de carga"""
    
    def __init__(self, parent, message="Cargando..."):
        self.parent = parent
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.dots_label = None
        self.dots_count = 0
        self.message = message
        self.is_running = False
        
    def show(self):
        """Mostrar el loader"""
        self.frame.pack(expand=True)
        
        self.dots_label = ctk.CTkLabel(
            self.frame,
            text="",
            font=("Arial", 24, "bold"),
            text_color=COLORS["INFO"]
        )
        self.dots_label.pack(pady=20)
        
        message_label = ctk.CTkLabel(
            self.frame,
            text=self.message,
            font=("Arial", 16),
            text_color="yellow"
        )
        message_label.pack(pady=10)
        
        self.is_running = True
        self._animate()
        
        return self.frame
    
    def hide(self):
        """Ocultar el loader"""
        self.is_running = False
        if self.frame and self.frame.winfo_exists():
            self.frame.destroy()
    
    def _animate(self):
        """Animación del loader de puntos"""
        if not self.is_running:
            return
            
        try:
            if self.frame and self.frame.winfo_exists() and self.dots_label:
                dots = "." * (self.dots_count % 4)
                self.dots_label.configure(text=dots)
                self.dots_count += 1
                
                if self.frame.winfo_exists():
                    self.frame.after(300, self._animate)
        except Exception:
            self.is_running = False


class App(ctk.CTk):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        WindowManager._instance = self
        
        # Variables de configuración
        self.config = {
            "start_hidden": False,
            "always_on_top": False,
            "global_sensitivity": 5
        }
        
        # Widgets
        self.loader = None
        self.menu_buttons = {}
        self.current_view = None
        
        self._setup_window()
        self._setup_menu()
        self._setup_content_area()
        self._setup_footer()
        
        # Inicializar sistema
        self._init_system()
        
        # Mostrar vista inicial
        self.show_welcome()
        
        # Iniciar oculto si está configurado
        if self.config["start_hidden"]:
            self.withdraw()
            print("🚀 Aplicación iniciada en segundo plano")
        else:
            print("🚀 Aplicación iniciada")
    
    # ================== CONFIGURACIÓN INICIAL ==================
    
    def _setup_window(self):
        """Configurar propiedades de la ventana"""
        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.resizable(False, False)
        self._setup_icon()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configurar atajo global
        self.hotkey_setup = HotkeyManager.setup_global_hotkey()
    
    def _setup_icon(self):
        """Configurar icono de la ventana"""
        icon_files = ["icon.ico", "icon.png"]
        for icon_file in icon_files:
            if os.path.exists(icon_file):
                try:
                    if icon_file.endswith(".ico"):
                        self.iconbitmap(icon_file)
                    else:
                        # Para imágenes PNG necesitarías convertir a formato compatible
                        pass
                except:
                    pass
                break
    
    def _setup_menu(self):
        """Configurar menú lateral"""
        self.menu_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.menu_frame.pack(side="left", fill="y")
        self.menu_frame.pack_propagate(False)
        
        # Logo
        logo_label = ctk.CTkLabel(
            self.menu_frame,
            text="Norman13xx5",
            font=("Arial", 22, "bold"),
            text_color=COLORS["INFO"]
        )
        logo_label.pack(pady=(30, 20))
        
        # Separador
        separator = ctk.CTkFrame(self.menu_frame, height=2, fg_color="gray")
        separator.pack(fill="x", padx=20, pady=10)
        
        # Botones del menú
        menu_items = [
            ("🎯 Anti-Recoil", self.show_aim_assist),
            ("👥 Usuarios", self.show_users),
            ("⚙️ Configuración", self.show_settings),
            ("📝 Editor", self.show_editor),
        ]
        
        for text, command in menu_items:
            btn = ctk.CTkButton(
                self.menu_frame,
                text=text,
                command=command,
                fg_color=BUTTON_COLORS.get(text, COLORS["PRIMARY"]),
                hover_color=COLORS["DARK"],
                height=45,
                font=("Arial", 14),
                corner_radius=8
            )
            btn.pack(pady=8, padx=20, fill="x")
            self.menu_buttons[text] = btn
        
        # Espaciador
        ctk.CTkLabel(self.menu_frame, text="").pack(expand=True, fill="y")
        
        # Botón de ayuda de atajo
        shortcut_btn = ctk.CTkButton(
            self.menu_frame,
            text="📋 Ctrl+B",
            fg_color=COLORS["SECONDARY"],
            hover_color="#560BAD",
            height=35,
            font=("Arial", 12),
            corner_radius=6,
            command=self.show_hotkey_info
        )
        shortcut_btn.pack(pady=10, padx=20, fill="x")
        
        # Botón salir
        exit_btn = ctk.CTkButton(
            self.menu_frame,
            text="❌ Salir",
            fg_color=COLORS["DANGER"],
            hover_color="#EF233C",
            height=45,
            font=("Arial", 14, "bold"),
            corner_radius=8,
            command=self.on_closing
        )
        exit_btn.pack(pady=20, padx=20, fill="x")
    
    def _setup_content_area(self):
        """Configurar área de contenido principal"""
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
    
    def _setup_footer(self):
        """Configurar pie de página con estados"""
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
        
        self.hotkey_info_label = ctk.CTkLabel(
            self.footer_frame,
            text="Ctrl+B: Mostrar/Ocultar",
            font=("Arial", 10),
            text_color="gray"
        )
        self.hotkey_info_label.pack(side="right", padx=10)
    
    def _init_system(self):
        """Inicializar el sistema de aim assist"""
        try:
            aim_controller.start()
            print("✓ Sistema de aim assist iniciado en segundo plano")
            self.system_status.configure(text="Sistema: Activo", text_color=COLORS["SUCCESS"])
            self._start_status_updates()
        except Exception as e:
            print(f"✗ Error al iniciar sistema: {e}")
            self.system_status.configure(text="Sistema: Error", text_color=COLORS["DANGER"])
    
    # ================== MANEJO DE VISTAS ==================
    
    def clear_content(self):
        """Limpiar el contenido dinámico"""
        for widget in self.dynamic_content.winfo_children():
            widget.destroy()
    
    def show_loader(self, message="Cargando..."):
        """Mostrar animación de carga"""
        if self.loader:
            self.loader.hide()
        self.loader = LoaderWidget(self.dynamic_content, message)
        return self.loader.show()
    
    def hide_loader(self):
        """Ocultar animación de carga"""
        if self.loader:
            self.loader.hide()
            self.loader = None
    
    def highlight_menu_button(self, selected_button):
        """Resaltar el botón del menú seleccionado"""
        for btn_text, btn in self.menu_buttons.items():
            if btn_text == selected_button:
                btn.configure(fg_color=COLORS["DARK"], hover_color=COLORS["DARK"])
            else:
                original_color = BUTTON_COLORS.get(btn_text, COLORS["PRIMARY"])
                btn.configure(fg_color=original_color, hover_color=COLORS["DARK"])
    
    # ================== VISTAS PRINCIPALES ==================
    
    def show_welcome(self):
        """Mostrar pantalla de bienvenida"""
        self.clear_content()
        self.highlight_menu_button("")
        
        self.title_label.configure(text="Bienvenido al Control de Anti-Recoil")
        self.subtitle_label.configure(text="Selecciona una opción del menú lateral")
        
        self.show_loader("Cargando vista de bienvenida...")
        self.after(100, self._load_welcome_content)
    
    def _load_welcome_content(self):
        """Cargar contenido de bienvenida"""
        self.hide_loader()
        
        welcome_frame = ctk.CTkFrame(self.dynamic_content, fg_color="transparent")
        welcome_frame.pack(expand=True)
        
        # Logo
        logo_text = ctk.CTkLabel(welcome_frame, text="🎮", font=("Arial", 100))
        logo_text.pack(pady=20)
        
        # Título principal
        main_text = ctk.CTkLabel(
            welcome_frame,
            text="Control de Anti-Recoil para Rainbow Six Siege",
            font=("Arial", 24, "bold")
        )
        main_text.pack(pady=10)
        
        # Tarjeta de atajo
        self._create_shortcut_card(welcome_frame)
        
        # Instrucciones
        self._create_instructions_section(welcome_frame)
        
        # Advertencia
        warning = ctk.CTkLabel(
            welcome_frame,
            text="⚠️ Usar únicamente en servidores privados o modo práctica",
            font=("Arial", 11),
            text_color="orange"
        )
        warning.pack(pady=20)
    
    def _create_shortcut_card(self, parent):
        """Crear tarjeta de atajo de teclado"""
        shortcut_frame = ctk.CTkFrame(
            parent,
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
    
    def _create_instructions_section(self, parent):
        """Crear sección de instrucciones"""
        inst_frame = ctk.CTkFrame(parent, corner_radius=10)
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
    
    def show_aim_assist(self):
        """Mostrar vista de anti-recoil"""
        self.clear_content()
        self.highlight_menu_button("🎯 Anti-Recoil")
        
        self.title_label.configure(text="Control de Anti-Recoil")
        self.subtitle_label.configure(text="Configura y controla la compensación de recoil")
        
        self.show_loader("Cargando vista Anti-Recoil...")
        self.after(150, self._load_aim_assist_view)
    
    def _load_aim_assist_view(self):
        """Cargar vista de aim assist"""
        self.hide_loader()
        InicioView(self.dynamic_content, self.show_welcome)
    
    def show_users(self):
        """Mostrar vista de gestión de usuarios"""
        self.clear_content()
        self.highlight_menu_button("👥 Usuarios")
        
        self.title_label.configure(text="Gestión de Usuarios")
        self.subtitle_label.configure(text="Administra perfiles y configuraciones")
        
        self.show_loader("Cargando vista de Usuarios...")
        self.after(100, self._load_users_view)
    
    def _load_users_view(self):
        """Cargar vista de usuarios"""
        self.hide_loader()
        from views.users_view import UsersView
        UsersView(self.dynamic_content)
    
    def show_settings(self):
        """Mostrar vista de configuración"""
        self.clear_content()
        self.highlight_menu_button("⚙️ Configuración")
        
        self.title_label.configure(text="Configuración del Sistema")
        self.subtitle_label.configure(text="Ajustes avanzados y preferencias")
        
        self.show_loader("Cargando vista de Configuración...")
        self.after(100, self._load_settings_view)
    
    def _load_settings_view(self):
        """Cargar vista de configuración"""
        self.hide_loader()
        from views.settings_view import SettingsView
        SettingsView(self.dynamic_content, self.config, self.update_config)
    
    def show_editor(self):
        """Mostrar vista del editor"""
        self.clear_content()
        self.highlight_menu_button("📝 Editor")
        
        self.title_label.configure(text="Editor de Configuraciones")
        self.subtitle_label.configure(text="Crea y edita configuraciones de armas")
        
        self.show_loader("Cargando Editor de Configuraciones...")
        self.after(200, self._load_editor_view)
    
    def _load_editor_view(self):
        """Cargar vista del editor"""
        self.hide_loader()
        try:
            from editor_config import EditorConfigView
            EditorConfigView(self.dynamic_content, self.show_welcome)
        except ImportError as e:
            error_label = ctk.CTkLabel(
                self.dynamic_content,
                text=f"Error al cargar el editor: {e}",
                font=("Arial", 14),
                text_color="red"
            )
            error_label.pack(pady=50)
            print(f"Error cargando editor: {e}")
    
    # ================== UTILIDADES ==================
    
    def show_hotkey_info(self):
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
    
    def _start_status_updates(self):
        """Iniciar actualizaciones periódicas del estado"""
        self._update_status()
    
    def _update_status(self):
        """Actualizar estado del sistema"""
        if not self.winfo_exists():
            return
        
        try:
            # Actualizar estado del aim assist
            if aim_controller.enabled:
                self.aim_status.configure(
                    text="Aim Assist: ACTIVO (Num Lock)",
                    text_color=COLORS["SUCCESS"]
                )
            else:
                self.aim_status.configure(
                    text="Aim Assist: INACTIVO (Presiona Num Lock)",
                    text_color=COLORS["DANGER"]
                )
            
            # Actualizar estado de visibilidad
            if self.state() == 'withdrawn' or not self.winfo_viewable():
                self.hotkey_info_label.configure(
                    text="Ctrl+B: Mostrar ventana",
                    text_color="yellow"
                )
            else:
                self.hotkey_info_label.configure(
                    text="Ctrl+B: Ocultar ventana",
                    text_color="gray"
                )
        except Exception as e:
            print(f"Error en actualización de estado: {e}")
            return
        
        # Programar próxima actualización
        if self.winfo_exists():
            self.after(1000, self._update_status)
    
    def update_config(self, key, value):
        """Actualizar configuración"""
        self.config[key] = value
    
    def on_closing(self):
        """Manejar cierre de la aplicación"""
        print("\n=== Cerrando aplicación ===")
        print("Deteniendo aim assist...")
        
        # Detener aim assist
        aim_controller.stop()
        
        # Remover atajo global
        HotkeyManager.remove_global_hotkey()
        
        # Confirmar salida
        from tkinter import messagebox
        if messagebox.askyesno(
            "Salir",
            "¿Estás seguro de que quieres salir?\n\nEl aim assist se detendrá completamente."
        ):
            print("Aplicación cerrada correctamente")
            self.quit()
            self.destroy()
            sys.exit(0)


def run_app():
    """Función principal para ejecutar la aplicación"""
    print("=" * 50)
    print("CONTROL DE ANTI-RECOIL - RAINBOW SIX SIEGE")
    print("=" * 50)
    print("📱 Iniciando aplicación...")
    print("🎮 Aim Assist funcionará en segundo plano")
    print(f"🔥 Atajo global: {HOTKEY.upper()} (mostrar/ocultar)")
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
        try:
            keyboard.unhook_all()
            print("✓ Recursos liberados")
        except:
            pass


if __name__ == "__main__":
    run_app()
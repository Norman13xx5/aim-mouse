import customtkinter as ctk
from inicio import InicioView
from aim_assist import aim_controller
import keyboard
import ctypes
from ctypes import wintypes
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
                # Si overlay activo, mostrar sin activar (no robar foco)
                if app.config.get('overlay_mode') and os.name == 'nt':
                    try:
                        hwnd = app.winfo_id()
                        SW_SHOWNOACTIVATE = 4
                        SWP_NOSIZE = 0x0001
                        SWP_NOMOVE = 0x0002
                        SWP_NOACTIVATE = 0x0010
                        SWP_SHOWWINDOW = 0x0040
                        HWND_TOPMOST = -1
                        ctypes.windll.user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
                        ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW | SWP_NOACTIVATE)
                        # Asegurar estilos overlay aplicados
                        try:
                            app._apply_overlay_settings()
                        except Exception:
                            pass
                    except Exception as e:
                        # Fallback normal
                        app.deiconify()
                        app.lift()
                else:
                    app.deiconify()
                    app.lift()
                    # Si no está en modo overlay, forzar foco de forma breve
                    if not app.config.get('overlay_mode'):
                        try:
                            app.focus_force()
                            app.attributes('-topmost', True)
                            app.after(100, lambda: app.attributes('-topmost', False))
                        except Exception:
                            pass
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
            "overlay_mode": False,
            "overlay_clickthrough": False,
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
        # Aplicar modo overlay si está configurado
        # Ejecutar tras ventana creada
        try:
            self.after(200, self._apply_overlay_settings)
        except Exception:
            pass

    def _apply_overlay_settings(self):
        """Aplicar configuración de overlay (topmost + opcional click-through) en Windows."""
        try:
            if os.name != 'nt':
                return

            hwnd = self.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_TOOLWINDOW = 0x00000080
            HWND_TOPMOST = -1
            HWND_NOTOPMOST = -2
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040

            exstyle = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

            if self.config.get("overlay_mode"):
                # Asegurar que esté siempre arriba pero no robe foco
                ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW | SWP_NOACTIVATE)
                # Añadir estilos de layered y toolwindow (quita de Alt-Tab)
                # Intentar añadir WS_EX_NOACTIVATE si disponible (algunas versiones de Windows)
                WS_EX_NOACTIVATE = 0x04000000
                new_style = exstyle | WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
                if self.config.get("overlay_clickthrough"):
                    new_style |= WS_EX_TRANSPARENT
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                # Instalar hook para evitar activación por click, mouseactivate, setfocus
                try:
                    self._install_mouse_activate_hook(hwnd)
                except Exception:
                    pass
            else:
                # Quitar estilo click-through si estaba puesto y restaurar topmost según setting
                new_style = exstyle & ~WS_EX_TRANSPARENT
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                if self.config.get("always_on_top"):
                    ctypes.windll.user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
                else:
                    ctypes.windll.user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
                # Quitar hook si existe
                try:
                    self._remove_mouse_activate_hook(hwnd)
                except Exception:
                    pass
        except Exception as e:
            print(f"No se pudo aplicar overlay settings: {e}")

    def _install_mouse_activate_hook(self, hwnd):
        """Sobrescribir WndProc para evitar activación por click.
        Intercepta WM_MOUSEACTIVATE, WM_ACTIVATE, WM_SETFOCUS, WM_NCACTIVATE."""
        if os.name != 'nt':
            return

        user32 = ctypes.windll.user32
        GWL_WNDPROC = -4

        # Definir tipos
        WNDPROCTYPE = ctypes.WINFUNCTYPE(wintypes.LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

        # Si ya instalado, no reinstalar
        if getattr(self, '_wndproc_ref', None) is not None:
            return

        def _wndproc(hWnd, msg, wParam, lParam):
            # Códigos de mensajes para evitar activación
            WM_ACTIVATE = 0x0006
            WM_SETFOCUS = 0x0007
            WM_NCACTIVATE = 0x0086
            WM_MOUSEACTIVATE = 0x0021
            
            # WM_MOUSEACTIVATE: no activar pero procesar (MA_NOACTIVATE = 3)
            if msg == WM_MOUSEACTIVATE:
                return 3
            # WM_ACTIVATE: si es activación, ignorar
            if msg == WM_ACTIVATE:
                if wParam != 0:  # Si es activación
                    return 0  # Ignorar activación
            # WM_SETFOCUS: ignorar completamente
            if msg == WM_SETFOCUS:
                return 0
            # WM_NCACTIVATE: devolver TRUE sin activar frame no-cliente
            if msg == WM_NCACTIVATE:
                return 1
            
            # Para otros mensajes, llamar al procedimiento original si existe
            orig = getattr(self, '_orig_wndproc', None)
            if orig:
                return user32.CallWindowProcW(orig, hWnd, msg, wParam, lParam)
            return user32.DefWindowProcW(hWnd, msg, wParam, lParam)

        wndproc = WNDPROCTYPE(_wndproc)

        # Guardar referencia para evitar que el GC lo recoja
        self._wndproc_ref = wndproc

        # Establecer nuevo WndProc y guardar el anterior
        try:
            SetWindowLongPtr = user32.SetWindowLongPtrW
        except AttributeError:
            SetWindowLongPtr = user32.SetWindowLongW

        prev = SetWindowLongPtr(hwnd, GWL_WNDPROC, ctypes.cast(wndproc, ctypes.c_void_p).value)
        self._orig_wndproc = prev

    def _remove_mouse_activate_hook(self, hwnd):
        """Restaurar el WndProc original si fue reemplazado."""
        if os.name != 'nt':
            return
        user32 = ctypes.windll.user32
        GWL_WNDPROC = -4

        orig = getattr(self, '_orig_wndproc', None)
        if not orig:
            return

        try:
            try:
                SetWindowLongPtr = user32.SetWindowLongPtrW
            except AttributeError:
                SetWindowLongPtr = user32.SetWindowLongW

            SetWindowLongPtr(hwnd, GWL_WNDPROC, orig)
        except Exception:
            pass

        # Limpieza
        try:
            del self._orig_wndproc
        except Exception:
            pass
        try:
            del self._wndproc_ref
        except Exception:
            pass
    
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
        """Configurar menú lateral mejorado con diseño profesional"""
        self.menu_frame = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#0F172A")
        self.menu_frame.pack(side="left", fill="y")
        self.menu_frame.pack_propagate(False)
        
        # ===== ENCABEZADO ELEGANTE =====
        header_frame = ctk.CTkFrame(self.menu_frame, fg_color="#1A1F3A", corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        # Logo principal
        logo_label = ctk.CTkLabel(
            header_frame,
            text="🎯 AIM ASSIST",
            font=("Arial", 16, "bold"),
            text_color="#00D4FF"
        )
        logo_label.pack(pady=18, padx=20)
        
        # Subtítulo
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Control Anti-Recoil v2.0",
            font=("Arial", 9),
            text_color="#64748B"
        )
        subtitle.pack(pady=(0, 12), padx=20)
        
        # Separador decorativo dual
        ctk.CTkFrame(header_frame, height=1, fg_color="#00D4FF").pack(fill="x", padx=20)
        ctk.CTkFrame(header_frame, height=1, fg_color="#1E40AF").pack(fill="x", padx=20, pady=10)
        
        # ===== ÁREA DE BOTONES =====
        buttons_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        buttons_frame.pack(fill="both", expand=False, padx=15, pady=15)
        
        # Botones principales con mejor estilo
        self.menu_buttons = {}
        menu_items = [
            ("🎯 Anti-Recoil", COLORS["PRIMARY"], self.show_aim_assist),
            ("👥 Usuarios", COLORS["SECONDARY"], self.show_users),
            ("⚙️ Configuración", COLORS["ACCENT"], self.show_settings),
            ("📝 Editor", COLORS["INFO"], self.show_editor),
        ]
        
        for text, color, command in menu_items:
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                font=("Arial", 11, "bold"),
                fg_color=color,
                hover_color=self._lighter_color(color),
                text_color="white",
                command=command,
                height=48,
                corner_radius=10,
                border_width=0,
                cursor="hand2"
            )
            btn.pack(fill="x", pady=6)
            self.menu_buttons[text] = btn
        
        # ===== SEPARADOR =====
        ctk.CTkFrame(buttons_frame, height=1, fg_color="#1E293B", corner_radius=0).pack(fill="x", pady=15)
        
        # ===== SECCIÓN UTILIDADES =====
        utils_label = ctk.CTkLabel(
            buttons_frame,
            text="UTILIDADES",
            font=("Arial", 9, "bold"),
            text_color="#64748B"
        )
        utils_label.pack(anchor="w", padx=5, pady=(10, 8))
        
        btn_hotkey = ctk.CTkButton(
            buttons_frame,
            text="⌨️ Hotkey (Ctrl+B)",
            font=("Arial", 10),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color="#CBD5E1",
            command=self.show_hotkey_info,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color="#334155",
            cursor="hand2"
        )
        btn_hotkey.pack(fill="x", pady=5)
        
        # ===== ESPACIADOR =====
        ctk.CTkLabel(buttons_frame, text="").pack(expand=True, fill="y")
        
        # ===== BOTÓN SALIR =====
        exit_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ SALIR",
            fg_color=COLORS["DANGER"],
            hover_color="#EF233C",
            height=45,
            font=("Arial", 12, "bold"),
            corner_radius=10,
            command=self.on_closing,
            cursor="hand2"
        )
        exit_btn.pack(fill="x", pady=(15, 0))
    
    def _setup_content_area(self):
        """Configurar área de contenido principal mejorada"""
        # Frame externo con gradiente visual
        outer_frame = ctk.CTkFrame(self, fg_color="transparent")
        outer_frame.pack(side="right", expand=True, fill="both", padx=0, pady=0)
        
        # Fondo superior decorativo
        top_bar = ctk.CTkFrame(outer_frame, height=8, fg_color="#00D4FF", corner_radius=0)
        top_bar.pack(fill="x", padx=0, pady=0)
        
        # Frame principal con padding
        self.content_frame = ctk.CTkFrame(outer_frame, fg_color="#0F172A", corner_radius=0)
        self.content_frame.pack(expand=True, fill="both", padx=0, pady=0)
        
        # ===== ENCABEZADO CON ESTADO =====
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="#1A1F3A", height=80, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        left_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_header.pack(side="left", fill="both", expand=True, padx=25, pady=15)
        
        self.title_label = ctk.CTkLabel(
            left_header,
            text="Bienvenido",
            font=("Arial", 28, "bold"),
            text_color="#00D4FF"
        )
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(
            left_header,
            text="Sistema Anti-Recoil Profesional",
            font=("Arial", 11),
            text_color="#64748B"
        )
        self.subtitle_label.pack(anchor="w", pady=(3, 0))
        
        # Estado en esquina derecha
        right_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_header.pack(side="right", padx=25, pady=15)
        
        self.system_status_label = ctk.CTkLabel(
            right_header,
            text="● INACTIVO",
            font=("Arial", 11, "bold"),
            text_color="#EF4444"
        )
        self.system_status_label.pack()
        
        # Separador
        ctk.CTkFrame(self.content_frame, height=1, fg_color="#1E293B").pack(fill="x")
        
        # ===== ÁREA DE CONTENIDO DINÁMICO =====
        self.dynamic_content = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.dynamic_content.pack(expand=True, fill="both", padx=30, pady=25)
    
    def _setup_footer(self):
        """Configurar pie de página mejorado con indicadores"""
        self.footer_frame = ctk.CTkFrame(self.content_frame, fg_color="#1A1F3A", height=60, corner_radius=0)
        self.footer_frame.pack(fill="x", padx=0, pady=0, side="bottom")
        self.footer_frame.pack_propagate(False)
        
        # Contenedor con padding
        footer_inner = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        footer_inner.pack(fill="both", expand=True, padx=25, pady=12)
        
        # Estado del sistema
        status_frame = ctk.CTkFrame(footer_inner, fg_color="transparent")
        status_frame.pack(side="left", fill="x", expand=True)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="Estado del Sistema:",
            font=("Arial", 10),
            text_color="#64748B"
        )
        status_label.pack(side="left", padx=(0, 8))
        
        self.system_status = ctk.CTkLabel(
            status_frame,
            text="🟡 Esperando...",
            font=("Arial", 10, "bold"),
            text_color="#FFD60A"
        )
        self.system_status.pack(side="left")
        
        # Separador vertical
        ctk.CTkFrame(footer_inner, width=1, fg_color="#334155").pack(side="left", fill="y", padx=15)
        
        # Info del hotkey
        hotkey_label = ctk.CTkLabel(
            footer_inner,
            text="⌨️ Presiona Ctrl+B para mostrar/ocultar",
            font=("Arial", 9),
            text_color="#94A3B8"
        )
        hotkey_label.pack(side="right")
    
    def _init_system(self):
        """Inicializar el sistema de aim assist"""
        try:
            aim_controller.start()
            print("✓ Sistema de aim assist iniciado en segundo plano")
            self._start_status_updates()
        except Exception as e:
            print(f"✗ Error al iniciar sistema: {e}")
    
    def _handle_menu_click(self, button_label):
        """Manejar clics en los botones del menú"""
        actions = {
            "🎯 Anti-Recoil": self.show_aim_assist,
            "👥 Usuarios": self.show_users,
            "⚙️ Configuración": self.show_settings,
            "📝 Editor": self.show_editor,
        }
        
        if button_label in actions:
            actions[button_label]()
    
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
        """Cargar contenido de bienvenida mejorado"""
        self.hide_loader()
        
        # Scroll frame
        scroll_frame = ctk.CTkScrollableFrame(self.dynamic_content, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)
        
        # Tarjeta de bienvenida principal
        welcome_card = ctk.CTkFrame(
            scroll_frame,
            fg_color="#1A1F3A",
            corner_radius=15,
            border_width=2,
            border_color="#00D4FF"
        )
        welcome_card.pack(fill="x", pady=(0, 25), padx=0)
        
        # Icono principal
        icon_label = ctk.CTkLabel(
            welcome_card,
            text="🎮",
            font=("Arial", 60)
        )
        icon_label.pack(pady=(20, 10))
        
        # Título
        welcome_title = ctk.CTkLabel(
            welcome_card,
            text="Bienvenido a AIM ASSIST",
            font=("Arial", 26, "bold"),
            text_color="#00D4FF"
        )
        welcome_title.pack(pady=(5, 3))
        
        # Subtítulo
        welcome_subtitle = ctk.CTkLabel(
            welcome_card,
            text="Sistema Profesional de Control Anti-Recoil",
            font=("Arial", 12),
            text_color="#64748B"
        )
        welcome_subtitle.pack(pady=(0, 20))
        
        # Grid de características (2x2)
        features_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        features_frame.pack(fill="x", pady=20)
        
        features = [
            ("⚡ Ultra Rápido", "Compensación instantánea sin lag perceptible", "#1E40AF"),
            ("🎯 Preciso", "Calibrado para máxima exactitud y control", "#1E3A8A"),
            ("🔧 Configurable", "Ajusta parámetros según cada arma y distancia", "#1E40AF"),
            ("🎨 Moderno", "Interfaz elegante e intuitiva para todos", "#1E3A8A")
        ]
        
        for i, (title, desc, color) in enumerate(features):
            if i % 2 == 0:
                row_frame = ctk.CTkFrame(features_frame, fg_color="transparent")
                row_frame.pack(fill="x", padx=20, pady=10)
            
            feature_card = ctk.CTkFrame(
                row_frame,
                fg_color=color,
                corner_radius=10,
                border_width=1,
                border_color="#334155",
                height=100
            )
            feature_card.pack(side="left" if i % 2 == 0 else "right", fill="both", expand=True, padx=(0 if i % 2 == 0 else 10, 10))
            feature_card.pack_propagate(False)
            
            ft_title = ctk.CTkLabel(
                feature_card,
                text=title,
                font=("Arial", 12, "bold"),
                text_color="#00D4FF"
            )
            ft_title.pack(pady=(12, 3), padx=15, anchor="w")
            
            ft_desc = ctk.CTkLabel(
                feature_card,
                text=desc,
                font=("Arial", 10),
                text_color="#94A3B8",
                wraplength=180,
                justify="left"
            )
            ft_desc.pack(pady=(0, 12), padx=15, anchor="w")
        
        # Atajos rápidos
        self._create_shortcut_card(scroll_frame)
        
        # Instrucciones
        self._create_instructions_section(scroll_frame)
    
    def _create_shortcut_card(self, parent):
        """Crear tarjeta de atajo de teclado mejorada"""
        shortcut_frame = ctk.CTkFrame(
            parent,
            corner_radius=12,
            fg_color="transparent",
            border_width=2,
            border_color="#00D4FF"
        )
        shortcut_frame.pack(pady=25, padx=20, fill="x")
        
        # Fondo del contenido
        bg_frame = ctk.CTkFrame(shortcut_frame, fg_color="#1E40AF", corner_radius=10)
        bg_frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        shortcut_text = ctk.CTkLabel(
            bg_frame,
            text="⌨️  ATAJO RÁPIDO: Ctrl + B",
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        shortcut_text.pack(pady=15)
        
        shortcut_desc = ctk.CTkLabel(
            bg_frame,
            text="Presiona Ctrl+B en cualquier momento para mostrar/ocultar esta ventana sin perder el enfoque en el juego",
            font=("Arial", 11),
            text_color="#BFDBFE",
            wraplength=400
        )
        shortcut_desc.pack(pady=(0, 15), padx=20)
    
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
    
    def _lighter_color(self, hex_color):
        """Generar versión más clara de un color hex"""
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        lighter_rgb = tuple(min(int(c * 1.3), 255) for c in rgb)
        return "#{:02x}{:02x}{:02x}".format(*lighter_rgb)
    
    def _darker_color(self, hex_color):
        """Generar versión más oscura de un color hex"""
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(int(c * 0.7) for c in rgb)
        return "#{:02x}{:02x}{:02x}".format(*darker_rgb)
    
    def _update_status(self):
        """Actualizar estado del sistema"""
        if not self.winfo_exists():
            return
        
        try:
            # Actualizar estado del aim assist
            if aim_controller.enabled:
                self.system_status_label.configure(
                    text="● ACTIVO",
                    text_color="#4ADE80"
                )
                self.system_status.configure(
                    text="🟢 Aim Assist en funcionamiento",
                    text_color="#4ADE80"
                )
            else:
                self.system_status_label.configure(
                    text="● INACTIVO",
                    text_color="#EF4444"
                )
                self.system_status.configure(
                    text="🔴 Presiona Num Lock para activar",
                    text_color="#EF4444"
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
        # Si cambiamos opciones relacionadas con overlay, reaplicar estilos
        if key in ("overlay_mode", "overlay_clickthrough", "always_on_top"):
            try:
                self._apply_overlay_settings()
            except Exception:
                pass
    
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
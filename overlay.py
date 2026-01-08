import tkinter as tk
from tkinter import font
import threading
from aim_assist import aim_controller

class OverlayWindow:
    """Ventana overlay transparente que muestra información en tiempo real"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-topmost', True)  # Siempre al frente
        self.root.attributes('-alpha', 0.8)  # Semi-transparente
        self.root.configure(bg='#1a1a1a')
        
        # Configurar ventana sin bordes
        self.root.geometry('300x200+20+20')
        self.root.overrideredirect(True)
        
        # Crear frame principal
        main_frame = tk.Frame(self.root, bg='#1a1a1a', relief=tk.FLAT, borderwidth=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Fuentes
        title_font = font.Font(family="Arial", size=12, weight="bold")
        normal_font = font.Font(family="Arial", size=10)
        
        # Título
        title_label = tk.Label(
            main_frame, 
            text="⚙️ AIM ASSIST",
            font=title_font,
            fg='#4CC9F0',
            bg='#1a1a1a'
        )
        title_label.pack(pady=(0, 5))
        
        # Separador
        tk.Frame(main_frame, bg='#333333', height=1).pack(fill=tk.X, padx=5, pady=2)
        
        # Intensidad
        self.intensity_label = tk.Label(
            main_frame,
            text="Intensidad: 70%",
            font=normal_font,
            fg='#FFD60A',
            bg='#1a1a1a',
            justify=tk.LEFT
        )
        self.intensity_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Operador
        self.operator_label = tk.Label(
            main_frame,
            text="Operador: Ninguno",
            font=normal_font,
            fg='#7209B7',
            bg='#1a1a1a',
            justify=tk.LEFT
        )
        self.operator_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Disparos
        self.shots_label = tk.Label(
            main_frame,
            text="Disparos: 0",
            font=normal_font,
            fg='#FF006E',
            bg='#1a1a1a',
            justify=tk.LEFT
        )
        self.shots_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Ráfagas
        self.bursts_label = tk.Label(
            main_frame,
            text="Ráfagas: 0",
            font=normal_font,
            fg='#00F5FF',
            bg='#1a1a1a',
            justify=tk.LEFT
        )
        self.bursts_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Estado
        self.status_label = tk.Label(
            main_frame,
            text="Estado: LISTO",
            font=normal_font,
            fg='#4ADE80',
            bg='#1a1a1a',
            justify=tk.LEFT
        )
        self.status_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Separador
        tk.Frame(main_frame, bg='#333333', height=1).pack(fill=tk.X, padx=5, pady=2)
        
        # Info (pequeño)
        info_font = font.Font(family="Arial", size=8)
        info_label = tk.Label(
            main_frame,
            text="[P] Stats | [1-3] Distancia\n[A-R] Operadores | [+/-] Control",
            font=info_font,
            fg='#888888',
            bg='#1a1a1a',
            justify=tk.CENTER
        )
        info_label.pack(pady=3)
        
        # Configurar callback
        aim_controller.overlay_callback = self.update_overlay
        
    def update_overlay(self, stats):
        """Actualizar información del overlay"""
        try:
            self.intensity_label.config(text=f"Intensidad: {stats['intensity']}")
            self.operator_label.config(text=f"Operador: {stats['operator']}")
            self.shots_label.config(text=f"Disparos: {stats['shots']}")
            self.bursts_label.config(text=f"Ráfagas: {stats['bursts']}")
            
            # Actualizar estado
            if stats['reloading']:
                status = "🔄 RECARGANDO"
                color = '#FFA500'
            elif stats['aiming']:
                status = "🎯 APUNTANDO"
                color = '#FFD60A'
            else:
                status = "✅ LISTO"
                color = '#4ADE80'
            
            self.status_label.config(text=f"Estado: {status}", fg=color)
        except:
            pass  # Evitar errores si la ventana se cierra
    
    def run(self):
        """Ejecutar overlay"""
        self.root.mainloop()
    
    def close(self):
        """Cerrar overlay"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass


def start_overlay():
    """Iniciar overlay en un hilo separado"""
    overlay = OverlayWindow()
    threading.Thread(target=overlay.run, daemon=True).start()
    return overlay


if __name__ == "__main__":
    overlay = start_overlay()
    overlay.run()

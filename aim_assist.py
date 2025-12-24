import win32api
import time
import keyboard
import random
import threading
from typing import Dict, Any

class AimAssistController:
    def __init__(self):
        self.enabled = False
        self.running = False
        self.toggle_button = 'num lock'
        self.current_config = None
        self.thread = None
        
    def set_config(self, weapon_cfg: Dict[str, Any]):
        """Establecer la configuración del arma"""
        self.current_config = weapon_cfg
        print(f"Configuración actualizada:")
        print(f"  Horizontal Range: {weapon_cfg.get('horizontal_range')}")
        print(f"  Vertical: {weapon_cfg.get('min_vertical')}-{weapon_cfg.get('max_vertical')}")
    
    def write_mouse(self, x: str):
        """Simular movimiento del mouse"""
        try:
            dx, dy = map(int, x.split(';'))
            win32api.mouse_event(0x0001, dx, dy, 0, 0)
        except Exception as e:
            print(f"Error en movimiento del mouse: {e}")
    
    def is_mouse_down(self):
        """Verificar si botón izquierdo está presionado"""
        return win32api.GetKeyState(0x01) < 0
    
    def is_right_mouse_down(self):
        """Verificar si botón derecho está presionado"""
        return win32api.GetKeyState(0x02) < 0
    
    def aim_assist_loop(self):
        """Loop principal del aim assist"""
        print("Anti-recoil loop iniciado")
        last_toggle_state = False
        
        while self.running:
            # Verificar toggle (Num Lock)
            key_down = keyboard.is_pressed(self.toggle_button)
            if key_down != last_toggle_state:
                last_toggle_state = key_down
                if key_down:
                    self.enabled = not self.enabled
                    print(f"Aim Assist {'ENABLED' if self.enabled else 'DISABLED'}")
            
            # Verificar si tenemos configuración y estamos activados
            if self.enabled and self.current_config and self.is_right_mouse_down():
                # Si se presiona el botón izquierdo mientras el derecho está presionado
                if self.is_mouse_down():
                    self.apply_recoil_compensation()
                else:
                    # Pequeña pausa cuando no se está disparando
                    time.sleep(0.01)
            else:
                # Pausa más larga cuando no se necesita procesamiento
                time.sleep(0.05)
    
    def apply_recoil_compensation(self):
        """Aplicar compensación de recoil cuando se dispara"""
        if not self.current_config:
            return
        
        shot_count = 0
        config = self.current_config
        
        # Mientras ambos botones estén presionados y esté habilitado
        while (self.enabled and 
               self.is_right_mouse_down() and 
               self.is_mouse_down() and 
               self.running):
            
            # Calcular compensación vertical progresiva
            vertical_trend = min(shot_count * 0.1, 2.0)
            
            # Obtener offsets
            vertical_offset = random.uniform(
                config.get("min_vertical", 2) + vertical_trend,
                config.get("max_vertical", 4) + vertical_trend
            )
            
            horizontal_offset = random.uniform(
                -config.get("horizontal_range", 0.3),
                config.get("horizontal_range", 0.3)
            )
            
            time_offset = random.uniform(
                config.get("min_firerate", 0.01),
                config.get("max_firerate", 0.02)
            )
            
            # Aplicar movimiento del mouse hacia ABAJO (offset positivo en Y)
            # En Windows, positivo en Y mueve hacia ABAJO
            self.write_mouse(f"{int(horizontal_offset)};{int(vertical_offset)}")
            
            # Pausa entre disparos
            time.sleep(time_offset)
            shot_count += 1
            
            # Verificar que aún estén presionados los botones
            if not (self.is_right_mouse_down() and self.is_mouse_down()):
                break
    
    def start(self):
        """Iniciar el aim assist en segundo plano"""
        if self.running:
            print("Ya está ejecutándose")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.aim_assist_loop, daemon=True)
        self.thread.start()
        print("Aim Assist iniciado en segundo plano")
    
    def stop(self):
        """Detener el aim assist"""
        self.running = False
        self.enabled = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("Aim Assist detenido")
    
    def toggle(self, state: bool = None):
        """Activar/desactivar el aim assist"""
        if state is None:
            self.enabled = not self.enabled
        else:
            self.enabled = state
        print(f"Aim Assist {'activado' if self.enabled else 'desactivado'}")

# Instancia global para usar en toda la aplicación
aim_controller = AimAssistController()
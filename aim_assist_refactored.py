import win32api
import time
import keyboard
import random
import threading
from typing import Dict, Any, Callable
from datetime import datetime


class KeyManager:
    """Gestor centralizado de atajos de teclado"""
    def __init__(self):
        self.last_states = {}
        self.callbacks = {}
        
    def register_key(self, key: str, callback: Callable):
        """Registrar una tecla con su callback"""
        self.callbacks[key] = callback
        self.last_states[key] = False
    
    def update(self):
        """Procesar todas las teclas registradas"""
        for key, callback in self.callbacks.items():
            is_pressed = keyboard.is_pressed(key)
            was_pressed = self.last_states.get(key, False)
            
            # Callback solo en transición de soltar a presionar
            if is_pressed and not was_pressed:
                callback()
            
            self.last_states[key] = is_pressed


class PresetManager:
    """Gestor de presets (distancia, operadores, etc)"""
    def __init__(self):
        self.distance_presets = {
            '1': (0.4, 'CORTA (30m)'),
            '2': (0.7, 'MEDIA (15-20m)'),
            '3': (0.95, 'LARGA (25+m)')
        }
        self.operator_profiles = {
            'f1': ('Ash', 0.7, 'R4-C'),
            'f2': ('Twitch', 0.65, 'F2'),
            'f3': ('Jäger', 0.7, '416-C'),
            'f4': ('IQ', 0.7, '552 Commando'),
            'f5': ('Ela', 0.6, 'Scorpion'),
            'f6': ('Rook', 0.75, 'MP5'),
        }
        self.quick_configs = {
            'f7': ('2. attack', '2. attack.yaml'),
            'f8': ('3. defense', '3. defense.yaml'),
        }


class AimAssistController:
    def __init__(self):
        self.enabled = False
        self.running = False
        self.toggle_button = 'num lock'
        self.current_config = None
        self.current_operator = None
        self.config_manager = None
        self.current_game = "ar6"
        self.thread = None
        self.current_intensity = 1.0
        self.intensity_step = 0.05
        
        # Managers
        self.presets = PresetManager()
        self.keys = KeyManager()
        
        # Estado de entrada
        self.is_aiming = False
        self.is_reloading = False
        self.last_distance_preset = None
        self.aim_start_time = 0
        
        # Configuración
        self.first_shot_intensity = 0.3
        self.full_spray_bullets = 5
        self.reload_duration = 2.5
        self.zoom_threshold = 0.5
        
        # Estadísticas
        self.session_start = datetime.now()
        self.total_shots = 0
        self.total_bursts = 0
        self.current_burst_count = 0
        self.was_shooting = False
        self.overlay_callback = None
        
        self._setup_keybinds()
    
    def _setup_keybinds(self):
        """Configurar todos los atajos"""
        # Intensidad
        self.keys.register_key('+', lambda: self._adjust_intensity(+1))
        self.keys.register_key('-', lambda: self._adjust_intensity(-1))
        self.keys.register_key('*', lambda: self._reset_intensity())
        
        # Presets de distancia
        for preset in ['1', '2', '3']:
            self.keys.register_key(preset, lambda p=preset: self._apply_distance_preset(p))
        
        # Operadores (F1-F6)
        for op_key in ['f1', 'f2', 'f3', 'f4', 'f5', 'f6']:
            self.keys.register_key(op_key, lambda ok=op_key: self._load_operator(ok))
        
        # Configs rápidas (F7-F8)
        self.keys.register_key('f7', lambda: self._load_quick_config('f7'))
        self.keys.register_key('f8', lambda: self._load_quick_config('f8'))
        
        # Estadísticas
        self.keys.register_key('p', lambda: self._print_stats())
    
    def _adjust_intensity(self, direction: int):
        """Ajustar intensidad (+/-)"""
        delta = self.intensity_step * direction
        self.current_intensity = max(0.1, min(1.0, self.current_intensity + delta))
        print(f"{'🔼' if direction > 0 else '🔽'} Intensidad: {self.current_intensity:.0%}")
    
    def _reset_intensity(self):
        """Reset intensidad a 70%"""
        self.current_intensity = 0.7
        print(f"🔄 Intensidad reset a 70%")
    
    def _apply_distance_preset(self, preset: str):
        """Aplicar preset de distancia"""
        if preset != self.last_distance_preset:
            intensity, name = self.presets.distance_presets[preset]
            self.current_intensity = intensity
            print(f"📍 Preset: {name} ({intensity:.0%})")
            self.last_distance_preset = preset
    
    def _load_operator(self, op_key: str):
        """Cargar perfil de operador"""
        if op_key in self.presets.operator_profiles:
            name, intensity, weapon = self.presets.operator_profiles[op_key]
            self.current_intensity = intensity
            self.current_operator = name
            print(f"🎯 {name} ({weapon}) - Intensidad: {intensity:.0%}")
    
    def _load_quick_config(self, config_key: str):
        """Cargar configuración rápida"""
        if not self.config_manager or config_key not in self.presets.quick_configs:
            return
        
        try:
            config_name, config_file = self.presets.quick_configs[config_key]
            config_data = self.config_manager.load_config(self.current_game, config_name)
            self.set_config(config_data)
            print(f"📁 Config: {config_file}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _print_stats(self):
        """Mostrar estadísticas de sesión"""
        elapsed = (datetime.now() - self.session_start).total_seconds()
        minutes, seconds = int(elapsed // 60), int(elapsed % 60)
        avg_bullets = (self.total_shots / self.total_bursts) if self.total_bursts > 0 else 0
        
        print(f"\n📊 SESIÓN:")
        print(f"  Operador: {self.current_operator or 'N/A'}")
        print(f"  Disparos: {self.total_shots} | Ráfagas: {self.total_bursts}")
        print(f"  Promedio: {avg_bullets:.1f} balas/ráfaga")
        print(f"  Tiempo: {minutes}m {seconds}s | Intensidad: {self.current_intensity:.0%}\n")
    
    def set_config(self, weapon_cfg: Dict[str, Any]):
        """Establecer configuración del arma"""
        self.current_config = weapon_cfg
        self.total_shots = 0
        self.total_bursts = 0
        horiz = weapon_cfg.get('horizontal_range', 0)
        vert_min = weapon_cfg.get('min_vertical', 0)
        vert_max = weapon_cfg.get('max_vertical', 0)
        print(f"⚙️ Config: Horiz={horiz} | Vertical=[{vert_min}, {vert_max}]")
    
    def write_mouse(self, dx: float, dy: float):
        """Simular movimiento del mouse"""
        try:
            dx, dy = int(round(dx)), int(round(dy))
            win32api.mouse_event(0x0001, dx, dy, 0, 0)
        except Exception as e:
            print(f"❌ Error mouse: {e}")
    
    def is_mouse_down(self) -> bool:
        return win32api.GetKeyState(0x01) < 0
    
    def is_right_mouse_down(self) -> bool:
        return win32api.GetKeyState(0x02) < 0
    
    def aim_assist_loop(self):
        """Loop principal simplificado"""
        print("▶️  Anti-recoil iniciado")
        print("📋 ATAJOS: [+][-][*] intensidad | [1][2][3] distancia | [F1-F6] ops | [F7][F8] config | [P] stats | [NumLock] toggle")
        
        last_toggle = False
        
        while self.running:
            # Toggle principal (Num Lock)
            toggle_pressed = keyboard.is_pressed(self.toggle_button)
            if toggle_pressed != last_toggle:
                last_toggle = toggle_pressed
                if toggle_pressed:
                    self.enabled = not self.enabled
                    print(f"{'✅' if self.enabled else '❌'} Aim Assist {'ON' if self.enabled else 'OFF'}")
            
            # Procesar atajos registrados
            self.keys.update()
            
            # Detección de zoom (Space)
            space_pressed = keyboard.is_pressed('space')
            if space_pressed and not self.is_aiming:
                self.is_aiming = True
                self.aim_start_time = time.time()
            elif not space_pressed and self.is_aiming:
                self.is_aiming = False
            
            # Detección de recarga auto
            if self.is_reloading and time.time() - self.reload_start_time > self.reload_duration:
                self.is_reloading = False
                print("✅ Recarga completa")
            
            # Procesamiento de disparo
            if self.enabled and self.current_config and self.is_right_mouse_down():
                if self.is_mouse_down() and not self.is_reloading:
                    self.apply_recoil_compensation()
                    if not self.was_shooting:
                        self.total_bursts += 1
                        self.current_burst_count = 0
                    self.was_shooting = True
                else:
                    self.was_shooting = False
                    time.sleep(0.01)
            else:
                self.was_shooting = False
                time.sleep(0.05)
    
    def apply_recoil_compensation(self):
        """Aplicar compensación de recoil"""
        if not self.current_config:
            return
        
        config = self.current_config
        config_intensity = config.get("recoil_intensity", 0.7)
        recoil_intensity = config_intensity * self.current_intensity
        
        # Reducir retroceso en zoom
        if self.is_aiming and (time.time() - self.aim_start_time) > self.zoom_threshold:
            recoil_intensity *= 0.6
        
        shot_count = 0
        while self.enabled and self.is_right_mouse_down() and self.is_mouse_down() and self.running:
            # Control de primera bala
            if shot_count < self.full_spray_bullets:
                progress = shot_count / self.full_spray_bullets
                current_recoil = recoil_intensity * (self.first_shot_intensity + 
                                (1 - self.first_shot_intensity) * progress)
            else:
                current_recoil = recoil_intensity
            
            # Calcular offsets
            vertical_trend = min(shot_count * 0.1, 2.0)
            vertical_offset = random.uniform(
                config.get("min_vertical", 2) + vertical_trend,
                config.get("max_vertical", 4) + vertical_trend
            ) * current_recoil
            
            horizontal_offset = random.uniform(
                -config.get("horizontal_range", 0.3),
                config.get("horizontal_range", 0.3)
            ) * current_recoil
            
            time_offset = random.uniform(
                config.get("min_firerate", 0.01),
                config.get("max_firerate", 0.02)
            )
            
            # Aplicar movimiento
            self.write_mouse(horizontal_offset, vertical_offset)
            
            # Estadísticas
            self.total_shots += 1
            self.current_burst_count += 1
            if self.overlay_callback:
                self.overlay_callback({
                    'intensity': f"{self.current_intensity:.0%}",
                    'operator': self.current_operator or "N/A",
                    'shots': self.total_shots,
                    'bursts': self.total_bursts,
                })
            
            time.sleep(time_offset)
            shot_count += 1
    
    def start(self):
        """Iniciar aim assist"""
        if self.running:
            print("⚠️  Ya está ejecutándose")
            return
        self.running = True
        self.thread = threading.Thread(target=self.aim_assist_loop, daemon=True)
        try:
            self.thread.start()
            print("✅ Aim Assist iniciado")
        except Exception as e:
            self.running = False
            self.thread = None
            print(f"❌ Error: {e}")
    
    def stop(self):
        """Detener aim assist"""
        self.running = False
        self.enabled = False
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=1.0)
            except Exception:
                pass
        self.thread = None
        print("⏹️  Aim Assist detenido")
    
    def toggle(self, state: bool = None):
        """Toggle activación"""
        self.enabled = state if state is not None else not self.enabled
        print(f"{'✅' if self.enabled else '❌'} Aim Assist {'activado' if self.enabled else 'desactivado'}")


# Instancia global
aim_controller = AimAssistController()

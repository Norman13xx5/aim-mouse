import os
import yaml

class ConfigManager:
    def __init__(self):
        self.configs_dir = "configs"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Crear estructura de directorios si no existe"""
        if not os.path.exists(self.configs_dir):
            os.makedirs(self.configs_dir)
        
        # Crear subdirectorios para cada categoría principal
        categorias = ["ar6", "opcion2", "opcion3"]
        for categoria in categorias:
            path = os.path.join(self.configs_dir, categoria)
            if not os.path.exists(path):
                os.makedirs(path)
    
    def get_available_configs(self):
        """Obtener todas las configuraciones disponibles"""
        configs = {}
        
        for categoria in os.listdir(self.configs_dir):
            categoria_path = os.path.join(self.configs_dir, categoria)
            if os.path.isdir(categoria_path):
                configs[categoria] = []
                for archivo in os.listdir(categoria_path):
                    if archivo.endswith('.yaml'):
                        nombre = archivo.replace('.yaml', '')
                        configs[categoria].append(nombre)
        
        return configs
    
    def load_config(self, categoria, nombre):
        """Cargar configuración específica"""
        config_path = os.path.join(self.configs_dir, categoria, f"{nombre}.yaml")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"No se encontró el archivo: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        
        return config_data
    
    def save_config(self, categoria, nombre, data):
        """Guardar configuración"""
        categoria_path = os.path.join(self.configs_dir, categoria)
        if not os.path.exists(categoria_path):
            os.makedirs(categoria_path)
        
        config_path = os.path.join(categoria_path, f"{nombre}.yaml")
        
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False)
    # Agregar estos métodos a la clase ConfigManager en config_manager.py

def get_all_configs(self):
    """Obtener todas las configuraciones organizadas por juego"""
    all_configs = {}
    
    if not os.path.exists(self.configs_dir):
        return all_configs
    
    for game in os.listdir(self.configs_dir):
        game_path = os.path.join(self.configs_dir, game)
        if os.path.isdir(game_path):
            all_configs[game] = {}
            for config_file in os.listdir(game_path):
                if config_file.endswith('.yaml'):
                    config_name = config_file.replace('.yaml', '')
                    config_path = os.path.join(game_path, config_file)
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config_data = yaml.safe_load(f)
                        all_configs[game][config_name] = config_data
                    except Exception as e:
                        print(f"Error cargando {config_file}: {e}")
    
    return all_configs

def delete_config(self, game, config_name):
    """Eliminar una configuración"""
    config_path = os.path.join(self.configs_dir, game, f"{config_name}.yaml")
    
    if os.path.exists(config_path):
        os.remove(config_path)
        return True
    return False

def create_game_folder(self, game_name):
    """Crear una nueva carpeta de juego"""
    game_path = os.path.join(self.configs_dir, game_name)
    
    if not os.path.exists(game_path):
        os.makedirs(game_path)
        return True
    return False
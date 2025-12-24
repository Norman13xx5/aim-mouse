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
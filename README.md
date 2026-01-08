# aim-mouse
Python Mouse Automation: Recoil Compensation Logic Este repositorio contiene un script educativo desarrollado en Python diseñado para demostrar la automatización de periféricos de entrada (ratón) mediante la simulación de movimientos compensatorios en el eje Y.


# Control de Anti-Recoil 🎮

Sistema de control de anti-recoil para Rainbow Six Siege con interfaz gráfica moderna.

## 📋 Requisitos del Sistema

- **Python**: 3.7 o superior
- **Sistema Operativo**: Windows (requiere librerías específicas de Windows)

## 🔧 Instalación de Dependencias

### 1. Instalar Python
Descarga Python desde [python.org](https://www.python.org/downloads/) asegúrate de marcar "Add Python to PATH" durante la instalación.

### 2. Instalar las dependencias necesarias

Abre PowerShell o CMD en la carpeta del proyecto y ejecuta:

```bash
pip install customtkinter keyboard pyyaml pywin32
```

O instala desde el archivo de requisitos (si lo creas):

```bash
pip install -r requirements.txt
```

### 3. Dependencias individuales:

| Librería | Propósito |
|----------|-----------|
| **customtkinter** | Interfaz gráfica moderna (GUI) |
| **keyboard** | Detectar pulsaciones de teclas globales |
| **pyyaml** | Cargar y guardar configuraciones YAML |
| **pywin32** | Controlar el mouse a nivel del sistema Windows |

## 🚀 Cómo Usar

### Iniciando la aplicación:

```bash
python main.py
```

### Controles principales:

| Tecla/Acción | Función |
|--------------|---------|
| **Num Lock** | Activar/Desactivar Anti-Recoil |
| **[1]** | Corta distancia (40% retroceso) |
| **[2]** | Media distancia (70% retroceso) |
| **[3]** | Larga distancia (95% retroceso) |
| **[+]** | Aumentar intensidad retroceso |
| **[-]** | Reducir intensidad retroceso |
| **[*]** numpad | Reset a 70% (default) |
| **[Space]** | Zoom automático (-40% retroceso) |
| **[F1]** | Operador: Ash (R4-C) |
| **[F2]** | Operador: Twitch (F2) |
| **[F3]** | Operador: Jäger (416-C) |
| **[F4]** | Operador: IQ (552 Commando) |
| **[F5]** | Operador: Ela (Scorpion) |
| **[F6]** | Operador: Rook (MP5) |
| **[F7]** | 📁 Config rápida: 2. attack.yaml |
| **[F8]** | 📁 Config rápida: 3. defense.yaml |
| **[P]** | Mostrar estadísticas de sesión |
| **[E]** | ✅ LIBRE (voltear mira) |
| **[R]** | ✅ LIBRE (recargar) |
| **Click Derecho** | Mantener para apuntar |
| **Click Izquierdo** | Disparar (aplica anti-recoil automático) |

### Pasos para usar:

1. Ejecuta `python main.py`
2. Selecciona la categoría del arma (ej: R6, Opción2, Opción3)
3. Selecciona la configuración específica (ej: Attack, Defense, Twitch)
4. Haz clic en "Cargar Configuración"
5. Haz clic en "Activar Aim Assist"
6. En el juego:
   - Presiona **Num Lock** para activar/desactivar
   - El anti-recoil se aplica automáticamente al disparar

## 📁 Estructura del Proyecto

```
├── main.py                 # Aplicación principal
├── aim_assist.py          # Lógica del anti-recoil
├── config_manager.py      # Gestor de configuraciones
├── inicio.py              # Interfaz principal
├── configs/               # Configuraciones por categoría
│   ├── r6/
│   │   ├── attack.yaml
│   │   ├── defense.yaml
│   │   └── twitch.yaml
│   ├── opcion2/
│   │   └── twitch.yaml
│   └── opcion3/
└── README.md             # Este archivo
```

## ⚙️ Archivos de Configuración

Las configuraciones se guardan en formato YAML en la carpeta `configs/`. Ejemplo de estructura:

```yaml
horizontal_range: 0.3
min_vertical: 2
max_vertical: 4
min_firerate: 0.01
max_firerate: 0.02
```

## 🎯 Características

✅ Anti-recoil automático para Rainbow Six Siege  
✅ Interfaz gráfica intuitiva (Dark Mode)  
✅ Múltiples configuraciones por arma  
✅ **Presets por distancia** (corta, media, larga)  
✅ **Perfiles automáticos de operadores** (A, T, J, I, E, R)  
✅ **Zoom automático** (reduce retroceso en ADS)  
✅ **Detección de primera bala** (precisión mejorada)  
✅ **Pausa automática en recarga**  
✅ **Estadísticas de sesión en tiempo real**  
✅ Toggle con Num Lock durante el juego  
✅ Ejecución en segundo plano  
✅ Controles por click derecho + izquierdo  

## ⚠️ Notas Importantes

- Este programa está diseñado específicamente para **Windows**
- Requiere permisos de administrador para controlar el mouse globalmente
- Puede ser detectado por anti-cheat en algunos juegos - **úsalo responsablemente**
- El programa se ejecuta en segundo plano incluso con la ventana oculta

## 🔍 Solución de Problemas

### "No se puede importar win32api"
```bash
pip install pywin32
```

### "No se puede importar customtkinter"
```bash
pip install customtkinter
```

### "El atajo Ctrl+B no funciona"
- Asegúrate de que la aplicación tenga los permisos necesarios
- Intenta ejecutar como administrador

### "No se aplica el anti-recoil"
- Verifica que hayas cargado una configuración
- Comprueba que Num Lock esté activado
- Asegúrate de presionar click derecho + izquierdo simultáneamente

## 📝 Licencia

Uso personal únicamente.

---

**¡Diviértete mejorando tu puntería! 🎮**

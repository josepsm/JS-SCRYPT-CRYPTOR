# Instalación y entorno de desarrollo

## Herramientas

- Windows 10/11.
- Python (comprueba la versión instalada con `py --version`).
- Visual Studio Code, editor recomendado para abrir y modificar `encryptor.py`.
- Extensión oficial de Python para VS Code (opcional, recomendada).

## Preparar el proyecto en Windows

1. Instala Python desde https://www.python.org/downloads/ y activa **Add Python to PATH**.
2. Instala Visual Studio Code desde https://code.visualstudio.com/.
3. Descarga el repositorio y abre la carpeta en VS Code.
4. Selecciona **Terminal → New Terminal**.
5. Ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python encryptor.py
```

Si no puedes activar el entorno virtual:

```powershell
py -m pip install -r requirements.txt
py encryptor.py
```

## ¿Qué es cada herramienta?

- **Python:** lenguaje e intérprete que ejecuta el programa.
- **Visual Studio Code:** editor donde se escribe y modifica el código.
- **cryptography:** biblioteca que proporciona AES-GCM y Scrypt.
- **venv:** crea un entorno virtual separado para las dependencias del proyecto.
- **PyInstaller:** empaqueta el programa y sus dependencias en un ejecutable de Windows.

## Comprobar versiones

En la terminal:

```powershell
py --version
python --version
pip show cryptography
```

Anota la versión exacta de Python utilizada al crear cada versión del `.exe` en la descripción de la publicación de GitHub.

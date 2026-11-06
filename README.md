# JS SCRYPT — CRYPTOR

**Aplicación de cifrado local de mensajes, archivos y carpetas.**

JS SCRYPT — CRYPTOR es un proyecto escrito en Python que ofrece un menú de consola para proteger información mediante AES-256-GCM y derivación de claves con Scrypt. Incluye una herramienta XOR de división y reconstrucción 3-de-3.

> **Estado:** versión inicial publicada para revisión y aprendizaje. El proyecto no ha sido auditado por especialistas independientes. No se debe presentar como software de seguridad certificado.

## Funciones

1. Cifrar mensajes y guardarlos en archivos `.cryptor`.
2. Cifrar archivos y conservar su nombre original en los metadatos.
3. Descifrar mensajes y archivos.
4. Cifrar una carpeta completa en un único archivo `.cryptor`.
5. Descifrar una carpeta y recuperar su estructura.
6. Dividir un archivo en tres partes XOR.
7. Reconstruir un archivo utilizando las tres partes.
8. Salir del programa.

## Tecnologías

- **Lenguaje:** Python.
- **Criptografía:** biblioteca `cryptography`.
- **Cifrado autenticado:** AES-256-GCM.
- **Derivación de clave:** Scrypt.
- **Formato de metadatos:** JSON.
- **Compresión de carpetas:** ZIP mediante la biblioteca estándar `zipfile`.
- **Empaquetado para Windows:** PyInstaller (para generar el ejecutable `.exe`).

### Entorno de desarrollo

El código puede editarse en **Visual Studio Code (VS Code)**. VS Code es el editor; Python es el lenguaje y el intérprete que ejecuta el programa. Para conocer la versión exacta instalada en tu equipo, ejecuta `python --version` o `py --version` en la terminal. La versión de Python usada para crear un `.exe` debe anotarse en la publicación de esa compilación.

Este repositorio no fija una versión exacta de Python porque el ejecutable puede haberse generado desde otro entorno. Se recomienda Python 3.10 o posterior compatible con la versión de `cryptography` instalada.

## Instalación desde el código fuente

### Windows 10 / Windows 11

1. Instala Python desde [python.org](https://www.python.org/downloads/). Durante la instalación marca **Add Python to PATH**.
2. Instala [Visual Studio Code](https://code.visualstudio.com/) si deseas editar el código.
3. Descarga este repositorio con **Code → Download ZIP** y extrae la carpeta.
4. Abre la carpeta `JS-SCRYPT-CRYPTOR` en VS Code.
5. En VS Code abre **Terminal → New Terminal**.
6. Ejecuta estos comandos:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python encryptor.py
```

Si PowerShell no permite activar el entorno virtual, puedes instalar y ejecutar usando el lanzador `py`:

```powershell
py -m pip install -r requirements.txt
py encryptor.py
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python encryptor.py
```

## Uso rápido

Ejecuta `python encryptor.py`. En el menú, escribe el número de la función:

| Opción | Acción |
|---:|---|
| 1 | Cifrar mensaje |
| 2 | Cifrar archivo |
| 3 | Descifrar mensaje o archivo |
| 4 | Cifrar carpeta |
| 5 | Descifrar carpeta |
| 6 | Dividir archivo `.cryptor` en tres partes |
| 7 | Reconstruir desde las tres partes |
| 8 | Salir |

Las rutas se escriben completas. En Windows, por ejemplo: `C:\Users\Usuario\Documents\archivo.pdf`.

## Cómo funciona

### Scrypt

La contraseña no se usa directamente como clave AES. Scrypt deriva una clave de 32 bytes a partir de la contraseña y una sal aleatoria de 16 bytes. Los parámetros usados por esta versión son `N=2^15`, `r=8`, `p=1`. La sal se guarda en el archivo porque no es secreta.

### AES-256-GCM

Se genera un nonce aleatorio de 12 bytes y se cifra con AES-GCM usando la clave derivada. GCM proporciona confidencialidad e integridad/autenticación. Si la contraseña es incorrecta o el contenido cifrado fue modificado, la verificación de autenticidad falla.

### Archivo `.cryptor`

Los datos se almacenan en JSON con campos como `type`, `salt`, `nonce` y `encrypted`. Los bytes se representan en hexadecimal. Para archivos y carpetas también se guarda `original_name`. La representación hexadecimal aumenta el tamaño final.

### Cifrado de carpetas

La carpeta se comprime primero en un ZIP en memoria. Luego, el ZIP completo se cifra como un solo contenido. Al recuperar, el programa descifra y extrae el ZIP después de revisar las rutas y enlaces simbólicos.

### División XOR 3-de-3

El programa crea dos partes aleatorias y calcula una tercera usando XOR. Para reconstruir el archivo se necesitan las tres partes. Es un esquema sencillo 3-de-3, **no es Shamir Secret Sharing** y no permite reconstruir con solo dos partes. La función no agrega una etiqueta de autenticidad independiente a las partes: conserva el contenido exacto, pero una parte dañada puede producir un resultado corrupto.

## Seguridad y limitaciones

- Si pierdes la contraseña, no existe recuperación automática.
- No borres el archivo original hasta verificar que el `.cryptor` se puede descifrar correctamente.
- Mantén copias de seguridad.
- Guarda las tres partes XOR en ubicaciones separadas; si pierdes una, no podrás reconstruir el archivo.
- El programa lee archivos y carpetas completos en memoria; archivos muy grandes pueden consumir mucha RAM.
- El formato JSON hexadecimal aumenta el tamaño.
- No se ha realizado una auditoría de seguridad independiente. No uses esta versión como única protección de información crítica.
- No publiques archivos personales, contraseñas ni datos privados en el repositorio.

## Ejecutable para Windows (.exe)

El repositorio incluye una carpeta `release/` con instrucciones. El archivo ejecutable real debe ser copiado por el autor desde su compilación de Windows. No se incluye un `.exe` ficticio en este paquete.

También puedes distribuirlo en GitHub mediante **Releases**:
1. Abre el repositorio.
2. En la sección **Releases**, selecciona **Create a new release**.
3. Escribe una etiqueta, por ejemplo `v1.0.0`.
4. Adjunta el archivo real `CRYPTOR.exe`.
5. Publica la versión.

Para generar un ejecutable desde el código:

```powershell
py -m pip install pyinstaller
pyinstaller --onefile --console --name CRYPTOR encryptor.py
```

El ejecutable se genera en la carpeta `dist`. Prueba el `.exe` en otro equipo Windows antes de anunciarlo como versión estable. El usuario final no necesita instalar Python si el ejecutable se empaquetó correctamente, aunque Windows puede mostrar advertencias de SmartScreen para aplicaciones nuevas no firmadas.

## Estructura

```text
JS-SCRYPT-CRYPTOR/
├── encryptor.py
├── requirements.txt
├── README.md
├── LICENSE
├── SECURITY.md
├── .gitignore
├── docs/
│   ├── INSTALACION.md
│   ├── FUNCIONAMIENTO.md
│   └── SEGURIDAD.md
└── release/
    └── README.md
```

## Contribuciones

Las sugerencias y reportes de errores son bienvenidos. Antes de abrir un Issue público, no incluyas contraseñas, archivos cifrados privados ni información personal.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE`.

---

**JS SCRYPT — CRYPTOR**  
*Cifrado local. Control de tus archivos.*

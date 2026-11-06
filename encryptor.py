import os
import io
import shutil
import stat
import json
import zipfile

from getpass import getpass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


print("CRYPTOR: MOTOR CRIPTOGRÁFICO INICIADO")
print("AES-256-GCM: DISPONIBLE")
print("SCRYPT: DISPONIBLE")


# ==========================================
# GENERADOR DE CLAVES
# ==========================================

def generate_key(password):

    salt = os.urandom(16)

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**15,
        r=8,
        p=1
    )

    key = kdf.derive(password.encode("utf-8"))

    return key, salt


# ==========================================
# CIFRADO DE MENSAJES
# ==========================================

def encrypt_text(text, password):

    key, salt = generate_key(password)

    nonce = os.urandom(12)

    aes = AESGCM(key)

    encrypted = aes.encrypt(
        nonce,
        text.encode("utf-8"),
        None
    )

    return salt, nonce, encrypted


def save_encrypted_file(salt, nonce, encrypted, filename):

    data = {
        "type": "message",
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "encrypted": encrypted.hex()
    }

    if not filename.endswith(".cryptor"):
        filename += ".cryptor"

    if os.path.exists(filename):
        print(f"ERROR: el archivo {filename} ya existe.")
        return False

    with open(filename, "x") as file:
        json.dump(data, file, indent=4)

    print(f"Archivo {filename} guardado correctamente.")

    return True


# ==========================================
# CIFRADO DE ARCHIVOS
# ==========================================

def encrypt_file(filename, password):

    with open(filename, "rb") as file:
        file_data = file.read()

    key, salt = generate_key(password)

    nonce = os.urandom(12)

    aes = AESGCM(key)

    encrypted = aes.encrypt(
        nonce,
        file_data,
        None
    )

    original_name = os.path.basename(filename)

    print("\n¿Cómo deseas guardar el archivo?")
    print("[1] Conservar nombre original")
    print("[2] Elegir un nombre personalizado")

    choice = input("CRYPTOR >> ").strip()

    if choice == "1":

        output_name = original_name

    elif choice == "2":

        output_name = input("Nuevo nombre del archivo: ").strip()

        if not output_name:
            print("ERROR: nombre vacío.")
            return False

        if os.path.basename(output_name) != output_name:
            print("ERROR: introduce solamente un nombre, sin rutas.")
            return False

    else:

        print("ERROR: opción no válida.")
        return False

    if not output_name.endswith(".cryptor"):
        output_name += ".cryptor"

    data = {
        "type": "file",
        "original_name": original_name,
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "encrypted": encrypted.hex()
    }

    if os.path.exists(output_name):
        print(f"ERROR: el archivo {output_name} ya existe.")
        return False

    with open(output_name, "x") as file:
        json.dump(data, file, indent=4)

    print(f"Archivo cifrado correctamente: {output_name}")

    return True


# ==========================================
# CARGAR ARCHIVO CIFRADO
# ==========================================

def load_encrypted_file(filename):

    with open(filename, "r") as file:
        data = json.load(file)

    salt = bytes.fromhex(data["salt"])
    nonce = bytes.fromhex(data["nonce"])
    encrypted = bytes.fromhex(data["encrypted"])

    return salt, nonce, encrypted


# ==========================================
# DESCIFRADO DE MENSAJES Y ARCHIVOS
# ==========================================

def decrypt_file(filename, password):

    with open(filename, "r") as file:
        data = json.load(file)

    if data.get("type") == "folder":
        print("ERROR: utiliza la opción de descifrar carpeta.")
        return False

    salt = bytes.fromhex(data["salt"])
    nonce = bytes.fromhex(data["nonce"])
    encrypted = bytes.fromhex(data["encrypted"])

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**15,
        r=8,
        p=1
    )

    key = kdf.derive(password.encode("utf-8"))

    aes = AESGCM(key)

    decrypted = aes.decrypt(
        nonce,
        encrypted,
        None
    )

    original_name = data.get("original_name")

    if original_name is None:

        print("\nMENSAJE RECUPERADO:")
        print("--------------------------------")
        print(decrypted.decode("utf-8"))
        print("--------------------------------")

        return True

    if not original_name or os.path.basename(original_name) != original_name:
        print("ERROR: nombre de archivo no válido.")
        return False

    if os.path.exists(original_name):
        print("ERROR: ya existe un archivo con ese nombre.")
        return False

    with open(original_name, "xb") as file:
        file.write(decrypted)

    print(f"Archivo recuperado correctamente: {original_name}")

    return True


# ==========================================
# CREAR ZIP DE UNA CARPETA
# ==========================================

def create_zip_folder(folder_path):

    buffer = io.BytesIO()

    with zipfile.ZipFile(
        buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as archive:

        for root, dirs, files in os.walk(folder_path):

            for folder in dirs:

                folder_path_inside = os.path.join(root, folder)

                archive_name = os.path.relpath(
                    folder_path_inside,
                    folder_path
                )

                archive.write(
                    folder_path_inside,
                    archive_name
                )

            for file in files:

                file_path = os.path.join(root, file)

                archive_name = os.path.relpath(
                    file_path,
                    folder_path
                )

                archive.write(
                    file_path,
                    archive_name
                )

    return buffer.getvalue()


# ==========================================
# CIFRADO DE CARPETAS
# ==========================================

def encrypt_folder(folder_path, password):

    if not os.path.isdir(folder_path):
        print("ERROR: la carpeta no existe.")
        return False

    folder_path = os.path.abspath(folder_path)

    folder_name = os.path.basename(folder_path)

    output_name = folder_name + ".cryptor"

    output_path = os.path.join(
        os.path.dirname(folder_path),
        output_name
    )

    if os.path.exists(output_path):
        print("ERROR: ese archivo ya existe.")
        return False

    folder_data = create_zip_folder(folder_path)

    key, salt = generate_key(password)

    nonce = os.urandom(12)

    aes = AESGCM(key)

    encrypted = aes.encrypt(
        nonce,
        folder_data,
        None
    )

    data = {
        "type": "folder",
        "original_name": folder_name,
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "encrypted": encrypted.hex()
    }

    with open(output_path, "x") as file:
        json.dump(data, file, indent=4)

    print(f"Carpeta cifrada correctamente: {output_name}")

    return True


# ==========================================
# DESCIFRADO DE CARPETAS
# ==========================================

def decrypt_folder(filename, password):

    with open(filename, "r") as file:
        data = json.load(file)

    if data.get("type") != "folder":
        print("ERROR: este archivo no contiene una carpeta.")
        return False

    salt = bytes.fromhex(data["salt"])
    nonce = bytes.fromhex(data["nonce"])
    encrypted = bytes.fromhex(data["encrypted"])

    folder_name = data["original_name"]

    if not folder_name or os.path.basename(folder_name) != folder_name:
        print("ERROR: nombre de carpeta no válido.")
        return False

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**15,
        r=8,
        p=1
    )

    key = kdf.derive(password.encode("utf-8"))

    aes = AESGCM(key)

    decrypted = aes.decrypt(
        nonce,
        encrypted,
        None
    )

    output_folder = os.path.join(
        os.path.dirname(os.path.abspath(filename)),
        folder_name
    )

    if os.path.exists(output_folder):
        print("ERROR: ya existe una carpeta con ese nombre.")
        return False

    try:

        with zipfile.ZipFile(
            io.BytesIO(decrypted),
            "r"
        ) as archive:

            for info in archive.infolist():

                name = info.filename.replace("\\", "/")

                parts = name.split("/")

                if (
                    name.startswith("/")
                    or any(part == ".." for part in parts)
                    or ":" in parts[0]
                ):
                    raise ValueError("Ruta no permitida en el ZIP.")

                target = os.path.abspath(
                    os.path.join(output_folder, *parts)
                )

                if os.path.commonpath(
                    [output_folder, target]
                ) != output_folder:

                    raise ValueError("Ruta fuera de la carpeta.")

                mode = info.external_attr >> 16

                if stat.S_ISLNK(mode):
                    raise ValueError("Enlace simbólico no permitido.")

            os.makedirs(output_folder)

            archive.extractall(output_folder)

        print(f"Carpeta recuperada correctamente: {folder_name}")

        return True

    except Exception:

        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)

        raise


# ==========================================
# SISTEMA DE DIVISION 3 DE 3
# ==========================================

def split_cryptor_file(filename):

    with open(filename, "rb") as file:
        original_data = file.read()

    if not original_data:
        print("ERROR: el archivo está vacío.")
        return False

    part1 = os.urandom(len(original_data))

    part2 = os.urandom(len(original_data))

    part3 = bytes(
        a ^ b ^ c
        for a, b, c in zip(original_data, part1, part2)
    )

    filenames = [
        filename + ".parte1",
        filename + ".parte2",
        filename + ".parte3"
    ]

    if any(os.path.exists(name) for name in filenames):
        print("ERROR: una o más partes ya existen.")
        return False

    created_files = []

    try:

        parts = [part1, part2, part3]

        for name, part in zip(filenames, parts):

            with open(name, "xb") as file:
                file.write(part)

            created_files.append(name)

        print("Archivo dividido correctamente en 3 partes.")

        return True

    except Exception:

        for name in created_files:
            if os.path.exists(name):
                os.remove(name)

        raise


def reconstruct_cryptor_file(
    part1_path,
    part2_path,
    part3_path,
    output_path
):

    paths = [part1_path, part2_path, part3_path]

    parts = []

    for path in paths:

        with open(path, "rb") as file:
            parts.append(file.read())

    if not parts[0] or not (
        len(parts[0]) == len(parts[1]) == len(parts[2])
    ):
        print("ERROR: las partes están vacías o tienen tamaños diferentes.")
        return False

    reconstructed = bytes(
        a ^ b ^ c
        for a, b, c in zip(parts[0], parts[1], parts[2])
    )

    if os.path.exists(output_path):
        print("ERROR: el archivo reconstruido ya existe.")
        return False

    with open(output_path, "xb") as file:
        file.write(reconstructed)

    print("Archivo reconstruido correctamente.")

    return True


# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================

print()
print("========================================")
print("              JS SCRYPT")
print("========================================")
print()
print("          C R Y P T O R")
print("       SISTEMA DE CIFRADO SEGURO")
print("========================================")
print("  MOTOR: AES-256-GCM")
print("  DERIVACION: SCRYPT")
print("========================================")
print()
print("  [1]  CIFRAR MENSAJE")
print("  [2]  CIFRAR ARCHIVO")
print("  [3]  DESCIFRAR MENSAJE / ARCHIVO")
print("  [4]  CIFRAR CARPETA")
print("  [5]  DESCIFRAR CARPETA")
print("  [6]  DIVIDIR ARCHIVO CRYPTOR EN 3 PARTES")
print("  [7]  RECONSTRUIR ARCHIVO DESDE 3 PARTES")
print("  [8]  SALIR")
print()
print("----------------------------------------")


while True:

    option = input(
        "CRYPTOR >> Selecciona una opción: "
    ).strip()

    # OPCIÓN 1: CIFRAR MENSAJE

    if option == "1":

        password = getpass("Crea tu contraseña: ")

        confirm_password = getpass("Confirma tu contraseña: ")

        if not password:

            print("ERROR: la contraseña no puede estar vacía.")

        elif password != confirm_password:

            print("ERROR: las contraseñas no coinciden.")

        else:

            message = input(
                "Escribe el mensaje que deseas proteger: "
            )

            filename = input("Nombre del archivo: ").strip()

            if not filename:

                print("ERROR: nombre vacío.")

            else:

                salt, nonce, encrypted = encrypt_text(
                    message,
                    password
                )

                saved = save_encrypted_file(
                    salt,
                    nonce,
                    encrypted,
                    filename
                )

                if saved:
                    print("Mensaje cifrado correctamente.")

    # OPCIÓN 2: CIFRAR ARCHIVO

    elif option == "2":

        filename = input(
            "Ruta del archivo que deseas cifrar: "
        ).strip()

        password = getpass("Crea tu contraseña: ")

        confirm_password = getpass("Confirma tu contraseña: ")

        if not password:

            print("ERROR: la contraseña no puede estar vacía.")

        elif password != confirm_password:

            print("ERROR: las contraseñas no coinciden.")

        else:

            try:

                encrypt_file(filename, password)

            except FileNotFoundError:

                print("ERROR: el archivo original no existe.")

            except PermissionError:

                print("ERROR: no tienes permiso para leer ese archivo.")

            except Exception as e:

                print(f"ERROR inesperado: {e}")

    # OPCIÓN 3: DESCIFRAR MENSAJE O ARCHIVO

    elif option == "3":

        try:

            filename = input(
                "Nombre del archivo que deseas descifrar: "
            ).strip()

            if not filename.endswith(".cryptor"):
                filename += ".cryptor"

            password_attempt = getpass(
                "Introduce tu contraseña: "
            )

            decrypt_file(filename, password_attempt)

        except InvalidTag:

            print("ERROR: contraseña incorrecta o datos modificados.")

        except FileNotFoundError:

            print("ERROR: el archivo no existe.")

        except json.JSONDecodeError:

            print("ERROR: el archivo está dañado o no tiene un formato válido.")

        except PermissionError:

            print("ERROR: no tienes permiso para acceder al archivo.")

        except Exception as e:

            print(f"ERROR inesperado: {e}")

    # OPCIÓN 4: CIFRAR CARPETA

    elif option == "4":

        folder_path = input(
            "Ruta de la carpeta que deseas cifrar: "
        ).strip()

        password = getpass("Crea tu contraseña: ")

        confirm_password = getpass("Confirma tu contraseña: ")

        if not password:

            print("ERROR: la contraseña no puede estar vacía.")

        elif password != confirm_password:

            print("ERROR: las contraseñas no coinciden.")

        else:

            try:

                encrypt_folder(folder_path, password)

            except FileNotFoundError:

                print("ERROR: no se encontró la carpeta o alguno de sus archivos.")

            except PermissionError:

                print("ERROR: no tienes permiso para acceder a la carpeta.")

            except Exception as e:

                print(f"ERROR inesperado: {e}")

    # OPCIÓN 5: DESCIFRAR CARPETA

    elif option == "5":

        try:

            filename = input(
                "Nombre del archivo de carpeta que deseas descifrar: "
            ).strip()

            if not filename.endswith(".cryptor"):
                filename += ".cryptor"

            password_attempt = getpass(
                "Introduce tu contraseña: "
            )

            decrypt_folder(filename, password_attempt)

        except InvalidTag:

            print("ERROR: contraseña incorrecta o datos modificados.")

        except FileNotFoundError:

            print("ERROR: el archivo no existe.")

        except json.JSONDecodeError:

            print("ERROR: el archivo está dañado o no tiene un formato válido.")

        except PermissionError:

            print("ERROR: no tienes permiso para acceder al archivo.")

        except Exception as e:

            print(f"ERROR inesperado: {e}")

    # OPCIÓN 6: DIVIDIR ARCHIVO EN 3 PARTES

    elif option == "6":

        try:

            filename = input(
                "Ruta del archivo .cryptor que deseas dividir: "
            ).strip()

            if not filename.endswith(".cryptor"):
                filename += ".cryptor"

            split_cryptor_file(filename)

        except FileNotFoundError:

            print("ERROR: el archivo no existe.")

        except PermissionError:

            print("ERROR: no tienes permiso para acceder al archivo.")

        except Exception as e:

            print(f"ERROR inesperado: {e}")

    # OPCIÓN 7: RECONSTRUIR ARCHIVO DESDE 3 PARTES

    elif option == "7":

        try:

            part1 = input("Ruta de la parte 1: ").strip()
            part2 = input("Ruta de la parte 2: ").strip()
            part3 = input("Ruta de la parte 3: ").strip()

            output = input(
                "Nombre del archivo reconstruido (sin .cryptor): "
            ).strip()

            if not output:

                print("ERROR: nombre vacío.")

            else:

                if not output.endswith(".cryptor"):
                    output += ".cryptor"

                reconstruct_cryptor_file(
                    part1,
                    part2,
                    part3,
                    output
                )

        except FileNotFoundError:

            print("ERROR: no se encontró una de las tres partes.")

        except PermissionError:

            print("ERROR: no tienes permiso para acceder a los archivos.")

        except Exception as e:

            print(f"ERROR inesperado: {e}")

    # OPCIÓN 8: SALIR

    elif option == "8":

        print()
        print("========================================")
        print("       CRYPTOR FINALIZADO")
        print("       Gracias por utilizar CRYPTOR")
        print("========================================")

        break

    else:

        print("Opción no válida.")

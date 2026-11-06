# Funcionamiento técnico

## Generación de clave

`generate_key(password)` genera 16 bytes aleatorios de sal y usa Scrypt para derivar una clave de 32 bytes. Parámetros actuales: `N=2^15`, `r=8`, `p=1`.

## Cifrado de mensajes y archivos

`encrypt_text()` convierte el texto a UTF-8. `encrypt_file()` lee los bytes del archivo. Ambos caminos generan un nonce aleatorio de 12 bytes y cifran mediante `AESGCM.encrypt()`.

`save_encrypted_file()` guarda mensajes como JSON. Los archivos incluyen además el nombre original. Los campos binarios se codifican en hexadecimal.

## Descifrado

`decrypt_file()` lee el JSON, deriva otra vez la clave usando la contraseña y la sal almacenada y llama a `AESGCM.decrypt()`. Una contraseña incorrecta o datos manipulados hacen fallar la autenticación.

## Carpetas

`create_zip_folder()` crea un ZIP en memoria. `encrypt_folder()` cifra los bytes del ZIP. `decrypt_folder()` autentica y descifra, comprueba rutas sospechosas y enlaces simbólicos, y extrae el contenido.

## División XOR 3-de-3

Se crean dos secuencias aleatorias `A` y `B`; la tercera parte es `C = D XOR A XOR B`, donde `D` es el archivo original. La reconstrucción calcula `D = A XOR B XOR C`. Se requieren las tres partes. No es Shamir Secret Sharing. Las partes no tienen una autenticación independiente, por lo que conviene comprobar el archivo reconstruido.

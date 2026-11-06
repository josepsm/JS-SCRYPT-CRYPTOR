# Consideraciones de seguridad

- AES-256-GCM ofrece cifrado autenticado cuando se usa correctamente.
- Scrypt deriva una clave desde una contraseña y una sal aleatoria.
- La sal y el nonce se guardan junto al contenido cifrado; no son contraseñas.
- No reutilices ni publiques contraseñas. El programa no puede recuperarlas.
- El código no ha sido auditado independientemente.
- El procesamiento se realiza en memoria y puede ser inadecuado para archivos muy grandes.
- Las partes XOR necesitan las tres piezas para reconstruir y no incluyen una autenticación separada.
- Mantén siempre una copia original hasta comprobar la recuperación.

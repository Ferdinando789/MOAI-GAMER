# MOAI GAMER

Proyecto de compilación y publicación de **MOAI GAMER v0.1.82 para Android TV ARM32**.

## Estado

La compilación se reconstruye a partir del código original del repositorio privado `Ferdinando789/MOAI-Lite-Deluxe` (rama `experimental/moai-gamer-v80`), más Flycast oficial. El repositorio original no se modifica.

## Requisito para compilar

En **Settings → Secrets and variables → Actions**, crear el secreto `MOAI_SOURCE_TOKEN` con un token de acceso personal de alcance limitado (*fine-grained PAT*) que tenga permiso **Contents: Read-only** sobre `Ferdinando789/MOAI-Lite-Deluxe`. No pegar el token en archivos, chats ni capturas.

## Generar APK

Abrir **Actions → Build and Release MOAI GAMER → Run workflow**. El workflow descarga las fuentes y el núcleo ARM32, ejecuta los tests, genera la APK base y el módulo opcional y, si termina correctamente, los publica en **Releases** con la etiqueta `v0.1.82-arm32-test`.

La publicación se realiza desde el propio runner, sin utilizar `actions/upload-artifact`. Las APK son **de prueba**; la base y el módulo se firman con la misma clave de depuración recuperada del paquete de compilación original. No instalar sobre una versión con firma diferente sin comprobar compatibilidad.

**Nota:** El código fuente Android completo no está almacenado aquí todavía. Este repositorio contiene el proceso de reconstrucción y publicación, y depende de acceso al repositorio original privado.

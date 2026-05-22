# 📊 Excel Protection Manager - v1.0.0

Herramienta para recuperar el acceso a hojas de Excel protegidas cuando la contraseña ha sido olvidada.

---

## 🚀 Descripción

**Excel Protection Manager** es una aplicación que permite eliminar la protección de hojas en archivos de Excel (`.xlsx`) sin necesidad de conocer la contraseña original.

Este proyecto nace de una necesidad real: recuperar acceso a editar información bloqueada por una contraseña olvidada, sin comprometer la integridad del archivo.

---

## ✨ Características

- Eliminación de protección de hojas de Excel
- Procesamiento rápido y automático
- No requiere contraseña
- Compatible con archivos `.xlsx`
- Distribución como ejecutable (`.exe`)

---

## 🧠 ¿Cómo funciona?

Los archivos `.xlsx` son archivos comprimidos que contienen múltiples archivos XML internos.

La protección de hojas en Excel no utiliza cifrado fuerte, sino restricciones dentro del archivo.

La aplicación:

1. Extrae el contenido del archivo `.xlsx`
2. Localiza los archivos de hojas (`sheet*.xml`)
3. Elimina la etiqueta `<sheetProtection>`
4. Reconstruye el archivo Excel

✅ Resultado: la hoja queda completamente editable.

---

## 🔮 Mejoras futuras - v2.0.0

- Soporte para protección de estructura del libro
- Backup automático del archivo original
- Logs detallados
- Reactivar el bloqueo de la estructura
- Version portable para windows

---

## ⚠️ Uso responsable

Este software ha sido desarrollado con fines de recuperación de acceso a archivos propios.

❗ No debe utilizarse para:
- Acceder a archivos de terceros sin autorización
- Manipular información sin consentimiento

El uso indebido de esta herramienta es responsabilidad exclusiva del usuario.

<!-- ---

## 📦 Descarga

Puedes descargar la versión ejecutable desde la sección de releases:

👉 https://github.com/obregon-jose/excel-protection-manager/releases

---

## ▶️ Uso

1. Ejecuta el archivo `.exe`
2. Selecciona el archivo Excel protegido
3. Espera el procesamiento
4. Obtén el archivo sin protección -->


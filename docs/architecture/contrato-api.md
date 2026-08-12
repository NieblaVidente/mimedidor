# Contrato de la API — MiMedidor

**Tarjeta:** T-04b · **Estado:** propuesta para revisión de los tres integrantes.

Este documento es lo que permite que `client/` y `server/` avancen en paralelo: quien construye
una pantalla trabaja contra los ejemplos de este documento sin esperar a que el endpoint real
exista. Una vez que los tres lo aprueben en el PR, **se congela** — cambiarlo después implica
reabrir esta tarjeta y avisar al resto, no editarlo por su cuenta.

Formato: JSON sobre HTTP, excepto donde se indica `multipart/form-data` para la subida de imagen.
Todas las fechas en formato `AAAA-MM-DD` (ISO 8601, sin hora). Todos los montos y consumos son
números, no strings.

---

## 1. Convención de errores

Toda respuesta de error, en cualquier ruta, tiene esta forma — nunca se expone una traza interna
ni un mensaje de la base de datos:

```json
{
  "error": {
    "codigo": "IMAGEN_ILEGIBLE",
    "mensaje": "No se pudo detectar la carátula del hidrómetro en la foto"
  }
}
```

### Códigos de error

| Código | HTTP | Cuándo ocurre |
|---|---|---|
| `IMAGEN_ILEGIBLE` | 422 | El preprocesamiento (T-09) no pudo detectar la carátula, o el recorte del odómetro (T-10) no salió |
| `VALIDACION` | 400 | El cuerpo de la petición no cumple el formato esperado (campo faltante, tipo incorrecto) |
| `MEDIDOR_NO_ENCONTRADO` | 404 | El `medidor_id` referenciado no existe |
| `FACTURA_NO_ENCONTRADA` | 404 | El `id` de factura en la URL no existe |
| `LECTURA_INVALIDA` | 422 | La lectura a guardar es menor que la última lectura registrada para ese medidor (un hidrómetro no retrocede) |
| `ERROR_INTERNO` | 500 | Cualquier fallo no anticipado. Se loguea completo en el servidor; al cliente solo llega este código genérico |

---

## 2. `POST /api/lecturas/reconocer`

Recibe una foto, la pasa por la cadena T-09 → T-10 → T-11 y devuelve la lectura reconocida
**sin guardarla**. El usuario todavía tiene que confirmarla o corregirla desde la pantalla (T-16)
antes de que se persista con el siguiente endpoint.

**Request:** `multipart/form-data`

| Campo | Tipo | Descripción |
|---|---|---|
| `foto` | archivo (jpeg/png) | La fotografía tomada por la app |
| `medidor_id` | string (uuid) | A qué medidor pertenece la foto |

**Response 200 — reconocimiento exitoso:**

```json
{
  "lectura_reconocida": 1284.0,
  "confianza": 0.42
}
```

`confianza` es un valor entre 0 y 1 que reporta la librería de OCR elegida en T-02b; si esa
librería no expone una medida de confianza, se envía `null` y el campo se documenta como no
disponible en esa librería.

**Response 422 — no se pudo leer:**

```json
{
  "error": {
    "codigo": "IMAGEN_ILEGIBLE",
    "mensaje": "No se pudo detectar la carátula del hidrómetro en la foto"
  }
}
```

La pantalla (T-16) tiene que dejar corregir la lectura manualmente en ambos casos — tanto si vino
un número con baja confianza como si esta ruta devolvió error.

---

## 3. `POST /api/lecturas`

Guarda la lectura ya confirmada o corregida por el usuario. Internamente usa el procedimiento
almacenado de T-14 (transacción con inserción de la lectura + actualización del consumo del
período).

**Request:**

```json
{
  "medidor_id": "3f7a1c2e-df21-4b3a-9a11-8e2f6a9d0c31",
  "valor": 1284.0,
  "fecha": "2026-08-12",
  "origen": "reconocimiento",
  "foto_url": "https://.../fotos/3f7a1c2e.jpg"
}
```

`origen` es `"reconocimiento"` si el usuario aceptó el valor devuelto por
`/api/lecturas/reconocer` sin tocarlo, o `"manual"` si lo escribió o corrigió a mano. Este dato no
es cosmético: es el que permite calcular la exactitud real en T-11 (cuántas lecturas necesitaron
corrección manual).

**Response 201:**

```json
{
  "id": "9c1e2a4b-1234-4a11-8f2e-abc123def456",
  "medidor_id": "3f7a1c2e-df21-4b3a-9a11-8e2f6a9d0c31",
  "valor": 1284.0,
  "fecha": "2026-08-12",
  "origen": "reconocimiento",
  "consumo_desde_anterior_m3": 12.0,
  "dias_desde_anterior": 30
}
```

`consumo_desde_anterior_m3` y `dias_desde_anterior` vienen en `null` si es la primera lectura de
ese medidor (T-17 debe manejar ese caso explícitamente).

**Response 422 — lectura menor a la anterior:**

```json
{
  "error": {
    "codigo": "LECTURA_INVALIDA",
    "mensaje": "El valor ingresado (1200.0) es menor que la última lectura registrada (1284.0)"
  }
}
```

---

## 4. `GET /api/lecturas?medidor_id={id}`

Historial de lecturas de un medidor, ordenado por fecha ascendente, con el consumo ya calculado
entre lecturas consecutivas (T-17).

**Response 200:**

```json
{
  "lecturas": [
    {
      "id": "8a1b2c3d-...",
      "valor": 1272.0,
      "fecha": "2026-07-13",
      "origen": "manual",
      "consumo_desde_anterior_m3": null,
      "dias_desde_anterior": null
    },
    {
      "id": "9c1e2a4b-...",
      "valor": 1284.0,
      "fecha": "2026-08-12",
      "origen": "reconocimiento",
      "consumo_desde_anterior_m3": 12.0,
      "dias_desde_anterior": 30
    }
  ]
}
```

Si `medidor_id` no existe, responde `404` con `MEDIDOR_NO_ENCONTRADO`. Si el medidor existe pero
no tiene lecturas, responde `200` con `"lecturas": []`.

---

## 5. `POST /api/facturas`

Registra una factura ingresada manualmente por el usuario (T-18).

**Request:**

```json
{
  "medidor_id": "3f7a1c2e-df21-4b3a-9a11-8e2f6a9d0c31",
  "periodo_inicio": "2026-07-13",
  "periodo_fin": "2026-08-12",
  "consumo_facturado_m3": 14.0,
  "monto": 8250.0
}
```

`monto` va en colones costarricenses, sin símbolo ni separadores de miles — solo el número.

**Response 201:**

```json
{
  "id": "f1e2d3c4-5678-4abc-9def-0123456789ab",
  "medidor_id": "3f7a1c2e-df21-4b3a-9a11-8e2f6a9d0c31",
  "periodo_inicio": "2026-07-13",
  "periodo_fin": "2026-08-12",
  "consumo_facturado_m3": 14.0,
  "monto": 8250.0
}
```

---

## 6. `GET /api/facturas/{id}/comparacion`

Cierra el hilo funcional del sprint (T-18): compara el consumo facturado contra el consumo medido
por las lecturas propias del abonado en el mismo período de la factura.

**Response 200:**

```json
{
  "factura_id": "f1e2d3c4-5678-4abc-9def-0123456789ab",
  "consumo_medido_m3": 12.0,
  "consumo_facturado_m3": 14.0,
  "diferencia_m3": 2.0,
  "diferencia_porcentual": 14.3,
  "supera_umbral": false
}
```

`supera_umbral` se calcula contra un umbral configurable (por ahora, un valor fijo razonable
como 15 % de diferencia — se documenta la decisión final cuando se implemente T-18, no es parte
de este contrato).

Si `id` no existe: `404` con `FACTURA_NO_ENCONTRADA`.

---

## 7. Lo que NO cubre este documento

- Autenticación de usuarios — es `P-15` del Product Backlog, fuera del alcance del Sprint 1. Por
  ahora todas las rutas asumen un único usuario implícito, sin token ni sesión.
- El modelo de datos exacto (tablas, columnas) — eso es T-12. Este contrato usa nombres de campo
  consistentes con lo que T-12 va a necesitar, pero la fuente de verdad del modelo es esa tarjeta,
  no este documento.
- Paginación en `GET /api/lecturas` — con el volumen del Sprint 1 (dataset de ~12-15 medidores) no
  hace falta. Se agrega si hace falta en Sprint 2.

---

## 8. Aprobación

| Integrante | Revisó | Comentarios |
|---|---|---|
| José Pablo Ramírez Sánchez | ✅ (autor de la propuesta) | |
| Isaac Felipe Morún Moreira | ✅ | Aprobado en PR #5 |
| Yariel Andrey Elizondo Jiménez | ⏳ pendiente | No pudo revisar: invitación de colaborador al repositorio sin aceptar a la fecha del merge. Se congela por mayoría (2 de 3); si al revisar señala un cambio necesario, se ajusta en un PR aparte |

Congelado por decisión del equipo con 2 de 3 aprobaciones — justificación completa en el
comentario del PR #5. No es la ruta normal (que exige los tres), así que si esto se repite en
otra tarjeta, hay que resolver de raíz el acceso de Yariel al repositorio en vez de acostumbrarse
a la excepción.

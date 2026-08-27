# Casos de uso principales — MiMedidor

**Issue:** [#35](https://github.com/NieblaVidente/mimedidor/issues/35) (T-25) · Exigido por la
Guía de Entregables §3.3 y §5.

Los cinco casos de uso principales del sistema, escritos contra el código que existe hoy en
`main` — no contra el diseño ideal. Cada flujo se corresponde con pantallas y endpoints reales
(`client/src/Pantalla*.tsx`, `server/app/api/*.py`) y con los errores del contrato de la API
(`docs/architecture/contrato-api.md` §1).

**Actor único: el abonado.** No hay autenticación en este sprint (P-15, fuera de alcance), así
que todas las rutas asumen un solo usuario implícito. Donde los casos dicen "el abonado", en la
aplicación real eso es simplemente quien tenga la pantalla abierta.

---

## Resumen

| # | Caso de uso | Pantalla | Endpoints | ¿Recorrible hoy? |
|---|---|---|---|---|
| 1 | Registrar una lectura desde una foto, con el reconocimiento acertando | `PantallaCaptura` | `POST /api/lecturas/reconocer` → `POST /api/lecturas` | ⚠️ Parcial — ver §1 |
| 2 | Registrar una lectura corrigiendo a mano lo que el reconocimiento leyó mal | `PantallaCaptura` | `POST /api/lecturas/reconocer` → `POST /api/lecturas` | ✅ Sí |
| 3 | Consultar el historial y el consumo entre lecturas | `PantallaHistorial` | `GET /api/lecturas` | ✅ Sí |
| 4 | Registrar una factura y contrastarla contra las lecturas propias | `PantallaFactura` | `POST /api/facturas` → `GET /api/facturas/{id}/comparacion` | ✅ Sí |
| 5 | Borde: no hay lecturas suficientes en el período para comparar | `PantallaFactura` | `GET /api/facturas/{id}/comparacion` | ✅ Sí |

**El caso 2 es el camino normal hoy, no la excepción.** La exactitud medida del reconocimiento es
**0 de 2** (`docs/exactitud-reconocimiento.md`). Está escrito en ese orden a propósito.

---

## 1. Registrar una lectura desde una foto (reconocimiento acertando)

**Actor:** el abonado.

**Precondiciones:**
- Existe un medidor registrado en la base de datos, y el abonado conoce su `id` (un UUID).
- El navegador tiene permiso de cámara.
- El servidor tiene Tesseract instalado y la base de datos accesible.

**Flujo principal:**

| # | El abonado… | El sistema… |
|---|---|---|
| 1 | Escribe el ID del medidor y pulsa **Abrir cámara** | Pide acceso a la cámara con `getUserMedia` y muestra el visor con una guía de encuadre |
| 2 | Encuadra la carátula dentro de la guía y pulsa **Tomar foto** | Captura el fotograma, apaga la cámara y muestra "Reconociendo la lectura…" |
| 3 | — | Envía la foto a `POST /api/lecturas/reconocer`, que corre la cadena T-09 → T-10 → T-11 |
| 4 | — | Muestra el valor reconocido en el campo editable, marcado como *"Lectura reconocida automáticamente — revisala antes de confirmar"*, con `origen = "reconocimiento"` |
| 5 | Verifica que el número coincide con lo que ve en el medidor y pulsa **Confirmar lectura** | Envía `POST /api/lecturas`, que ejecuta el procedimiento transaccional `registrar_lectura` (T-14) |
| 6 | — | Muestra la lectura guardada y, si no es la primera del medidor, el consumo y los días desde la anterior |

**Resultado esperado:** una fila nueva en `lectura` con `origen = 'reconocimiento'`, su fila
correspondiente en `lectura_evento` (escritas en la misma transacción), y el consumo del período
calculado en pantalla.

**Flujos alternativos:**

| Situación | Código | Qué ve el abonado |
|---|---|---|
| El navegador niega el permiso de cámara | — | *"No se pudo acceder a la cámara. Revisá los permisos del navegador."* |
| No se detecta la carátula o no se puede leer el odómetro | `IMAGEN_ILEGIBLE` (422) | *"No se pudo leer la lectura automáticamente. Escribila a mano."* → **continúa por el caso 2** |
| El `medidor_id` no existe al guardar | `MEDIDOR_NO_ENCONTRADO` (404) | El mensaje de error del contrato |
| El valor es menor que la última lectura de ese medidor | `LECTURA_INVALIDA` (422) | *"El valor ingresado (…) es menor que la última lectura registrada (…)"* |

> ⚠️ **Honestidad sobre este caso.** El flujo está implementado de punta a punta y es recorrible,
> pero el paso 5 — que el número reconocido *coincida* — **no se ha logrado ni una vez sobre
> fotos reales**: la exactitud medida es 0 de 2 (`docs/exactitud-reconocimiento.md`). Lo que se
> puede demostrar hoy es que la foto se procesa, que devuelve *algún* número o falla de forma
> visible, y que el guardado funciona. Este caso queda documentado porque es el objetivo del
> producto y el flujo existe, no porque ya funcione bien. Ver `CLAUDE.md` §8: no se maquilla.

---

## 2. Registrar una lectura corrigiendo a mano el reconocimiento

**Este es el camino normal hoy.** Existe precisamente porque sabemos que el reconocimiento falla
seguido — por eso el contrato de la API separó "reconocer" de "guardar" desde T-04b.

**Actor:** el abonado.

**Precondiciones:** las mismas del caso 1.

**Flujo principal:**

| # | El abonado… | El sistema… |
|---|---|---|
| 1-3 | Igual que el caso 1 (ID, cámara, foto) | Igual que el caso 1 |
| 4 | — | Devuelve un número equivocado, o falla con `IMAGEN_ILEGIBLE` y deja el campo vacío |
| 5 | Escribe el valor correcto leyéndolo del medidor | Al primer cambio del campo, marca `origen = "manual"` automáticamente y el texto pasa a *"Ingresada manualmente"* |
| 6 | Pulsa **Confirmar lectura** | Guarda con `POST /api/lecturas`, igual que el caso 1 |

**Resultado esperado:** una fila en `lectura` con `origen = 'manual'`. Ese campo no es cosmético:
es el que permite calcular después cuántas lecturas necesitaron corrección humana, que es la
medida real de exactitud del reconocimiento en producción.

**Detalle de implementación relevante:** el cambio de `origen` a `"manual"` lo hace
`manejarCambioValor` en `PantallaCaptura.tsx` — basta con que el abonado toque el campo. No hay
forma de guardar un valor editado a mano que quede marcado como reconocimiento automático, ni
por descuido.

**Flujos alternativos:** los mismos del caso 1 para el guardado (`MEDIDOR_NO_ENCONTRADO`,
`LECTURA_INVALIDA`), más:

| Situación | Qué ve el abonado |
|---|---|
| Deja el campo vacío o escribe algo que no es un número | *"Ingresá una lectura numérica válida antes de confirmar."* (validación del cliente, no llega al servidor) |

---

## 3. Consultar el historial y el consumo entre lecturas

**Actor:** el abonado.

**Precondiciones:** existe un medidor y el abonado conoce su ID.

**Flujo principal:**

| # | El abonado… | El sistema… |
|---|---|---|
| 1 | Escribe el ID del medidor en la sección **Historial de lecturas** y pulsa **Ver historial** | Llama a `GET /api/lecturas?medidor_id=…` |
| 2 | — | Muestra una tabla con fecha, lectura, origen y consumo del período, de la más vieja a la más nueva |

**Resultado esperado:** una fila por lectura registrada. El consumo entre lecturas consecutivas
se calcula al vuelo (diferencia de valores y de fechas contra la lectura anterior) — **no está
guardado como columna**, por la razón documentada en `docs/architecture/modelo-datos.md` §3: un
dato derivado guardado se desincroniza en cuanto se corrige una lectura.

**Flujos alternativos:**

| Situación | Código | Qué ve el abonado |
|---|---|---|
| El medidor no existe | `MEDIDOR_NO_ENCONTRADO` (404) | El mensaje de error del contrato |
| El medidor existe pero no tiene lecturas | — (200 con lista vacía) | *"Este medidor todavía no tiene lecturas registradas."* |
| Es la primera lectura del medidor | — | *"Primera lectura registrada de este medidor — todavía no hay consumo que calcular."* en vez de un `0` engañoso |

---

## 4. Registrar una factura y contrastarla contra las lecturas propias

Este es el caso que cierra el hilo funcional del proyecto: es el momento en que el abonado
descubre si lo que le cobran coincide con lo que él mismo midió.

**Actor:** el abonado, con la factura en papel o digital del operador enfrente.

**Precondiciones:** existe el medidor, y **hay al menos dos lecturas propias que cubran el
período de la factura** (si no, ver el caso 5).

**Flujo principal:**

| # | El abonado… | El sistema… |
|---|---|---|
| 1 | Completa el formulario **Registrar factura**: medidor, inicio y fin del período, consumo facturado en m³ y monto en colones | Valida en el cliente que ningún campo esté vacío y que los números sean números |
| 2 | Pulsa **Registrar y comparar** | Llama a `POST /api/facturas` y, con el `id` devuelto, encadena `GET /api/facturas/{id}/comparacion` |
| 3 | — | Muestra el consumo facturado, el consumo medido por sus lecturas, y la diferencia en m³ y en porcentaje |
| 4 | — | Si la diferencia supera el 15 %, agrega una alerta: *"La diferencia supera el umbral esperado — vale la pena revisarla."* |

**Resultado esperado:** una fila nueva en `factura` y la comparación en pantalla, redactada en
lenguaje natural (*"El operador facturó X m³ más/menos de lo que midieron tus propias
lecturas"*).

**Cómo se calcula el consumo medido:** igual que lo haría el operador real — la lectura más
reciente hasta el **inicio** del período contra la más reciente hasta el **fin** del período. No
se promedia ni se interpola nada.

**El umbral del 15 %** es un valor fijo de este sprint
(`UMBRAL_DIFERENCIA_PORCENTUAL` en `server/app/api/facturas.py`), tal como lo permite el contrato
de la API §6. Hacerlo configurable por el abonado es alcance de un sprint futuro.

**Flujos alternativos:**

| Situación | Código | Qué ve el abonado |
|---|---|---|
| `periodo_fin` es anterior o igual a `periodo_inicio` | `VALIDACION` (400) | *"periodo_fin debe ser posterior a periodo_inicio"* |
| El medidor no existe | `MEDIDOR_NO_ENCONTRADO` (404) | El mensaje de error del contrato |
| La factura no existe al pedir la comparación | `FACTURA_NO_ENCONTRADA` (404) | El mensaje de error del contrato |
| Faltan campos o hay texto donde va un número | — (validación del cliente) | *"Completá todos los campos con valores válidos antes de registrar la factura."* |

---

## 5. Caso de borde: no hay lecturas suficientes en el período

**Por qué merece ser un caso de uso propio:** es la situación más probable para un abonado nuevo.
Alguien que instala la aplicación hoy y registra su primera lectura no tiene con qué comparar su
próxima factura, y el sistema tiene que decirlo con claridad en vez de mostrar un `0` que se
leería como *"el operador te está cobrando de más por todo"*.

**Actor:** el abonado.

**Precondiciones:** existe el medidor y la factura, pero **no** hay dos lecturas propias que
cubran el período facturado — porque no hay ninguna, porque solo hay una, o porque las que hay
son todas posteriores al inicio del período.

**Flujo principal:**

| # | El abonado… | El sistema… |
|---|---|---|
| 1-2 | Registra la factura igual que en el caso 4 | Guarda la factura y pide la comparación |
| 3 | — | Al no encontrar las dos lecturas necesarias, devuelve `consumo_medido_m3`, `diferencia_m3` y `diferencia_porcentual` en `null`, y `supera_umbral` en `false` |
| 4 | — | Muestra el consumo facturado, un `—` donde iría el consumo medido, y el texto *"No hay suficientes lecturas propias en este período para comparar todavía."* |

**Resultado esperado:** la factura **sí queda registrada** (no se pierde el trabajo del abonado);
lo único que falta es la comparación, y se dice explícitamente. Cuando el abonado registre las
lecturas que faltan, la comparación de esa misma factura pasa a dar un resultado.

**Por qué `null` y no `0`:** es el mismo criterio de T-11 sobre no maquillar resultados. Un `0`
sería un número inventado que el abonado podría interpretar como un dato real; `null` con un
mensaje explícito dice la verdad — que todavía no se puede saber. La lógica está en
`comparar_factura` (`server/app/api/facturas.py`) y su docstring lo deja escrito.

**Nota sobre un caso relacionado:** si el consumo facturado por el operador es `0`, tampoco se
calcula el porcentaje (no se puede dividir entre cero) y se aplica el mismo tratamiento.

---

## Cómo se verificaron estos casos

El criterio de aceptación de T-25 pide que cada caso *"se pueda recorrer en la aplicación real y
dé lo que dice"*. No se escribieron leyendo el código: se recorrieron contra el servidor FastAPI
real, levantado contra una base PostgreSQL 16 con datos de prueba. Las respuestas de abajo son
las que devolvió el sistema, copiadas tal cual.

**Casos 1 y 2 — guardar una lectura reconocida y una corregida a mano:**

```
POST /api/lecturas  {"valor":1272.0,"fecha":"2026-06-30","origen":"manual"}
→ HTTP 201  {"valor":1272.0,"origen":"manual",
             "consumo_desde_anterior_m3":null,"dias_desde_anterior":null}

POST /api/lecturas  {"valor":1284.0,"fecha":"2026-07-30","origen":"reconocimiento"}
→ HTTP 201  {"valor":1284.0,"origen":"reconocimiento",
             "consumo_desde_anterior_m3":12.0,"dias_desde_anterior":30}
```

**Caso 3 — historial:**

```
GET /api/lecturas?medidor_id=…   (medidor sin lecturas)
→ {"lecturas":[]}

GET /api/lecturas?medidor_id=…   (con las dos lecturas de arriba)
→ primera: consumo null · segunda: 12.0 m³ en 30 días
```

**Caso 4 — comparación con lecturas suficientes:**

```
GET /api/facturas/{id}/comparacion
→ {"consumo_medido_m3":12.0,"consumo_facturado_m3":14.0,
   "diferencia_m3":2.0,"diferencia_porcentual":14.3,"supera_umbral":false}
```

Coincide **exactamente** con el ejemplo del contrato de la API §6, escrito en T-04b mucho antes
de que existiera la implementación.

**Caso 5 — comparación sin lecturas suficientes:**

```
GET /api/facturas/{id}/comparacion   (medidor sin ninguna lectura)
→ {"consumo_medido_m3":null,"consumo_facturado_m3":14.0,
   "diferencia_m3":null,"diferencia_porcentual":null,"supera_umbral":false}
```

**Flujos alternativos, todos con la forma de error del contrato §1:**

```
POST /api/lecturas   (valor menor que la última lectura)
→ HTTP 422  {"error":{"codigo":"LECTURA_INVALIDA",
             "mensaje":"el valor 1000 es menor que la última lectura registrada (1284.00)"}}

GET /api/lecturas?medidor_id=…   (medidor inexistente)
→ HTTP 404  {"error":{"codigo":"MEDIDOR_NO_ENCONTRADO", …}}

POST /api/facturas   (periodo_fin anterior a periodo_inicio)
→ HTTP 400  {"error":{"codigo":"VALIDACION",
             "mensaje":"periodo_fin debe ser posterior a periodo_inicio"}}

GET /api/facturas/{id}/comparacion   (factura inexistente)
→ HTTP 404  {"error":{"codigo":"FACTURA_NO_ENCONTRADA", …}}
```

Vale la pena notar el mensaje de `LECTURA_INVALIDA`: el procedimiento PL/pgSQL lo lanza junto con
un bloque `CONTEXTO` que trae su propia firma y el número de línea. Ese detalle del motor **no
aparece** en la respuesta — se queda en el log del servidor, como exige `CLAUDE.md` §11.

Además, los flujos de las pantallas están cubiertos por las pruebas automatizadas que corren en
cada Pull Request: 31 unitarias del servidor, 15 del cliente, 4 de integración contra una base
real, y la verificación transaccional en SQL. El inventario completo es el Issue
[#36](https://github.com/NieblaVidente/mimedidor/issues/36) (T-26).

---

## Qué NO cubren estos casos

Para que quede explícito, en la misma línea que el contrato de la API §7:

- **Autenticación y multi-usuario.** No hay login (P-15). Los casos asumen un abonado implícito.
- **Alta de usuarios, viviendas y medidores desde la aplicación.** El modelo de datos las
  contempla (`docs/architecture/modelo-datos.md`) y los scripts las crean, pero no hay pantalla
  ni endpoint para darlas de alta — hoy se insertan directo en la base. Por eso todos los casos
  arrancan con *"el abonado conoce el ID del medidor"*.
- **Corregir o borrar una lectura ya guardada.** El rol `mimedidor_app` no tiene `DELETE` a
  propósito (`database/README.md`); una corrección se registra como una lectura nueva.
- **Funcionar sin conexión.** Ser una PWA instalable sigue siendo el objetivo del producto, pero
  el service worker todavía no está armado (`CLAUDE.md` §13.5).

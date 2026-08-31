# Documento técnico — Entrega semana 7

**Proyecto:** MiMedidor · **Sprint:** 1 · **Fecha de entrega:** 20 de agosto de 2026
**Universidad Invenio · TICE · III Trimestre 2026 · Invenio Fest**

| Integrante | Rol Scrum |
|---|---|
| José Pablo Ramírez Sánchez | Scrum Master · Equipo de desarrollo |
| Yariel Andrey Elizondo Jiménez | Equipo de desarrollo |
| Isaac Felipe Morún Moreira | Product Owner · Equipo de desarrollo |

> **Nota sobre este documento.** Reporta el estado real del proyecto, incluyendo lo que no
> funciona. El resultado del reconocimiento automático de dígitos en este sprint es **0 %** de
> aciertos, y está explicado en detalle en la §5 junto con por qué falla y qué se hará. Esa
> decisión de reportarlo tal cual es deliberada: el objetivo del Sprint 1 era **medir** la
> exactitud real sobre fotos de campo, no que fuera buena. Ese número es la línea base que
> justifica el trabajo del Sprint 2.

---

## 1. Resumen

MiMedidor es una aplicación web que permite a un hogar costarricense fotografiar su hidrómetro,
obtener la lectura por visión por computadora, mantener un historial propio y contrastarlo contra
lo que le factura su operador (AyA, ASADA o municipalidad).

El objetivo del Sprint 1 era construir **un hilo funcional completo de punta a punta**:
foto → lectura → historial → factura → comparación. Ese hilo está construido: las cinco rutas de
la API existen y están probadas, las tres pantallas existen y están probadas, y la base de datos
tiene esquema, roles y control transaccional funcionando y verificados en cada Pull Request.

Lo que **no** se logró es que el reconocimiento automático acierte, y que las capas se ejecuten
juntas. Ambas cosas están medidas y explicadas en las §5 y §7.

**Estado del tablero:** 19 tarjetas cerradas, 2 en revisión (las de esta entrega), 2 en curso
(la recolección del dataset de campo).

---

## 2. Alcance

### 2.1 Lo que se implementó

| Área | Entregado |
|---|---|
| **Visión por computadora** | Detección de la carátula y corrección de perspectiva (T-09); segmentación de la ventana del odómetro (T-10); reconocimiento de dígitos con medición de exactitud (T-11) |
| **API** | 5 rutas: `POST /api/lecturas/reconocer`, `POST /api/lecturas`, `GET /api/lecturas`, `POST /api/facturas`, `GET /api/facturas/{id}/comparacion` |
| **Base de datos** | Esquema propio, 6 tablas normalizadas a 3FN, 2 roles con mínimo privilegio, y un procedimiento transaccional con manejo de errores |
| **Cliente** | 3 pantallas: captura con cámara y corrección manual, historial con consumo entre lecturas, y registro de factura con comparación |
| **Infraestructura** | Repositorio con `main` protegida, pipeline de integración continua con 3 jobs, contrato de la API congelado y Definition of Done acordado por los tres |
| **Pruebas** | 31 en el servidor (`pytest`) y 15 en el cliente (Vitest). Algunas del servidor se saltan cuando el dataset de fotos no está disponible, porque las fotos no se versionan |

### 2.2 Lo que quedó fuera a propósito

Estas cosas no se hicieron porque se decidió no hacerlas, no porque faltara tiempo:

- **Autenticación y gestión de usuarios.** El identificador del medidor se ingresa a mano. Sin
  esto no se puede usar de verdad, pero tampoco aporta nada a las rúbricas de este sprint.
- **Docker, Kubernetes, entorno de *staging* y despliegue Blue/Green.** Retirados del alcance
  verbalmente por el profesor de Ingeniería de Software II, aunque el enunciado escrito original
  los mencionara.
- **Entrenar un modelo propio de reconocimiento.** El sprint pide usar una librería existente y
  medir qué tan mal funciona. Entrenar algo propio sin dataset suficiente habría sido inventar
  una solución antes de entender el problema.
- **Pruebas end-to-end con Cypress.** Planificadas para el Sprint 2.

### 2.3 Lo que quedó incompleto

Esto sí es trabajo pendiente, no una decisión:

- **El dataset de campo va en 2 de 12 medidores** (T-07/T-08, en curso). Es el cuello de botella
  del proyecto: sin fotos no se puede medir ni mejorar el reconocimiento, ni decidir a qué marca
  de hidrómetro acotar el MVP.
- **El reconocimiento automático no acierta.** Ver §5.
- **Cliente y servidor nunca se han ejecutado juntos.** Ver §7.
- **La aplicación todavía no es una PWA.** Falta el *manifest* y el *service worker*.
- **No hay entrega continua.** El pipeline valida cada cambio pero no despliega.

---

## 3. Arquitectura de la solución

![Diagrama de arquitectura de MiMedidor](architecture/arquitectura.svg)

El detalle completo, componente por componente, está en
[`docs/architecture/arquitectura.md`](architecture/arquitectura.md). En resumen:

**Tres capas de ejecución y una de validación.** El navegador ejecuta las pantallas y el acceso a
la cámara; el servidor expone la API **y** ejecuta el procesamiento de imagen en el mismo proceso;
PostgreSQL guarda los datos y hace cumplir las reglas transaccionales; y GitHub Actions valida las
tres capas anteriores en cada Pull Request.

**Flujo de una lectura.** El abonado toma la foto en el navegador. Se envía a
`POST /api/lecturas/reconocer`, que **no guarda nada**: encadena corrección de perspectiva →
recorte del odómetro → lectura de dígitos, y devuelve el número reconocido. El abonado lo confirma
o lo corrige, y recién entonces `POST /api/lecturas` lo persiste llamando a un procedimiento
almacenado que escribe la lectura y su registro de auditoría en una sola transacción.

**Por qué reconocer y guardar están separados.** Es una decisión de diseño tomada antes de saber
el resultado de §5, y que ese resultado terminó confirmando: sabíamos que el reconocimiento iba a
fallar seguido, así que el usuario **tiene** que poder corregir antes de confirmar. Si el
reconocimiento guardara directo, cada error del OCR se convertiría en un dato falso en el
historial del abonado.

**Por qué el procesamiento de imagen no importa nada del framework web.** Las funciones de
`server/app/vision/` reciben un arreglo de imagen y devuelven un resultado. No conocen FastAPI.
Eso permite probarlas sin levantar el servidor y deja el componente que evalúa Computación
Gráfica aislado y demostrable por separado.

---

## 4. Tecnologías y justificación de cada decisión

### 4.1 Aplicación web progresiva, no aplicación móvil nativa (T-01)

**Decisión: PWA.**

- Cypress —la herramienta de pruebas end-to-end que pide la rúbrica de Ingeniería de Software II—
  funciona directo sobre web. Con nativo habría que usar Appium o Detox y confirmar que se acepta.
- El despliegue continuo a un servidor es viable dentro del trimestre; publicar en una tienda de
  aplicaciones no lo es.
- Es reversible: si el proyecto continúa después del curso, se puede envolver en nativo.
- No requiere que el abonado instale nada desde una tienda.

**Estado honesto:** la decisión sigue en pie, pero la parte propiamente "progresiva" (*manifest* y
*service worker*) todavía no está construida. Hoy es una aplicación web de una sola página.

### 4.2 Python + FastAPI en el backend

El corazón del proyecto son las tres tarjetas de visión por computadora. En Python, OpenCV y el
OCR son una función más del backend. Con Node haría falta o un microservicio Python aparte —con su
propio despliegue, su red y sus modos de falla— o usar `opencv.js`/`tesseract.js`, que son
versiones empobrecidas justo del componente que evalúa Computación Gráfica. Un servicio extra no
se paga solo en un sprint de diez días.

### 4.3 PostgreSQL como motor relacional (T-02a)

Confirmado con el profesor de Base de Datos como motor válido: la rúbrica exige un motor
relacional, no uno específico. La rúbrica describe los mecanismos con vocabulario de SQL Server,
así que la equivalencia usada está documentada en
[`database/README.md`](../database/README.md):

| La rúbrica pide | En PostgreSQL |
|---|---|
| `BEGIN TRANSACTION` / `COMMIT` / `ROLLBACK` | Igual — es sintaxis estándar |
| `TRY...CATCH` | Bloque `BEGIN ... EXCEPTION WHEN ... END` en PL/pgSQL |
| `THROW` | `RAISE EXCEPTION` |
| `XACT_ABORT` | No hace falta: PostgreSQL revierte la transacción completa por defecto ante cualquier error no capturado |

### 4.4 SQL plano, sin ORM

No es preferencia de estilo. La rúbrica de Base de Datos exige procedimientos almacenados, roles
con mínimo privilegio y control transaccional **escritos por nosotros**. Un ORM esconde
exactamente lo que hay que poder mostrar y defender.

### 4.5 Tesseract para el reconocimiento de dígitos (T-02b)

Se evaluaron tres opciones. El criterio de esta decisión no era la exactitud sobre hidrómetros
—eso se midió después, en T-11— sino que funcionara y se instalara en el pipeline sin pelear:

- **EasyOCR** se descartó: depende de PyTorch y descarga modelos pre-entrenados de internet la
  primera vez que corre, lo que vuelve el pipeline lento y dependiente de la red en cada corrida.
- **El OCR por redes neuronales de OpenCV** se descartó: requiere descargar y cablear modelos
  aparte, desproporcionado para una tarjeta cuyo único objetivo era probar que *alguna* librería
  funcionara.
- **Tesseract** ganó: el motor y sus datos se instalan con un solo paquete del sistema, no
  descarga nada en tiempo de ejecución, y `pytesseract` es una envoltura fina en Python.

**Cómo envejeció esta decisión.** Ver §5: Tesseract está entrenado sobre tipografía impresa
continua, y un odómetro mecánico tiene líneas divisorias físicas entre casillas de dígitos que
Tesseract lee como si fueran el número "1". La decisión fue correcta para su criterio —era la
opción con menos piezas móviles para empezar— pero el resultado indica que un OCR genérico
probablemente no sea la herramienta adecuada para este problema.

### 4.6 Integración continua con GitHub Actions

Tres jobs en cada Pull Request:

| Job | Qué hace |
|---|---|
| **Cliente** | ESLint, compilador de TypeScript, build de producción y Vitest. Instala desde cero, así que detecta dependencias usadas pero no declaradas |
| **Servidor** | `ruff` y `pytest`. Instala Tesseract como paquete del sistema, así que las pruebas de OCR corren de verdad, no simuladas |
| **Base de datos** | Levanta PostgreSQL 16 real, corre los scripts sobre una instancia limpia y **fuerza un error a propósito** para confirmar que la transacción revierte sin dejar nada a medias |

`main` está protegida: no se puede escribir directo, y todo entra por Pull Request con al menos
una aprobación y los tres checks en verde.

---

## 5. Resultado del reconocimiento automático — el número real

**0 de 2 lecturas (0 %) coinciden exactamente con la lectura real.**

El detalle completo está en
[`docs/exactitud-reconocimiento.md`](exactitud-reconocimiento.md). Lo esencial:

### 5.1 Qué se midió

El pipeline completo —corrección de perspectiva → recorte del odómetro → lectura de dígitos—
sobre cada foto real disponible, comparando contra la lectura anotada a mano en el momento de
tomar la foto. Coincidencia exacta, dígito por dígito.

### 5.2 Los dos casos

| Foto | Lo que devolvió Tesseract | Interpretado | Real | ¿Correcta? |
|---|---|---|---|---|
| Captura 1 | `0051401691` (10 caracteres) | descartada, sin resultado | `0051069` | No — pero **se detecta a sí misma como no confiable** |
| Captura 2 | `0015110` (7 caracteres) | `15110` | `51069` | No — y **no hay forma de saberlo** |

Los dos fallan por la misma causa, pero de dos maneras muy distintas, y la diferencia importa:

**El primer caso falla de forma segura.** El texto trae 10 caracteres donde deberían ir 7. Como la
cantidad de dígitos está claramente fuera de rango, el sistema lo descarta y no devuelve nada, en
vez de forzar un número. Es el comportamiento deseable: falla de forma visible.

**El segundo caso falla en silencio.** Acá el conteo de caracteres "cuadra" por coincidencia —7
caracteres, la cantidad correcta— pero los dígitos están mal. El sistema devuelve `15110` cuando
la lectura real es `51069`, sin ninguna señal de alerta. **Esta es la falla que más importa
documentar**, porque produce un dato falso con apariencia de válido.

### 5.3 Por qué falla

La causa raíz son las **líneas divisorias verticales entre casillas de dígitos** del odómetro.
Tesseract está entrenado sobre tipografía impresa continua y lee cada separador físico como si
fuera un "1" suelto entre los números reales. Es un problema conocido de aplicar OCR genérico a un
display de rodillos mecánico.

Durante T-11 sí se logró una mejora: antes, el recorte que llegaba al OCR incluía la línea de
texto de certificación que está debajo de los dígitos, y Tesseract mezclaba ambas devolviendo
números del modelo o del serial. Eso se corrigió aislando la fila de dígitos. Mejoró lo que le
llega a Tesseract, pero no resolvió el problema de las líneas divisorias.

### 5.4 Por qué este número no es representativo

Se midió sobre **2 fotos, casi idénticas entre sí, del mismo medidor**. No se puede concluir de
ahí cómo se comportará sobre otros modelos, ángulos o condiciones de luz. Es un punto de partida,
no una conclusión general. El dataset va en 2 de 12 medidores porque la recolección sigue en
curso.

### 5.5 Qué se hace al respecto

**A corto plazo, la red de seguridad ya está construida.** La corrección manual no es un detalle
accesorio: es la razón por la que reconocer y guardar están separados en el contrato de la API
(§3). El abonado siempre ve el número antes de confirmarlo y puede cambiarlo, y el sistema guarda
si la lectura vino del reconocimiento o de una corrección manual — que es justamente el dato que
permitirá medir la exactitud real cuando haya uso.

**Para el Sprint 2, tres caminos en orden de costo:**

1. **Conseguir más dataset.** Bloqueante para todo lo demás: sin más fotos no se puede calibrar
   nada con criterio.
2. **Tratar las líneas divisorias explícitamente** — detectarlas y borrarlas antes del OCR, o
   segmentar cada casilla de dígito por separado y reconocerla individualmente.
3. **Cambiar de método.** Comparación contra plantillas de dígitos, o un modelo entrenado para
   este tipo de odómetro. Solo tiene sentido evaluarlo cuando haya dataset suficiente.

---

## 6. Proceso de trabajo

- **Scrum** con las ceremonias registradas y fechadas en [`docs/scrum/`](scrum/). El Sprint 1 se
  gestionó en un tablero de Trello, respaldado en
  [`docs/scrum/sprint-1-tarjetas.md`](scrum/sprint-1-tarjetas.md); desde el Sprint 2 las tareas
  son Issues del propio repositorio, para que cada Pull Request quede enlazado a la tarea que
  resuelve.
- **Feature Branch Workflow**: una rama por tarea, `main` protegida, todo por Pull Request.
- **Definition of Done** acordado por los tres el 12 de agosto y versionado en
  [`docs/definition-of-done.md`](definition-of-done.md): rama, PR, una aprobación de otro
  integrante, CI en verde, merge, documentación actualizada y criterios de aceptación verificados.
- **Deuda técnica registrada** en [`docs/deuda-tecnica.md`](deuda-tecnica.md): los atajos tomados
  a propósito, con la justificación y qué haría falta para cerrarlos.

---

## 7. Riesgos y pendientes para el Sprint 2

Ordenados por lo que más nos preocupa.

### 7.1 Cliente y servidor nunca se han ejecutado juntos

Las pantallas llaman rutas relativas (`/api/…`), que asumen que cliente y servidor se sirven desde
el mismo origen. En producción eso se cumpliría; en desarrollo no, porque cada uno escucha en un
puerto distinto y no hay un proxy configurado.

Consecuencia honesta: **cada capa está probada por separado, pero el hilo completo del sprint
nunca se ha corrido de punta a punta contra el servidor real.** Las pruebas del cliente sustituyen
el módulo que habla con la API, y las del servidor sustituyen la conexión a la base de datos —
todas pasan, y aun así el sistema integrado no se ha ejecutado nunca.

Es lo primero que hay que cerrar en el Sprint 2, antes de cualquier funcionalidad nueva. El
arreglo en sí es chico; lo que importa es que hasta hacerlo no podemos afirmar que el hilo
funciona.

### 7.2 El dataset de campo va en 2 de 12 medidores

Es el cuello de botella real del proyecto. Bloquea tres cosas a la vez: medir el reconocimiento
con una muestra representativa, decidir a qué marca de hidrómetro acotar el MVP, y calibrar la
detección de la ventana del odómetro para modelos distintos al único que tenemos.

Agravante: uno de los dos medidores registrados **no tiene la marca del fabricante confirmada**
(la carátula muestra el nombre del operador, no del fabricante).

### 7.3 El reconocimiento automático no acierta

Detallado en la §5. No bloquea la entrega —el sistema funciona con corrección manual— pero es el
diferenciador del producto, así que no puede quedar así.

### 7.4 No hay entrega continua

El pipeline valida cada cambio pero no despliega a ningún ambiente, y la rúbrica de Ingeniería de
Software II la pide explícitamente.

### 7.5 La aplicación todavía no es una PWA

Falta el *manifest* y el *service worker*. La decisión de T-01 sigue siendo válida y el trabajo es
acotado, pero mientras no se haga, describirla como PWA sería inexacto.

### 7.6 La rúbrica de Señales y Sistemas sigue sin publicarse

Es el riesgo más difícil de mitigar porque no depende de nosotros. El encaje propuesto —tratar la
imagen como señal bidimensional y la serie histórica de lecturas como señal unidimensional— está
documentado, pero no se puede validar contra criterios que no existen todavía.

### 7.7 Deuda técnica registrada

Tres puntos ya documentados con su justificación en
[`docs/deuda-tecnica.md`](deuda-tecnica.md): el recorte de posición fija como respaldo en la
segmentación, la vista y la función de base de datos que el modelo documenta pero que nunca se
escribieron, y una clase de error duplicada en el cliente.

---

## 8. Cómo verificar lo entregado

| Qué | Dónde |
|---|---|
| Modelo entidad-relación y justificación de 3FN | [`docs/architecture/modelo-datos.md`](architecture/modelo-datos.md) |
| Contrato de la API | [`docs/architecture/contrato-api.md`](architecture/contrato-api.md) |
| Arquitectura detallada | [`docs/architecture/arquitectura.md`](architecture/arquitectura.md) |
| Scripts de base de datos | [`database/scripts/`](../database/scripts/) |
| Medición de exactitud | [`docs/exactitud-reconocimiento.md`](exactitud-reconocimiento.md) |
| Registro del dataset de campo | [`docs/dataset-campo/registro-medidores.md`](dataset-campo/registro-medidores.md) |
| Ceremonias de Scrum | [`docs/scrum/`](scrum/) |
| Definition of Done | [`docs/definition-of-done.md`](definition-of-done.md) |
| Deuda técnica | [`docs/deuda-tecnica.md`](deuda-tecnica.md) |
| Pipeline de integración continua | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) |
| Evidencia de `main` protegida | [`docs/evidencia/`](evidencia/) |

Para levantar el proyecto en una máquina nueva:
[`docs/como-empezar.md`](como-empezar.md).

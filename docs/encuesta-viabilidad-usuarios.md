# Encuesta de viabilidad con usuarios — MiMedidor

Instrumento para preguntarle a personas reales si MiMedidor les serviría y si lo usarían. Todas
las preguntas son de **sí o no**, con un espacio de comentarios abiertos al final.

No es una autoevaluación del equipo: las respuestas las da gente de afuera, y el número que salga
se reporta tal cual. Aplica la misma regla que el resto del proyecto —
**no se maquilla un resultado** (`CLAUDE.md` §8). Una encuesta con 40 % de "no" bien explicada
vale más que una con 100 % de "sí" conseguida a fuerza de preguntas inducidas.

---

## 1. En qué se apoya

**ISO/IEC/IEEE 29148** (ingeniería de requisitos) establece que los requisitos deben derivarse de
las **necesidades declaradas de los interesados**, no de lo que el equipo de desarrollo supone que
necesitan. El *Concept of Operations* que describe esa norma se construye desde la perspectiva de
quien va a operar el sistema. Esta encuesta es el instrumento con el que se recogen esas
necesidades declaradas para MiMedidor.

Sobre ese esqueleto se organizan las dimensiones del marco **TELOS** que el equipo decidió cubrir:

| Dimensión | Qué responde | Sección |
|---|---|---|
| **Operativa** | ¿La usarían de verdad? ¿Pueden, en las condiciones reales de su casa? | A, C, F |
| **Técnica** | ¿Tienen el equipo y las condiciones que el sistema asume? | A, D |
| **Económica** | ¿Vale algo para ellos? ¿Cuánto, comparado con las alternativas del mercado? | E |

Las dimensiones **legal** y **de cronograma** de TELOS quedan fuera de este instrumento a
propósito: no son cosas que un abonado pueda responder. La legal se evalúa aparte (manejo de datos
personales del abonado), y la de cronograma es interna del equipo.

> **Nota honesta sobre el anclaje.** IEEE no publica un formulario de viabilidad estandarizado.
> Lo que aporta 29148 es el principio (los requisitos salen de los interesados, documentados y
> trazables), y TELOS aporta las dimensiones. Si un profesor pregunta "¿dónde dice IEEE que la
> encuesta sea así?", la respuesta correcta es esta, no inventar una cláusula.

---

## 2. Cómo se aplica

**A quién.** Personas que pagan o revisan el recibo del agua de su vivienda, en Costa Rica.
No sirve encuestar a alguien que nunca ha visto un recibo de agua: no es el usuario del producto.

**Cuántas.** Mínimo **15** respuestas para poder decir algo; meta **30**. Repartir entre los tres
integrantes y entre zonas distintas — si las 15 salen del mismo barrio, la muestra está sesgada y
hay que anotarlo, igual que se anota con el dataset de fotos.

**Duración.** Unos 5 minutos.

**Reglas para quien la aplica:**

1. **No explicar MiMedidor antes de la sección C.** Las secciones A y B miden la situación actual
   de la persona. Si primero se le cuenta la idea, contesta pensando en la idea y no en su realidad.
2. **No inducir el sí.** Leer la pregunta como está escrita. Nada de "¿verdad que le serviría…?".
3. **Si la persona duda, la respuesta es "no".** Un "mmm, tal vez" no es un sí.
4. **Anotar los comentarios textuales**, aunque contradigan lo que esperábamos. Son la parte más
   valiosa del formulario.
5. La encuesta es **anónima**: no se anota nombre, cédula, dirección exacta ni teléfono.

---

## 3. Advertencia metodológica — leerla antes de reportar resultados

Una encuesta de sí/no sobre intención hipotética **sobreestima siempre**. Preguntarle a alguien
"¿usaría esta aplicación gratis?" produce un sí en la enorme mayoría de los casos, porque decir
que sí no le cuesta nada. Esto se conoce como sesgo de aquiescencia y sesgo de hipoteticidad, y no
se elimina cambiando la redacción.

Por eso, al interpretar los resultados, **no todas las preguntas pesan igual**:

- **Peso alto** — las de conducta pasada (B2, B3, B4) y las que implican un costo real (E2, E3).
  Preguntan por algo que la persona ya hizo o ya decidió, no por lo que cree que haría.
- **Peso medio** — las de condiciones materiales (A4, A5, C1, C2, D2). Son verificables: la
  persona sabe si tiene señal en el patio o no.
- **Peso bajo** — las de intención declarada (C3, E1, F1, F2). Sirven para detectar un rechazo
  fuerte (si acá sale que no, es una señal muy mala), pero un sí alto no prueba casi nada.

Reportar los tres grupos por separado. Un informe que diga "el 95 % lo usaría" sin este matiz es
exactamente el tipo de número inflado que el proyecto decidió no producir.

---

## 4. El formulario

### Datos de la respuesta

No identifican a la persona. Se llenan antes de empezar.

| Campo | |
|---|---|
| N.º de respuesta | ______ |
| Fecha | ______ |
| Cantón / distrito | ______________________ |
| ¿Quién le factura el agua? | ☐ AyA  ☐ ASADA  ☐ Municipalidad  ☐ No sabe |
| Aplicada por | ☐ José Pablo  ☐ Yariel  ☐ Isaac |

**Leer antes de empezar:**

> Estamos haciendo un proyecto de la universidad sobre el consumo de agua en los hogares. Son unas
> 26 preguntas de sí o no, toma como cinco minutos y es anónimo — no anotamos su nombre ni su
> dirección. Puede no contestar lo que no quiera, y puede parar cuando guste. ¿Le parece bien?

---

### 🚦 Pregunta filtro — antes de todo lo demás

**Esta pregunta va sola, en su propia pantalla o página, antes del resto del cuestionario.**

| # | Pregunta | Sí | No |
|---|---|---|---|
| A1 | ¿Es usted quien paga o revisa el recibo del agua de su casa? | ☐ | ☐ |

> ### ⛔ Si la respuesta es «no», el cuestionario TERMINA acá
>
> Agradecer y cerrar. **No mostrar ninguna otra pregunta.** La persona no es usuaria del
> producto, y sus respuestas al resto no se pueden usar para nada.
>
> **Si el formulario es digital**, esto tiene que estar implementado como salto de sección —
> en Google Forms: *«Ir a una sección según la respuesta»* → «No» → *«Enviar formulario»*. Una
> nota de texto pidiéndole a la persona que se detenga **no funciona**: ya se probó y no
> funcionó (ver §9).
>
> Estas respuestas no se anotan como una fila de «no» en el registro: se cuentan aparte, como
> descartadas por filtro.

---

### Sección A — Su situación hoy

*Solo para quien contestó «sí» en A1. No mencionar MiMedidor todavía.*

| # | Pregunta | Sí | No |
|---|---|---|---|
| A2 | ¿Sabe dónde está el medidor de agua (hidrómetro) de su vivienda? | ☐ | ☐ |
| A3 | ¿Alguna vez le ha visto los números al medidor? | ☐ | ☐ |
| A4 | ¿Tiene un teléfono con cámara? | ☐ | ☐ |
| A5 | ¿Tiene internet en su casa, sea wifi o datos del teléfono? | ☐ | ☐ |

---

### Sección B — El problema, antes de contar la solución

| # | Pregunta | Sí | No |
|---|---|---|---|
| B1 | ¿Alguna vez le ha parecido que el recibo del agua le llegó más alto de lo normal? | ☐ | ☐ |
| B2 | **Solo si B1 fue «sí»:** cuando eso pasó, ¿pudo comprobar por su cuenta si la lectura era correcta? | ☐ | ☐ ·  ☐ no aplica |
| B3 | ¿Ha reclamado alguna vez por el monto del recibo del agua? | ☐ | ☐ |
| B4 | ¿Sabe interpretar los números del medidor para saber cuánta agua gastó? | ☐ | ☐ |
| B5 | ¿Ha tenido alguna vez una fuga que se dio cuenta solo cuando le llegó el recibo? | ☐ | ☐ |

> **B2 es condicional, no un filtro.** Su redacción («cuando eso pasó») presupone que B1 fue
> «sí». A quien nunca le llegó un recibo alto, B2 no le aplica — y contestarla «no» ensucia el
> dato, porque un «no» ahí significa «no pude comprobarlo», que es justo la evidencia del
> problema que el producto resuelve.
>
> A diferencia de A1, **B2 no corta el cuestionario**: el resto de las preguntas siguen siendo
> válidas. Solo hay que poder distinguir «no pude» de «no me aplica», y por eso lleva una
> tercera casilla. En un formulario digital va como pregunta condicional, o con tres opciones.

---

### Ahora sí — describir MiMedidor

*Leer tal cual, sin adornar:*

> MiMedidor es una aplicación para el teléfono. Usted le toma una foto al medidor de su casa, y la
> aplicación intenta leer sola los números. Decimos "intenta" porque hoy se equivoca seguido —
> cuando falla, usted escribe el número a mano. La aplicación le guarda un historial de sus
> lecturas, le calcula cuánta agua gastó entre una y otra, y le permite comparar eso contra lo que
> le facturaron. No hay que instalar ningún aparato ni cambiar el medidor.

---

### Sección C — ¿Podría usarla? (viabilidad operativa)

| # | Pregunta | Sí | No |
|---|---|---|---|
| C1 | ¿Puede llegar hasta su medidor sin dificultad (no está con candado, tapado ni obstruido)? | ☐ | ☐ |
| C2 | ¿Cree que podría tomarle una foto clara a los números, tal como está el medidor hoy? | ☐ | ☐ |
| C3 | ¿Estaría dispuesto a hacer eso una vez al mes? | ☐ | ☐ |
| C4 | Si la aplicación lee mal el número y hay que corregirlo a mano, ¿lo seguiría usando igual? | ☐ | ☐ |
| C5 | ¿Le parece entendible lo que hace la aplicación, con la explicación que le acabo de dar? | ☐ | ☐ |

---

### Sección D — ¿Tiene con qué? (viabilidad técnica)

| # | Pregunta | Sí | No |
|---|---|---|---|
| D1 | ¿Usaría una aplicación que se abre desde el navegador, sin bajarla de la tienda de aplicaciones? | ☐ | ☐ |
| D2 | ¿Tiene señal o wifi en el lugar donde está el medidor? | ☐ | ☐ |
| D3 | ¿Le daría confianza que la aplicación guarde las fotos de su medidor? | ☐ | ☐ |
| D4 | ¿Le molestaría tener que escribir usted mismo el número del medidor la primera vez? | ☐ | ☐ |

> **Ojo con D3 y D4:** están redactadas al revés a propósito. En D3 lo bueno para el proyecto es el
> "sí"; en D4 lo bueno es el "no". Sirve para detectar a quien está contestando en automático.

---

### Sección E — ¿Vale algo para usted? (viabilidad económica)

| # | Pregunta | Sí | No |
|---|---|---|---|
| E1 | ¿Usaría MiMedidor si fuera gratuito? | ☐ | ☐ |
| E2 | ¿Pagaría una suscripción mensual pequeña por un servicio así? | ☐ | ☐ |
| E3 | ¿Compraría un aparato de entre ₡75.000 y ₡215.000 que midiera su consumo automáticamente? | ☐ | ☐ |
| E4 | ¿Cree que saber su consumo real le ayudaría a gastar menos agua? | ☐ | ☐ |
| E5 | ¿Cree que le ayudaría a detectar un cobro equivocado? | ☐ | ☐ |

> E3 es la pregunta de contraste: el rango pretendía representar lo que cuestan los productos
> existentes (Flume, Phyn, Moen Flo). Si la mayoría dice que no a E3 y que sí a E1, eso respalda la
> tesis del proyecto: el valor está en resolverlo **sin hardware**.
>
> ⚠️ **Corrección posterior (T-41, 2026-09-02).** El rango de ₡75.000 a ₡215.000 se derivó de una
> cifra equivocada: se creía que esos productos costaban 150–430 dólares, y los precios oficiales
> verificados van de **269 a 624** (ver [`fuentes.md`](fuentes.md) §3). **La pregunta se dejó tal
> como se aplicó**, porque este documento registra el instrumento real y no el que habría
> correspondido.
>
> El error **no debilita el hallazgo, lo refuerza**: se preguntó por un precio más barato que el
> real, y aun así solo el 18,8 % dijo que compraría. Al precio verdadero la disposición sería igual
> o menor. Queda anotado igual, porque hay que poder explicarlo si alguien lo pregunta.

---

### Sección F — Cierre

| # | Pregunta | Sí | No |
|---|---|---|---|
| F1 | ¿Le gustaría probar MiMedidor cuando esté lista? | ☐ | ☐ |
| F2 | ¿Se la recomendaría a alguien más de su familia o de su barrio? | ☐ | ☐ |

---

### Comentarios

*Espacio libre. Anotar textual lo que diga la persona, incluso si es una crítica o algo que no
esperábamos. Si no dice nada, dejarlo vacío — no rellenar.*

```
_______________________________________________________________________________

_______________________________________________________________________________

_______________________________________________________________________________

_______________________________________________________________________________
```

---

## 5. Trazabilidad — qué mide cada pregunta

Tabla para la entrega: permite mostrar que el instrumento no se armó al azar, sino contra las
dimensiones declaradas (requisito de trazabilidad de ISO/IEC/IEEE 29148).

| Preguntas | Dimensión TELOS | Qué decide |
|---|---|---|
| A1 | — (filtro que corta) | Si la persona pertenece a la población objetivo. Un «no» acá termina el cuestionario y la respuesta se cuenta como descartada, no como una fila del registro |
| A2, A3, B4 | Operativa | Si el abonado tiene alguna relación con su medidor hoy |
| A4, A5, D1, D2 | Técnica | Si existen las condiciones materiales que el sistema asume (§1 de `CLAUDE.md`: cámara, conectividad, PWA sin tienda) |
| B1, B3, B5 | Operativa (conducta real) | Si el problema que el proyecto dice resolver le ocurre de verdad a la gente |
| B2 | Operativa (conducta real, **condicional a B1**) | Si quien tuvo el problema pudo verificarlo por su cuenta. Solo aplica a quien contestó «sí» en B1 |
| C1, C2 | Operativa | Si la caja de concreto a ras de suelo permite la captura en la práctica |
| C3, C4, C5 | Operativa | Si el flujo con corrección manual — el camino real hoy — es aceptable |
| D3, D4 | Técnica / confianza | Fricción de adopción y percepción sobre las fotos |
| E1, E2, E3 | Económica | Disposición a usar y a pagar, contra la alternativa de hardware existente |
| E4, E5 | Económica (valor percibido) | Si el beneficio que el proyecto promete es el que la gente valora |
| F1, F2 | Operativa (intención) | Interés declarado y potencial de difusión |

---

## 6. Registro de resultados

Una fila por respuesta. Los comentarios van completos en la sección de abajo, no resumidos.

| # | Fecha | Cantón | Operador | A1 | A2 | A3 | A4 | A5 | B1 | B2 | B3 | B4 | B5 | C1 | C2 | C3 | C4 | C5 | D1 | D2 | D3 | D4 | E1 | E2 | E3 | E4 | E5 | F1 | F2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | | | | | | | | | | | | | | | | | | | |

En la columna `B2`, anotar `n/a` cuando B1 fue «no» — no dejarla en blanco ni marcarla «no»
(§9 explica por qué esa distinción importa).

**Se llevan dos conteos separados, no uno:**

| | |
|---|---|
| Respuestas **válidas** (contestaron «sí» en A1) | 0 |
| Descartadas por el filtro A1 | 0 |

Solo el primero cuenta contra el mínimo de 15. El segundo se reporta igual, porque cuántas
personas quedaron fuera del filtro también dice algo — y porque ocultarlo sería maquillar la
tasa de respuesta.

### Comentarios recogidos

| # | Comentario textual |
|---|---|
| | |

---

## 7. Cómo se interpreta el resultado

Criterios fijados **antes** de recoger los datos, para no acomodar la conclusión al número que
salga — mismo criterio que se usó para la decisión de marca en T-08.

| Señal | Umbral | Qué significa |
|---|---|---|
| **El problema existe** | B1 ≥ 50 % sí **y** B2 ≥ 50 % no *(sobre quienes contestaron «sí» en B1, no sobre el total)* | Hay gente a la que le llegó un recibo dudoso y no pudo verificarlo. Es la premisa del proyecto: si esto no se cumple, el producto resuelve un problema que la gente no tiene |
| **Se puede usar en la práctica** | C1 y C2 ≥ 70 % sí | Las condiciones físicas reales de las cajas de medidor permiten la captura |
| **El flujo real es aceptable** | C4 ≥ 60 % sí | La gente tolera corregir a mano, que es el camino normal hoy (0 % de acierto del OCR, ver `docs/exactitud-reconocimiento.md`) |
| **La tesis del "sin hardware" se sostiene** | E1 alto **y** E3 bajo | Quieren la solución, pero no pagando por un aparato — que es exactamente el hueco que el proyecto dice llenar |
| **Hay interés real** | F1 ≥ 60 % sí | Interés declarado; recordar que esta señal es de peso bajo (§3) |

**Si un umbral no se cumple, se reporta que no se cumplió y se explica.** No se ajusta el umbral
después de ver los datos, no se descartan respuestas incómodas, y no se redondea para arriba.

---

## 8. Estado

- [x] Formulario revisado por los tres integrantes antes de aplicarlo
- [x] Primera recolección: 33 respuestas, 16 válidas
- [x] Corrección del filtro tras esa primera vuelta (T-51, §9)
- [ ] Segunda recolección con el formulario corregido, si alcanza el tiempo
- [ ] Interpretación escrita contra los criterios de §7

---

## 9. Corrección del filtro tras la primera recolección (T-51)

### Qué pasó

La primera vuelta recogió **33 respuestas** y solo **16 quedaron válidas**: hubo que descartar el
**51,5 %** *después* de recolectar.

La causa no fue de quien respondió, fue del formulario: **la pregunta filtro no cortaba el
cuestionario.** A1 preguntaba si la persona paga o revisa el recibo del agua, y quien contestaba
que no seguía viendo y contestando las 25 preguntas restantes. Esas respuestas no se pueden usar
—alguien que no ve el recibo no puede decir si el monto le pareció alto— así que se descartaron
enteras.

La instrucción existía, pero como **nota de texto debajo de la tabla**: «si A1 es no, agradecer y
terminar acá». Una nota no corta nada. Es la diferencia entre pedirle a la gente que se detenga y
que el formulario no la deje seguir.

### Qué se corrigió

1. **A1 salió de la sección A** y quedó sola, antes del resto, con la instrucción de cierre en
   grande y las indicaciones concretas para implementarla como salto de sección en un formulario
   digital. Ya no es una nota al pie: es una compuerta.
2. **B2 tenía el mismo problema en menor grado**, y no se había detectado. Su redacción
   («*cuando eso pasó*») presupone que B1 fue «sí». A quien nunca le llegó un recibo alto, B2 no
   le aplica, pero el formulario la obligaba a contestar sí o no igual. Un «no» ahí es ambiguo:
   puede significar «no pude comprobarlo» —que es la evidencia del problema— o «no me pasó
   nunca», que no dice nada. Ahora lleva una tercera casilla de «no aplica» y está marcada como
   condicional.
3. **El registro lleva dos conteos separados** (§6): respuestas válidas y descartadas por filtro.
   Antes había un solo número, y eso hacía invisible el 51,5 % hasta que alguien lo contara a
   mano.
4. **El umbral de §7 aclara el denominador de B2**: se calcula sobre quienes contestaron «sí» en
   B1, no sobre el total. Con la casilla de «no aplica» esa distinción ya no es teórica.

### Qué NO se corrigió, y por qué

Se revisaron las demás preguntas buscando el mismo patrón. Hay pares donde una respuesta hace
menos probable la siguiente —si no sabe dónde está el medidor (A2), es raro que le haya visto los
números (A3); si no puede llegar hasta él (C1), difícilmente pueda fotografiarlo (C2)— pero en
esos casos la segunda pregunta **sigue siendo contestable y su respuesta significa algo**. No son
condicionales, son correlacionadas. Convertirlas en saltos escondería información real.

### Qué pasa con las 16 respuestas ya recogidas

**Siguen siendo válidas y no se mezclan con las nuevas.** Se recogieron con un instrumento
distinto —sin filtro que cortara y sin la casilla de «no aplica» en B2— así que juntarlas sería
sumar cosas que no se midieron igual.

Si hay una segunda vuelta, se analiza aparte y se reporta el n de cada una. El resultado
principal de la primera vuelta —87,5 % usaría una aplicación gratuita contra 18,8 % que compraría
un medidor comercial— **se sostiene con n = 16**, porque los intervalos no se traslapan. Duplicar
la muestra lo haría más firme; no lo cambia.

### Por qué esto se cuenta en vez de taparse

Es un error metodológico del equipo, detectado por el equipo, corregido por el equipo y con el
costo escrito: se perdió la mitad de una recolección. Contarlo antes de que alguien lo pregunte
vale más que un n = 16 sin explicación — y es la misma regla que se aplica al 0 % de exactitud
del reconocimiento (`CLAUDE.md` §8).

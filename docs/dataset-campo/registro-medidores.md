# Registro del dataset de campo — T-07 / T-08

Tabla viva: se va completando a medida que se toman más fotos. Cada fila es un medidor.
Las fotos en sí **no se suben a este repositorio** — viven en la carpeta compartida de OneDrive,
según ya está decidido en `.gitignore` (`/dataset-fotos/`). Esta tabla es el único registro que
queda versionado en Git.

**Carpeta compartida (OneDrive):** https://1drv.ms/f/c/c31b36613fb4e58a/IgATzPdfhuG3RI9f6rN32Io1AfR8DdPKv99Rl6m_NpmHbkU?e=hB1P3T

## Protocolo de captura — 6 tomas por medidor

| Toma | Qué es |
|---|---|
| Contexto | Alejada, se ve la caja completa y el entorno — ubica el medidor, no se usa para leer |
| Carátula frontal | De frente, sin inclinar la cámara, toda la carátula redonda |
| Ángulo natural | La que sale al agacharse y disparar sin acomodar nada |
| Ángulo inclinado | A propósito inclinada — le enseña al sistema a corregir perspectiva (T-09) |
| Primer plano del odómetro | Bien de cerca, dígitos grandes y nítidos |
| Etiqueta del cuerpo | La plaquita de metal/plástico del cuerpo (marca, modelo, serie) — no la carátula |

Como los medidores en Costa Rica suelen estar enterrados a ras de suelo, "carátula frontal" y
"ángulo natural" a veces terminan siendo casi la misma toma — no pasa nada, priorizar que se vea
bien la lectura y la etiqueta antes que forzar 6 ángulos artificialmente distintos.

## Criterio de decisión de marca (T-08)

- Una marca en ≥60 % de la muestra → el MVP se acota a esa marca
- Dos marcas dominantes → MVP a la principal, la segunda documentada como extensión
- Cinco o más marcas sin predominio → replantear alcance, anotarlo como riesgo

⚠️ **La marca es la del fabricante del medidor, no el nombre del operador/ASADA/municipalidad**
que aparece grande en la carátula de algunos modelos. Si no es legible, anotar "no legible/no
confirmada" — no adivinar ni usar el nombre del operador como si fuera la marca.

## Registro

| # | Código | Marca | Modelo | N.º serie | Lectura real | Fecha | Hora | Tomado por | Zona | Clima / condición | Tomas logradas (de 6) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Medidor1 | ARAD (confirmada) | — | — | Mostrada: `025888` (1 rojo) · Volumen: **2588,8 m³** | 2026-07-31 | 10:00 | José Pablo | Casa de José Pablo | Oscuro/nublado | 1 — primer plano del odómetro |
| 2 | Medidor2 | No confirmada (carátula dice "ASADA Tronadora", que es el operador, no el fabricante; etiqueta del cuerpo dice modelo `MJ-SDC`, serie `2423279`, no se ve fabricante) | MJ-SDC | 2423279 | Mostrada: `0051069` (2 rojos) · Volumen: **510,69 m³** | 2026-08-16 | 14:50 | Yariel | Casa de Yariel | Oscuro, minutos antes de llover — condición adversa | 2 — carátula frontal/ángulo natural (capturas 1 y 2, casi idénticas) + contexto (captura 3) |
| 3 | Medidor3 | ACTARIS (confirmada) | MULTIMAG | 255875 | Mostrada: `452991` (2 rojos) · Volumen: **4529,91 m³** | 2026-08-17 | — | Isaac | No consta | Caja a ras de suelo, tierra suelta, sombra parcial; la captura2 se tomó con flash | 3 — carátula frontal (c2), ángulo natural (c1), contexto (c3 y c4) |

**Total: 3 de 8 medidores** (meta revisada en el Planning del Sprint 2: 6 nuevos, 2 por
integrante, sobre los 2 ya registrados). Ninguno con las 6 tomas completas todavía. Isaac lleva
1 de sus 2.

> **Zonas: cada integrante sale en su propia provincia.** Los tres viven en provincias distintas,
> así que no hay riesgo de pisarse ni de registrar dos veces el mismo medidor.
>
> No es solo un reparto cómodo. El protocolo de captura de más arriba pide repartir zonas «para no
> sesgar la muestra hacia un solo barrio», y tres provincias distintas dan variedad real de marcas,
> de antigüedad de instalación y de condiciones de la caja — que es justo lo que necesita la
> decisión de alcance por marca de T-08 para no acotar el MVP sobre una muestra engañosa.
>
> **Fechas: sin fecha fija**, con el riesgo aceptado explícitamente. La justificación completa de
> esta decisión y de la meta revisada está en [`docs/scrum/sprint-2.md`](../scrum/sprint-2.md),
> sección «Salidas de campo (T-07)»; acá se anota porque es lo que hay que tener a mano al salir,
> no dentro del acta de una ceremonia.

### ⚠️ Dos columnas de lectura, y por qué

Desde Medidor3 se registran **dos valores distintos**, porque sirven a dos propósitos que no son
el mismo:

- **Mostrada** — la cadena de dígitos tal como aparece en el odómetro, sin punto decimal. Es la
  verdad de referencia contra la que se mide el reconocimiento (T-32): el OCR tiene que reproducir
  esos caracteres, no interpretarlos.
- **Volumen** — el valor físico en m³, con los dígitos rojos tratados como decimales. Es el que
  usa el producto para calcular consumo y contrastarlo contra la factura.

En Medidor3 los dos últimos dígitos son **rojos**, y en un hidrómetro los rojos son la parte
decimal. `452991` mostrado equivale a `4529,91 m³`.

La verificación de sentido común lo respalda: 452 991 m³ acumulados serían del orden de 3 000 m³
por mes, imposible en una casa; 4 529,91 m³ dan unos 30 m³ mensuales durante doce años, que sí es
un perfil doméstico.

**Esto importa más allá del registro.** El producto compara consumo medido contra consumo
facturado, y la factura del operador viene en m³. Si se guarda la cadena mostrada como si fuera
m³, la comparación —que es la función central de MiMedidor— queda desviada por un factor de 100.

### El hallazgo: la cantidad de dígitos rojos cambia según el medidor

Confirmado con quienes tomaron cada lectura:

| Medidor | Marca | Dígitos rojos | Mostrada | Volumen real | Factor |
|---|---|---|---|---|---|
| Medidor1 | ARAD | **1** | `025888` | 2588,8 m³ | ×10 |
| Medidor2 | MJ-SDC | **2** | `0051069` | 510,69 m³ | ×100 |
| Medidor3 | ACTARIS | **2** | `452991` | 4529,91 m³ | ×100 |

**No es una constante del sistema: es una propiedad de cada medidor.** Con un solo modelo en el
dataset se podía confundir con un desfase global y corregirlo con una división fija. Con tres
modelos y dos escalas distintas queda claro que la posición del punto decimal tiene que viajar con
el medidor, no con el código.

Esto era una decisión aplazada a propósito, no un descuido. `server/app/vision/reconocimiento.py`
lo dejó anotado en su propio docstring:

> «Algunos odómetros marcan en rojo los últimos dígitos para indicar una fracción de m³; decidir
> esa convención de punto decimal no es parte del alcance de T-11 (no hay todavía evidencia
> suficiente de campo para fijarla) y queda para una tarjeta futura una vez que el dataset de
> T-07/T-08 crezca.»

**Esa condición ya se cumplió.** El dataset creció lo suficiente para fijar la convención, y
además demostró que no puede ser única. Queda registrado en un Issue aparte.

## Pendiente

- Completar las tomas que faltan de Medidor3 (ángulo inclinado, primer plano del odómetro,
  etiqueta del cuerpo) y anotar su zona, que no consta
- Completar las tomas que faltan de Medidor1 (contexto, ángulo inclinado, etiqueta del cuerpo —
  esta última podría revelar la marca real de Medidor2 también, si se repite el modelo)
- Seguir sumando medidores en cuanto el clima lo permita, repartiendo zonas entre los tres para no
  sesgar la muestra hacia un solo barrio
- Al menos 3 medidores en condiciones adversas deliberadas (sombra, vidrio sucio, dígito a medio
  giro) — el clima lluvioso de estas dos capturas ya podría contar como una de las tres, si se
  documenta como tal

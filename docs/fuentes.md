# Fuentes de las cifras que justifican el proyecto — T-41

Cada afirmación de `CLAUDE.md` §1 que sostiene el porqué de MiMedidor, con su fuente, la cita
textual y la fecha en que se consultó.

**Verificado el 2026-09-02.** Dos de las tres afirmaciones estaban mal enunciadas y se
corrigieron; la corrección se explica en cada caso.

---

## 1. Agua no contabilizada en Costa Rica

> **Más del 50 % del agua producida por el AyA en 2023 no se contabilizó ni facturó.**

| | |
|---|---|
| **Institución** | Contraloría General de la República (CGR) |
| **Informe** | `SIGYD_D_2024022683` |
| **Período auditado** | 1 de enero de 2018 – 31 de diciembre de 2023 |
| **Publicado** | noviembre de 2024 |
| **Cita textual** | «En el 2023 más del 50 % del agua producida por el AyA no se contabiliza ni factura» |
| **Consultado en** | https://delfino.cr/2024/11/contraloria-mas-del-50-del-agua-producida-por-el-aya-en-2023-no-se-contabilizo-ni-facturo |

### ⚠️ Qué se corrigió

`CLAUDE.md` decía **«ronda el 49–58 %»** y se lo atribuía a **ARESEP**. Las dos cosas estaban mal:

- **La atribución.** La cifra es de la **Contraloría**, no de ARESEP. ARESEP se ha pronunciado
  sobre el efecto del agua no contabilizada en la tarifa, pero el dato no es suyo.
- **El rango.** No se encontró ninguna fuente que diga «49–58 %». Lo que hay es «más del 50 % en
  2023» (Contraloría) y un rango de 53–58 % atribuido a la Defensoría de los Habitantes que **no
  se pudo verificar contra un documento primario** y por eso no se cita.

### Limitación de esta fuente

Es una **fuente secundaria**: la nota de prensa reporta el informe y lo enlaza, pero el informe
primario de la CGR no se descargó ni se leyó. Para la entrega final conviene bajar
`SIGYD_D_2024022683` del sitio de la Contraloría y citar la página exacta.

---

## 2. Estado de los hidrómetros del Gran Área Metropolitana

> **Alrededor del 60 % de los hidrómetros del AyA en el GAM no funciona apropiadamente.**

| | |
|---|---|
| **Institución** | Autoridad Reguladora de los Servicios Públicos (ARESEP) |
| **Título** | «60 % medidores de agua incumplen normativa» |
| **Publicado** | 9 de enero de 2017 |
| **Estudio realizado en** | 2015 |
| **Muestra** | 419 hidrómetros, aleatoria y representativa |
| **Alcance** | Gran Área Metropolitana, operador AyA |
| **Cita textual** | «alrededor de un 60 % de los medidores de agua de Acueductos y Alcantarillados (AyA) del Gran Área Metropolitana, no funcionan apropiadamente» |
| **URL** | https://aresep.go.cr/noticias/60-medidores-de-agua-incumplen-normativa/ |

**Esta afirmación queda confirmada tal como estaba escrita**, y es fuente primaria: la publica la
propia ARESEP. Datos adicionales del mismo estudio: solo el 37,2 % de los medidores responde al
caudal mínimo de la norma, y alrededor del 39 % está dentro del margen de error permitido.

### ⚠️ Limitación que hay que declarar al citarla

**El estudio es de 2015 y se publicó en 2017: tiene once años.** No describe necesariamente el
parque de medidores de hoy. Al usarla conviene decir el año, no presentarla como una foto actual.
Si el AyA ejecutó reemplazos desde entonces, la proporción pudo cambiar — no se investigó.

---

## 3. Precio del hardware comercial equivalente

> **Los medidores inteligentes comerciales cuestan entre 269 y 624 dólares.**

Precios de lista consultados el **2026-09-02** en los sitios oficiales de cada fabricante:

| Producto | Precio | Fuente |
|---|---|---|
| Flume 2 Smart Water Monitor | **269 USD** | https://flumewater.com/product/ |
| Phyn Plus Smart Water Assistant + Shutoff (2.ª gen) | **499 USD** (MSRP) | https://phyn.com/blogs/press-releases/phyn-plus-the-most-accurate-whole-home-leak-detector-and-water-monitor-gets-smaller-lighter-and-more-affordable |
| Moen Flo Smart Water Monitor and Shutoff | **623,99 USD** | https://shop.moen.com/products/flo-smart-water-monitor-and-shutoff |

### ⚠️ Qué se corrigió, y por qué importa

`CLAUDE.md` decía **«150–430 dólares»**. Ningún precio oficial cae en ese rango: el más barato de
los tres cuesta 269 y el más caro 624.

**Consecuencia sobre la encuesta.** La pregunta E3 preguntó por **₡75.000 a ₡215.000**, un rango
derivado de esa cifra equivocada. O sea que a los encuestados se les preguntó por un precio **más
barato que el real**.

Eso **no invalida el hallazgo: lo refuerza.** Solo el 18,8 % dijo que compraría un aparato a ese
precio; al precio verdadero, que es más alto, la disposición a comprar sería igual o menor. La
conclusión del estudio de viabilidad —que la vía viable no pasa por hardware— se sostiene con más
margen del que se creía, no con menos.

Queda anotado igual, porque el instrumento aplicado preguntó por un rango que no correspondía al
mercado y eso hay que poder explicarlo si alguien lo pregunta.

### Limitación

Los precios de lista cambian y varían por comercio. Se citan con fecha de consulta. Además
**conviene comparar gamas equivalentes**: el Flume 2 solo monitorea, mientras que el Phyn Plus y
el Moen Flo incluyen corte automático del agua, que es una función que MiMedidor no ofrece ni
pretende ofrecer.

---

## Cómo mantener este documento

Si alguna cifra se usa en un entregable, se cita desde acá. Si una fuente se cae o se actualiza,
se corrige **la afirmación**, no la fuente: `CLAUDE.md` §8 lo dice para el número de exactitud del
reconocimiento y aplica igual para la justificación del proyecto.

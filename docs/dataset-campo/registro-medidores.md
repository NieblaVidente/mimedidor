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
| 1 | Medidor1 | ARAD (confirmada) | — | — | 025888 m³ | 2026-07-31 | 10:00 | José Pablo | Casa de José Pablo | Oscuro/nublado | 1 — primer plano del odómetro |
| 2 | Medidor2 | No confirmada (carátula dice "ASADA Tronadora", que es el operador, no el fabricante; etiqueta del cuerpo dice modelo `MJ-SDC`, serie `2423279`, no se ve fabricante) | MJ-SDC | 2423279 | 0051069 m³ | 2026-08-16 | 14:50 | Yariel | Casa de Yariel | Oscuro, minutos antes de llover — condición adversa | 2 — carátula frontal/ángulo natural (capturas 1 y 2, casi idénticas) + contexto (captura 3) |

**Total: 2 de 12 medidores mínimos.** Ninguno con las 6 tomas completas todavía.

## Pendiente

- Completar las tomas que faltan de Medidor1 (contexto, ángulo inclinado, etiqueta del cuerpo —
  esta última podría revelar la marca real de Medidor2 también, si se repite el modelo)
- Seguir sumando medidores en cuanto el clima lo permita, repartiendo zonas entre los tres para no
  sesgar la muestra hacia un solo barrio
- Al menos 3 medidores en condiciones adversas deliberadas (sombra, vidrio sucio, dígito a medio
  giro) — el clima lluvioso de estas dos capturas ya podría contar como una de las tres, si se
  documenta como tal

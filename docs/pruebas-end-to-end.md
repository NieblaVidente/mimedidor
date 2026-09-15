# Pruebas end-to-end: por qué son dos jobs y no uno

> Tarjeta T-50 (#93). Cierra el riesgo §13.4 de [`CLAUDE.md`](../CLAUDE.md).

## El resumen

| Job de CI | Contra qué corre | Trabajador de servicio | Qué prueba |
|---|---|---|---|
| `e2e` | `npm run dev` (puerto 5173) | **Desactivado** | El hilo completo sobre el código fuente |
| `e2e-pwa` | `npm run preview` (puerto 4173) | **Activo** | El mismo hilo sobre el build, más que una versión nueva reemplace a la cacheada |

Los dos corren la misma prueba del hilo (`cypress/e2e/hilo-completo.cy.ts`), sin duplicarla: el
segundo job la reejecuta con otra configuración de Cypress
(`client/cypress.preview.config.ts`).

## Por qué no alcanza con uno

El trabajador de servicio **está desactivado en desarrollo a propósito** desde T-31
(`devOptions: { enabled: false }` en `client/vite.config.ts`): uno cacheando durante `vite dev`
esconde los cambios que uno acaba de hacer, y eso vuelve el desarrollo un ejercicio de adivinanza.

La consecuencia era que **el único camino que el abonado usa en producción era el único que nunca
se ejercitaba**. No estaba roto; simplemente no se probaba. Un trabajador de servicio sirviendo una
versión vieja desde caché es un fallo especialmente feo: la aplicación abre, responde, se ve bien —
y muestra otra cosa. El peor día para descubrirlo es el de la feria.

Activarlo también en desarrollo habría cerrado el hueco de la prueba abriendo uno peor. Correr las
dos cosas es la única forma de tener las dos propiedades.

## Los tres problemas que hubo que resolver

**1. `vite preview` sirve el build, no el código fuente.** El job construye primero
(`npm run build`) y recién después levanta `preview`.

**2. El proxy a `/api` no aplicaba.** `server.proxy` de `vite.config.ts` es del servidor de
desarrollo; `vite preview` es otro servidor y lee su propia sección. Se agregó `preview.proxy`.
Preview no es producción —allá el build y la API salen del mismo origen y no hay ningún proxy—:
este proxy existe solo para poder ejercitar el build sin montar esa infraestructura.

**3. La caché sobrevive entre corridas.** La prueba desregistra los trabajadores de servicio y
vacía las cachés antes de empezar (`limpiarTrabajadoresYCaches`). En CI cada corrida arranca con
una máquina nueva, pero en la máquina de un integrante no, y una caché ya poblada haría pasar por
bueno un registro que nunca ocurrió.

## Cómo se detecta que se sirvió una versión vieja

Sin algo que distinga un build de otro, «se quedó pegado en el anterior» no se puede afirmar. Por
eso la aplicación muestra en el pie el valor de `VITE_VERSION_BUILD`
(`client/src/App.tsx`), que el pipeline fija en el SHA del commit.

La prueba `cypress/e2e-pwa/trabajador-de-servicio.cy.ts` hace esto:

1. Limpia el navegador y visita la aplicación, hasta que el trabajador de servicio **controle** la
   página.
2. Anota la versión que muestra el pie.
3. **Reconstruye el cliente a mitad de la prueba** (`cy.exec('npm run build')`) con otro valor de
   `VITE_VERSION_BUILD`. `vite preview` lee el disco en cada petición, así que no hace falta
   reiniciarlo.
4. Recarga hasta que el pie muestre la versión nueva, y **falla** si después de varios intentos
   sigue mostrando la vieja.

El paso 4 reintenta en vez de esperar un tiempo fijo porque con `registerType: 'autoUpdate'` el
reemplazo tarda dos recargas: en la primera el navegador descubre el trabajador de servicio nuevo
y lo instala, y recién en la siguiente es él quien responde.

La otra prueba del archivo comprueba que **nada de `/api` quedó guardado en caché**. Hoy eso pasa
solo, porque no hay `runtimeCaching` configurado; la prueba existe para que deje de pasar el día
que alguien agregue uno «para que cargue más rápido». Un historial servido desde caché serían
datos viejos presentados como actuales, que es justo lo que este producto no puede hacer.

## Correrlas a mano

```bash
# El hilo sobre el código fuente (lo de siempre, T-22)
cd client && npm run e2e

# El hilo sobre el build, con el trabajador de servicio activo (T-50)
cd client
VITE_VERSION_BUILD=local npm run build
npm run preview -- --port 4173 &
npm run e2e:pwa
```

En los dos casos hacen falta PostgreSQL con `datos_de_prueba.sql` aplicado y la API en el 8000
(ver [`como-empezar.md`](como-empezar.md)).

## Lo que sigue sin cubrirse

- **El funcionamiento sin conexión no existe todavía**, así que tampoco se prueba: guardar una
  lectura sin señal y sincronizarla después no está implementado (`CLAUDE.md` §13.5).
- **La instalación como aplicación** (el diálogo de «agregar a pantalla de inicio») no se
  automatiza: depende del navegador y del sistema operativo. La evidencia de que funciona es
  manual, en `docs/evidencia/`.

# Walkthrough Histórico Integral: Servidor FastMCP LinkedIn (`linkedin`)

## 📌 1. Visión General y Arquitectura del Sistema

El proyecto **MCP LinkedIn** es un servidor open-source desarrollado bajo el estándar **Model Context Protocol (MCP)** con **FastMCP 2.2+** y **Playwright**, diseñado para permitir a agentes de Inteligencia Artificial interactuar con LinkedIn de forma supervisada, ética, robusta y con ritmo humano.

### Componentes de la Arquitectura
1. **Motor Dual de Navegación**:
   - **Brave Browser** headless con evasión de fingerprints (`--disable-blink-features=AutomationControlled`, Chrome 124, locale `es-ES`).
   - **Obscura Stealth** (`obscura.exe`), motor ligero en Rust + V8 nativo para scraping WAF de alto rendimiento y bajo consumo.
2. **Arquitectura Paso Cero CDP (Puerto 9222)**:
   - Sincronización atómica y en caliente de cookies vía WebSocket (`Storage.getCookies`) desde la instancia abierta de Brave Browser.
   - Elimina la necesidad de pasar por formularios de login, evitando bloqueos por inicios de sesión simultáneos y preservando la sesión activa del usuario.
3. **Salvaguardas de Seguridad y Human-in-the-Loop (HITL)**:
   - Confirmación explícita en dos fases (`confirm=True`) en acciones destructivas (`linkedin_delete_post`) y envíos de mensajes directos (`linkedin_send_message`).
   - Jitter gaussiano aleatorio (1.5s–3.0s) entre peticiones consecutivas para emular cadencia humana y evitar rate limits.
   - Sanitización estricta de cookies para erradicar errores `HTTP 999` (desescape de comillas en `JSESSIONID`, purga de subdominios ajenos y deduplicación de `li_at`).
4. **Plan B Interactivo Desacoplado**:
   - Proyección en escritorio interactivo mediante `schtasks /IT` para resolver retos puntuales (2FA o reCAPTCHA) sin robar el foco del usuario (`SW_SHOWNOACTIVATE`).

---

## 🔑 2. Almacenamiento de Credenciales y Sesión

- **Credenciales JSON**: `%USERPROFILE%\.gemini\config\mcp-auth\linkedin_creds.json` (email y contraseña cifrados / protegidos).
- **Estado Persistente de Almacenamiento**: `%USERPROFILE%\.gemini\config\mcp-auth\linkedin_storage_state.json` (cookies sanitizadas y orígenes de sesión).
- **Distribución Precompilada**: Paquetes Wheel (`.whl`) y Source Distribution (`.tar.gz`) en `dist/`.

---

## 🛠️ 3. Catálogo Completo de Herramientas Implementadas (21 Herramientas)

### A. Publicación y Distribución (4 herramientas)
| Herramienta | Parámetros | Descripción |
|---|---|---|
| `linkedin_create_post` | `text`, `image_path` (opc), `first_comment` (opc) | Publica posts ricos con imágenes HD mediante `expect_file_chooser()` y primer comentario automático con motor Tiptap. |
| `linkedin_get_recent_posts` | `limit` (default: 5) | Extrae publicaciones recientes del perfil con texto, métricas de impresiones, URN y URL canónica. |
| `linkedin_check_session` | Ninguno | Valida la vigencia de la sesión activa y estado del storage state. |
| `linkedin_renew_session_interactive` | `timeout_sec` (default: 180) | Plan B interactivo en pantalla pasiva (/IT) para resolución de captchas o 2FA. |

### B. Gestión de Publicaciones - Menú de 3 Puntos (7 herramientas)
| Herramienta | Parámetros | Descripción |
|---|---|---|
| `linkedin_toggle_feature_post` | `post_url` (opc), `post_index` (default: 0) | Fija o quita la publicación de la sección de **Destacados** del perfil. |
| `linkedin_toggle_save_post` | `post_url` (opc), `post_index` (default: 0) | Guarda o desguarda la publicación en los marcadores personales de LinkedIn. |
| `linkedin_get_post_embed_code` | `post_url` (opc), `post_index` (default: 0) | Extrae el snippet HTML `<iframe>` para incrustar el post en páginas web. |
| `linkedin_get_post_link` | `post_url` (opc), `post_index` (default: 0) | Obtiene el enlace directo y limpio de la publicación. |
| `linkedin_edit_post` | `new_text`, `post_url` (opc), `post_index` (default: 0) | Abre el modal de edición, actualiza el contenido de texto y guarda los cambios. |
| `linkedin_delete_post` | `confirm` (bool), `post_url` (opc), `post_index` (default: 0) | Eliminación definitiva con salvaguarda modal. Aborta si `confirm` no es `True`. |
| `linkedin_get_comment_settings_url` | `post_url` (opc), `post_index` (default: 0) | Obtiene directrices y acceso para configurar quién puede comentar. |

### C. Búsqueda y Prospección Profesional (3 herramientas)
| Herramienta | Parámetros | Descripción |
|---|---|---|
| `linkedin_search_people` | `keywords`, `location` (opc), `limit` (default: 10) | Busca profesionales extrayendo nombre, titular profesional, ubicación y enlace. |
| `linkedin_search_jobs` | `keywords`, `location` (default: 'Madrid'), `remote_only` (bool), `limit` (default: 10) | Busca ofertas de empleo activas con filtros geográficos y remotos. |
| `linkedin_search_companies` | `keywords`, `limit` (default: 10) | Busca organizaciones, empresas y centros de trabajo. |

### D. Mensajería Directa e Inbox - Benchmark Stickerdaniel (3 herramientas)
| Herramienta | Parámetros | Descripción |
|---|---|---|
| `linkedin_get_inbox_messages` | `limit` (default: 10), `unread_only` (bool) | Consulta conversaciones recientes de `/messaging/` con remitente, extracto, timestamps y no leídos. |
| `linkedin_get_conversation_thread` | `thread_id_or_index`, `limit` (default: 20) | Extrae el historial completo de mensajes cronológicos de un chat. |
| `linkedin_send_message` | `recipient_or_thread`, `message_text`, `confirm` (bool) | Envío directo de mensaje con salvaguarda en dos fases (`confirm=True`). Si es `False`, genera borrador previo. |

### E. Inteligencia de Perfiles, Feed y Mercado - Benchmark Eliasbiondo (4 herramientas)
| Herramienta | Parámetros | Descripción |
|---|---|---|
| `linkedin_get_profile_details` | `profile_url_or_username` (default: 'me') | Extracción profunda de perfil: Acerca de, Experiencias laborales con fechas/duraciones, Educación, Habilidades y Destacados. |
| `linkedin_get_feed_posts` | `limit` (default: 10) | Extrae publicaciones activas del timeline global mediante detección semántica de botones de interacción social. |
| `linkedin_get_job_details` | `job_url_or_id` | Detalle exhaustivo de oferta de empleo con descripción íntegra, requisitos y badges de modalidad. |
| `linkedin_get_company_details` | `company_url_or_slug` | Ficha institucional corporativa: resumen, web oficial, sector, tamaño, sede y especialidades. |

---

## 🛡️ 4. Análisis Forense de DOM, Selectores y Lecciones Aprendidas (2026)

Durante el ciclo de desarrollo y pruebas en vivo, se documentaron y resolvieron los siguientes retos críticos del DOM de LinkedIn:

1. **Inputs Fantasma en `/login` (`TimeoutError` en fill)**:
   - LinkedIn inyecta campos ocultos en el DOM para WebAuthn y autocompletado (`type="password"` y `type="email"`) con dimensiones de 0 píxeles (`visible: false`).
   - *Solución*: Filtrar estrictamente por la pseudoclase `:visible` o verificar dimensiones positivas (`offsetWidth > 0 && offsetHeight > 0`).
2. **Colisión de Botones SSO vs. Formulario Nativo**:
   - El botón *"Iniciar sesión con Microsoft"* contiene la subcadena *"Iniciar sesión"*, redirigiendo a `login.live.com` si se usa coincidencia parcial.
   - *Solución*: Enviar el formulario presionando `Enter` en el input de contraseña (`press("Enter")`) o usar coincidencia exacta de rol (`name="Iniciar sesión", exact=True`).
3. **Diálogos Modales Post-Publicación (Intercepción de Puntero)**:
   - Tras publicar con éxito, LinkedIn despliega un elemento flotante `<dialog data-testid="dialog">` para promocionar el post, bloqueando eventos de ratón.
   - *Solución*: Despacho preventivo de la tecla `Escape` o ejecución de clics nativos vía JavaScript (`evaluate('b => b.click()')`).
4. **Editor Tiptap / ProseMirror en Primer Comentario**:
   - La caja de comentarios está construida sobre Tiptap (`div.tiptap.ProseMirror`). El método `fill()` de Playwright no dispara los eventos sintácticos necesarios y omite el procesamiento de hipervínculos.
   - *Solución*: Enfoque explícito con `.click()`, tipeo con cadencia simulada (`page.keyboard.type(line, delay=5)`), saltos con `Shift+Enter` (para evitar envíos prematuros) y verificación de contenido en el DOM.
5. **Causa Raíz de la Pérdida de Sesión y Checkpoints de Seguridad**:
   - Cada intento de autenticación automatizada por formulario contra `/login` invalida la cookie de sesión activa previa (`li_at`) y activa el motor de defensa de LinkedIn, levantando un checkpoint de seguridad reCAPTCHA (*"Vamos a hacer una comprobación rápida de seguridad"*).
   - *Garantía de Persistencia Definitiva*: La arquitectura **Paso Cero CDP** extrae pasivamente `li_at` desde la sesión de Brave sin tocar nunca la ruta `/login`. Una vez resuelto el checkpoint en Brave, la cookie se congela en `linkedin_storage_state.json` y el sistema opera en modo 100% desatendido sin riesgo de revocación.

---

## 🎨 5. Nueva Infografía Técnica v2 (Gemini NotebookLM Studio)

### Proceso de Generación y Sincronización
1. **Conexión al Cuaderno Central**: Conectado a NotebookLM (`bad774e8-adeb-458a-8632-cff7ca06c94e`) bajo la cuenta `solari21@gmail.com`.
2. **Purga e Ingesta de Fuentes**: Eliminadas las versiones obsoletas e ingestadas las especificaciones técnicas actuales:
   - `README.md`
   - `SKILL.md`
   - `TODO.md`
   - `walkthrough.md`
   - Repositorio oficial de GitHub (`https://github.com/solari21/mcp-linkedin`)
3. **Generación del Artefacto Blueprint**:
   - Creado artefacto Studio (`12c8df74-bf0d-47e8-857e-4aced02915da`) con prompt de ingeniería de sistemas de alta fidelidad:
     - Estilo visual de plano arquitectónico (blueprint) en azul tecnológico, blanco y gris grafito.
     - Cero elementos infantiles, personajes de cómic o caricaturas.
     - Estructurado en 4 secciones modulares:
       * **Sección 1**: Núcleo de Navegación Dual (Brave Headless + Obscura Stealth) y Paso Cero CDP (puerto 9222).
       * **Sección 2**: Seguridad y Resiliencia (Jitter gaussiano, sanitización anti-HTTP 999, salvaguardas HITL en 2 fases con `confirm=True`, Plan B interactivo).
       * **Sección 3**: Dinámica Interna y Selectores DOM Resilientes (Pseudoclase `:visible`, escape de `<dialog>` flotantes y motor Tiptap/ProseMirror).
       * **Sección 4**: Catálogo Completo de 21 Herramientas dividido en 5 suites con badges técnicos.
4. **Descarga y Publicación del Asset**:
   - Descargada en resolución ultra-alta: [infografia_mcp_linkedin.png](file:///c:/Users/solari21.SOLARI21PC/Antigravity%20Projects/MCP%20Linkedin/assets/infografia_mcp_linkedin.png) (2752×1536 px, 5.03 MB).
   - Commiteada y subida a la rama `main` en GitHub (`commit d293fb2`).

---

## 📋 6. Protocolo de Publicación y Primer Comentario Oficial

### Texto de la Publicación Oficial
```text
🚀 ¡Lanzamos MCP LinkedIn: Servidor oficial de Model Context Protocol para LinkedIn!

Conecta asistentes de IA y agentes autónomos directamente con tu perfil y red profesional con FastMCP y Playwright sobre Brave Browser.

✨ 21 herramientas especializadas organizadas en 5 suites:
1️⃣ Publicación enriquecida: Texto con emojis, hashtags, imágenes en alta resolución y primer comentario automático.
2️⃣ Control integral (Menú de 3 puntos): Destacar en el perfil, guardar, editar, copiar enlaces limpios e incrustar iframes.
3️⃣ Prospección inteligente: Búsqueda de profesionales, ofertas de empleo con filtros y centros de empresa.
4️⃣ Mensajería supervisada: Consulta de bandeja de entrada (/messaging/), lectura de hilos y envío seguro en dos fases (confirm=True).
5️⃣ Inteligencia de mercado: Extracción profunda de perfiles estructurados, feed y ofertas laborales.

🛡️ Arquitectura Paso Cero CDP:
Sincronización en caliente pasiva vía Brave CDP (puerto 9222) que previene captchas y preserva la sesión activa sin solicitar credenciales.

Agradecimientos especiales a Elias Biondo (https://www.linkedin.com/in/eliasbiondo/) y Daniel Sticker (@stickerdaniel en GitHub: https://github.com/stickerdaniel), cuyos proyectos open-source han servido como referencia para ampliar las capacidades del servidor.

📦 Código abierto, paquete Wheel (.whl) y roadmap disponibles en GitHub.
#ArtificialIntelligence #ModelContextProtocol #FastMCP #OpenSource #Automation #Python #Playwright #BraveBrowser #DeveloperTools
```

### Primer Comentario Oficial (Verificado en DOM con Badge de Autor)
```text
Dejo por aquí los accesos directos al proyecto:

🔗 Repositorio en GitHub:
https://github.com/solari21/mcp-linkedin

📦 Releases Oficiales y Paquete Wheel (v1.0.0):
https://github.com/solari21/mcp-linkedin/releases/tag/v1.0.0

🎯 Tablero de Roadmap y Tareas en Progreso (GitHub Projects):
https://github.com/users/solari21/projects/2

¡Cualquier feedback, issue o PR para sumar nuevas herramientas es más que bienvenido! ⭐
```

---

## 🏛️ 7. Gobernanza del Ecosistema Antigravity

- **Configuración Global MCP**: Registrado en `~/.gemini/config/mcp_config.json` bajo `"linkedin"`.
- **Skill Global Estandarizada**: Documentada en `~/.gemini/config/skills/linkedin-automation/SKILL.md`.
- **Normativa Canónica**: Registrada como Entrada #21 en Sección V del archivo canónico `AGENTS.md`.
- **Roadmap Interactivo**: Gestionado activamente en el tablero [GitHub Projects V2 #2](https://github.com/users/solari21/projects/2).

---

## 🔍 8. Análisis Forense: Dominio de Cookies, Tasa 429 y Checkpoint reCAPTCHA

### 1. El Bug de Dominio en `li_at` (`.www.linkedin.com` vs `.linkedin.com`)
- **Causa Raíz**: En `linkedin_interactive_login.py` (línea 105), el código forzaba `c["domain"] = ".www.linkedin.com"`.
- **Efecto Colateral**: El motor Chromium de Playwright solo adjuntaba la cookie en subdominios directos de `www`, pero la omitía en el dominio raíz (`linkedin.com/feed/`) y llamadas internas de API.
- **Consecuencia**: LinkedIn interpretaba la petición como un usuario no autenticado, forzando una redirección HTTP 302 a `/login`. Al intentar el fallback de tecleo de credenciales en `/login`, LinkedIn activó sus defensas anti-bot.

### 2. ¿Qué significa la "Tasa 429" (HTTP 429 Too Many Requests)?
- **Mecanismo de LinkedIn**: Cuando se reciben múltiples peticiones automatizadas consecutivas en un intervalo muy corto a `linkedin.com/feed/` (o fallos de autenticación repetidos sin sesión válida), el cortafuegos de LinkedIn activa una limitación temporal de tasa (HTTP 429).
- **Manifestación**: LinkedIn devuelve una página vacía (`<html><head></head><body></body></html>`) o redirige a un desafío de seguridad en lugar de cargar el feed.
- **Resolución**: Dejar transcurrir el período de enfriamiento (cooldown) y acceder mediante cookies canónicas extraídas pasivamente por CDP o mediante la sesión viva en Brave Browser.

### 3. Checkpoint de Seguridad reCAPTCHA ("Vamos a hacer una comprobación rápida de seguridad")
- **Detección**: Google reCAPTCHA Enterprise detecta la presencia de banderas de automatización (`navigator.webdriver`, clicks por CDP sin aceleración humana) cuando se intenta automatizar el login por formulario.
- **Protocolo Canónico**: Ante el checkpoint `linkedin.com/checkpoint/challenge/...`, la resolución humana mediante un clic único en la casilla `[ ] No soy un robot` en el navegador visible desbloquea la cuenta al instante, expidiendo una nueva cookie `li_at` auténtica que el servidor MCP captura de inmediato vía CDP.


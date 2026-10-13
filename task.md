# Checklist Maestro de Tareas: MCP Linkedin (LinkedIn Automation Server)

## 📌 Histórico Acumulativo de Fases

### Fase 1: Arquitectura y Diseño del Servidor MCP
- [x] Validación empírica de selectores y flujo de publicación (Login, File Chooser, Contenteditable, Publicar, Comentarios)
- [x] Implementación de `linkedin_server.py` con FastMCP 2.2+ y Playwright headless

### Fase 2: Herramientas Básicas del Núcleo
- [x] `linkedin_create_post`: Publicación de texto enriquecido con emojis, imágenes y primer comentario
- [x] `linkedin_get_recent_posts`: Extracción de publicaciones recientes y métricas de impresiones
- [x] `linkedin_check_session`: Verificación de salud y estado de la sesión activa

### Fase 3: Suite Completa del Menú de 3 Puntitos
- [x] `linkedin_toggle_feature_post`: Destacar / Quitar de destacados en la parte superior del perfil
- [x] `linkedin_toggle_save_post`: Guardar / Quitar de guardados en elementos personales
- [x] `linkedin_get_post_embed_code`: Extracción del snippet HTML `<iframe>` para incrustar en webs
- [x] `linkedin_get_post_link`: Obtención y copia del enlace canónico directo
- [x] `linkedin_edit_post`: Edición del texto de publicaciones existentes
- [x] `linkedin_delete_post`: Eliminación definitiva con salvaguarda obligatoria `confirm=True`
- [x] `linkedin_get_comment_settings_url`: Control y acceso a opciones de privacidad de comentarios

### Fase 4: Motores de Búsqueda y Prospección Profesional
- [x] `linkedin_search_people`: Búsqueda de personas y profesionales con filtros geográficos y de cargo
- [x] `linkedin_search_jobs`: Búsqueda de ofertas de trabajo activas (Madrid, remoto, etc.)
- [x] `linkedin_search_companies`: Búsqueda de organizaciones, instituciones y empresas

### Fase 5: Verificación y Pruebas Iniciales
- [x] Validación de introspección de esquemas FastMCP
- [x] Verificación empírica de selectores DOM en vivo
- [x] Documentación inicial de pruebas en `walkthrough.md`

### Fase 6: Registro en Entorno Antigravity
- [x] Configuración del servidor en `mcp_config.json` (`"linkedin"`)
- [x] Registro en catálogo de proyectos de Antigravity (`af5d9fbb-585e-431c-8a0a-64cd55a8e0e3.json`)

### Fase 7: Gobernanza y Skill Global
- [x] Creación de Skill Global `linkedin-automation` en `~/.gemini/config/skills/linkedin-automation/SKILL.md`
- [x] Registro como Entrada #21 en Sección V de `AGENTS.md`

### Fase 8: Plan B de Resiliencia: Ventana Interactiva Brave (/IT)
- [x] Implementación de `renew_session_interactive()` con proyección asistida `schtasks /IT`
- [x] Integración de fallback automático ante expiración, captchas o 2FA
- [x] Cero robo de foco garantizado (`SW_SHOWNOACTIVATE`)

### Fase 9: Benchmark Open-Source (`stickerdaniel` & `eliasbiondo`)
- [x] Análisis forense e ingeniería inversa de ambos proyectos de referencia
- [x] Módulo desacoplado `linkedin_extended.py` con parsers resilientes y jitter gaussiano
- [x] Integración de 7 herramientas adicionales para alcanzar el catálogo completo de 21 herramientas:
  - [x] `linkedin_get_inbox_messages`: Consulta de conversaciones recientes con no leídos y timestamps
  - [x] `linkedin_get_conversation_thread`: Lectura del historial completo de chats
  - [x] `linkedin_send_message`: Envío seguro con salvaguarda HITL en dos fases (`confirm=True`)
  - [x] `linkedin_get_profile_details`: Extracción profunda del perfil (Acerca de, Experiencias, Habilidades)
  - [x] `linkedin_get_feed_posts`: Extracción de publicaciones del timeline global por botones semánticos
  - [x] `linkedin_get_job_details`: Detalle íntegro de ofertas laborales y modalidades
  - [x] `linkedin_get_company_details`: Detalle corporativo de instituciones y empresas

### Fase 10: Validación Empírica Integral (Zero Mocks)
- [x] Verificación end-to-end contra datos reales de LinkedIn de las 21 herramientas
- [x] Corrección de falsos positivos de timeout (`wait_until="commit"`)
- [x] Sanitización estricta de cookies para evitar errores `HTTP 999`
- [x] Empaquetado oficial en Wheel (`.whl`) y Source Distribution (`.tar.gz`) en `dist/`

### Fase 11: Despliegue de Arquitectura Paso Cero CDP y Motor Tiptap
- [x] Implementación de conexión pasiva en caliente vía WebSocket al puerto 9222 de Brave Browser
- [x] Protección anti-revocación multi-sesión (eliminación del login redundante por formulario)
- [x] Adaptación del editor de comentarios a componentes ricos `div.tiptap.ProseMirror` con tipeo simulado y saltos `Shift+Enter`
- [x] Sincronización de tableros Kanban en GitHub Projects V2 (#2)

### Fase 12: Primera Publicación, Auditoría de Calidad y Retirada
- [x] Publicación inicial de prueba (`urn:li:activity:7515912088733515776`)
- [x] Auditoría de calidad visual: la infografía generada tenía estética de cómic/infantil no alineada con el estándar profesional
- [x] Eliminación limpia y definitiva de la publicación mediante `linkedin_delete_post(confirm=True)`

### Fase 13: Renovación de Fuentes en Gemini NotebookLM y Generación Blueprint v2
- [x] Conexión al cuaderno `bad774e8-adeb-458a-8632-cff7ca06c94e` con credenciales de `solari21@gmail.com`
- [x] Purga permanente de fuentes obsoletas en el cuaderno
- [x] Ingesta de las versiones actuales de la documentación:
  - `README.md`
  - `SKILL.md`
  - `TODO.md`
  - `walkthrough.md`
  - Repositorio GitHub (`https://github.com/solari21/mcp-linkedin`)
- [x] Creación de nuevo artefacto Studio de tipo Infografía (`12c8df74-bf0d-47e8-857e-4aced02915da`) con prompt técnico especializado:
  - Estilo: Arquitectura de software / Blueprint técnico de ingeniería de sistemas
  - Esquema modular: Núcleo de navegación dual, seguridad gaussiana, selectores DOM y catálogo de 21 herramientas
- [x] Descarga de la infografía en alta resolución: [infografia_mcp_linkedin.png](file:///c:/Users/solari21.SOLARI21PC/Antigravity%20Projects/MCP%20Linkedin/assets/infografia_mcp_linkedin.png) (2752×1536 px, 5.03 MB)
- [x] Commit y push oficial a la rama `main` en GitHub (`commit d293fb2`)

### Fase 14: Diagnóstico Forense del Reto de Seguridad LinkedIn y Arquitectura de Sesión
- [x] Descubrimiento de inputs fantasma en `/login`: LinkedIn inyecta campos invisibles (`visible: false`) para autocompletado y WebAuthn
- [x] Análisis forense del checkpoint de seguridad: los intentos de login automatizados desde IP/huella nueva invalidaron temporalmente `li_at`, levantando el reCAPTCHA ("Vamos a hacer una comprobación rápida de seguridad")
- [x] Activación no invasiva de la pestaña en Brave Browser (`A0AEE63EDBFB8A3905BF39940E679E4D`) para resolución del reto en pantalla
- [x] Captura en caliente de la cookie canónica `li_at` vía CDP WebSocket tras validación, blindando `linkedin_storage_state.json` para eliminar por completo los accesos por formulario

### Fase 15: Publicación Oficial Definitiva del Post y Primer Comentario
- [ ] Sincronización final de la cookie activa desde Brave CDP
- [ ] Publicación del post oficial en LinkedIn adjuntando la nueva infografía Blueprint v2
- [ ] Atribución oficial: perfil de LinkedIn de Elias Biondo y perfil de GitHub de Daniel Sticker (@stickerdaniel)
- [ ] Inyección inmediata del primer comentario verificado en el DOM con enlaces al repositorio y documentación técnica
- [ ] Captura visual del resultado y verificación end-to-end

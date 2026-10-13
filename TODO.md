# 📋 TO-DO List & Roadmap - MCP LinkedIn

Lista de tareas, funcionalidades activas y backlog evolutivo para el servidor **MCP LinkedIn**.

---

## 🚀 Versión 1.0.0 (Lanzamiento Inicial - Completado)

- [x] **Arquitectura y Core MCP**:
  - [x] Migración a SDK FastMCP (mcp>=1.2.0) con decoradores `@mcp.tool()`.
  - [x] Gestión de ciclo de vida del navegador (Brave Browser primario con fallback a Chromium).
  - [x] Manejo inteligente de credenciales mediante `.env`, variables de entorno y archivos JSON locales.
  - [x] Soporte para modo Headless y Plan B interactivo asistido en Windows (`schtasks /IT`).

- [x] **Publicación y Distribución de Contenido**:
  - [x] Creación de publicaciones de texto con emojis y hashtags (`linkedin_create_post`).
  - [x] Carga de imágenes en alta resolución mediante `expect_file_chooser()`.
  - [x] Publicación automática de primer comentario con enlaces para evitar penalización de alcance.
  - [x] Consulta de publicaciones recientes con métricas de impresiones y engagement (`linkedin_get_recent_posts`).

- [x] **Control Integral del Menú de 3 Puntos**:
  - [x] Fijar y desmarcar de destacados del perfil (`linkedin_toggle_feature_post`).
  - [x] Guardar y retirar de marcadores guardados (`linkedin_toggle_save_post`).
  - [x] Extracción de código HTML `<iframe>` para incrustar posts (`linkedin_get_post_embed_code`).
  - [x] Copia y resolución de enlace canónico directo y limpio (`linkedin_get_post_link`).
  - [x] Edición de publicaciones existentes desde modal de LinkedIn (`linkedin_edit_post`).
  - [x] Eliminación segura con factor de confirmación (`linkedin_delete_post`).
  - [x] Consulta de directrices de privacidad de comentarios (`linkedin_get_comment_settings_url`).

- [x] **Búsqueda e Inteligencia Profesional**:
  - [x] Buscador de profesionales por palabras clave, cargo y ubicación (`linkedin_search_people`).
  - [x] Buscador de empleos activos con filtro de modalidad (`linkedin_search_jobs`).
  - [x] Ficha completa de oferta de trabajo con requisitos y cuerpo íntegro (`linkedin_get_job_details`).
  - [x] Buscador y ficha institucional de empresas (`linkedin_search_companies`, `linkedin_get_company_details`).
  - [x] Extracción profunda de perfil personal (`linkedin_get_profile_details`).
  - [x] Extracción de publicaciones del feed principal (`linkedin_get_feed_posts`).

- [x] **Bandeja de Entrada y Mensajería Supervisada**:
  - [x] Lectura de conversaciones en `/messaging/` con marcas de no leído (`linkedin_get_inbox_messages`).
  - [x] Consulta cronológica de hilos de mensajes específicos (`linkedin_get_conversation_thread`).
  - [x] Envío supervisado con salvaguarda en dos fases (`confirm=True`) (`linkedin_send_message`).

- [x] **Empaquetado, CI/CD y Distribución**:
  - [x] Estándar PEP 621 con `pyproject.toml` y entry points de consola (`mcp-linkedin`).
  - [x] Precompilación de paquetes Wheel (`.whl`) y tarball (`.tar.gz`) en `dist/`.
  - [x] Instaladores asistidos `install.bat` (Windows) e `install.sh` (Linux/macOS).
  - [x] Workflows de GitHub Actions para CI (lint, sintaxis y build) y distribución automática de binarios (.whl y .tar.gz) en GitHub Releases con action-gh-release.

---

## 🔮 Versión 1.1.0 (Próximas Funcionalidades / Backlog)

- [ ] **Encuestas Interactivas (Polls)**:
  - [ ] Herramienta para crear encuestas con opciones múltiples y duración configurable.
  - [ ] Consulta y monitorización de votos y porcentajes en tiempo real.

- [ ] **Publicación Programada Nativa**:
  - [ ] Aprovechamiento del selector nativo de LinkedIn para programar fecha y hora diferida.

- [ ] **Carruseles y Documentos PDF**:
  - [ ] Soporte para subir presentaciones diapositiva a diapositiva mediante PDF.

- [ ] **Exportación y Métricas Históricas**:
  - [ ] Exportación periódica de analíticas a bases de datos locales SQLite o archivos CSV/Excel.

- [ ] **Webhooks y Notificaciones Locales**:
  - [ ] Servicio en segundo plano para notificar mensajes nuevos en bandeja de entrada vía toast/webhook local.

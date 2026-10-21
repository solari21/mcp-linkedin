# Checklist Maestro de Tareas: MCP Linkedin (LinkedIn Automation Server)

## 📌 Bloque I · Fases Históricas Consolidadas (Hitos Previos 1 a 18)

- [x] **Fase 1: Arquitectura y Diseño del Servidor MCP**: Validación de selectores, `linkedin_server.py` con FastMCP y Playwright headless.
- [x] **Fase 2: Herramientas Básicas del Núcleo**: `linkedin_create_post`, `linkedin_get_recent_posts`, `linkedin_check_session`.
- [x] **Fase 3: Suite Completa del Menú de 3 Puntitos**: Destacar, guardar, iframe embed, enlaces canónicos, editar y eliminar con `confirm=True`.
- [x] **Fase 4: Motores de Búsqueda y Prospección Profesional**: `linkedin_search_people`, `linkedin_search_jobs`, `linkedin_search_companies`.
- [x] **Fase 5: Verificación y Pruebas Iniciales**: Introspección FastMCP y documentación inicial en `walkthrough.md`.
- [x] **Fase 6: Registro en Entorno Antigravity**: Configuración en `mcp_config.json` (`"linkedin"`).
- [x] **Fase 7: Gobernanza y Skill Global**: Creación de Skill Global `linkedin-automation` y Entrada #21 en Sección V de `AGENTS.md`.
- [x] **Fase 8: Plan B de Resiliencia (Ventana Interactiva Brave /IT)**: Fallback asistido con `schtasks /IT` con cero robo de foco (`SW_SHOWNOACTIVATE`).
- [x] **Fase 9: Benchmark Open-Source (`stickerdaniel` & `eliasbiondo`)**: Módulo `linkedin_extended.py` y ampliación a 21 herramientas.
- [x] **Fase 10: Validación Empírica Integral (Zero Mocks)**: Verificación end-to-end contra datos reales, empaquetado Wheel y sdist.
- [x] **Fase 11: Despliegue de Arquitectura Paso Cero CDP y Motor Tiptap**: Sincronización pasiva WebSocket 9222, motor Tiptap multilínea.
- [x] **Fase 12: Primera Publicación, Auditoría de Calidad y Retirada**: Publicación de prueba y purga con `linkedin_delete_post(confirm=True)`.
- [x] **Fase 13: Renovación de Fuentes en Gemini NotebookLM y Blueprint v2**: Infografía técnica Blueprint v2 (`infografia_mcp_linkedin.png`, 2752×1536 px).
- [x] **Fase 14: Diagnóstico Forense de Seguridad y Checkpoints**: Filtrado de inputs fantasma, detección de bucle de popups `schtasks`.
- [x] **Fase 15: Erradicación Radical del Bucle de Popups y Blindaje a 1 Año**: Extirpación de popups automáticos, expiración forzada a 1 año, respaldo `.bak`.
- [x] **Fase 16: Captura Pasiva de Sesión en Brave y Verificación Headless**: Extracción pasiva CDP WebSocket dual y guardado atómico.
- [x] **Fase 17: Publicación Oficial Definitiva del Post y Primer Comentario**: Publicación oficial en vivo (`urn:li:activity:7515951568215588864`).
- [x] **Fase 18: Blindaje Documental, Lecciones de Producción y Sincronización Global**: TODO.md, README.md, `walkthrough.md`, `AGENTS.md` (Regla II.32), `SKILL.md`.

---

## 🚀 Bloque II · Fase 19 en Curso: Integración REA MCP (The Gauntlet Loop)

### 1. La Tarea (Caja 1)
Integrar en el proyecto `MCP Linkedin` las capacidades de ingeniería inversa, telemetría y análisis pasivo del proyecto `MCP REA` (Reverse Engineer Anything), resolviendo la fragilidad del raspado DOM mediante las 4 sinergias estratégicas:
1. **Sinergia A**: Mapeo y Extracción de la API Interna Voyager (`/voyager/api/`) en JSON estructurado inmune a cambios del DOM.
2. **Sinergia B**: Auditoría Pasiva de Sesión y Diagnóstico Pre-Vuelo sin evaluación de JS, clics ni navegación que dispare Cloudflare 302 / checkpoints.
3. **Sinergia C**: Ingeniería Inversa de la Arquitectura Móvil Android (`com.linkedin.android`) y endpoints nativos de alta velocidad.
4. **Sinergia D**: Calibración de Señales Algorítmicas de Visibilidad y Retención (**Dwell Time**, expansión "Ver más" y DTPI).

### 2. El Método (Caja 2: The Gauntlet Loop)
- [ ] **Fase 1: Planificación y Checklist del Listón**
- [ ] **Fase 2: Construcción (Versión 1 - 0 Placeholders / 0 Stubs)**
  - [ ] Implementación de `linkedin_voyager.py` (cliente de API privada Voyager con normalización de respuestas JSON).
  - [ ] Implementación de `linkedin_preflight.py` (diagnóstico pasivo CDP pre-vuelo y detección atómica de frescura de tokens).
  - [ ] Implementación de `linkedin_mobile_api.py` (mapeo Rest.li 2.0 móvil e integración con herramientas REA `inspect_android_package`).
  - [ ] Implementación de `linkedin_dwell.py` (motor de análisis de Dwell Time, visibilidad de gancho antes del pliegue y propensión de expansión).
  - [ ] Integración de herramientas en `linkedin_server.py` y orquestación híbrida (Voyager primario $\rightarrow$ DOM fallback).
  - [ ] Actualización de metadatos en `pyproject.toml` (bump a v1.2.0 y registro de módulos en `py-modules`).
- [ ] **Fase 3: Pruebas y Recolección de Evidencias Reales**
  - [ ] Verificación sintáctica y auditoría AST con `verify_ast_clean.py` (0 NameError).
  - [ ] Pruebas empíricas de diagnóstico pasivo pre-vuelo con Brave CDP.
  - [ ] Pruebas de deserialización y parseo de Voyager API para perfiles, feed y empleos.
  - [ ] Pruebas de cálculo de métricas de Dwell Time contra textos reales y publicaciones de LinkedIn.
  - [ ] Verificación de herramientas REA en el ecosistema MCP.
- [ ] **Fase 4: Auditoría del Árbitro Adversarial (Ronda 1)**
  - [ ] Activación de árbitro implacable con aislamiento cognitivo.
  - [ ] Identificación de fallos y objeciones ordenados por gravedad.
- [ ] **Fase 5: Corrección Sistemática de Objeciones**
  - [ ] Subsanación de todas las objeciones detectadas en el código y pruebas.
- [ ] **Fase 6: Re-evaluación Adversarial (Ronda 2 / Certificación del Listón)**
  - [ ] Certificación formal del 100% de los criterios del listón.
- [ ] **Fase 7: Barrera de Salida Universal (Universal Exit Gate)**
  - [ ] Actualización bilingüe completa `README.md` y `README_EN.md` con las nuevas capacidades y arquitectura híbrida.
  - [ ] Generación de nuevos paquetes de distribución Wheel (`.whl`) y sdist (`.tar.gz`) v1.2.0 en `dist/`.
  - [ ] Registro documental en `walkthrough.md`.

### 3. Listón de Aceptación (Caja 3: Checklist del Árbitro)
- [ ] **C1**: Implementación 100% libre de mocks, stubs o datos simulados; código real y tipado.
- [ ] **C2**: Desacoplamiento de lectura: el cliente Voyager debe obtener datos estructurados JSON sin depender de selectores CSS.
- [ ] **C3**: Diagnóstico pasivo pre-vuelo: valida el estado de la sesión (`li_at`, `JSESSIONID`, `bcookie`) por CDP sin evaluar JS en el contexto de página ni forzar redirecciones en bucle.
- [ ] **C4**: Mapeo completo de la arquitectura móvil de LinkedIn Android con integración con REA para auditoría de APKs.
- [ ] **C5**: Métricas empíricas de Dwell Time integradas y calibradas con los umbrales de telemetría de LinkedIn (<1s micro-dwell, $\ge$1.5s qualified, $\ge$4s high-engagement).
- [ ] **C6**: Auditoría AST completa (`verify_ast_clean.py`) superada con 0 NameError o importaciones faltantes en todos los archivos del proyecto.
- [ ] **C7**: Paridad bilingüe estricta entre `README.md` y `README_EN.md` reflejando la nueva versión v1.2.0 y el catálogo ampliado de herramientas.

### 4. Entregable (Caja 4)
- Código modular en producción (`linkedin_voyager.py`, `linkedin_preflight.py`, `linkedin_mobile_api.py`, `linkedin_dwell.py`, `linkedin_server.py`).
- Paquetes compilados v1.2.0 en `dist/`.
- Documentación completa sincronizada (`README.md`, `README_EN.md`, `walkthrough.md`, `task.md`).
- Resumen final de auditoría del árbitro adversarial con balance de rondas.

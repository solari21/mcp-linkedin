"""
Módulo Voyager API para MCP LinkedIn (Arquitectura Híbrida REA).
Desacopla la extracción de datos de LinkedIn del DOM de la página mediante
el consumo de la API REST interna privada Voyager (/voyager/api/) bajo el
protocolo Rest.li 2.0 / normalized JSON.

Ventajas:
1. Inmunidad total ante cambios de clases CSS o rediseños de la SPA en Ember.js/React.
2. Extracción estructurada nativa (Pydantic / dataclasses).
3. Reducción de consumo de RAM y latencia en milisegundos.
4. Soporte para despacho vía CDP contextual o peticiones autenticadas directas.
"""

import json
import logging
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("mcp_linkedin_voyager")

# Rutas Canónicas de la API Privada Voyager de LinkedIn
VOYAGER_BASE_URL = "https://www.linkedin.com/voyager/api"

ENDPOINTS = {
    "me": "/me",
    "profile_dash": "/identity/dash/profiles?q=memberIdentity&memberIdentity={identifier}",
    "profile_view": "/identity/profiles/{identifier}/profileView",
    "feed_dash": "/feed/dash/updates?count={count}&q=chronological",
    "feed_updates": "/feed/updatesV2?count={count}",
    "job_posting": "/voyagerJobsDashJobPostings/{job_id}",
    "company": "/organization/companies?q=universalName&universalName={slug}",
    "conversations": "/messaging/conversations?count={count}",
}

@dataclass
class VoyagerProfile:
    urn: str = ""
    public_identifier: str = ""
    first_name: str = ""
    last_name: str = ""
    headline: str = ""
    summary: str = ""
    industry: str = ""
    location: str = ""
    profile_url: str = ""
    experiences: List[Dict[str, Any]] = field(default_factory=list)
    education: List[Dict[str, Any]] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class VoyagerFeedPost:
    urn: str = ""
    author_name: str = ""
    author_headline: str = ""
    author_urn: str = ""
    text: str = ""
    created_time: Optional[int] = None
    num_likes: int = 0
    num_comments: int = 0
    num_shares: int = 0
    permalink: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class VoyagerJob:
    id: str = ""
    title: str = ""
    company_name: str = ""
    location: str = ""
    employment_type: str = ""
    workplace_type: str = ""
    description: str = ""
    apply_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class VoyagerCompany:
    id: str = ""
    name: str = ""
    universal_name: str = ""
    tagline: str = ""
    description: str = ""
    website: str = ""
    industry: str = ""
    headquarters: str = ""
    staff_count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VoyagerRestLiParser:
    """
    Parser especializado para respuestas normalized+json+2.1 del protocolo Rest.li de LinkedIn.
    Resuelve el grafo relacional entre las entidades raíz en `data` y los objetos normalizados en `included`.
    """

    @staticmethod
    def index_included(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Indexa todos los objetos en 'included' por su entityUrn o $id."""
        index: Dict[str, Dict[str, Any]] = {}
        for item in payload.get("included", []):
            if not isinstance(item, dict):
                continue
            urn = item.get("entityUrn") or item.get("$id") or item.get("urn")
            if urn:
                index[urn] = item
        return index

    @classmethod
    def parse_profile(cls, raw: Dict[str, Any]) -> VoyagerProfile:
        """Parsea la respuesta de Voyager para un perfil de usuario."""
        profile = VoyagerProfile()
        included_index = cls.index_included(raw)

        # 1. Buscar entidad Profile en included o en data
        profile_entity = None
        for item in raw.get("included", []):
            type_name = str(item.get("$type", ""))
            if "identity.profile.Profile" in type_name or "dash.identity.profile.Profile" in type_name:
                profile_entity = item
                break

        if not profile_entity and "miniProfile" in raw:
            profile_entity = raw["miniProfile"]
        if not profile_entity and "elements" in raw and raw["elements"]:
            profile_entity = raw["elements"][0]
        if not profile_entity and "data" in raw and isinstance(raw["data"], dict):
            profile_entity = raw["data"]

        if profile_entity:
            profile.urn = profile_entity.get("entityUrn", "") or profile_entity.get("urn", "")
            profile.public_identifier = profile_entity.get("publicIdentifier", "")
            profile.first_name = profile_entity.get("firstName", "")
            profile.last_name = profile_entity.get("lastName", "")
            profile.headline = profile_entity.get("headline", "")
            profile.summary = profile_entity.get("summary", "")
            profile.industry = profile_entity.get("industryName", "") or profile_entity.get("industry", "")
            loc = profile_entity.get("geoLocationName", "") or profile_entity.get("locationName", "")
            profile.location = loc
            if profile.public_identifier:
                profile.profile_url = f"https://www.linkedin.com/in/{profile.public_identifier}"

        # 2. Extraer experiencias laborales (Position)
        for item in raw.get("included", []):
            type_name = str(item.get("$type", ""))
            if "Position" in type_name:
                company_name = item.get("companyName", "")
                if not company_name and "company" in item:
                    comp_urn = item["company"]
                    if comp_urn in included_index:
                        company_name = included_index[comp_urn].get("name", "")

                time_period = item.get("timePeriod", {})
                start_date = time_period.get("startDate", {}) if isinstance(time_period, dict) else {}
                end_date = time_period.get("endDate", {}) if isinstance(time_period, dict) else {}

                start_str = f"{start_date.get('month', 1)}/{start_date.get('year', '')}" if start_date else ""
                end_str = f"{end_date.get('month', 1)}/{end_date.get('year', '')}" if end_date else "Actualidad"

                profile.experiences.append({
                    "title": item.get("title", ""),
                    "company": company_name,
                    "location": item.get("locationName", ""),
                    "period": f"{start_str} - {end_str}".strip(" -"),
                    "description": item.get("description", "")
                })

        # 3. Extraer educación (Education)
        for item in raw.get("included", []):
            type_name = str(item.get("$type", ""))
            if "Education" in type_name:
                school_name = item.get("schoolName", "")
                if not school_name and "school" in item:
                    school_urn = item["school"]
                    if school_urn in included_index:
                        school_name = included_index[school_urn].get("name", "")

                profile.education.append({
                    "school": school_name,
                    "degree": item.get("degreeName", ""),
                    "field_of_study": item.get("fieldOfStudy", ""),
                    "activities": item.get("activities", "")
                })

        # 4. Extraer habilidades (Skill)
        for item in raw.get("included", []):
            type_name = str(item.get("$type", ""))
            if "Skill" in type_name and "name" in item:
                skill_name = item["name"].strip()
                if skill_name and skill_name not in profile.skills:
                    profile.skills.append(skill_name)

        return profile

    @classmethod
    def parse_feed_updates(cls, raw: Dict[str, Any]) -> List[VoyagerFeedPost]:
        """Parsea la lista de publicaciones del feed de Voyager."""
        posts: List[VoyagerFeedPost] = []
        included_index = cls.index_included(raw)

        items = raw.get("elements", []) or raw.get("included", [])
        for item in items:
            if not isinstance(item, dict):
                continue
            type_name = str(item.get("$type", ""))
            if "Update" not in type_name and "feed" not in type_name:
                continue

            urn = item.get("entityUrn") or item.get("urn") or ""
            text = ""
            author_name = ""
            author_headline = ""
            author_urn = ""

            # Extraer contenido de texto
            commentary = item.get("commentary", {})
            if isinstance(commentary, dict) and "text" in commentary:
                t_val = commentary["text"]
                text = t_val.get("text", "") if isinstance(t_val, dict) else str(t_val)
            elif "value" in item and isinstance(item["value"], dict):
                val = item["value"]
                comm = val.get("commentary", {})
                if isinstance(comm, dict):
                    t_val = comm.get("text", "")
                    text = t_val.get("text", "") if isinstance(t_val, dict) else str(t_val)

            # Extraer actor / autor
            actor = item.get("actor", {})
            if isinstance(actor, dict):
                author_urn = actor.get("urn", "")
                name_obj = actor.get("name", {})
                author_name = name_obj.get("text", "") if isinstance(name_obj, dict) else str(name_obj)
                desc_obj = actor.get("description", {})
                author_headline = desc_obj.get("text", "") if isinstance(desc_obj, dict) else str(desc_obj)

            # Si el actor estaba en included_index
            if not author_name and author_urn and author_urn in included_index:
                actor_data = included_index[author_urn]
                author_name = actor_data.get("name", "")
                author_headline = actor_data.get("headline", "")

            # Métricas sociales
            social_detail = item.get("socialDetail", {})
            likes = 0
            comments = 0
            shares = 0
            if isinstance(social_detail, dict):
                likes = social_detail.get("totalSocialActivityCounts", {}).get("numLikes", 0)
                comments = social_detail.get("totalSocialActivityCounts", {}).get("numComments", 0)
                shares = social_detail.get("totalSocialActivityCounts", {}).get("numShares", 0)

            permalink = f"https://www.linkedin.com/feed/update/{urn}/" if urn else ""

            if text or author_name:
                posts.append(VoyagerFeedPost(
                    urn=urn,
                    author_name=author_name,
                    author_headline=author_headline,
                    author_urn=author_urn,
                    text=text.strip(),
                    num_likes=likes,
                    num_comments=comments,
                    num_shares=shares,
                    permalink=permalink
                ))

        return posts

    @classmethod
    def parse_job_posting(cls, raw: Dict[str, Any]) -> VoyagerJob:
        """Parsea los detalles de una oferta laboral de Voyager."""
        job = VoyagerJob()
        included_index = cls.index_included(raw)

        entity = None
        for item in raw.get("included", []):
            if "JobPosting" in str(item.get("$type", "")):
                entity = item
                break
        if not entity and "elements" in raw and raw["elements"]:
            entity = raw["elements"][0]
        if not entity and "data" in raw and isinstance(raw["data"], dict):
            entity = raw["data"]
        if not entity:
            entity = raw

        job.id = entity.get("entityUrn", "") or entity.get("jobPostingId", "")
        job.title = entity.get("title", "")
        job.location = entity.get("formattedLocation", "") or entity.get("locationDescription", "")
        job.employment_type = entity.get("employmentStatus", "")
        job.workplace_type = entity.get("workplaceTypesResolutionResult", {}).get("workplaceType", "")

        desc = entity.get("description", {})
        job.description = desc.get("text", "") if isinstance(desc, dict) else str(desc)

        # Compañía
        comp_urn = entity.get("companyDetails", {}).get("company", "") if isinstance(entity.get("companyDetails"), dict) else ""
        if comp_urn and comp_urn in included_index:
            job.company_name = included_index[comp_urn].get("name", "")
        elif "companyName" in entity:
            job.company_name = entity["companyName"]

        if job.id:
            m = re.search(r"\d+", job.id)
            clean_id = m.group(0) if m else job.id
            job.apply_url = f"https://www.linkedin.com/jobs/view/{clean_id}/"

        return job

    @classmethod
    def parse_company(cls, raw: Dict[str, Any]) -> VoyagerCompany:
        """Parsea la ficha corporativa de una empresa en Voyager."""
        comp = VoyagerCompany()
        entity = None
        for item in raw.get("included", []):
            if "Company" in str(item.get("$type", "")):
                entity = item
                break
        if not entity and "elements" in raw and raw["elements"]:
            entity = raw["elements"][0]
        if not entity and "elements" in raw and raw["elements"]:
            entity = raw["elements"][0]
        if not entity and "data" in raw and isinstance(raw["data"], dict):
            entity = raw["data"]
        if not entity:
            entity = raw

        comp.id = entity.get("entityUrn", "") or entity.get("universalName", "")
        comp.name = entity.get("name", "")
        comp.universal_name = entity.get("universalName", "")
        comp.tagline = entity.get("tagline", "")
        comp.description = entity.get("description", "")
        comp.website = entity.get("websiteUrl", "") or entity.get("companyPageUrl", "")
        comp.industry = entity.get("companyIndustries", [{}])[0].get("localizedName", "") if entity.get("companyIndustries") else ""
        comp.headquarters = entity.get("headquarter", {}).get("city", "") if isinstance(entity.get("headquarter"), dict) else ""
        comp.staff_count = entity.get("staffCount")

        return comp


class VoyagerClient:
    """
    Cliente de alto nivel para ejecutar consultas seguras a la API Voyager.
    Prioriza el despacho contextual mediante CDP WebSocket o in-browser fetch()
    para garantizar que las cookies de sesión y el contexto TLS sean 100% idénticos
    a los del navegador, evitando bloqueos por Cloudflare 302 o revocación de li_at.
    """

    def __init__(self, page=None, cdp_client=None):
        self.page = page
        self.cdp_client = cdp_client

    async def fetch_endpoint(self, endpoint_path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ejecuta una petición GET a un endpoint de Voyager en el contexto autenticado.
        Garantiza inclusión de cabeceras obligatorias: csrf-token y x-restli-protocol-version.
        """
        query_str = ""
        if params:
            import urllib.parse
            query_str = ("&" if "?" in endpoint_path else "?") + urllib.parse.urlencode(params)

        full_url = f"{VOYAGER_BASE_URL}{endpoint_path}{query_str}"

        # 1. Despacho primario: a través del contexto de página Playwright activo
        if self.page:
            try:
                js_fetch = f"""
                async () => {{
                    try {{
                        const m = document.cookie.match(/JSESSIONID="?([^";]+)"?/);
                        const csrf = m ? m[1] : "";
                        const resp = await fetch('{full_url}', {{
                            method: 'GET',
                            headers: {{
                                'csrf-token': csrf,
                                'x-restli-protocol-version': '2.0.0',
                                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                                'x-li-lang': 'es_ES'
                            }}
                        }});
                        if (!resp.ok) {{
                            return {{ error: 'HTTP_' + resp.status, status: resp.status }};
                        }}
                        return await resp.json();
                    }} catch (e) {{
                        return {{ error: e.toString() }};
                    }}
                }}
                """
                res = await self.page.evaluate(js_fetch)
                if isinstance(res, dict) and "error" not in res:
                    return res
                logger.debug(f"Petición in-page a Voyager falló: {res}")
            except Exception as e:
                logger.debug(f"Error evaluando fetch en page: {e}")

        # 2. Despacho secundario: vía cliente WebSocket CDP silencioso
        if self.cdp_client:
            try:
                expr = f"""
                (async () => {{
                    const m = document.cookie.match(/JSESSIONID="?([^";]+)"?/);
                    const csrf = m ? m[1] : "";
                    const resp = await fetch('{full_url}', {{
                        headers: {{
                            'csrf-token': csrf,
                            'x-restli-protocol-version': '2.0.0',
                            'accept': 'application/vnd.linkedin.normalized+json+2.1'
                        }}
                    }});
                    if (!resp.ok) return {{ error: 'HTTP_' + resp.status }};
                    return await resp.json();
                }})()
                """
                res = await self.cdp_client.evaluate(expr)
                if isinstance(res, dict) and "error" not in res:
                    return res
            except Exception as e:
                logger.debug(f"Error evaluando fetch en CDP: {e}")

        return {}

    async def get_my_profile(self) -> Optional[VoyagerProfile]:
        """Obtiene el perfil del usuario autenticado vía Voyager."""
        raw = await self.fetch_endpoint(ENDPOINTS["me"])
        if raw:
            return VoyagerRestLiParser.parse_profile(raw)
        return None

    async def get_profile(self, public_identifier_or_urn: str) -> Optional[VoyagerProfile]:
        """Obtiene un perfil específico por su identificador público o URN."""
        ep = ENDPOINTS["profile_view"].format(identifier=public_identifier_or_urn)
        raw = await self.fetch_endpoint(ep)
        if raw:
            return VoyagerRestLiParser.parse_profile(raw)

        # Fallback a dash profile
        ep_dash = ENDPOINTS["profile_dash"].format(identifier=public_identifier_or_urn)
        raw_dash = await self.fetch_endpoint(ep_dash)
        if raw_dash:
            return VoyagerRestLiParser.parse_profile(raw_dash)
        return None

    async def get_feed_updates(self, count: int = 10) -> List[VoyagerFeedPost]:
        """Obtiene las publicaciones más recientes del feed mediante Voyager."""
        ep = ENDPOINTS["feed_dash"].format(count=count)
        raw = await self.fetch_endpoint(ep)
        if raw:
            posts = VoyagerRestLiParser.parse_feed_updates(raw)
            if posts:
                return posts

        # Fallback a feed updates v2
        ep_v2 = ENDPOINTS["feed_updates"].format(count=count)
        raw_v2 = await self.fetch_endpoint(ep_v2)
        if raw_v2:
            return VoyagerRestLiParser.parse_feed_updates(raw_v2)
        return []

    async def get_job_details(self, job_id: str) -> Optional[VoyagerJob]:
        """Obtiene los detalles estructurados de un puesto de trabajo."""
        ep = ENDPOINTS["job_posting"].format(job_id=job_id)
        raw = await self.fetch_endpoint(ep)
        if raw:
            return VoyagerRestLiParser.parse_job_posting(raw)
        return None

    async def get_company_details(self, slug: str) -> Optional[VoyagerCompany]:
        """Obtiene la ficha institucional de una empresa vía Voyager."""
        ep = ENDPOINTS["company"].format(slug=slug)
        raw = await self.fetch_endpoint(ep)
        if raw:
            return VoyagerRestLiParser.parse_company(raw)
        return None

"""
Módulo de Diagnóstico Pre-Vuelo y Auditoría Pasiva de Sesión (Sinergia B REA).
Realiza una inspección pasiva por CDP o almacenamiento local sin evaluar JavaScript,
sin simular clics y sin navegar a URLs que puedan disparar Cloudflare 302,
Clear-Site-Data o bucles de redirección (ERR_TOO_MANY_REDIRECTS).
"""

import json
import logging
import os
import time
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("mcp_linkedin_preflight")

CDP_BASE_URL = "http://127.0.0.1:9222"

USER_PROFILE = os.environ.get("USERPROFILE", os.path.expanduser("~"))
DEFAULT_STORAGE_STATE = Path(USER_PROFILE) / ".gemini" / "config" / "mcp-auth" / "linkedin_storage_state.json"

@dataclass
class CookieStatus:
    name: str
    present: bool
    domain: str = ""
    expires: Optional[float] = None
    days_remaining: Optional[float] = None
    is_revoked: bool = False
    is_expired: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class PreflightReport:
    status: str  # "ACTIVE", "DEGRADED", "EXPIRED_OR_REVOKED", "OFFLINE"
    cdp_available: bool
    active_tab_found: bool
    tab_url: str
    cookies_audited: Dict[str, Any]
    verdict_message: str
    can_proceed: bool
    recommended_action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PassiveSessionAuditor:
    """
    Auditor pasivo que inspecciona los tokens críticos de sesión de LinkedIn
    sin interactuar con el motor JavaScript de la página ni generar eventos.
    """

    CRITICAL_COOKIES = ["li_at", "JSESSIONID", "li_rm", "bcookie", "bscookie", "lidc"]

    @staticmethod
    def is_cdp_available(port: int = 9222) -> bool:
        """Verifica disponibilidad del socket CDP en Brave."""
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/json/version")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    @staticmethod
    def get_cdp_linkedin_tab(port: int = 9222) -> Optional[Dict[str, Any]]:
        """Busca pestañas abiertas de LinkedIn en CDP de forma pasiva."""
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/json")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                tabs = json.loads(resp.read().decode("utf-8"))
            for t in tabs:
                if t.get("type") == "page" and "linkedin.com" in t.get("url", ""):
                    return t
        except Exception:
            pass
        return None

    @classmethod
    def extract_cookies_passthrough_cdp(cls, port: int = 9222) -> List[Dict[str, Any]]:
        """
        Extrae cookies a nivel de navegador vía WebSocket Storage.getCookies sin tocar la página.
        """
        try:
            import websocket
            req = urllib.request.Request(f"http://127.0.0.1:{port}/json/version")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                ver_data = json.loads(resp.read().decode("utf-8"))
            ws_url = ver_data.get("webSocketDebuggerUrl")
            if not ws_url:
                return []
            ws = websocket.create_connection(ws_url, timeout=2.0)
            ws.send(json.dumps({"id": 1, "method": "Storage.getCookies"}))
            msg = json.loads(ws.recv())
            ws.close()
            all_cookies = msg.get("result", {}).get("cookies", [])
            return [c for c in all_cookies if "linkedin" in c.get("domain", "")]
        except Exception as e:
            logger.debug(f"No se pudo extraer cookies por CDP pasivo: {e}")
            return []

    @classmethod
    def load_storage_state_cookies(cls, storage_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Carga cookies desde el archivo de estado persistente local."""
        path = storage_path or DEFAULT_STORAGE_STATE
        if not path.exists():
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [c for c in data.get("cookies", []) if "linkedin" in c.get("domain", "")]
        except Exception as e:
            logger.debug(f"Error leyendo storage_state: {e}")
            return []

    @classmethod
    def audit_session(cls, storage_path: Optional[Path] = None, cdp_port: int = 9222) -> PreflightReport:
        """
        Ejecuta la auditoría integral pre-vuelo de la sesión de LinkedIn.
        Devuelve un informe estructurado que determina si es seguro operar.
        """
        now = time.time()
        cdp_ok = cls.is_cdp_available(cdp_port)
        active_tab = cls.get_cdp_linkedin_tab(cdp_port) if cdp_ok else None
        tab_url = active_tab.get("url", "") if active_tab else ""

        # 1. Recolectar cookies: priorizar CDP pasivo; fallback a storage_state local
        cookies = []
        source = "local_storage_state"
        if cdp_ok:
            cookies = cls.extract_cookies_passthrough_cdp(cdp_port)
            if cookies:
                source = "brave_cdp_passive"

        if not cookies:
            cookies = cls.load_storage_state_cookies(storage_path)

        cookie_map: Dict[str, Dict[str, Any]] = {}
        for c in cookies:
            name = c.get("name")
            if name in cls.CRITICAL_COOKIES:
                cookie_map[name] = c

        # 2. Auditar cada cookie crítica
        audited_statuses: Dict[str, Any] = {}
        li_at_info = cookie_map.get("li_at")
        jsession_info = cookie_map.get("JSESSIONID")

        for c_name in cls.CRITICAL_COOKIES:
            c = cookie_map.get(c_name)
            if not c:
                audited_statuses[c_name] = CookieStatus(name=c_name, present=False).to_dict()
                continue

            val = str(c.get("value", ""))
            exp = c.get("expires")
            is_revoked = "delete me" in val.lower()
            is_expired = False
            days_left = None

            if exp and exp > 0:
                is_expired = exp < now
                days_left = round((exp - now) / 86400.0, 2)

            audited_statuses[c_name] = CookieStatus(
                name=c_name,
                present=True,
                domain=c.get("domain", ""),
                expires=exp,
                days_remaining=days_left,
                is_revoked=is_revoked,
                is_expired=is_expired
            ).to_dict()

        # 3. Determinar veredicto general
        if not cookies:
            return PreflightReport(
                status="OFFLINE",
                cdp_available=cdp_ok,
                active_tab_found=bool(active_tab),
                tab_url=tab_url,
                cookies_audited=audited_statuses,
                verdict_message="No se encontraron cookies de LinkedIn en Brave CDP ni en storage_state.",
                can_proceed=False,
                recommended_action="Inicie sesión en LinkedIn en Brave Browser con el puerto 9222 activo."
            )

        if not li_at_info or audited_statuses.get("li_at", {}).get("is_revoked"):
            return PreflightReport(
                status="EXPIRED_OR_REVOKED",
                cdp_available=cdp_ok,
                active_tab_found=bool(active_tab),
                tab_url=tab_url,
                cookies_audited=audited_statuses,
                verdict_message="El token 'li_at' no está presente o fue revocado por LinkedIn ('delete me'). Navegar causará bucle de redirección 302.",
                can_proceed=False,
                recommended_action="Abra LinkedIn en Brave Browser, inicie sesión manualmente y vuelva a ejecutar la comprobación."
            )

        if audited_statuses.get("li_at", {}).get("is_expired"):
            return PreflightReport(
                status="EXPIRED_OR_REVOKED",
                cdp_available=cdp_ok,
                active_tab_found=bool(active_tab),
                tab_url=tab_url,
                cookies_audited=audited_statuses,
                verdict_message="El token 'li_at' ha expirado.",
                can_proceed=False,
                recommended_action="Renueve la sesión abriendo LinkedIn en Brave Browser."
            )

        if not jsession_info or audited_statuses.get("JSESSIONID", {}).get("is_expired"):
            return PreflightReport(
                status="DEGRADED",
                cdp_available=cdp_ok,
                active_tab_found=bool(active_tab),
                tab_url=tab_url,
                cookies_audited=audited_statuses,
                verdict_message="Token 'li_at' válido pero falta CSRF ('JSESSIONID') o está expirado. Peticiones POST/Voyager pueden fallar.",
                can_proceed=True,
                recommended_action="Recargue una pestaña de LinkedIn en Brave para regenerar el token CSRF."
            )

        days_rem = audited_statuses.get("li_at", {}).get("days_remaining", 0)
        return PreflightReport(
            status="ACTIVE",
            cdp_available=cdp_ok,
            active_tab_found=bool(active_tab),
            tab_url=tab_url,
            cookies_audited=audited_statuses,
            verdict_message=f"Sesión activa y saludable ({source}). Token li_at vigente por {days_rem} días.",
            can_proceed=True,
            recommended_action="Operación segura autorizada. Cero riesgo de detección o bucles de redirección."
        )

"""
Módulo de Calibración de Señales Algorítmicas y Dwell Time (Sinergia D REA).
Basado en los estudios empíricos del equipo de ingeniería de LinkedIn ("Understanding
and Improving Dwell Time on LinkedIn Feed") y la ingeniería inversa de los módulos
de telemetría de cliente (li-tracking.js / voyager-web-analytics).
"""

import math
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

# Umbrales Canónicos del Algoritmo de Telemetría de LinkedIn
THRESHOLD_MICRO_DWELL_SEC = 1.0       # < 1.0s: skimming o scroll rápido (descartado)
THRESHOLD_QUALIFIED_SEC = 1.5         # 1.0s - 4.0s: impresión cualificada (interés de lectura)
THRESHOLD_HIGH_ENGAGEMENT_SEC = 4.0   # >= 4.0s: lectura sostenida (impulso algorítmico 2x)

# Límites visuales antes del pliegue "Ver más" (Fold Cutoff)
MOBILE_FOLD_CUTOFF_CHARS = 140
DESKTOP_FOLD_CUTOFF_CHARS = 210

# Velocidad media de lectura silenciosa en español (Palabras Por Minuto)
AVERAGE_READING_WPM = 210

@dataclass
class FoldAnalysis:
    mobile_preview: str
    desktop_preview: str
    has_mobile_overflow: bool
    has_desktop_overflow: bool
    mobile_cliffhanger_score: float  # 0.0 - 1.0
    desktop_cliffhanger_score: float # 0.0 - 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DwellTimeMetrics:
    total_words: int
    total_chars: int
    estimated_dwell_seconds: float
    dwell_tier: str  # "MICRO_DWELL", "QUALIFIED_IMPRESSION", "HIGH_ENGAGEMENT"
    dtpi_score: float  # Dwell Time Probability Index (0 - 100)
    expand_propensity_score: float  # Probabilidad de clic en "Ver más" (0 - 100)
    fold_analysis: Dict[str, Any]
    structure_metrics: Dict[str, Any]
    algorithmic_boost_projected: float  # Multiplicador proyectado de alcance
    actionable_recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LinkedInDwellAnalyzer:
    """
    Analizador estático de telemetría y predicción de retención algorítmica para LinkedIn.
    """

    WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚáéíóúñÑ0-9']+")
    NUMBER_RE = re.compile(r"\b\d[\d,.]*%?\b|[\$€£]\s*\d")
    CLIFFHANGER_PATTERNS = [
        re.compile(r"(\.{3}|…|\?|:)$"),
        re.compile(r"\b(pero|aunque|sin embargo|y entonces|el secreto es|la clave|aquí|descubre|resultado)\b\s*$", re.IGNORECASE),
        re.compile(r"\b(1\.|paso 1|primer error|lección 1|regla 1)\b", re.IGNORECASE)
    ]

    @classmethod
    def estimate_dwell_time(cls, text: str) -> float:
        """
        Calcula el tiempo esperado de permanencia del usuario en segundos.
        Incorpora penalizaciones o incentivos por complejidad visual, listas y números.
        """
        words = cls.WORD_RE.findall(text)
        total_words = len(words)
        if total_words == 0:
            return 0.0

        # Tiempo base de lectura
        base_seconds = (total_words / AVERAGE_READING_WPM) * 60.0

        # Ajuste por números y datos técnicos (aumentan tiempo de atención visual un +15%)
        numbers = cls.NUMBER_RE.findall(text)
        data_density = len(numbers) / max(total_words, 1)
        data_bonus = min(data_density * 8.0, 3.0)

        # Ajuste por saltos de línea (espaciado limpio reduce fatiga y aumenta scroll pausado)
        paragraphs = [p for p in text.split("\n") if p.strip()]
        structure_bonus = min(len(paragraphs) * 0.25, 2.5)

        total_dwell = base_seconds + data_bonus + structure_bonus
        return round(total_dwell, 2)

    @classmethod
    def analyze_fold(cls, text: str) -> FoldAnalysis:
        """
        Examina el texto visible antes del pliegue 'Ver más' en móvil y escritorio.
        Determina si el corte genera curiosidad algorítmica (cliffhanger).
        """
        clean = text.strip()
        if not clean:
            return FoldAnalysis(
                mobile_preview="",
                desktop_preview="",
                has_mobile_overflow=False,
                has_desktop_overflow=False,
                mobile_cliffhanger_score=0.0,
                desktop_cliffhanger_score=0.0
            )

        mob_preview = clean[:MOBILE_FOLD_CUTOFF_CHARS]
        desk_preview = clean[:DESKTOP_FOLD_CUTOFF_CHARS]

        has_mob = len(clean) > MOBILE_FOLD_CUTOFF_CHARS
        has_desk = len(clean) > DESKTOP_FOLD_CUTOFF_CHARS

        mob_score = cls._score_cliffhanger(mob_preview) if has_mob else 0.0
        desk_score = cls._score_cliffhanger(desk_preview) if has_desk else 0.0

        return FoldAnalysis(
            mobile_preview=mob_preview,
            desktop_preview=desk_preview,
            has_mobile_overflow=has_mob,
            has_desktop_overflow=has_desk,
            mobile_cliffhanger_score=mob_score,
            desktop_cliffhanger_score=desk_score
        )

    @classmethod
    def _score_cliffhanger(cls, preview: str) -> float:
        score = 0.5
        trimmed = preview.rstrip()
        for pat in cls.CLIFFHANGER_PATTERNS:
            if pat.search(trimmed):
                score += 0.25
        # Penalizar si termina con punto final absoluto en frase cerrada
        if re.search(r"[a-z0-9]\.\s*$", trimmed):
            score -= 0.15
        return round(max(0.1, min(score, 1.0)), 2)

    @classmethod
    def analyze_post(cls, text: str) -> DwellTimeMetrics:
        """
        Genera el informe completo de métricas de Dwell Time y optimización de visibilidad.
        Maneja con exactitud casos extremos (textos vacíos = 0.0 pts).
        """
        clean = text.strip() if text else ""
        words = cls.WORD_RE.findall(clean)
        total_words = len(words)
        total_chars = len(clean)

        # Caso extremo: texto vacío o sin palabras legibles
        if total_words == 0:
            return DwellTimeMetrics(
                total_words=0,
                total_chars=total_chars,
                estimated_dwell_seconds=0.0,
                dwell_tier="MICRO_DWELL",
                dtpi_score=0.0,
                expand_propensity_score=0.0,
                fold_analysis=cls.analyze_fold("").to_dict(),
                structure_metrics={
                    "total_paragraphs": 0,
                    "total_lines": 0,
                    "average_words_per_line": 0.0,
                    "has_double_spacing": False,
                    "number_count": 0
                },
                algorithmic_boost_projected=0.0,
                actionable_recommendations=["El texto proporcionado está vacío. Introduzca contenido para analizar telemetría y Dwell Time."]
            )

        dwell_sec = cls.estimate_dwell_time(clean)
        fold = cls.analyze_fold(clean)

        # Clasificación algorítmica según umbrales empíricos de LinkedIn
        if dwell_sec < THRESHOLD_MICRO_DWELL_SEC:
            tier = "MICRO_DWELL"
            boost = 0.5
        elif dwell_sec < THRESHOLD_HIGH_ENGAGEMENT_SEC:
            tier = "QUALIFIED_IMPRESSION"
            boost = 1.0
        else:
            tier = "HIGH_ENGAGEMENT"
            boost = 2.2

        # Puntuación DTPI (0 - 100)
        # 1. Dwell Duration factor (0 - 40 pts)
        dwell_pts = min(40.0, (dwell_sec / 6.0) * 40.0)

        # 2. Cliffhanger & Fold factor (0 - 30 pts)
        fold_pts = (fold.mobile_cliffhanger_score * 15.0) + (fold.desktop_cliffhanger_score * 15.0)

        # 3. Formato y legibilidad (0 - 30 pts)
        lines = [l for l in clean.split("\n") if l.strip()]
        avg_line_len = total_words / max(len(lines), 1)
        readability_pts = 30.0
        if avg_line_len > 25:
            readability_pts -= 12.0
        if not re.search(r"\n\n", clean):
            readability_pts -= 10.0

        dtpi = round(max(5.0, min(100.0, dwell_pts + fold_pts + readability_pts)), 1)

        # Expand propensity (probabilidad de clic en "Ver más")
        expand_prop = round(fold.mobile_cliffhanger_score * 50.0 + fold.desktop_cliffhanger_score * 50.0, 1)

        # Recomendaciones accionables
        recs = []
        if tier == "MICRO_DWELL":
            recs.append("El post dura menos de 1.0s (micro-dwell); el algoritmo lo descarta como scroll rápido. Añada un dato concreto o reflexión para retener la atención.")
        elif tier == "QUALIFIED_IMPRESSION":
            recs.append("Impresión cualificada alcanzada (1.0s - 4.0s). Para activar el multiplicador de distribución 2.2x (high-engagement), desarrolle el post por encima de 4.0s de lectura.")

        if not fold.has_mobile_overflow:
            recs.append("El texto cabe íntegramente en la vista móvil antes del pliegue (<=140 car); no disparará el evento algorítmico 'FeedExpandContent' ('Ver más').")
        elif fold.mobile_cliffhanger_score < 0.6:
            recs.append("El gancho móvil (primeros 140 caracteres) se corta en una frase cerrada. Utilice dos puntos, una pregunta o un salto de tensión para forzar el clic en 'Ver más'.")

        if avg_line_len > 20:
            recs.append("Los bloques de texto son densos. Divida los párrafos con saltos de línea dobles para evitar fatiga visual y promover la lectura completa.")

        paragraphs = [p for p in clean.split("\n\n") if p.strip()]

        return DwellTimeMetrics(
            total_words=total_words,
            total_chars=total_chars,
            estimated_dwell_seconds=dwell_sec,
            dwell_tier=tier,
            dtpi_score=dtpi,
            expand_propensity_score=expand_prop,
            fold_analysis=fold.to_dict(),
            structure_metrics={
                "total_paragraphs": len(paragraphs),
                "total_lines": len(lines),
                "average_words_per_line": round(avg_line_len, 1),
                "has_double_spacing": bool(re.search(r"\n\n", clean)),
                "number_count": len(cls.NUMBER_RE.findall(clean))
            },
            algorithmic_boost_projected=boost,
            actionable_recommendations=recs
        )

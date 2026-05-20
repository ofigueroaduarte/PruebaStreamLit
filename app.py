"""
Simulador de Tiempos de Ciclo — Manufactura
============================================
Matriz 3 productos × 3 procesos.
Cada celda tiene su propia distribución de probabilidad (oculta al usuario).

ZONA DE DISEÑO — solo el ingeniero modifica este bloque.
"""

import streamlit as st
import numpy as np
from dataclasses import dataclass
from typing import Callable

# ══════════════════════════════════════════════════════════════════
#  DEFINICIÓN DE PRODUCTOS Y PROCESOS
# ══════════════════════════════════════════════════════════════════

PRODUCTOS = [
    {"id": "P1", "nombre": "Carcasa de Bomba",    "icono": "🔩"},
    {"id": "P2", "nombre": "Engranaje Helicoidal", "icono": "⚙️"},
    {"id": "P3", "nombre": "Soporte Estructural",  "icono": "🏗️"},
]

PROCESOS = [
    {"id": "fundicion", "nombre": "Fundición",           "icono": "🔥", "color": "#EF4444"},
    {"id": "soldadura", "nombre": "Soldadura",           "icono": "⚡", "color": "#F59E0B"},
    {"id": "acabado",   "nombre": "Acabado Superficial", "icono": "✨", "color": "#10B981"},
]

# ══════════════════════════════════════════════════════════════════
#  DISTRIBUCIONES POR CELDA  (producto × proceso)
#  Todas en segundos. rango_normal = (min_ok, max_ok).
#
#  Justificación de diseño:
#    Maquinado   → Normal    (CNC controlado, baja variabilidad)
#    Fundición   → LogNormal (cola larga por solidificación variable)
#    Acabado     → Weibull   (tiempo hasta alcanzar rugosidad objetivo)
# ══════════════════════════════════════════════════════════════════

@dataclass
class Celda:
    generador: Callable[[], float]
    rango_normal: tuple
    unidad: str = "s"
    decimales: int = 1


MATRIZ: dict[tuple, Celda] = {
    # ── CARCASA DE BOMBA ─────────────────────────────────────────
    ("P1", "fundicion"): Celda(
        generador=lambda: np.random.lognormal(mean=np.log(520), sigma=0.12),
        rango_normal=(420, 640),
    ),
    ("P1", "soldadura"): Celda(
        generador=lambda: np.random.normal(loc=185, scale=15),
        rango_normal=(150, 220),
    ),
    ("P1", "acabado"): Celda(
        generador=lambda: np.random.weibull(a=3.5) * 95,
        rango_normal=(55, 135),
    ),
    # ── ENGRANAJE HELICOIDAL ──────────────────────────────────────
    ("P2", "fundicion"): Celda(
        generador=lambda: np.random.lognormal(mean=np.log(390), sigma=0.10),
        rango_normal=(320, 470),
    ),
    ("P2", "soldadura"): Celda(
        generador=lambda: np.random.normal(loc=140, scale=12),
        rango_normal=(110, 170),
    ),
    ("P2", "acabado"): Celda(
        generador=lambda: np.random.weibull(a=2.8) * 130,
        rango_normal=(70, 185),
    ),
    # ── SOPORTE ESTRUCTURAL ───────────────────────────────────────
    ("P3", "fundicion"): Celda(
        generador=lambda: np.random.lognormal(mean=np.log(680), sigma=0.15),
        rango_normal=(530, 860),
    ),
    ("P3", "soldadura"): Celda(
        generador=lambda: np.random.normal(loc=260, scale=20),
        rango_normal=(215, 305),
    ),
    ("P3", "acabado"): Celda(
        generador=lambda: np.random.weibull(a=4.0) * 72,
        rango_normal=(45, 100),
    ),
}

DIST_NOMBRES = {
    "fundicion": "LogNormal",
    "soldadura": "Normal",
    "acabado":   "Weibull",
}

# ══════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Simulador de Tiempos · Manufactura",
    page_icon="🏭",
    layout="wide",
)

# ══════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; }
.stApp { background: #111318; color: #D1D5DB; }

.hdr {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.4rem 2rem 1rem 2rem;
    border-bottom: 1px solid #2D3140; margin-bottom: 1.8rem;
}
.hdr-left h1 {
    font-family: 'Rajdhani', sans-serif; font-weight: 700;
    font-size: 1.6rem; letter-spacing: 4px; color: #F59E0B;
    margin: 0; text-transform: uppercase;
}
.hdr-left p {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; color: #6B7280; margin: 0.2rem 0 0 0; letter-spacing: 2px;
}
.hdr-badge {
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    background: #1C1F2E; border: 1px solid #2D3140;
    color: #9CA3AF; padding: 0.4rem 0.9rem; border-radius: 6px;
}

.proc-header {
    text-align: center; padding: 0.7rem 0.5rem;
    border-radius: 8px 8px 0 0; margin-bottom: -2px;
    font-weight: 700; font-size: 0.9rem; letter-spacing: 2px;
    text-transform: uppercase;
}

.prod-label {
    display: flex; flex-direction: column;
    justify-content: center; align-items: flex-start;
    padding: 0.6rem 0.8rem;
    background: #1C1F2E; border: 1px solid #2D3140;
    border-radius: 8px; height: 100%; min-height: 110px;
}
.prod-icono { font-size: 1.6rem; line-height: 1; }
.prod-nombre { font-weight: 700; font-size: 1rem; color: #E5E7EB; letter-spacing: 1px; margin-top: 0.3rem; line-height: 1.2; }
.prod-id { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #6B7280; margin-top: 0.2rem; }

.celda {
    background: #1C1F2E; border: 1px solid #2D3140;
    border-radius: 8px; padding: 1rem 0.8rem;
    text-align: center; min-height: 110px;
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    position: relative; overflow: hidden;
}
.celda::after {
    content: ''; position: absolute;
    bottom: 0; left: 0; right: 0; height: 3px; background: #2D3140;
}
.celda.ok::after     { background: #10B981; }
.celda.alerta::after { background: #EF4444; }

.celda-valor {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem; font-weight: 700; color: #6B7280;
}
.celda-valor.ok     { color: #34D399; }
.celda-valor.alerta { color: #F87171; }

.celda-unidad {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: #6B7280; margin-top: 0.25rem; letter-spacing: 1px;
}
.celda-dist { font-size: 0.6rem; color: #4B5563; margin-top: 0.4rem; font-family: 'JetBrains Mono', monospace; }

.dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-right: 4px; background: #374151; }
.dot.ok     { background: #34D399; box-shadow: 0 0 6px #34D399; }
.dot.alerta { background: #F87171; box-shadow: 0 0 6px #F87171; }

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #B45309 0%, #F59E0B 100%);
    color: #111318; border: none; border-radius: 8px;
    font-family: 'Rajdhani', sans-serif; font-weight: 700;
    font-size: 1rem; letter-spacing: 3px; padding: 0.65rem 2rem;
    width: 100%; text-transform: uppercase;
}
div[data-testid="stButton"] > button:hover { opacity: 0.85; }

.resumen-card {
    background: #1C1F2E; border: 1px solid #2D3140;
    border-radius: 8px; padding: 0.8rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; color: #9CA3AF; margin-top: 1rem;
}
.resumen-card b { color: #F59E0B; }

.leyenda {
    display: flex; gap: 1.5rem; font-size: 0.75rem; color: #6B7280;
    font-family: 'JetBrains Mono', monospace; justify-content: center;
    margin-top: 1.2rem; padding-top: 1rem; border-top: 1px solid #2D3140;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  ESTADO DE SESIÓN
# ══════════════════════════════════════════════════════════════════

if "resultados" not in st.session_state:
    st.session_state.resultados = {}
if "n" not in st.session_state:
    st.session_state.n = 0

# ══════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════

badge_txt = f"SIM #{st.session_state.n:04d}" if st.session_state.n > 0 else "ESPERANDO"

st.markdown(f"""
<div class="hdr">
  <div class="hdr-left">
    <h1>⬡ Simulador de Tiempos de Ciclo</h1>
    <p>Manufactura · Matriz Producto × Proceso · Modo estocástico</p>
  </div>
  <div class="hdr-badge">{badge_txt}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  BOTÓN
# ══════════════════════════════════════════════════════════════════

col_btn, _ = st.columns([2, 3])
with col_btn:
    if st.button("▶  GENERAR MUESTRA"):
        for p in PRODUCTOS:
            for pr in PROCESOS:
                key = (p["id"], pr["id"])
                st.session_state.resultados[key] = MATRIZ[key].generador()
        st.session_state.n += 1
        st.rerun()

# ══════════════════════════════════════════════════════════════════
#  ENCABEZADOS DE PROCESO
# ══════════════════════════════════════════════════════════════════

col_lbl, col_m, col_f, col_a = st.columns([1.6, 1, 1, 1])
with col_lbl:
    st.markdown("<div style='height:52px'></div>", unsafe_allow_html=True)

for col_ui, proc in zip([col_m, col_f, col_a], PROCESOS):
    with col_ui:
        st.markdown(f"""
        <div class="proc-header" style="background:{proc['color']}18;
             border:1px solid {proc['color']}55; color:{proc['color']};">
            {proc['icono']} {proc['nombre']}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  FILAS DE PRODUCTOS
# ══════════════════════════════════════════════════════════════════

resultados = st.session_state.resultados
total_ok = total_alerta = 0

for prod in PRODUCTOS:
    col_lbl, col_m, col_f, col_a = st.columns([1.6, 1, 1, 1])

    with col_lbl:
        st.markdown(f"""
        <div class="prod-label">
            <div class="prod-icono">{prod['icono']}</div>
            <div class="prod-nombre">{prod['nombre']}</div>
            <div class="prod-id">{prod['id']}</div>
        </div>
        """, unsafe_allow_html=True)

    for col_ui, proc in zip([col_m, col_f, col_a], PROCESOS):
        key = (prod["id"], proc["id"])
        celda = MATRIZ[key]
        valor = resultados.get(key)

        if valor is None:
            estado = "idle"
            valor_str = "—"
        else:
            dentro = celda.rango_normal[0] <= valor <= celda.rango_normal[1]
            estado = "ok" if dentro else "alerta"
            valor_str = f"{valor:.{celda.decimales}f}"
            total_ok    += 1 if estado == "ok"    else 0
            total_alerta += 1 if estado == "alerta" else 0

        with col_ui:
            st.markdown(f"""
            <div class="celda {estado}">
                <div class="celda-valor {estado}">{valor_str}</div>
                <div class="celda-unidad">
                    <span class="dot {estado}"></span>{celda.unidad}
                </div>
                <div class="celda-dist">{DIST_NOMBRES[proc['id']]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  RESUMEN + LEYENDA
# ══════════════════════════════════════════════════════════════════

if st.session_state.n > 0:
    total = total_ok + total_alerta
    pct_ok = (total_ok / total * 100) if total else 0
    st.markdown(f"""
    <div class="resumen-card">
        Muestra <b>#{st.session_state.n:04d}</b> &nbsp;·&nbsp;
        Celdas en rango: <b style="color:#34D399">{total_ok}/9</b> &nbsp;·&nbsp;
        Fuera de rango: <b style="color:#F87171">{total_alerta}/9</b> &nbsp;·&nbsp;
        Cumplimiento: <b style="color:#F59E0B">{pct_ok:.0f}%</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="leyenda">
    <span><span class="dot ok" style="display:inline-block"></span> Dentro de rango normal</span>
    <span><span class="dot alerta" style="display:inline-block"></span> Fuera de rango normal</span>
    <span>Tiempos en segundos</span>
</div>
""", unsafe_allow_html=True)

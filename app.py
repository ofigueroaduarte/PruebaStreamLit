"""
Simulador de Variables de Proceso Industrial
=============================================
Cada variable tiene una distribución de probabilidad configurada por diseño.
El usuario final solo ve los valores generados al presionar el botón.
"""

import streamlit as st
import numpy as np
from dataclasses import dataclass
from typing import Callable


# ══════════════════════════════════════════════════════════════════
#  ZONA DE DISEÑO — Aquí se configuran las distribuciones.
#  El usuario final NUNCA ve este bloque.
# ══════════════════════════════════════════════════════════════════

@dataclass
class Variable:
    nombre: str
    unidad: str
    descripcion: str
    icono: str
    generador: Callable[[], float]
    decimales: int
    rango_normal: tuple   # (min, max) para colorear el valor


VARIABLES: list[Variable] = [
    Variable(
        nombre="Temperatura de Horno",
        unidad="°C",
        descripcion="Temperatura interior del horno de fusión",
        icono="🌡️",
        generador=lambda: np.random.normal(loc=850.0, scale=12.5),
        decimales=1,
        rango_normal=(820, 880),
    ),
    Variable(
        nombre="Presión de Línea",
        unidad="bar",
        descripcion="Presión en la línea de vapor principal",
        icono="⚙️",
        generador=lambda: np.random.lognormal(mean=np.log(6.5), sigma=0.08),
        decimales=2,
        rango_normal=(5.8, 7.2),
    ),
    Variable(
        nombre="Velocidad de Banda",
        unidad="m/min",
        descripcion="Velocidad de la banda transportadora",
        icono="🏭",
        generador=lambda: np.random.uniform(low=12.0, high=18.0),
        decimales=2,
        rango_normal=(13.0, 17.0),
    ),
    Variable(
        nombre="Humedad Relativa",
        unidad="%",
        descripcion="Humedad en cámara de secado",
        icono="💧",
        generador=lambda: np.clip(np.random.beta(a=2.5, b=4.0) * 100, 20, 80),
        decimales=1,
        rango_normal=(30, 60),
    ),
    Variable(
        nombre="Tiempo de Ciclo",
        unidad="s",
        descripcion="Tiempo entre piezas (distribución Weibull)",
        icono="⏱️",
        generador=lambda: np.random.weibull(a=3.2) * 45,
        decimales=1,
        rango_normal=(30, 70),
    ),
    Variable(
        nombre="Defectos por Lote",
        unidad="unid",
        descripcion="Cantidad de piezas defectuosas (Poisson λ=2.3)",
        icono="🔍",
        generador=lambda: float(np.random.poisson(lam=2.3)),
        decimales=0,
        rango_normal=(0, 5),
    ),
]

# Etiquetas de distribución (visibles en la UI como referencia técnica)
DIST_LABELS = {
    "Temperatura de Horno":  "Normal(μ=850, σ=12.5)",
    "Presión de Línea":      "LogNormal(μ=6.5, σ=0.08)",
    "Velocidad de Banda":    "Uniforme[12, 18]",
    "Humedad Relativa":      "Beta(α=2.5, β=4.0)×100",
    "Tiempo de Ciclo":       "Weibull(k=3.2, λ=45)",
    "Defectos por Lote":     "Poisson(λ=2.3)",
}


# ══════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Simulador de Proceso",
    page_icon="🏭",
    layout="centered",
)


# ══════════════════════════════════════════════════════════════════
#  CSS PERSONALIZADO
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Barlow', sans-serif; }

.stApp { background-color: #0d1117; color: #e6edf3; }

.sim-header {
    text-align: center; padding: 2rem 0 1rem 0;
    border-bottom: 1px solid #21262d; margin-bottom: 2rem;
}
.sim-header h1 {
    font-family: 'Share Tech Mono', monospace; font-size: 1.8rem;
    color: #58a6ff; letter-spacing: 3px; margin: 0;
}
.sim-header p {
    color: #8b949e; font-size: 0.85rem; margin-top: 0.4rem;
    letter-spacing: 1px; text-transform: uppercase;
}

.var-card {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 10px; padding: 1.1rem 1.3rem;
    margin-bottom: 1rem; position: relative; overflow: hidden;
}
.var-card::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0;
    width: 3px; background: #58a6ff; border-radius: 10px 0 0 10px;
}
.var-card.alerta::before { background: #f85149; }
.var-card.ok::before     { background: #3fb950; }

.var-top { display: flex; justify-content: space-between; align-items: flex-start; }
.var-nombre { font-weight: 700; font-size: 0.95rem; color: #e6edf3; }
.var-icono  { font-size: 1.4rem; }
.var-desc   { font-size: 0.75rem; color: #8b949e; margin-top: 0.2rem; }

.var-valor {
    font-family: 'Share Tech Mono', monospace; font-size: 2rem;
    font-weight: bold; margin-top: 0.6rem; color: #58a6ff;
}
.var-valor.ok     { color: #3fb950; }
.var-valor.alerta { color: #f85149; }
.var-unidad { font-size: 0.8rem; color: #8b949e; margin-left: 4px; }

.dist-badge {
    display: inline-block; font-size: 0.65rem;
    font-family: 'Share Tech Mono', monospace;
    background: #21262d; color: #8b949e; border-radius: 4px;
    padding: 2px 7px; margin-top: 0.4rem; letter-spacing: 0.5px;
}

div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
    color: white; border: none; border-radius: 8px;
    font-family: 'Share Tech Mono', monospace; font-size: 1rem;
    letter-spacing: 2px; padding: 0.7rem 2.5rem;
    width: 100%; text-transform: uppercase;
}
div[data-testid="stButton"] button:hover { opacity: 0.88; }

.muestra-badge {
    font-family: 'Share Tech Mono', monospace; font-size: 0.75rem;
    color: #8b949e; text-align: right; margin-bottom: 1rem;
}
.sim-footer {
    text-align: center; color: #30363d; font-size: 0.72rem;
    font-family: 'Share Tech Mono', monospace; margin-top: 2.5rem;
    padding-top: 1rem; border-top: 1px solid #21262d; letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  ESTADO DE SESIÓN
# ══════════════════════════════════════════════════════════════════

if "valores" not in st.session_state:
    st.session_state.valores = {v.nombre: None for v in VARIABLES}
if "n_muestras" not in st.session_state:
    st.session_state.n_muestras = 0


# ══════════════════════════════════════════════════════════════════
#  INTERFAZ
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="sim-header">
    <h1>⬡ SIMULADOR DE PROCESO</h1>
    <p>Sistema de monitoreo de variables industriales · Modo simulación</p>
</div>
""", unsafe_allow_html=True)

if st.button("▶  GENERAR NUEVA MUESTRA"):
    for v in VARIABLES:
        st.session_state.valores[v.nombre] = v.generador()
    st.session_state.n_muestras += 1

if st.session_state.n_muestras > 0:
    st.markdown(
        f'<div class="muestra-badge">Muestra #{st.session_state.n_muestras:04d}</div>',
        unsafe_allow_html=True,
    )

col_izq, col_der = st.columns(2)

for i, var in enumerate(VARIABLES):
    col = col_izq if i % 2 == 0 else col_der
    valor = st.session_state.valores[var.nombre]

    if valor is None:
        estado_card = estado_valor = ""
        valor_str = "—"
    else:
        dentro = var.rango_normal[0] <= valor <= var.rango_normal[1]
        estado_card = estado_valor = "ok" if dentro else "alerta"
        fmt = f".{var.decimales}f"
        valor_str = f"{valor:{fmt}}"

    col.markdown(f"""
    <div class="var-card {estado_card}">
        <div class="var-top">
            <div>
                <div class="var-nombre">{var.nombre}</div>
                <div class="var-desc">{var.descripcion}</div>
            </div>
            <div class="var-icono">{var.icono}</div>
        </div>
        <div class="var-valor {estado_valor}">
            {valor_str}<span class="var-unidad">{var.unidad}</span>
        </div>
        <div class="dist-badge">{DIST_LABELS[var.nombre]}</div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.n_muestras > 0:
    st.markdown("""
    <div style="display:flex;gap:1.2rem;font-size:0.75rem;color:#8b949e;
                margin-top:0.5rem;justify-content:center;">
        <span><span style="color:#3fb950">●</span> Dentro de rango normal</span>
        <span><span style="color:#f85149">●</span> Fuera de rango normal</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="sim-footer">
    DISTRIBUCIONES CONFIGURADAS POR DISEÑO · PARÁMETROS NO VISIBLES AL USUARIO FINAL
</div>
""", unsafe_allow_html=True)

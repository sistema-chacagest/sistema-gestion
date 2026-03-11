import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
from pathlib import Path

# ═══════════════════════════════════════════════════════════
#  DATABASE / PERSISTENCIA
# ═══════════════════════════════════════════════════════════
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "clientes":              DATA_DIR / "clientes.json",
    "proveedores":           DATA_DIR / "proveedores.json",
    "facturas_venta":        DATA_DIR / "facturas_venta.json",
    "facturas_compra":       DATA_DIR / "facturas_compra.json",
    "cobranzas":             DATA_DIR / "cobranzas.json",
    "pagos":                 DATA_DIR / "pagos.json",
    "movimientos_bancarios": DATA_DIR / "movimientos_bancarios.json",
    "cheques_cartera":       DATA_DIR / "cheques_cartera.json",
    "cheques_emitidos":      DATA_DIR / "cheques_emitidos.json",
}

def load_data(key):
    path = FILES[key]
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    save_data(key, [])
    return []

def save_data(key, data):
    with open(FILES[key], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def get_next_id(key):
    data = load_data(key)
    return max((item.get("id", 0) for item in data), default=0) + 1

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def date_str():
    return datetime.now().strftime("%Y-%m-%d")

CONDICIONES_IVA = ["Responsable Inscripto", "Monotributista", "Exento en IVA", "Consumidor Final"]
BANCOS = ["Galicia", "Provincia", "Santander", "Supervielle", "Nación", "Comafi", "Mercado Pago"]
ALICUOTAS_IVA = {"21%": 0.21, "10.5%": 0.105, "27%": 0.27, "Exento": 0.0}
CUENTAS_GASTOS = [
    "Sueldos y Jornales", "Alquileres", "Servicios (Luz/Gas/Agua)",
    "Telefonía e Internet", "Honorarios Profesionales", "Materiales y Suministros",
    "Mantenimiento y Reparaciones", "Publicidad y Marketing", "Seguros",
    "Fletes y Transporte", "Gastos Bancarios", "Impuestos y Tasas", "Otros Gastos",
]

# ═══════════════════════════════════════════════════════════
#  CONFIG STREAMLIT
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Gestión Empresarial",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>

/* ── RESET & BASE ── */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0a0f1e !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] > div:first-child { padding: 0; }

/* hide default sidebar elements */
[data-testid="stSidebar"] .stSelectbox,
[data-testid="stSidebar"] label { display: none !important; }

/* ── LOGO AREA ── */
.sidebar-logo {
    padding: 28px 22px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 8px;
}
.sidebar-logo .logo-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; margin-bottom: 12px;
    box-shadow: 0 4px 15px rgba(99,102,241,0.4);
}
.sidebar-logo h2 {
    color: #f8fafc !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    letter-spacing: 0.5px;
}
.sidebar-logo p {
    color: #64748b !important;
    font-size: 0.72rem !important;
    margin: 3px 0 0 !important;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

/* ── NAV SECTION LABEL ── */
.nav-label {
    color: #334155 !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 16px 22px 6px;
}

/* ── NAV BUTTONS ── */
.nav-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 11px 22px;
    margin: 2px 10px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.18s ease;
    text-decoration: none;
    border: 1px solid transparent;
}
.nav-btn:hover {
    background: rgba(255,255,255,0.06);
    border-color: rgba(255,255,255,0.08);
}
.nav-btn.active {
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.15));
    border-color: rgba(99,102,241,0.35);
    box-shadow: 0 2px 12px rgba(99,102,241,0.15);
}
.nav-btn .nav-icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
    background: rgba(255,255,255,0.05);
}
.nav-btn.active .nav-icon {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    box-shadow: 0 3px 10px rgba(99,102,241,0.4);
}
.nav-btn .nav-text {
    color: #94a3b8 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}
.nav-btn.active .nav-text {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
}
.nav-btn .nav-arrow {
    margin-left: auto;
    color: #334155;
    font-size: 0.75rem;
    opacity: 0;
    transition: opacity 0.15s;
}
.nav-btn.active .nav-arrow, .nav-btn:hover .nav-arrow { opacity: 1; color: #6366f1; }

/* ── SIDEBAR FOOTER ── */
.sidebar-footer {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 16px 22px;
    border-top: 1px solid rgba(255,255,255,0.06);
    background: #0a0f1e;
}
.sidebar-footer p {
    color: #334155 !important;
    font-size: 0.7rem !important;
    margin: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── TOP HEADER ── */
.top-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid #f1f5f9;
}
.top-header h1 {
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    margin: 0 !important;
    letter-spacing: -0.5px;
}
.top-header p {
    color: #64748b !important;
    font-size: 0.82rem !important;
    margin: 3px 0 0 !important;
}
.header-badge {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white !important;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ── SECTION HEADER ── */
.section-header {
    display: flex; align-items: center; gap: 10px;
    margin: 18px 0 12px;
    padding-bottom: 10px;
    border-bottom: 2px solid #f1f5f9;
}
.section-header .sh-icon {
    width: 30px; height: 30px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
}
.section-header h3 {
    margin: 0 !important;
    color: #0f172a !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
}

/* ── METRIC CARDS ── */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #f1f5f9;
    border-radius: 14px;
    padding: 16px 20px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s;
}
[data-testid="metric-container"]:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.08); }
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.78rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.5px; }
[data-testid="stMetricValue"] { color: #0f172a !important; font-size: 1.45rem !important; font-weight: 800 !important; }

/* ── BADGES ── */
.badge-success { background:#dcfce7;color:#15803d;padding:3px 11px;border-radius:20px;font-size:0.75rem;font-weight:600;border:1px solid #bbf7d0; }
.badge-warning { background:#fef9c3;color:#a16207;padding:3px 11px;border-radius:20px;font-size:0.75rem;font-weight:600;border:1px solid #fde68a; }
.badge-danger  { background:#fee2e2;color:#b91c1c;padding:3px 11px;border-radius:20px;font-size:0.75rem;font-weight:600;border:1px solid #fecaca; }
.badge-info    { background:#dbeafe;color:#1d4ed8;padding:3px 11px;border-radius:20px;font-size:0.75rem;font-weight:600;border:1px solid #bfdbfe; }
.badge-neutral { background:#f1f5f9;color:#475569;padding:3px 11px;border-radius:20px;font-size:0.75rem;font-weight:600;border:1px solid #e2e8f0; }
.badge-purple  { background:#ede9fe;color:#6d28d9;padding:3px 11px;border-radius:20px;font-size:0.75rem;font-weight:600;border:1px solid #ddd6fe; }

/* ── INFO BOXES ── */
.info-box    { background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:12px 16px;margin:8px 0;border-left:3px solid #3b82f6; }
.success-box { background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:12px 16px;margin:8px 0;border-left:3px solid #22c55e; }
.warning-box { background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:12px 16px;margin:8px 0;border-left:3px solid #f59e0b; }

/* ── FORMS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 9px !important;
    border: 1.5px solid #e2e8f0 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
.stSelectbox > div > div {
    border-radius: 9px !important;
    border: 1.5px solid #e2e8f0 !important;
}
label { color: #374151 !important; font-size: 0.82rem !important; font-weight: 600 !important; }

/* ── BUTTONS ── */
.stButton > button {
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.875rem !important;
    transition: all 0.18s ease !important;
    letter-spacing: 0.2px;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
}
.stButton > button[kind="secondary"] {
    border: 1.5px solid #e2e8f0 !important;
    color: #374151 !important;
    background: white !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #6366f1 !important;
    color: #6366f1 !important;
    background: #fafafe !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f8fafc;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
    border: 1px solid #f1f5f9;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    color: #64748b !important;
    padding: 8px 16px !important;
    font-family: 'Outfit', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #6366f1 !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08) !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #f1f5f9; }
.dataframe { font-family: 'Outfit', sans-serif !important; font-size: 0.83rem !important; }

/* ── MAIN BG ── */
.main { background: #fafbfd; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  SIDEBAR — NAVEGACIÓN ELEGANTE
# ═══════════════════════════════════════════════════════════
MENU_ITEMS = [
    ("🏠", "Inicio",    "Panel de Control"),
    ("💰", "Ventas",    "Clientes & Facturación"),
    ("🛒", "Compras",   "Proveedores & Gastos"),
    ("🏦", "Tesorería", "Pagos & Cobranzas"),
    ("🏧", "Bancos",    "Movimientos & Cheques"),
    ("📊", "Reportes",  "Balance & Análisis"),
]

if "modulo_activo" not in st.session_state:
    st.session_state.modulo_activo = "Inicio"

with st.sidebar:
    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">◆</div>
        <h2>GestorPRO</h2>
        <p>Sistema de Gestión</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-label">Navegación</div>', unsafe_allow_html=True)

    for icon, nombre, desc in MENU_ITEMS:
        activo = st.session_state.modulo_activo == nombre
        css = "nav-btn active" if activo else "nav-btn"
        st.markdown(f"""
        <div class="{css}">
            <div class="nav-icon">{icon}</div>
            <div>
                <div class="nav-text">{nombre}</div>
            </div>
            <div class="nav-arrow">›</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(nombre, key=f"nav_{nombre}", use_container_width=True,
                     help=desc, type="secondary"):
            st.session_state.modulo_activo = nombre
            st.rerun()

    st.markdown("""
    <div class="sidebar-footer">
        <p>v1.0 · 2025 · GestorPRO</p>
    </div>
    """, unsafe_allow_html=True)

modulo_raw = st.session_state.modulo_activo
modulo = f"🏠 {modulo_raw}" if modulo_raw == "Inicio" else \
         f"💰 {modulo_raw}" if modulo_raw == "Ventas" else \
         f"🛒 {modulo_raw}" if modulo_raw == "Compras" else \
         f"🏦 {modulo_raw}" if modulo_raw == "Tesorería" else \
         f"🏧 {modulo_raw}" if modulo_raw == "Bancos" else \
         f"📊 {modulo_raw}"

# ── TOP HEADER ──
HEADER_MAP = {
    "Inicio":    ("Panel de Control",  "Resumen ejecutivo del sistema"),
    "Ventas":    ("Ventas",            "Clientes, facturación y cuentas corrientes"),
    "Compras":   ("Compras",           "Proveedores, gastos y cuentas corrientes"),
    "Tesorería": ("Tesorería",         "Órdenes de pago, cobranzas y cheques"),
    "Bancos":    ("Bancos",            "Movimientos bancarios y conciliación"),
    "Reportes":  ("Reportes",          "Balance general y análisis financiero"),
}
h_titulo, h_sub = HEADER_MAP.get(modulo_raw, ("Sistema", ""))
st.markdown(f"""
<div class="top-header">
    <div>
        <h1>{h_titulo}</h1>
        <p>{h_sub}</p>
    </div>
    <span class="header-badge">◆ GestorPRO</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  HELPERS UI
# ═══════════════════════════════════════════════════════════
def card_cliente(c):
    badge_map = {"Responsable Inscripto":"badge-info","Monotributista":"badge-success",
                 "Exento en IVA":"badge-neutral","Consumidor Final":"badge-warning"}
    badge = badge_map.get(c["condicion_iva"], "badge-neutral")
    st.markdown(f"""
    <div style='background:white;border:1px solid #e8eaf6;border-radius:8px;padding:11px;margin:5px 0;box-shadow:0 1px 4px rgba(0,0,0,0.05)'>
        <div style='display:flex;justify-content:space-between;align-items:flex-start'>
            <div>
                <strong style='color:#1a237e'>{c['razon_social']}</strong>
                <br><small style='color:#666'>CUIT: {c['cuit']} · {c.get('email','-')}</small>
                <br><small style='color:#888'>{c.get('direccion','-')}</small>
            </div>
            <span class="{badge}">{c['condicion_iva']}</span>
        </div>
    </div>""", unsafe_allow_html=True)

def totales_box(neto, iva_label, iva_monto, total, color="#1a237e"):
    st.markdown(f"""
    <div style='background:#f8f9ff;border:1px solid #c5cae9;border-radius:10px;padding:16px;margin-top:8px'>
        <div style='display:flex;justify-content:space-between;margin-bottom:6px'><span>Neto:</span><strong>${neto:,.2f}</strong></div>
        <div style='display:flex;justify-content:space-between;margin-bottom:6px'><span>IVA ({iva_label}):</span><strong>${iva_monto:,.2f}</strong></div>
        <hr style='margin:7px 0;border-color:#e8eaf6'>
        <div style='display:flex;justify-content:space-between'>
            <span style='color:{color};font-weight:700;font-size:1.05rem'>TOTAL:</span>
            <strong style='color:{color};font-size:1.05rem'>${total:,.2f}</strong>
        </div>
    </div>""", unsafe_allow_html=True)

def mov_banco(banco, fecha, tipo, importe, descripcion, categoria):
    movs = load_data("movimientos_bancarios")
    movs.append({"id": get_next_id("movimientos_bancarios"), "banco": banco,
                 "fecha": fecha, "tipo": tipo, "importe": importe,
                 "descripcion": descripcion, "categoria": categoria, "fecha_carga": now_str()})
    save_data("movimientos_bancarios", movs)

# ═══════════════════════════════════════════════════════════
#  MÓDULO: INICIO
# ═══════════════════════════════════════════════════════════
def page_inicio():
    st.markdown("## 🏠 Panel de Control")
    clientes   = load_data("clientes")
    proveedores= load_data("proveedores")
    fv         = load_data("facturas_venta")
    fc         = load_data("facturas_compra")
    cheques    = load_data("cheques_cartera")

    por_cobrar = sum(f.get("saldo_pendiente",0) for f in fv  if f.get("saldo_pendiente",0)>0)
    por_pagar  = sum(f.get("saldo_pendiente",0) for f in fc  if f.get("saldo_pendiente",0)>0)
    en_cartera = sum(c.get("importe",0)         for c in cheques if c.get("estado")=="En Cartera")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("👥 Clientes",    len(clientes))
    c2.metric("🏪 Proveedores", len(proveedores))
    c3.metric("📥 A Cobrar",    f"${por_cobrar:,.0f}")
    c4.metric("📤 A Pagar",     f"${por_pagar:,.0f}")
    c5.metric("💳 Cheques",     f"${en_cartera:,.0f}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📊 Últimas Facturas Venta")
        for f in sorted(fv, key=lambda x: x.get("fecha",""), reverse=True)[:5]:
            est = f.get("estado","Pendiente")
            b   = "badge-success" if est in ("Pagada","Cobrada") else "badge-warning"
            st.markdown(f"""<div style='background:#f8f9ff;border:1px solid #e8eaf6;border-radius:8px;padding:9px;margin:5px 0;display:flex;justify-content:space-between;align-items:center'>
                <div><strong>{f.get('numero_comprobante','')}</strong> — {f.get('cliente_razon_social','')}
                <br><small style='color:#666'>{f.get('fecha','')} · ${f.get('total',0):,.2f}</small></div>
                <span class="{b}">{est}</span></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("### 📊 Últimas Facturas Compra")
        for f in sorted(fc, key=lambda x: x.get("fecha",""), reverse=True)[:5]:
            est = f.get("estado","Pendiente")
            b   = "badge-success" if est=="Pagada" else "badge-warning"
            st.markdown(f"""<div style='background:#f8f9ff;border:1px solid #e8eaf6;border-radius:8px;padding:9px;margin:5px 0;display:flex;justify-content:space-between;align-items:center'>
                <div><strong>{f.get('numero_comprobante','')}</strong> — {f.get('proveedor_razon_social','')}
                <br><small style='color:#666'>{f.get('fecha','')} · ${f.get('total_factura',0):,.2f}</small></div>
                <span class="{b}">{est}</span></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⏰ Cheques Emitidos Próximos a Vencer")
    hoy = date.today()
    for c in load_data("cheques_emitidos"):
        if c.get("estado")=="Pendiente" and c.get("fecha_vencimiento"):
            try:
                dias = (date.fromisoformat(c["fecha_vencimiento"]) - hoy).days
                if 0 <= dias <= 15:
                    st.warning(f"🔔 Cheque #{c.get('numero','')} · {c.get('banco','')} · ${c.get('importe',0):,.2f} · Vence en **{dias} días**")
            except: pass

# ═══════════════════════════════════════════════════════════
#  MÓDULO: VENTAS
# ═══════════════════════════════════════════════════════════
def page_ventas():
    st.markdown("## 💰 Módulo de Ventas")
    tabs = st.tabs(["👥 Clientes","🧾 Emisión de Factura","📋 Cuenta Corriente","📊 CC General"])
    with tabs[0]: ventas_clientes()
    with tabs[1]: ventas_facturacion()
    with tabs[2]: ventas_cc_individual()
    with tabs[3]: ventas_cc_general()

def ventas_clientes():
    st.markdown("### 👥 Gestión de Clientes")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header"><div class="sh-icon">➕ </div><h3>Nuevo Cliente</h3></div>', unsafe_allow_html=True)
        with st.form("form_cli", clear_on_submit=True):
            rs   = st.text_input("Razón Social *")
            cuit = st.text_input("CUIT *", placeholder="XX-XXXXXXXX-X")
            dir_ = st.text_input("Dirección")
            mail = st.text_input("Email")
            iva  = st.selectbox("Condición IVA *", CONDICIONES_IVA)
            tel  = st.text_input("Teléfono")
            if st.form_submit_button("💾 Guardar Cliente", use_container_width=True):
                if not rs or not cuit:
                    st.error("Razón Social y CUIT son obligatorios.")
                else:
                    clientes = load_data("clientes")
                    if any(c["cuit"]==cuit for c in clientes):
                        st.error("Ya existe un cliente con ese CUIT.")
                    else:
                        clientes.append({"id":get_next_id("clientes"),"razon_social":rs.upper(),
                            "cuit":cuit,"direccion":dir_,"email":mail,"condicion_iva":iva,
                            "telefono":tel,"fecha_alta":date_str()})
                        save_data("clientes", clientes)
                        st.success(f"✅ Cliente '{rs.upper()}' guardado.")
                        st.rerun()
    with col2:
        st.markdown('<div class="section-header"><div class="sh-icon">📋 </div><h3>Lista de Clientes</h3></div>', unsafe_allow_html=True)
        clientes = load_data("clientes")
        buscar = st.text_input("🔍 Buscar", key="buscar_cli")
        lista = [c for c in clientes if buscar.lower() in c["razon_social"].lower() or buscar in c["cuit"]] if buscar else clientes
        for c in lista:
            card_cliente(c)

def ventas_facturacion():
    st.markdown("### 🧾 Emisión de Factura")
    clientes = load_data("clientes")
    if not clientes:
        st.warning("⚠️ No hay clientes cargados."); return
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header"><div class="sh-icon">Da</div><h3>tos del Comprobante</h3></div>', unsafe_allow_html=True)
        opts = {f"{c['razon_social']} — {c['cuit']}": c for c in clientes}
        cli  = opts[st.selectbox("Cliente *", list(opts.keys()))]
        cond = cli["condicion_iva"]
        st.markdown(f'<div class="info-box"><b>Condición IVA:</b> {cond}<br><b>Dirección:</b> {cli.get("direccion","-")}<br><b>Email:</b> {cli.get("email","-")}</div>', unsafe_allow_html=True)
        tipo = st.selectbox("Tipo Comprobante",
            ["Factura A","Nota de Crédito A","Nota de Débito A"] if cond=="Responsable Inscripto"
            else ["Factura B","Nota de Crédito B","Nota de Débito B"])
        num  = st.text_input("N° Comprobante", value=f"0001-{get_next_id('facturas_venta'):08d}")
        fech = st.date_input("Fecha", value=date.today())
        fvto = st.date_input("Fecha Vencimiento")
        conc = st.text_area("Concepto")
    with col2:
        st.markdown('<div class="section-header"><div class="sh-icon">Im</div><h3>portes</h3></div>', unsafe_allow_html=True)
        ali_opts = ["21%","10.5%","27%","Exento"] if cond=="Responsable Inscripto" else ["Exento"]
        ali  = st.selectbox("Alícuota IVA", ali_opts)
        neto = st.number_input("Importe Neto ($)", min_value=0.0, step=0.01, format="%.2f")
        tasa = ALICUOTAS_IVA.get(ali, 0)
        iva_m= round(neto * tasa, 2)
        total= round(neto + iva_m, 2)
        totales_box(neto, ali, iva_m, total)
        pv   = st.text_input("Punto de Venta", value="0001")
        st.markdown('<div class="warning-box"><small>⚠️ <b>AFIP:</b> Registro contable interno. Para comprobantes electrónicos válidos, conectar certificado AFIP en Configuración.</small></div>', unsafe_allow_html=True)
        if st.button("🖨️ Emitir Factura", use_container_width=True, type="primary"):
            if neto <= 0:
                st.error("El neto debe ser mayor a 0.")
            else:
                fv = load_data("facturas_venta")
                fv.append({"id":get_next_id("facturas_venta"),"numero_comprobante":num,
                    "tipo_comprobante":tipo,"punto_venta":pv,"fecha":str(fech),"fecha_vencimiento":str(fvto),
                    "cliente_id":cli["id"],"cliente_razon_social":cli["razon_social"],"cliente_cuit":cli["cuit"],
                    "condicion_iva":cond,"concepto":conc,"alicuota":ali,"neto":neto,"iva":iva_m,
                    "total":total,"saldo_pendiente":total,"estado":"Pendiente","fecha_emision":now_str()})
                save_data("facturas_venta", fv)
                st.success(f"✅ Factura {num} emitida. Total: ${total:,.2f}")
                st.balloons()

def ventas_cc_individual():
    st.markdown("### 📋 Cuenta Corriente por Cliente")
    clientes = load_data("clientes")
    if not clientes: st.info("No hay clientes."); return
    opts = {f"{c['razon_social']} — {c['cuit']}": c for c in clientes}
    cli  = opts[st.selectbox("Cliente", list(opts.keys()), key="ccv_cli")]
    fv   = [f for f in load_data("facturas_venta") if f["cliente_id"]==cli["id"]]
    cob  = [c for c in load_data("cobranzas")       if c.get("cliente_id")==cli["id"]]
    movs = []
    for f in fv:  movs.append({"Fecha":f["fecha"],"Tipo":f["tipo_comprobante"],"Comprobante":f["numero_comprobante"],"Concepto":f.get("concepto","-"),"Debe":f["total"],"Haber":0,"Saldo":0})
    for c in cob: movs.append({"Fecha":c["fecha"],"Tipo":"Cobranza","Comprobante":c.get("referencia","-"),"Concepto":c.get("forma_pago","-"),"Debe":0,"Haber":c["importe"],"Saldo":0})
    movs.sort(key=lambda x: x["Fecha"])
    saldo=0
    for m in movs: saldo+=m["Debe"]-m["Haber"]; m["Saldo"]=saldo
    tf=sum(f["total"] for f in fv); tc=sum(c["importe"] for c in cob)
    c1,c2,c3=st.columns(3)
    c1.metric("Facturado",f"${tf:,.2f}"); c2.metric("Cobrado",f"${tc:,.2f}"); c3.metric("Saldo",f"${tf-tc:,.2f}")
    if movs:
        df=pd.DataFrame(movs)
        df["Debe"]=df["Debe"].apply(lambda x: f"${x:,.2f}" if x else "-")
        df["Haber"]=df["Haber"].apply(lambda x: f"${x:,.2f}" if x else "-")
        df["Saldo"]=df["Saldo"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else: st.info("Sin movimientos.")

def ventas_cc_general():
    st.markdown("### 📊 Cuentas Corrientes — Todos los Clientes")
    clientes=load_data("clientes"); fv=load_data("facturas_venta"); cob=load_data("cobranzas")
    rows=[]
    for c in clientes:
        tf=sum(f["total"] for f in fv if f["cliente_id"]==c["id"])
        tc=sum(co["importe"] for co in cob if co.get("cliente_id")==c["id"])
        s=tf-tc
        if s!=0: rows.append({"Cliente":c["razon_social"],"CUIT":c["cuit"],"Condición IVA":c["condicion_iva"],"Facturado":tf,"Cobrado":tc,"Saldo":s})
    if rows:
        df=pd.DataFrame(rows).sort_values("Saldo",ascending=False)
        st.metric("Total a Cobrar",f"${df['Saldo'].sum():,.2f}")
        dd=df.copy()
        for col in ["Facturado","Cobrado","Saldo"]: dd[col]=dd[col].apply(lambda x: f"${x:,.2f}")
        st.dataframe(dd, use_container_width=True, hide_index=True)
    else: st.success("✅ Todas las cuentas en cero.")

# ═══════════════════════════════════════════════════════════
#  MÓDULO: COMPRAS
# ═══════════════════════════════════════════════════════════
def page_compras():
    st.markdown("## 🛒 Módulo de Compras")
    tabs = st.tabs(["🏪 Proveedores","📄 Carga de Gastos","📋 Cuenta Corriente","📊 CC General"])
    with tabs[0]: compras_proveedores()
    with tabs[1]: compras_gastos()
    with tabs[2]: compras_cc_individual()
    with tabs[3]: compras_cc_general()

def compras_proveedores():
    st.markdown("### 🏪 Gestión de Proveedores")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header"><div class="sh-icon">➕ </div><h3>Nuevo Proveedor</h3></div>', unsafe_allow_html=True)
        with st.form("form_prov", clear_on_submit=True):
            rs   = st.text_input("Razón Social *")
            cuit = st.text_input("CUIT *")
            dir_ = st.text_input("Dirección")
            mail = st.text_input("Email")
            iva  = st.selectbox("Condición IVA *", CONDICIONES_IVA)
            tel  = st.text_input("Teléfono")
            cg   = st.selectbox("Cuenta de Gastos", CUENTAS_GASTOS)
            if st.form_submit_button("💾 Guardar Proveedor", use_container_width=True):
                if not rs or not cuit: st.error("Razón Social y CUIT son obligatorios.")
                else:
                    provs = load_data("proveedores")
                    if any(p["cuit"]==cuit for p in provs): st.error("CUIT ya existe.")
                    else:
                        provs.append({"id":get_next_id("proveedores"),"razon_social":rs.upper(),
                            "cuit":cuit,"direccion":dir_,"email":mail,"condicion_iva":iva,
                            "telefono":tel,"cuenta_gastos":cg,"fecha_alta":date_str()})
                        save_data("proveedores", provs)
                        st.success(f"✅ Proveedor '{rs.upper()}' guardado.")
                        st.rerun()
    with col2:
        st.markdown('<div class="section-header"><div class="sh-icon">📋 </div><h3>Lista de Proveedores</h3></div>', unsafe_allow_html=True)
        provs  = load_data("proveedores")
        buscar = st.text_input("🔍 Buscar", key="buscar_prov")
        lista  = [p for p in provs if buscar.lower() in p["razon_social"].lower() or buscar in p["cuit"]] if buscar else provs
        for p in lista:
            badge_map = {"Responsable Inscripto":"badge-info","Monotributista":"badge-success","Exento en IVA":"badge-neutral","Consumidor Final":"badge-warning"}
            b = badge_map.get(p["condicion_iva"],"badge-neutral")
            st.markdown(f"""<div style='background:white;border:1px solid #e8eaf6;border-radius:8px;padding:11px;margin:5px 0'>
                <div style='display:flex;justify-content:space-between'>
                    <div><strong style='color:#1a237e'>{p['razon_social']}</strong>
                    <br><small style='color:#666'>CUIT: {p['cuit']} · {p.get('email','-')}</small>
                    <br><small style='color:#888'>Cuenta: {p.get('cuenta_gastos','-')}</small></div>
                    <span class="{b}">{p['condicion_iva']}</span>
                </div></div>""", unsafe_allow_html=True)

def compras_gastos():
    st.markdown("### 📄 Carga de Factura de Compra")
    provs = load_data("proveedores")
    if not provs: st.warning("No hay proveedores."); return
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header"><div class="sh-icon">Da</div><h3>tos del Comprobante</h3></div>', unsafe_allow_html=True)
        opts = {f"{p['razon_social']} — {p['cuit']}": p for p in provs}
        prov = opts[st.selectbox("Proveedor *", list(opts.keys()))]
        cond = prov["condicion_iva"]
        tipo = st.selectbox("Tipo Comprobante", ["Factura A","Factura B","Factura C","Ticket","Recibo"])
        num  = st.text_input("N° Comprobante *")
        fech = st.date_input("Fecha Comprobante", value=date.today())
        fvto = st.date_input("Fecha Vencimiento Pago")
        cg   = st.selectbox("Cuenta de Gastos", CUENTAS_GASTOS,
                   index=CUENTAS_GASTOS.index(prov.get("cuenta_gastos",CUENTAS_GASTOS[0]))
                   if prov.get("cuenta_gastos") in CUENTAS_GASTOS else 0)
        conc = st.text_area("Concepto")
    with col2:
        st.markdown('<div class="section-header"><div class="sh-icon">Im</div><h3>portes</h3></div>', unsafe_allow_html=True)
        es_exento = cond in ["Monotributista","Consumidor Final"]
        if es_exento:
            st.info("Proveedor Monotributista/CF → importe cargado como Exento.")
            neto_ex = st.number_input("Importe Total ($)", min_value=0.0, step=0.01, format="%.2f")
            n21=n105=n27=iva21=iva105=iva27=0.0
        else:
            n21  = st.number_input("Neto gravado 21% ($)",  min_value=0.0, step=0.01, format="%.2f")
            n105 = st.number_input("Neto gravado 10.5% ($)",min_value=0.0, step=0.01, format="%.2f")
            n27  = st.number_input("Neto gravado 27% ($)",  min_value=0.0, step=0.01, format="%.2f")
            neto_ex = st.number_input("Importe Exento ($)", min_value=0.0, step=0.01, format="%.2f")
            iva21=round(n21*0.21,2); iva105=round(n105*0.105,2); iva27=round(n27*0.27,2)
        tneto = n21+n105+n27+neto_ex
        tiva  = iva21+iva105+iva27
        tfact = tneto+tiva
        st.markdown("**Retenciones**")
        ret_iva  = st.number_input("Retención IVA ($)",             min_value=0.0, step=0.01, format="%.2f")
        ret_iibb = st.number_input("Retención IIBB ($)",            min_value=0.0, step=0.01, format="%.2f")
        ret_ii   = st.number_input("Ret. Impuestos Internos ($)",   min_value=0.0, step=0.01, format="%.2f")
        tret = ret_iva+ret_iibb+ret_ii
        tapag= tfact-tret
        st.markdown(f"""<div style='background:#f8f9ff;border:1px solid #c5cae9;border-radius:10px;padding:14px;margin-top:8px'>
            <div style='display:flex;justify-content:space-between;margin-bottom:5px'><span>Neto:</span><strong>${tneto:,.2f}</strong></div>
            <div style='display:flex;justify-content:space-between;margin-bottom:5px'><span>IVA:</span><strong>${tiva:,.2f}</strong></div>
            <div style='display:flex;justify-content:space-between;margin-bottom:5px'><span>Total Factura:</span><strong>${tfact:,.2f}</strong></div>
            <div style='display:flex;justify-content:space-between;margin-bottom:5px;color:#c62828'><span>(-) Retenciones:</span><strong>-${tret:,.2f}</strong></div>
            <hr style='margin:7px 0;border-color:#e8eaf6'>
            <div style='display:flex;justify-content:space-between'><span style='color:#1a237e;font-weight:700'>A PAGAR:</span><strong style='color:#1a237e;font-size:1.05rem'>${tapag:,.2f}</strong></div>
        </div>""", unsafe_allow_html=True)
        if st.button("💾 Registrar Factura", use_container_width=True, type="primary"):
            if not num or tfact<=0: st.error("Complete datos obligatorios e importe.")
            else:
                fc = load_data("facturas_compra")
                fc.append({"id":get_next_id("facturas_compra"),"proveedor_id":prov["id"],
                    "proveedor_razon_social":prov["razon_social"],"proveedor_cuit":prov["cuit"],
                    "condicion_iva":cond,"tipo_comprobante":tipo,"numero_comprobante":num,
                    "fecha":str(fech),"fecha_vencimiento":str(fvto),"cuenta_gastos":cg,"concepto":conc,
                    "neto_21":n21,"iva_21":iva21,"neto_105":n105,"iva_105":iva105,
                    "neto_27":n27,"iva_27":iva27,"neto_exento":neto_ex,
                    "total_neto":tneto,"total_iva":tiva,"total_factura":tfact,
                    "ret_iva":ret_iva,"ret_iibb":ret_iibb,"ret_imp_int":ret_ii,
                    "total_retenciones":tret,"total_a_pagar":tapag,
                    "saldo_pendiente":tapag,"estado":"Pendiente","fecha_carga":now_str()})
                save_data("facturas_compra", fc)
                st.success(f"✅ Factura {num} registrada. A pagar: ${tapag:,.2f}")
                st.rerun()

def compras_cc_individual():
    st.markdown("### 📋 Cuenta Corriente por Proveedor")
    provs = load_data("proveedores")
    if not provs: st.info("No hay proveedores."); return
    opts  = {f"{p['razon_social']} — {p['cuit']}": p for p in provs}
    prov  = opts[st.selectbox("Proveedor", list(opts.keys()), key="ccp_prov")]
    fc    = [f for f in load_data("facturas_compra") if f["proveedor_id"]==prov["id"]]
    pags  = [p for p in load_data("pagos")           if p.get("proveedor_id")==prov["id"]]
    movs  = []
    for f in fc:   movs.append({"Fecha":f["fecha"],"Tipo":f["tipo_comprobante"],"Comprobante":f["numero_comprobante"],"Concepto":f.get("concepto","-"),"Debe":f["total_a_pagar"],"Haber":0,"Saldo":0})
    for p in pags: movs.append({"Fecha":p["fecha"],"Tipo":"Pago","Comprobante":p.get("referencia","-"),"Concepto":p.get("forma_pago","-"),"Debe":0,"Haber":p["importe"],"Saldo":0})
    movs.sort(key=lambda x: x["Fecha"])
    saldo=0
    for m in movs: saldo+=m["Debe"]-m["Haber"]; m["Saldo"]=saldo
    tf=sum(f["total_a_pagar"] for f in fc); tp=sum(p["importe"] for p in pags)
    c1,c2,c3=st.columns(3)
    c1.metric("Facturado",f"${tf:,.2f}"); c2.metric("Pagado",f"${tp:,.2f}"); c3.metric("Saldo",f"${tf-tp:,.2f}")
    if movs:
        df=pd.DataFrame(movs)
        df["Debe"]=df["Debe"].apply(lambda x: f"${x:,.2f}" if x else "-")
        df["Haber"]=df["Haber"].apply(lambda x: f"${x:,.2f}" if x else "-")
        df["Saldo"]=df["Saldo"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else: st.info("Sin movimientos.")

def compras_cc_general():
    st.markdown("### 📊 Cuentas Corrientes — Todos los Proveedores")
    provs=load_data("proveedores"); fc=load_data("facturas_compra"); pags=load_data("pagos")
    rows=[]
    for p in provs:
        tf=sum(f["total_a_pagar"] for f in fc  if f["proveedor_id"]==p["id"])
        tp=sum(pa["importe"]      for pa in pags if pa.get("proveedor_id")==p["id"])
        s=tf-tp
        if s!=0: rows.append({"Proveedor":p["razon_social"],"CUIT":p["cuit"],"Condición IVA":p["condicion_iva"],"Cuenta Gastos":p.get("cuenta_gastos","-"),"Facturado":tf,"Pagado":tp,"Saldo":s})
    if rows:
        df=pd.DataFrame(rows).sort_values("Saldo",ascending=False)
        st.metric("Total a Pagar",f"${df['Saldo'].sum():,.2f}")
        dd=df.copy()
        for col in ["Facturado","Pagado","Saldo"]: dd[col]=dd[col].apply(lambda x: f"${x:,.2f}")
        st.dataframe(dd, use_container_width=True, hide_index=True)
    else: st.success("✅ Todas las cuentas en cero.")

# ═══════════════════════════════════════════════════════════
#  MÓDULO: TESORERÍA
# ═══════════════════════════════════════════════════════════
def page_tesoreria():
    st.markdown("## 🏦 Módulo de Tesorería")
    tabs = st.tabs(["💸 Órdenes de Pago","📥 Cobranzas","💳 Cheques en Cartera"])
    with tabs[0]: tesoreria_pagos()
    with tabs[1]: tesoreria_cobranzas()
    with tabs[2]: tesoreria_cheques_cartera()

def tesoreria_pagos():
    st.markdown("### 💸 Orden de Pago a Proveedor")
    provs = load_data("proveedores")
    if not provs: st.warning("No hay proveedores."); return
    opts = {f"{p['razon_social']} — {p['cuit']}": p for p in provs}
    prov = opts[st.selectbox("Proveedor", list(opts.keys()), key="tp_prov")]
    pend = [f for f in load_data("facturas_compra") if f["proveedor_id"]==prov["id"] and f.get("saldo_pendiente",0)>0]
    if not pend: st.info("✅ Sin facturas pendientes."); return
    opts_f = {f"{f['tipo_comprobante']} {f['numero_comprobante']} — ${f['saldo_pendiente']:,.2f} — {f['fecha']}": f for f in pend}
    sel_f  = st.multiselect("Facturas a cancelar", list(opts_f.keys()))
    total  = sum(opts_f[k]["saldo_pendiente"] for k in sel_f)
    if sel_f: st.markdown(f"**Total a pagar:** <span style='color:#1a237e;font-size:1.1rem;font-weight:700'>${total:,.2f}</span>", unsafe_allow_html=True)
    forma  = st.selectbox("Forma de Pago", ["Transferencia Bancaria","Efectivo","Cheque Propio","Cheque de Tercero"])
    fech   = st.date_input("Fecha de Pago", value=date.today())
    ref    = st.text_input("N° Referencia")
    banco  = st.selectbox("Banco", BANCOS) if forma=="Transferencia Bancaria" else None
    obs    = st.text_area("Observaciones", height=70)

    if forma=="Cheque de Tercero":
        ch_cart = [c for c in load_data("cheques_cartera") if c.get("estado")=="En Cartera"]
        if not ch_cart: st.warning("No hay cheques en cartera.")
        else:
            opts_ch = {f"Cheque #{c['numero']} — {c['banco']} — ${c['importe']:,.2f} — Vto:{c['fecha_vencimiento']}": c for c in ch_cart}
            ch_sel_k = st.selectbox("Seleccionar cheque", list(opts_ch.keys()))
            ch_sel   = opts_ch[ch_sel_k]
    else:
        ch_sel = None

    if forma=="Cheque Propio":
        st.markdown("**Datos del Cheque a Emitir**")
        c1,c2=st.columns(2)
        with c1:
            ch_banco=st.selectbox("Banco",BANCOS,key="chp_banco"); ch_num=st.text_input("N° Cheque",key="chp_num")
            ch_imp=st.number_input("Importe ($)",min_value=0.0,step=0.01,format="%.2f",value=float(total),key="chp_imp")
        with c2:
            ch_fem=st.date_input("Fecha Emisión",value=date.today(),key="chp_fem")
            ch_fvt=st.date_input("Fecha Vencimiento",key="chp_fvt")
            ch_ben=st.text_input("Beneficiario",value=prov["razon_social"],key="chp_ben")
        if st.button("📝 Emitir Cheque y Registrar Pago", use_container_width=True, type="primary"):
            ch_emitidos=load_data("cheques_emitidos")
            ch_emitidos.append({"id":get_next_id("cheques_emitidos"),"banco":ch_banco,"numero":ch_num,
                "importe":ch_imp,"fecha_emision":str(ch_fem),"fecha_vencimiento":str(ch_fvt),
                "beneficiario":ch_ben,"estado":"Pendiente","fecha_carga":now_str()})
            save_data("cheques_emitidos",ch_emitidos)
            _do_pago(prov,sel_f,opts_f,total,forma,str(fech),ref,ch_banco,obs,f"Cheque {ch_num}")
        return

    if st.button("✅ Registrar Pago", type="primary", use_container_width=True, disabled=not sel_f):
        if ch_sel:
            ch_list=load_data("cheques_cartera")
            for c in ch_list:
                if c["id"]==ch_sel["id"]: c["estado"]="Entregado"; c["entregado_a"]=prov["razon_social"]; c["fecha_entrega"]=str(fech); break
            save_data("cheques_cartera",ch_list)
        _do_pago(prov,sel_f,opts_f,total,forma,str(fech),ref,banco,obs,"")

def _do_pago(prov,sel_f,opts_f,total,forma,fecha,ref,banco,obs,ch_ref):
    pags=load_data("pagos")
    pags.append({"id":get_next_id("pagos"),"proveedor_id":prov["id"],"proveedor_razon_social":prov["razon_social"],
        "facturas":sel_f,"importe":total,"forma_pago":forma,"banco":banco,"cheque_ref":ch_ref,
        "fecha":fecha,"referencia":ref,"observaciones":obs,"fecha_carga":now_str()})
    save_data("pagos",pags)
    fc=load_data("facturas_compra")
    for k in sel_f:
        fid=opts_f[k]["id"]
        for f in fc:
            if f["id"]==fid: f["saldo_pendiente"]=0; f["estado"]="Pagada"; break
    save_data("facturas_compra",fc)
    if banco: mov_banco(banco,fecha,"Egreso",total,f"Pago {prov['razon_social']} · {ref}",forma)
    st.success(f"✅ Pago registrado ${total:,.2f} a {prov['razon_social']}")
    st.rerun()

def tesoreria_cobranzas():
    st.markdown("### 📥 Cobranza de Facturas")
    clientes=load_data("clientes")
    if not clientes: st.warning("No hay clientes."); return
    opts={f"{c['razon_social']} — {c['cuit']}": c for c in clientes}
    cli=opts[st.selectbox("Cliente",list(opts.keys()),key="cob_cli")]
    pend=[f for f in load_data("facturas_venta") if f["cliente_id"]==cli["id"] and f.get("saldo_pendiente",0)>0]
    if not pend: st.info("✅ Sin facturas pendientes."); return
    opts_f={f"{f['tipo_comprobante']} {f['numero_comprobante']} — ${f['saldo_pendiente']:,.2f}": f for f in pend}
    sel_f=st.multiselect("Facturas a cobrar",list(opts_f.keys()))
    total=sum(opts_f[k]["saldo_pendiente"] for k in sel_f)
    if sel_f: st.markdown(f"**Total a cobrar:** <span style='color:#2e7d32;font-size:1.1rem;font-weight:700'>${total:,.2f}</span>", unsafe_allow_html=True)
    forma=st.selectbox("Forma de Cobro",["Transferencia Bancaria","Efectivo","Cheque de Tercero"])
    fecha=st.date_input("Fecha",value=date.today())
    ref=st.text_input("N° Referencia",key="cob_ref")
    banco=st.selectbox("Banco Destino",BANCOS) if forma=="Transferencia Bancaria" else None
    ch_data=None
    if forma=="Cheque de Tercero":
        c1,c2=st.columns(2)
        with c1:
            ch_banco=st.selectbox("Banco Librador",BANCOS,key="chcob_b"); ch_num=st.text_input("N° Cheque",key="chcob_n")
            ch_imp=st.number_input("Importe Cheque ($)",min_value=0.0,step=0.01,format="%.2f",value=float(total),key="chcob_i")
        with c2:
            ch_lib=st.text_input("Librador",key="chcob_l"); ch_fem=st.date_input("Fecha Emisión",key="chcob_fe")
            ch_fvt=st.date_input("Fecha Vencimiento",key="chcob_fv")
        ch_data={"banco":ch_banco,"numero":ch_num,"importe":ch_imp,"librador":ch_lib,
                 "fecha_emision":str(ch_fem),"fecha_vencimiento":str(ch_fvt)}
    if st.button("✅ Registrar Cobranza",type="primary",use_container_width=True,disabled=not sel_f):
        if ch_data:
            chc=load_data("cheques_cartera")
            chc.append({"id":get_next_id("cheques_cartera"),**ch_data,
                "recibido_de":cli["razon_social"],"estado":"En Cartera","fecha_ingreso":str(fecha)})
            save_data("cheques_cartera",chc)
        cobs=load_data("cobranzas")
        cobs.append({"id":get_next_id("cobranzas"),"cliente_id":cli["id"],"cliente_razon_social":cli["razon_social"],
            "facturas":sel_f,"importe":total,"forma_pago":forma,"banco":banco,"fecha":str(fecha),"referencia":ref,"fecha_carga":now_str()})
        save_data("cobranzas",cobs)
        fv=load_data("facturas_venta")
        for k in sel_f:
            fid=opts_f[k]["id"]
            for f in fv:
                if f["id"]==fid: f["saldo_pendiente"]=0; f["estado"]="Cobrada"; break
        save_data("facturas_venta",fv)
        if banco: mov_banco(banco,str(fecha),"Ingreso",total,f"Cobranza {cli['razon_social']} · {ref}",forma)
        st.success(f"✅ Cobranza ${total:,.2f} registrada.")
        st.rerun()

def tesoreria_cheques_cartera():
    st.markdown("### 💳 Cheques en Cartera")
    cheques=[c for c in load_data("cheques_cartera") if c.get("estado")=="En Cartera"]
    if not cheques: st.info("No hay cheques en cartera."); return
    total=sum(c["importe"] for c in cheques)
    st.metric("Total en Cartera",f"${total:,.2f}",f"{len(cheques)} cheques")
    hoy=date.today()
    for c in sorted(cheques,key=lambda x: x.get("fecha_vencimiento","")):
        try:
            dias=(date.fromisoformat(c["fecha_vencimiento"])-hoy).days
            if dias<0: est=f"<span class='badge-danger'>Vencido {abs(dias)}d</span>"
            elif dias<=7: est=f"<span class='badge-warning'>Vence en {dias}d</span>"
            else: est=f"<span class='badge-success'>Vence en {dias}d</span>"
        except: est=""
        st.markdown(f"""<div style='background:white;border:1px solid #e8eaf6;border-radius:10px;padding:13px;margin:7px 0;box-shadow:0 2px 5px rgba(0,0,0,0.05)'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                <div><strong style='color:#1a237e'>Cheque #{c.get('numero','-')} — {c.get('banco','-')}</strong>
                <br><span style='color:#2e7d32;font-size:1.05rem;font-weight:700'>${c.get('importe',0):,.2f}</span>
                <br><small>Librador: {c.get('librador','-')} · De: {c.get('recibido_de','-')}</small>
                <br><small style='color:#666'>Emisión: {c.get('fecha_emision','-')} · Vto: {c.get('fecha_vencimiento','-')}</small></div>
                <div>{est}</div>
            </div></div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  MÓDULO: BANCOS
# ═══════════════════════════════════════════════════════════
def page_bancos():
    st.markdown("## 🏧 Módulo de Bancos")
    tabs=st.tabs(["🏦 Movimientos","💳 Cheques Cartera","📋 Cheques Diferidos"])
    with tabs[0]: bancos_movimientos()
    with tabs[1]: bancos_cheques_cartera()
    with tabs[2]: bancos_cheques_diferidos()

def bancos_movimientos():
    st.markdown("### 🏦 Movimientos Bancarios")
    c1,c2,c3=st.columns(3)
    banco_f=c1.selectbox("Banco",["Todos"]+BANCOS,key="mb_b")
    tipo_f =c2.selectbox("Tipo", ["Todos","Ingreso","Egreso"],key="mb_t")
    buscar =c3.text_input("🔍 Descripción",key="mb_s")
    # Saldos
    todos=load_data("movimientos_bancarios")
    cols=st.columns(len(BANCOS))
    for i,b in enumerate(BANCOS):
        ing=sum(m["importe"] for m in todos if m.get("banco")==b and m.get("tipo")=="Ingreso")
        egr=sum(m["importe"] for m in todos if m.get("banco")==b and m.get("tipo")=="Egreso")
        cols[i].metric(b,f"${ing-egr:,.0f}")
    st.markdown("---")
    with st.expander("➕ Registrar Movimiento Manual"):
        with st.form("form_mov",clear_on_submit=True):
            cc1,cc2=st.columns(2)
            with cc1: mb=st.selectbox("Banco",BANCOS); mt=st.selectbox("Tipo",["Ingreso","Egreso"]); mf=st.date_input("Fecha",value=date.today())
            with cc2: mi=st.number_input("Importe",min_value=0.0,step=0.01,format="%.2f"); mc=st.text_input("Categoría"); md=st.text_input("Descripción")
            if st.form_submit_button("💾 Guardar",use_container_width=True):
                mov_banco(mb,str(mf),mt,mi,md,mc); st.success("✅ Registrado."); st.rerun()
    movs=todos
    if banco_f!="Todos": movs=[m for m in movs if m.get("banco")==banco_f]
    if tipo_f !="Todos": movs=[m for m in movs if m.get("tipo")==tipo_f]
    if buscar:           movs=[m for m in movs if buscar.lower() in m.get("descripcion","").lower()]
    if movs:
        df=pd.DataFrame([{"Fecha":m.get("fecha"),"Banco":m.get("banco"),"Tipo":m.get("tipo"),
            "Importe":f"+${m['importe']:,.2f}" if m.get("tipo")=="Ingreso" else f"-${m['importe']:,.2f}",
            "Descripción":m.get("descripcion",""),"Categoría":m.get("categoria","")}
            for m in sorted(movs,key=lambda x:x.get("fecha",""),reverse=True)])
        st.dataframe(df,use_container_width=True,hide_index=True)
    else: st.info("Sin movimientos.")

def bancos_cheques_cartera():
    st.markdown("### 💳 Cheques de Terceros en Cartera")
    ch=load_data("cheques_cartera")
    fest=st.selectbox("Estado",["En Cartera","Entregado","Todos"],key="bch_est")
    if fest!="Todos": ch=[c for c in ch if c.get("estado")==fest]
    if not ch: st.info("Sin cheques."); return
    total=sum(c.get("importe",0) for c in ch if c.get("estado")=="En Cartera")
    st.metric("Total en Cartera",f"${total:,.2f}")
    hoy=date.today()
    rows=[]
    for c in sorted(ch,key=lambda x:x.get("fecha_vencimiento","")):
        try: dias=(date.fromisoformat(c["fecha_vencimiento"])-hoy).days; ds=f"{dias}d" if dias>=0 else f"Vencido {abs(dias)}d"
        except: ds="-"
        rows.append({"N° Cheque":c.get("numero","-"),"Banco":c.get("banco","-"),
            "Importe":f"${c.get('importe',0):,.2f}","Librador":c.get("librador","-"),
            "Recibido de":c.get("recibido_de","-"),"F. Emisión":c.get("fecha_emision","-"),
            "F. Vencimiento":c.get("fecha_vencimiento","-"),"Días":ds,"Estado":c.get("estado","-")})
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

def bancos_cheques_diferidos():
    st.markdown("### 📋 Cheques Diferidos Emitidos")
    ch=load_data("cheques_emitidos")
    fest=st.selectbox("Mostrar",["Pendientes","Conciliados","Todos"],key="bchd_est")
    if fest=="Pendientes":   ch=[c for c in ch if c.get("estado")=="Pendiente"]
    elif fest=="Conciliados":ch=[c for c in ch if c.get("estado")=="Conciliado"]
    if not ch: st.info("Sin cheques."); return
    tp=sum(c.get("importe",0) for c in load_data("cheques_emitidos") if c.get("estado")=="Pendiente")
    st.metric("Total Pendiente de Débito",f"${tp:,.2f}")
    hoy=date.today()
    for c in sorted(ch,key=lambda x:x.get("fecha_vencimiento","")):
        try:
            dias=(date.fromisoformat(c["fecha_vencimiento"])-hoy).days
            if c["estado"]=="Conciliado": badge="<span class='badge-success'>Conciliado ✓</span>"
            elif dias<0: badge=f"<span class='badge-danger'>Vencido {abs(dias)}d</span>"
            elif dias<=5: badge=f"<span class='badge-warning'>Vence en {dias}d</span>"
            else: badge=f"<span class='badge-info'>Vence en {dias}d</span>"
        except: badge=""
        col_i,col_b=st.columns([4,1])
        with col_i:
            st.markdown(f"""<div style='background:white;border:1px solid #e8eaf6;border-radius:10px;padding:13px;margin:6px 0;box-shadow:0 2px 5px rgba(0,0,0,0.05)'>
                <strong style='color:#1a237e'>Cheque #{c.get('numero','-')} — {c.get('banco','-')}</strong> &nbsp;{badge}
                <br><span style='color:#c62828;font-size:1.05rem;font-weight:700'>${c.get('importe',0):,.2f}</span>
                <br><small>Beneficiario: <strong>{c.get('beneficiario','-')}</strong></small>
                <br><small style='color:#666'>Emisión: {c.get('fecha_emision','-')} · Vto: {c.get('fecha_vencimiento','-')}</small>
            </div>""", unsafe_allow_html=True)
        if c.get("estado")=="Pendiente":
            with col_b:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ Conciliar",key=f"conc_{c['id']}"):
                    all_ch=load_data("cheques_emitidos")
                    for ch2 in all_ch:
                        if ch2["id"]==c["id"]: ch2["estado"]="Conciliado"; ch2["fecha_conciliacion"]=str(hoy); break
                    save_data("cheques_emitidos",all_ch)
                    mov_banco(c["banco"],str(hoy),"Egreso",c["importe"],f"Débito cheque #{c['numero']} a {c['beneficiario']}","Cheque Debitado")
                    st.success(f"Cheque #{c['numero']} conciliado.")
                    st.rerun()

# ═══════════════════════════════════════════════════════════
#  MÓDULO: REPORTES
# ═══════════════════════════════════════════════════════════
def page_reportes():
    st.markdown("## 📊 Reportes y Balance")
    tabs=st.tabs(["📈 Ingresos vs Egresos","💼 Por Cuenta de Gastos","🏦 Por Banco","📋 Balance General"])
    with tabs[0]: rep_ive()
    with tabs[1]: rep_cuentas()
    with tabs[2]: rep_bancos()
    with tabs[3]: rep_balance()

def _fechas(key):
    c1,c2=st.columns(2)
    d=c1.date_input("Desde",value=date(date.today().year,1,1),key=f"{key}_d")
    h=c2.date_input("Hasta",value=date.today(),key=f"{key}_h")
    return str(d),str(h)

def rep_ive():
    st.markdown("### 📈 Ingresos vs Egresos")
    d,h=_fechas("ive")
    fv=[f for f in load_data("facturas_venta")  if d<=f.get("fecha","")<=h]
    fc=[f for f in load_data("facturas_compra") if d<=f.get("fecha","")<=h]
    tv=sum(f.get("total",0)        for f in fv); iva_v=sum(f.get("iva",0)       for f in fv); nv=sum(f.get("neto",0) for f in fv)
    tc=sum(f.get("total_factura",0)for f in fc); iva_c=sum(f.get("total_iva",0) for f in fc); nc=sum(f.get("total_neto",0) for f in fc)
    c1,c2,c3=st.columns(3)
    c1.metric("💚 Ingresos",f"${tv:,.2f}",f"Neto ${nv:,.2f}")
    c2.metric("🔴 Egresos", f"${tc:,.2f}",f"Neto ${nc:,.2f}")
    c3.metric("💰 Resultado",f"${tv-tc:,.2f}")
    st.markdown("---")
    ca,cb=st.columns(2)
    with ca:
        st.markdown(f"""<div style='background:#e8f5e9;border-radius:10px;padding:16px'>
            <b>📥 Ventas</b><br>Neto: <b>${nv:,.2f}</b><br>IVA: <b>${iva_v:,.2f}</b><br>
            <hr style='border-color:#a5d6a7;margin:8px 0'>Total: <b style='color:#2e7d32;font-size:1.1rem'>${tv:,.2f}</b>
            <br><small>{len(fv)} comprobantes</small></div>""", unsafe_allow_html=True)
    with cb:
        st.markdown(f"""<div style='background:#ffebee;border-radius:10px;padding:16px'>
            <b>📤 Compras</b><br>Neto: <b>${nc:,.2f}</b><br>IVA: <b>${iva_c:,.2f}</b><br>
            <hr style='border-color:#ef9a9a;margin:8px 0'>Total: <b style='color:#c62828;font-size:1.1rem'>${tc:,.2f}</b>
            <br><small>{len(fc)} comprobantes</small></div>""", unsafe_allow_html=True)
    diva=iva_v-iva_c
    col="#c62828" if diva>0 else "#2e7d32"
    lab="IVA a pagar" if diva>0 else "IVA a favor"
    st.markdown(f"""<div style='background:#f3e5f5;border-radius:10px;padding:14px;margin-top:12px'>
        <b>🧾 Posición IVA</b><br>Débito (ventas): <b>${iva_v:,.2f}</b> · Crédito (compras): <b>${iva_c:,.2f}</b>
        <br><span style='color:{col};font-weight:700;font-size:1.05rem'>{lab}: ${abs(diva):,.2f}</span></div>""", unsafe_allow_html=True)

def rep_cuentas():
    st.markdown("### 💼 Egresos por Cuenta de Gastos")
    d,h=_fechas("cg")
    fc=[f for f in load_data("facturas_compra") if d<=f.get("fecha","")<=h]
    if not fc: st.info("Sin compras en el período."); return
    por={}
    for f in fc: k=f.get("cuenta_gastos","Sin clasificar"); por[k]=por.get(k,0)+f.get("total_factura",0)
    total=sum(por.values())
    st.metric("Total Egresos",f"${total:,.2f}")
    for k,v in sorted(por.items(),key=lambda x:x[1],reverse=True):
        pct=(v/total*100) if total else 0
        st.markdown(f"""<div style='background:white;border:1px solid #e8eaf6;border-radius:8px;padding:11px;margin:5px 0'>
            <div style='display:flex;justify-content:space-between;margin-bottom:5px'><strong>{k}</strong><strong>${v:,.2f}</strong></div>
            <div style='background:#e8eaf6;border-radius:4px;height:6px'><div style='background:#3949ab;width:{pct:.1f}%;height:6px;border-radius:4px'></div></div>
            <small style='color:#666'>{pct:.1f}% del total</small></div>""", unsafe_allow_html=True)

def rep_bancos():
    st.markdown("### 🏦 Resumen por Banco")
    d,h=_fechas("rb")
    movs=[m for m in load_data("movimientos_bancarios") if d<=m.get("fecha","")<=h]
    for b in BANCOS:
        mb=[m for m in movs if m.get("banco")==b]
        if not mb: continue
        ing=sum(m["importe"] for m in mb if m.get("tipo")=="Ingreso")
        egr=sum(m["importe"] for m in mb if m.get("tipo")=="Egreso")
        with st.expander(f"🏦 {b} — Saldo período: ${ing-egr:,.2f} ({len(mb)} mov.)"):
            c1,c2,c3=st.columns(3)
            c1.metric("Ingresos",f"${ing:,.2f}"); c2.metric("Egresos",f"${egr:,.2f}"); c3.metric("Saldo",f"${ing-egr:,.2f}")
            df=pd.DataFrame([{"Fecha":m["fecha"],"Tipo":m["tipo"],
                "Importe":f"+${m['importe']:,.2f}" if m.get("tipo")=="Ingreso" else f"-${m['importe']:,.2f}",
                "Descripción":m.get("descripcion",""),"Categoría":m.get("categoria","")}
                for m in sorted(mb,key=lambda x:x["fecha"],reverse=True)])
            st.dataframe(df,use_container_width=True,hide_index=True)

def rep_balance():
    st.markdown("### 📋 Balance General")
    d,h=_fechas("bal")
    fv  =[f for f in load_data("facturas_venta")  if d<=f.get("fecha","")<=h]
    fc  =[f for f in load_data("facturas_compra") if d<=f.get("fecha","")<=h]
    cobs=[c for c in load_data("cobranzas")       if d<=c.get("fecha","")<=h]
    pags=[p for p in load_data("pagos")           if d<=p.get("fecha","")<=h]
    tv=sum(f.get("total",0)         for f in fv)
    tc=sum(f.get("total_factura",0) for f in fc)
    cob=sum(c.get("importe",0)      for c in cobs)
    pag=sum(p.get("importe",0)      for p in pags)
    pcob=sum(f.get("saldo_pendiente",0) for f in load_data("facturas_venta")  if f.get("saldo_pendiente",0)>0)
    ppag=sum(f.get("saldo_pendiente",0) for f in load_data("facturas_compra") if f.get("saldo_pendiente",0)>0)
    ch_v=sum(c.get("importe",0) for c in load_data("cheques_cartera") if c.get("estado")=="En Cartera")
    st.markdown(f"""<div style='background:linear-gradient(135deg,#1a237e,#3949ab);color:white;border-radius:12px;padding:20px;margin-bottom:16px'>
        <h2 style='margin:0 0 4px;color:white'>Balance General</h2><p style='margin:0;opacity:.8'>Período: {d} al {h}</p></div>""", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown(f"""<div style='background:white;border:1px solid #e8eaf6;border-radius:10px;padding:16px'>
            <b style='color:#2e7d32'>📥 INGRESOS</b>
            <div style='display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #f5f5f5'><span>Ventas Facturadas</span><strong>${tv:,.2f}</strong></div>
            <div style='display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #f5f5f5'><span>Cobrado en período</span><strong>${cob:,.2f}</strong></div>
            <div style='display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #f5f5f5'><span>Cuentas por Cobrar</span><strong>${pcob:,.2f}</strong></div>
            <div style='display:flex;justify-content:space-between;padding:7px 0'><span>Cheques en Cartera</span><strong>${ch_v:,.2f}</strong></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style='background:white;border:1px solid #e8eaf6;border-radius:10px;padding:16px'>
            <b style='color:#c62828'>📤 EGRESOS</b>
            <div style='display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #f5f5f5'><span>Compras Facturadas</span><strong>${tc:,.2f}</strong></div>
            <div style='display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #f5f5f5'><span>Pagado en período</span><strong>${pag:,.2f}</strong></div>
            <div style='display:flex;justify-content:space-between;padding:7px 0'><span>Cuentas por Pagar</span><strong>${ppag:,.2f}</strong></div>
        </div>""", unsafe_allow_html=True)
    res=tv-tc; col="#2e7d32" if res>=0 else "#c62828"; lab="SUPERÁVIT" if res>=0 else "DÉFICIT"
    st.markdown(f"""<div style='background:{col};color:white;border-radius:12px;padding:18px;text-align:center;margin-top:14px'>
        <div style='font-size:.9rem;opacity:.9'>{lab} DEL PERÍODO</div>
        <div style='font-size:2.4rem;font-weight:700'>${abs(res):,.2f}</div>
        <div style='opacity:.8;font-size:.85rem'>Ventas ${tv:,.2f} — Compras ${tc:,.2f}</div></div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  ROUTER PRINCIPAL
# ═══════════════════════════════════════════════════════════
if   modulo == "🏠 Inicio":    page_inicio()
elif modulo == "💰 Ventas":    page_ventas()
elif modulo == "🛒 Compras":   page_compras()
elif modulo == "🏦 Tesorería": page_tesoreria()
elif modulo == "🏧 Bancos":    page_bancos()
elif modulo == "📊 Reportes":  page_reportes()

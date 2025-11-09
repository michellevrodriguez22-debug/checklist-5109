
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage

# ============================================================
# APP: Checklist de Rotulado General — Resolución 5109/2005
# + Complementarias vigentes (solo cuando apliquen)
# ============================================================

st.set_page_config(page_title="Checklist de Rotulado — Resolución 5109/2005", layout="wide")
st.title("Checklist de Rotulado General — Resolución 5109 de 2005 (Colombia)")

st.markdown(
    "> Lista de verificación para rótulos de alimentos y materias primas **según la Resolución 5109 de 2005** "
    "y referencias complementarias vigentes (p. ej., **Decreto 3075/1997** para habilitación y control sanitario, "
    "**rótulo complementario** para importados). "
    "⚠️ Este recurso **no** cubre la tabla nutricional ni los sellos frontales (eso está en tu app 810/2492)."
)

# -------------------------
# Sidebar: datos generales
# -------------------------
st.sidebar.header("Datos de la verificación")
producto = st.sidebar.text_input("Nombre del producto")
proveedor = st.sidebar.text_input("Fabricante / Importador / Reenvasador")
responsable = st.sidebar.text_input("Responsable de la verificación")
fecha_verif = st.sidebar.text_input("Fecha del informe (AAAA-MM-DD)", datetime.now().strftime("%Y-%m-%d"))
invima_registro = st.sidebar.text_input("Registro sanitario INVIMA (producto terminado)")
invima_estado_activo = st.sidebar.checkbox("Verificado ACTIVO y coincidente en el portal INVIMA", value=False)
invima_url = st.sidebar.text_input("URL de consulta INVIMA (opcional)")
nombre_pdf = st.sidebar.text_input("Nombre del PDF (sin .pdf)", f"informe_5109_{datetime.now().strftime('%Y%m%d')}")
solo_no = st.sidebar.checkbox("Mostrar solo 'No cumple'", value=False)

# ------------------------------------------------------------
# Definición de categorías e ítems (orden de revisión exigido)
# ------------------------------------------------------------
CATEGORIAS = {
    # 1. Empezar por el registro sanitario, como pidió el usuario
    "1. Registro sanitario y datos legales": [
        ("Registro sanitario impreso y legible en el empaque",
         "El número INVIMA debe estar **impreso sobre el empaque**, visible, legible e indeleble. Aplica a producto terminado.",
         "Res. 5109/2005 Art. 5.7; Dec. 3075/1997."),
        ("Registro sanitario coincide con la consulta INVIMA (nombre/denominación/marca)",
         "Verificar que la información del rótulo coincida con la ficha del registro en el portal INVIMA (nombre comercial/denominación, presentaciones autorizadas).",
         "Res. 5109/2005 Art. 5.7; Dec. 3075/1997."),
        ("Registro sanitario vigente y ACTIVO",
         "Confirmar estado ACTIVO (no vencido/cancelado/suspendido) en el portal INVIMA.",
         "Dec. 3075/1997 (control sanitario)."),
        ("Nombre y dirección del responsable (fabricante/importador/reenvasador)",
         "Indicar razón social y **dirección completa** del responsable declarado en el rótulo.",
         "Res. 5109/2005 Art. 5.8."),
        ("País de origen",
         "Declarar “Hecho en …” o “Producto de …” cuando aplique.",
         "Res. 5109/2005 Art. 5.9."),
    ],

    # 2. Identificación visible del producto
    "2. Identificación visible del producto": [
        ("Denominación del alimento (verdadera naturaleza)",
         "La denominación debe reflejar la **verdadera naturaleza** del producto; la marca **no** sustituye la denominación.",
         "Res. 5109/2005 Art. 5.1 y 5.1.2."),
        ("Marca comercial (no sustituye la denominación)",
         "La marca puede acompañar, pero nunca reemplazar la denominación del alimento.",
         "Res. 5109/2005 Art. 5.1.2."),
        ("Contenido neto en cara principal con unidades SI",
         "Declarar contenido neto en la **cara principal de exhibición**, usando unidades del **SI** (g, kg, mL, L), legible y sin incluir el envase.",
         "Res. 5109/2005 (Anexo de contenido neto) y Art. 3."),
        ("Lote impreso en el empaque (trazabilidad)",
         "El **lote** debe estar impreso en el empaque, legible e indeleble, para asegurar trazabilidad.",
         "Res. 5109/2005 Art. 5.4."),
        ("Fecha de vencimiento/duración mínima impresa",
         "La fecha debe estar **impresa** en el empaque, legible y en formato claro (ej.: DD/MM/AAAA).",
         "Res. 5109/2005 Art. 5.5."),
        ("Condiciones de conservación y/o instrucciones de uso si aplica",
         "Indicar condiciones especiales de conservación (p. ej., refrigeración) y uso/preparación cuando sean necesarias para seguridad/estabilidad.",
         "Res. 5109/2005 Art. 5.6."),
    ],

    # 3. Lista de ingredientes, aditivos y alérgenos
    "3. Lista de ingredientes, aditivos y alérgenos": [
        ("Lista de ingredientes en orden decreciente",
         "Listar **todos** los ingredientes en orden decreciente de peso al momento de fabricación (de mayor a menor).",
         "Res. 5109/2005 Art. 5.2."),
        ("Aditivos alimentarios con función y nombre específico",
         "Declarar aditivos por **categoría funcional** y **nombre específico** (p. ej., Conservante (Sorbato de potasio)).",
         "Res. 5109/2005 Art. 5.2.1."),
        ("Declaración de alérgenos (lista o leyenda ‘Contiene: …’)",
         "Indicar alérgenos cuando apliquen, p. ej.: gluten (trigo, cebada, centeno, avena), huevo, leche (incl. lactosa), soya, maní, frutos secos, pescado, crustáceos, mostaza, apio, sésamo, sulfitos ≥10 mg/kg.",
         "Buenas prácticas y lineamientos de rotulado; Res. 5109/2005 Art. 5.2 (interpretación)."),
    ],

    # 4. Información al consumidor y presentación gráfica
    "4. Información al consumidor y presentación": [
        ("Idioma en español (rótulo complementario si es importado)",
         "Toda la información obligatoria debe estar **en español**; para importados se permite **rótulo complementario adherido** con la traducción completa.",
         "Res. 5109/2005 Art. 5 (información en español)."),
        ("Legibilidad, indelebilidad y contraste",
         "Textos legibles e indelebles, con contraste suficiente y sin ocultar información por pliegues/sellos.",
         "Res. 5109/2005 Art. 4 y 6."),
        ("No inducir a error",
         "Evitar frases, imágenes o símbolos que atribuyan propiedades que el alimento no tiene o conlleven a confusión.",
         "Res. 5109/2005 Art. 4."),
        ("Ubicación del rótulo (cara visible)",
         "El rótulo debe estar en la **cara visible** al consumidor sin obstrucciones.",
         "Res. 5109/2005 Art. 3."),
    ],

    # 5. Regímenes particulares por situación de producto
    "5. Condiciones particulares": [
        ("Productos importados — rótulo complementario",
         "Cuando la etiqueta original no esté en español o falte información obligatoria, adherir rótulo complementario con los datos exigidos.",
         "Res. 5109/2005 Art. 5 (español); práctica regulatoria vigente."),
        ("Productos reenvasados",
         "Conservar la información original e incluir **responsable del reenvasado** con dirección.",
         "Res. 5109/2005 Art. 3 y 4."),
        ("Venta a granel / fraccionados",
         "Exhibir información mínima mediante rótulos/carteles (denominación, ingredientes cuando aplique, responsable, país de origen, lote/fecha en envase inmediato, etc.).",
         "Res. 5109/2005 (principios de información al consumidor)."),
        ("Envases muy pequeños (limitaciones de espacio)",
         "Si el área impide toda la información en el envase, usar medios alternos complementarios (pliegos, insertos o rótulo adicional) sin omitir lo esencial.",
         "Criterio práctico alineado con 5109/2005 (visibilidad y legibilidad)."),
    ],

    # 6. Documentación de soporte
    "6. Control y evidencia documental": [
        ("Soportes regulatorios disponibles",
         "Disponer de registro sanitario, contratos de maquila/reenvasado, certificados de origen y demás soportes.",
         "Dec. 3075/1997 (habilitación/control)."),
        ("Fichas técnicas y especificaciones",
         "Fichas de materias primas y producto final actualizadas, coherentes con lo declarado.",
         "Buenas prácticas de calidad."),
        ("Control de cambios del arte de etiqueta",
         "Historial de versiones y aprobaciones internas del arte del rótulo.",
         "Buenas prácticas documentales."),
    ]
}

APLICA = {
    # Por claridad, mapeo aproximado
    "Registro sanitario impreso y legible en el empaque": "Producto terminado",
    "Registro sanitario coincide con la consulta INVIMA (nombre/denominación/marca)": "Producto terminado",
    "Registro sanitario vigente y ACTIVO": "Producto terminado",
    "Nombre y dirección del responsable (fabricante/importador/reenvasador)": "Ambos",
    "País de origen": "Ambos",

    "Denominación del alimento (verdadera naturaleza)": "Ambos",
    "Marca comercial (no sustituye la denominación)": "Ambos",
    "Contenido neto en cara principal con unidades SI": "Producto terminado",
    "Lote impreso en el empaque (trazabilidad)": "Ambos",
    "Fecha de vencimiento/duración mínima impresa": "Ambos",
    "Condiciones de conservación y/o instrucciones de uso si aplica": "Producto terminado",

    "Lista de ingredientes en orden decreciente": "Producto terminado",
    "Aditivos alimentarios con función y nombre específico": "Ambos",
    "Declaración de alérgenos (lista o leyenda ‘Contiene: …’)": "Producto terminado",

    "Idioma en español (rótulo complementario si es importado)": "Ambos",
    "Legibilidad, indelebilidad y contraste": "Ambos",
    "No inducir a error": "Ambos",
    "Ubicación del rótulo (cara visible)": "Ambos",

    "Productos importados — rótulo complementario": "Producto terminado",
    "Productos reenvasados": "Producto terminado",
    "Venta a granel / fraccionados": "Producto terminado",
    "Envases muy pequeños (limitaciones de espacio)": "Producto terminado",

    "Soportes regulatorios disponibles": "Ambos",
    "Fichas técnicas y especificaciones": "Ambos",
    "Control de cambios del arte de etiqueta": "Ambos",
}

# -------------------------
# Estado, notas y evidencias
# -------------------------
if "status_5109" not in st.session_state:
    st.session_state.status_5109 = {i[0]: "none" for c in CATEGORIAS.values() for i in c}
if "note_5109" not in st.session_state:
    st.session_state.note_5109 = {i[0]: "" for c in CATEGORIAS.values() for i in c}
if "evidence_5109" not in st.session_state:
    st.session_state.evidence_5109 = {i[0]: [] for c in CATEGORIAS.values() for i in c}

def split_obs(text: str, chunk: int = 110) -> str:
    if not text:
        return ""
    s = str(text)
    return "\\n".join([s[i:i+chunk] for i in range(0, len(s), chunk)])

# -------------------------
# Render: checklist por ítem
# -------------------------
st.header("Checklist por etapas (5109/2005)")
st.markdown("Responde con ✅ Cumple / ❌ No cumple / ⚪ No aplica. Si marcas **No cumple**, podrás **adjuntar evidencia**.")

for categoria, items in CATEGORIAS.items():
    st.subheader(categoria)
    for (titulo, que_verificar, referencia) in items:
        estado = st.session_state.status_5109.get(titulo, "none")
        if solo_no and estado != "no":
            continue

        st.markdown(f"### {titulo}")
        st.markdown(f"**Qué verificar:** {que_verificar}")
        st.markdown(f"**Referencia normativa:** {referencia}")
        st.caption(f"Aplica a: {APLICA.get(titulo, 'Ambos')}")

        # Botonera estado
        c1, c2, c3, _ = st.columns([0.12, 0.12, 0.12, 0.64])
        with c1:
            if st.button("✅ Cumple", key=f"{titulo}_yes"):
                st.session_state.status_5109[titulo] = "yes"
        with c2:
            if st.button("❌ No cumple", key=f"{titulo}_no"):
                st.session_state.status_5109[titulo] = "no"
        with c3:
            if st.button("⚪ No aplica", key=f"{titulo}_na"):
                st.session_state.status_5109[titulo] = "na"

        # Estado visual
        estado = st.session_state.status_5109[titulo]
        if estado == "yes":
            st.markdown("<div style='background:#e6ffed;padding:6px;border-radius:5px;'>✅ Cumple</div>", unsafe_allow_html=True)
        elif estado == "no":
            st.markdown("<div style='background:#ffe6e6;padding:6px;border-radius:5px;'>❌ No cumple</div>", unsafe_allow_html=True)
        elif estado == "na":
            st.markdown("<div style='background:#f2f2f2;padding:6px;border-radius:5px;'>⚪ No aplica</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#fff;padding:6px;border-radius:5px;'>Sin responder</div>", unsafe_allow_html=True)

        # -----------------------------
        # Herramientas en cuadros azules
        # -----------------------------
        if titulo in ["Lote impreso en el empaque (trazabilidad)", "Fecha de vencimiento/duración mínima impresa"]:
            st.markdown("<div style='background:#e6f0ff;padding:10px;border-radius:8px;'><b>Herramienta:</b> Validador rápido de formato.</div>", unsafe_allow_html=True)
            colf1, colf2 = st.columns(2)
            with colf1:
                lote = st.text_input("Ejemplo de lote impreso (opcional)", key=f"lote_{titulo}")
                if lote:
                    st.caption("Sugerencia: usar códigos alfanuméricos claros; evitar zonas de borra/abrasión.")
            with colf2:
                fecha_txt = st.text_input("Ejemplo de fecha impresa (opcional)", key=f"fecha_{titulo}")
                if fecha_txt:
                    ok = False
                    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%b/%Y", "%m/%Y"]:
                        try:
                            _ = datetime.strptime(fecha_txt, fmt)
                            ok = True
                            break
                        except Exception:
                            pass
                    if ok:
                        st.success("Formato legible reconocido (ejemplo válido).")
                    else:
                        st.warning("No se reconoce un formato estándar (p. ej., DD/MM/AAAA).")

        if titulo == "Contenido neto en cara principal con unidades SI":
            st.markdown("<div style='background:#e6f0ff;padding:10px;border-radius:8px;'><b>Herramienta:</b> Verifica la unidad y presencia en cara principal.</div>", unsafe_allow_html=True)
            colu1, colu2 = st.columns(2)
            with colu1:
                unidad = st.selectbox("Unidad declarada", ["g", "kg", "mL", "L", "otra"], key="u_si")
                cara = st.radio("¿Está en cara principal de exhibición?", ["Sí", "No"], index=0, key="cara_si")
            with colu2:
                if unidad in ["g", "kg", "mL", "L"] and cara == "Sí":
                    st.success("✅ Unidad SI correcta en cara principal.")
                else:
                    st.error("⚠️ Revise unidad (SI) y/o ubicación en cara principal.")

        if titulo == "Declaración de alérgenos (lista o leyenda ‘Contiene: …’)":
            st.markdown("<div style='background:#e6f0ff;padding:10px;border-radius:8px;'><b>Ayuda:</b> Marque si están declarados alérgenos comunes.</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            alergs = [
                "Gluten (trigo/cebada/centeno/avena)", "Huevo", "Leche (incl. lactosa)",
                "Soya", "Maní", "Frutos secos", "Pescado", "Crustáceos",
                "Mostaza", "Apio", "Sésamo", "Sulfitos (≥10 mg/kg)"
            ]
            checks = {}
            for i, a in enumerate(alergs):
                with cols[i % 3]:
                    checks[a] = st.checkbox(a, key=f"al_{a}")
            declarados = [k for k,v in checks.items() if v]
            if declarados:
                st.info("Declarados: " + ", ".join(declarados))
            else:
                st.caption("No marcados.")

        if titulo == "Productos importados — rótulo complementario":
            st.markdown("<div style='background:#e6f0ff;padding:10px;border-radius:8px;'>"
                        "<b>Checklist rótulo complementario:</b> adherido, completo en español, legible, "
                        "sin cubrir información crítica; incluir denominación, ingredientes, responsable, país de origen, "
                        "lote y fecha impresos.</div>", unsafe_allow_html=True)

        # Observación + Evidencia
        nota = st.text_area("Observación (opcional)", value=st.session_state.note_5109.get(titulo, ""), key=f"{titulo}_nota")
        st.session_state.note_5109[titulo] = nota

        if st.session_state.status_5109[titulo] == "no":
            st.markdown("**Adjunta evidencia (JPG/PNG):**")
            files = st.file_uploader("Subir imágenes", type=["jpg","jpeg","png"], accept_multiple_files=True, key=f"upl_{titulo}")
            if files:
                caption = st.text_input("Descripción breve para estas imágenes (opcional)", key=f"cap_{titulo}")
                if st.button("Agregar evidencia", key=f"btn_add_{titulo}"):
                    for f in files:
                        st.session_state.evidence_5109[titulo].append({
                            "name": f.name,
                            "base64": base64.b64encode(f.read()).decode("utf-8"),
                            "caption": caption or ""
                        })
                    st.success(f"Se agregaron {len(files)} imagen(es) a: {titulo}")
            ev_list = st.session_state.evidence_5109.get(titulo, [])
            if ev_list:
                st.markdown("**Evidencia acumulada:**")
                cols = st.columns(4)
                for idx, ev in enumerate(ev_list):
                    img_bytes = base64.b64decode(ev["base64"])
                    with cols[idx % 4]:
                        st.image(img_bytes, caption=ev["caption"] or ev["name"], use_column_width=True)

        st.markdown("---")

# -----------------
# Métricas de avance
# -----------------
yes_count = sum(1 for v in st.session_state.status_5109.values() if v == "yes")
no_count = sum(1 for v in st.session_state.status_5109.values() if v == "no")
answered_count = yes_count + no_count
percent = round((yes_count / answered_count * 100), 1) if answered_count > 0 else 0.0
st.metric("Cumplimiento total (sobre ítems contestados)", f"{percent}%")
st.write(
    f"CUMPLE: {yes_count} — NO CUMPLE: {no_count} — "
    f"NO APLICA: {sum(1 for v in st.session_state.status_5109.values() if v == 'na')} — "
    f"SIN RESPONDER: {sum(1 for v in st.session_state.status_5109.values() if v == 'none')}"
)

# -----------------
# Generación de PDF
# -----------------
def split_obs_pdf(text: str, chunk: int = 100) -> str:
    if not text:
        return ""
    s = str(text)
    return "\\n".join([s[i:i+chunk] for i in range(0, len(s), chunk)])

def generar_pdf():
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=8*mm, rightMargin=8*mm,
        topMargin=8*mm, bottomMargin=8*mm
    )
    styles = getSampleStyleSheet()
    style_header = ParagraphStyle("header", parent=styles["Normal"], fontSize=9, leading=11)
    style_cell   = ParagraphStyle("cell",   parent=styles["Normal"], fontSize=8, leading=10)

    story = []
    fecha_str = fecha_verif or datetime.now().strftime("%Y-%m-%d")
    portada = (
        f"<b>Informe de verificación — Rotulado general (Res. 5109/2005)</b><br/>"
        f"<b>Fecha:</b> {fecha_str} &nbsp;&nbsp; "
        f"<b>Producto:</b> {producto or '-'} &nbsp;&nbsp; "
        f"<b>Responsable:</b> {responsable or '-'}<br/>"
        f"<b>Fabricante/Importador:</b> {proveedor or '-'} &nbsp;&nbsp; "
        f"<b>Registro INVIMA:</b> {invima_registro or '-'} &nbsp;&nbsp; "
        f"<b>Estado:</b> {'ACTIVO y coincidente' if invima_estado_activo else 'No verificado/No activo'}"
    )
    if invima_url.strip():
        portada += f" &nbsp;&nbsp; <b>Consulta:</b> {invima_url}"
    story.append(Paragraph(portada, style_header))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Este informe cubre la verificación de rotulado general exigida por la Resolución 5109 de 2005 y referencias complementarias vigentes.", style_header))
    story.append(Spacer(1, 5*mm))

    # Tabla de resultados
    data = [["Ítem", "Estado", "Observación", "Referencia"]]
    for items in CATEGORIAS.values():
        for (titulo, _, referencia) in items:
            estado_val = st.session_state.status_5109.get(titulo, "none")
            estado_humano = (
                "Cumple" if estado_val == "yes"
                else "No cumple" if estado_val == "no"
                else "No aplica" if estado_val == "na"
                else "Sin responder"
            )
            obs = st.session_state.note_5109.get(titulo, "") or "-"
            obs = "-" if not obs else split_obs_pdf(obs, 110)
            data.append([
                Paragraph(str(titulo),          style_cell),
                Paragraph(str(estado_humano),   style_cell),
                Paragraph(obs,                  style_cell),
                Paragraph(str(referencia),      style_cell),
            ])

    tbl = Table(data, colWidths=[100*mm, 25*mm, 85*mm, 55*mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f2f2f2")),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,0), 9),
        ("GRID",       (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN",     (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",(0,0), (-1,-1), 3),
        ("RIGHTPADDING",(0,0), (-1,-1), 3),
    ]))
    story.append(tbl)

    # Evidencias en página nueva
    any_ev = any(len(v) > 0 for v in st.session_state.evidence_5109.values())
    if any_ev:
        story.append(PageBreak())
        story.append(Paragraph("<b>Evidencia fotográfica</b>", style_header))
        story.append(Spacer(1, 3*mm))
        for titulo, ev_list in st.session_state.evidence_5109.items():
            if not ev_list:
                continue
            story.append(Paragraph(f"<b>Ítem:</b> {titulo}", style_header))
            story.append(Paragraph("<b>Evidencia de incumplimiento:</b>", style_header))
            story.append(Spacer(1, 2*mm))
            for ev in ev_list:
                try:
                    img_bytes = base64.b64decode(ev["base64"])
                    story.append(RLImage(BytesIO(img_bytes), width=85*mm, height=55*mm))
                    if ev.get("caption"):
                        story.append(Paragraph(ev["caption"], style_cell))
                    story.append(Spacer(1, 3*mm))
                except Exception as e:
                    story.append(Paragraph(f"<i>⚠️ Error al cargar imagen {ev.get('name', '')}: {e}</i>", style_cell))
            story.append(Spacer(1, 5*mm))

    doc.build(story)
    buf.seek(0)
    return buf

# --------------
# Botón PDF
# --------------
st.subheader("Generar informe PDF (A4 horizontal)")
if st.button("Generar PDF"):
    pdf = generar_pdf()
    file_name = (nombre_pdf.strip() or f"informe_5109_{datetime.now().strftime('%Y%m%d')}") + ".pdf"
    st.download_button("Descargar PDF", data=pdf, file_name=file_name, mime="application/pdf")

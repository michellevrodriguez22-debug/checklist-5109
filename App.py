
# app_5109_definitiva_v3.py
# Versión extendida (≈500+ líneas): flujo INVIMA → cara frontal → cara posterior → condiciones → documentación
# Sin herramientas interactivas. Con ejemplos en “Qué verificar” para Lote y Fecha. Referencias explícitas.
# Evidencias por ítem y PDF horizontal con portada + evidencias en página nueva.

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

# =========================================================
# CONFIGURACIÓN INICIAL
# =========================================================
st.set_page_config(page_title="Checklist Rotulado — Resolución 5109/2005", layout="wide")
st.title("Checklist de Rotulado — Resolución 5109 de 2005 (Colombia)")

# =========================================================
# SIDEBAR (datos generales)
# =========================================================
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

# =========================================================
# ÍTEMS ORDENADOS (flujo real). Cada item: (titulo, que_verificar, referencia)
# =========================================================

CATEGORIAS = {
    # -----------------------------------------------------
    # 1. Verificación con INVIMA (registro sanitario)
    # -----------------------------------------------------
    "1. Verificación con INVIMA (registro sanitario)": [
        ("Registro sanitario impreso y legible en el empaque",
         "El número INVIMA debe estar **impreso sobre el empaque**, visible, legible e indeleble; aplica a producto terminado.",
         "Resolución 5109/2005 Art. 5.7; Decreto 3075/1997."),
        ("Registro sanitario coincide con la consulta INVIMA (nombre/denominación/marca)",
         "El rótulo debe coincidir con la ficha del registro (nombre comercial/denominación, presentaciones).",
         "Resolución 5109/2005 Art. 5.7; Decreto 3075/1997."),
        ("Registro sanitario vigente y ACTIVO",
         "Debe estar **ACTIVO** (no vencido, cancelado ni suspendido) según el portal INVIMA.",
         "Decreto 3075/1997 (control sanitario)."),
        ("Denominación del alimento coincidente con el registro",
         "La denominación impresa en el rótulo debe coincidir con la reportada en la ficha INVIMA.",
         "Resolución 5109/2005 Art. 5.1; Art. 5.7."),
        ("Nombre y dirección del responsable (fabricante/importador/reenvasador)",
         "Declarar razón social y **dirección completa** del responsable.",
         "Resolución 5109/2005 Art. 5.8."),
        ("País de origen",
         "Declarar “Hecho en …” o “Producto de …” cuando aplique.",
         "Resolución 5109/2005 Art. 5.9."),
        ("Presentación y contenido autorizados",
         "La presentación (peso/volumen) declarada en el rótulo debe estar autorizada en el registro sanitario.",
         "Resolución 5109/2005 Art. 5.7; práctica regulatoria (INVIMA)."),
    ],

    # -----------------------------------------------------
    # 2. Revisión de la cara frontal del empaque
    # -----------------------------------------------------
    "2. Revisión de la cara frontal": [
        ("Denominación del alimento (verdadera naturaleza)",
         "Debe reflejar la **verdadera naturaleza** del producto; la marca **no** sustituye la denominación.",
         "Resolución 5109/2005 Art. 5.1 y 5.1.2."),
        ("Marca comercial (no sustituye la denominación)",
         "La marca acompaña, pero nunca reemplaza la denominación del alimento.",
         "Resolución 5109/2005 Art. 5.1.2."),
        ("Contenido neto en cara principal con unidades SI",
         "Declarar contenido neto en la **cara principal** de exhibición, usando **unidades SI** (g, kg, mL, L), legible y sin incluir el envase.",
         "Resolución 5109/2005 (Anexo de contenido neto) y Art. 3."),
        ("Lote impreso en el empaque (trazabilidad)",
            "El **lote** debe estar impreso en el empaque, legible e indeleble, para trazabilidad. **Ejemplos de formato válido (referenciales):** "
            "**L230401**, **LOT230401**, **230401A**.",
            "Resolución 5109/2005 Art. 5.4."),
        ("Fecha de vencimiento / duración mínima impresa",
            "La fecha debe estar **impresa** en el empaque, legible y clara. **Ejemplos de formato válido (según caso):** "
            "**DD/MM/AAAA**, **DD-MM-AAAA**, o **MMM/AAAA** (para duración mínima).",
            "Resolución 5109/2005 Art. 5.5."),
        ("Ubicación visible del rótulo (cara principal)",
         "El rótulo debe estar en la **cara visible** al consumidor, sin obstrucciones mecánicas ni pliegues que dificulten la lectura.",
         "Resolución 5109/2005 Art. 3."),
        ("Afirmaciones de la cara principal no engañosas",
         "La información y recursos gráficos de portada no deben inducir a error respecto de la naturaleza, composición o cualidades del alimento.",
         "Resolución 5109/2005 Art. 4."),
        ("Legibilidad de la cara principal",
         "Textos, números y símbolos en la cara frontal deben ser legibles, indelebles y con contraste adecuado.",
         "Resolución 5109/2005 Art. 4 y 6."),
    ],

    # -----------------------------------------------------
    # 3. Revisión de la cara posterior / información general
    # -----------------------------------------------------
    "3. Revisión de la cara posterior / información general": [
        ("Lista de ingredientes en orden decreciente",
         "Listar **todos** los ingredientes en orden decreciente de peso al momento de fabricación (de mayor a menor).",
         "Resolución 5109/2005 Art. 5.2."),
        ("Aditivos alimentarios con función y nombre específico",
         "Declarar aditivos por **categoría funcional** y **nombre específico** (p. ej., Conservante (Sorbato de potasio)).",
         "Resolución 5109/2005 Art. 5.2.1."),
        ("Ingredientes compuestos (declaración desglosada)",
         "Si se usan ingredientes compuestos (p. ej., chocolate), listar sus componentes entre paréntesis cuando corresponda.",
         "Resolución 5109/2005 Art. 5.2 (interpretación)."),
        ("Aditivos con límites específicos (cuando aplique)",
         "Si el aditivo posee límites de uso, verificar su pertinencia con la ficha técnica y especificación del producto.",
         "Resolución 5109/2005 Art. 5.2.1; fichas técnicas vigentes."),
        ("Declaración de alérgenos",
         "Indicar alérgenos cuando apliquen: gluten (trigo/cebada/centeno/avena), huevo, leche (incl. lactosa), soya, maní, frutos secos, pescado, crustáceos, mostaza, apio, sésamo, sulfitos ≥10 mg/kg.",
         "Resolución 5109/2005 Art. 5.2 (interpretación y buenas prácticas)."),
        ("Prioridad visual suficiente para ingredientes y alérgenos",
         "La lista de ingredientes y la declaración de alérgenos deben ser legibles, sin ser ocultadas por otros elementos gráficos.",
         "Resolución 5109/2005 Art. 4 y 6."),
        ("Condiciones de conservación (cuando corresponda)",
         "Declarar condiciones especiales de conservación para preservar inocuidad y vida útil (p. ej., “Manténgase refrigerado a 4 °C”).",
         "Resolución 5109/2005 Art. 5.6."),
        ("Instrucciones de uso/preparación (cuando corresponda)",
         "Incluir instrucciones necesarias para el uso seguro y adecuado del producto (p. ej., “Agítese antes de usar”).",
         "Resolución 5109/2005 Art. 5.6."),
        ("Idioma en español (rótulo complementario si es importado)",
         "Toda la información obligatoria debe estar **en español**; para importados se permite **rótulo complementario** adherido con la traducción completa.",
         "Resolución 5109/2005 Art. 5."),
        ("No inducir a error (cara posterior)",
         "La información posterior tampoco debe inducir a error sobre la naturaleza/composición/beneficios del alimento.",
         "Resolución 5109/2005 Art. 4."),
        ("Legibilidad e indelebilidad general",
         "Textos, cifras y símbolos deben ser indelebles, con contraste suficiente y legibles en condiciones normales de compra.",
         "Resolución 5109/2005 Art. 4 y 6."),
        ("Ubicación del rótulo (información posterior)",
         "La información debe estar dispuesta en zonas visibles y accesibles del envase.",
         "Resolución 5109/2005 Art. 3."),
    ],

    # -----------------------------------------------------
    # 4. Condiciones particulares (situaciones especiales)
    # -----------------------------------------------------
    "4. Condiciones particulares": [
        ("Producto importado — rótulo complementario",
         "Si la etiqueta original no está en español o falta información obligatoria, adherir rótulo complementario con los datos exigidos.",
         "Resolución 5109/2005 Art. 5 (español)."),
        ("Producto reenvasado (en establecimiento autorizado)",
         "Conservar la información original e incluir **responsable del reenvasado** con dirección.",
         "Resolución 5109/2005 Art. 3 y 4; Decreto 3075/1997."),
        ("Venta a granel / fraccionados",
         "Exhibir información mínima mediante rótulos/carteles (denominación, ingredientes cuando aplique, responsable, país de origen, lote/fecha en envase inmediato, etc.).",
         "Resolución 5109/2005 (principios de información al consumidor)."),
        ("Envases muy pequeños (limitaciones de espacio)",
         "Si el área impide toda la información, usar medios complementarios (pliegos, insertos, rótulos adicionales) sin omitir lo esencial.",
         "Criterio práctico alineado con 5109/2005 (visibilidad/legibilidad)."),
        ("Multipacks o envases secundarios",
         "Cuando aplique, el envase secundario debe repetir la información esencial o remitir claramente a la existente en el envase primario.",
         "Criterio práctico y lineamientos de información al consumidor."),
        ("Promociones/obsequios adheridos",
         "Evitar que elementos promocionales oculten información obligatoria del rótulo.",
         "Resolución 5109/2005 Art. 4 (no inducir a error) y Art. 6 (legibilidad)."),
    ],

    # -----------------------------------------------------
    # 5. Evidencia documental y control
    # -----------------------------------------------------
    "5. Evidencia documental y control": [
        ("Soportes regulatorios disponibles",
         "Disponer de registro sanitario, contratos de maquila/reenvasado, certificados de origen y demás soportes.",
         "Decreto 3075/1997 (habilitación y control)."),
        ("Fichas técnicas y especificaciones",
         "Fichas de materias primas y producto final actualizadas, coherentes con lo declarado.",
         "Buenas prácticas de calidad."),
        ("Control de cambios del arte de etiqueta",
         "Historial de versiones y aprobaciones internas del arte del rótulo.",
         "Buenas prácticas documentales."),
        ("Coherencia documental vs rótulo",
         "La información del rótulo debe ser coherente con fichas técnicas, especificaciones, acuerdos con proveedor y análisis disponibles.",
         "Buenas prácticas de aseguramiento de calidad."),
        ("Evidencia de revisión periódica de artes",
         "Demostrar revisión periódica (y tras cambios regulatorios) de los artes de etiqueta antes de impresión/lanzamiento.",
         "Buenas prácticas de cumplimiento regulatorio."),
    ],
}

# =========================================================
# Mapa de aplicabilidad visible
# =========================================================
APLICA = {
    # 1. INVIMA
    "Registro sanitario impreso y legible en el empaque": "Producto terminado",
    "Registro sanitario coincide con la consulta INVIMA (nombre/denominación/marca)": "Producto terminado",
    "Registro sanitario vigente y ACTIVO": "Producto terminado",
    "Denominación del alimento coincidente con el registro": "Producto terminado",
    "Nombre y dirección del responsable (fabricante/importador/reenvasador)": "Ambos",
    "País de origen": "Ambos",
    "Presentación y contenido autorizados": "Producto terminado",

    # 2. Cara frontal
    "Denominación del alimento (verdadera naturaleza)": "Ambos",
    "Marca comercial (no sustituye la denominación)": "Ambos",
    "Contenido neto en cara principal con unidades SI": "Producto terminado",
    "Lote impreso en el empaque (trazabilidad)": "Ambos",
    "Fecha de vencimiento / duración mínima impresa": "Ambos",
    "Ubicación visible del rótulo (cara principal)": "Ambos",
    "Afirmaciones de la cara principal no engañosas": "Ambos",
    "Legibilidad de la cara principal": "Ambos",

    # 3. Posterior
    "Lista de ingredientes en orden decreciente": "Producto terminado",
    "Aditivos alimentarios con función y nombre específico": "Ambos",
    "Ingredientes compuestos (declaración desglosada)": "Producto terminado",
    "Aditivos con límites específicos (cuando aplique)": "Producto terminado",
    "Declaración de alérgenos": "Producto terminado",
    "Prioridad visual suficiente para ingredientes y alérgenos": "Producto terminado",
    "Condiciones de conservación (cuando corresponda)": "Producto terminado",
    "Instrucciones de uso/preparación (cuando corresponda)": "Producto terminado",
    "Idioma en español (rótulo complementario si es importado)": "Ambos",
    "No inducir a error (cara posterior)": "Ambos",
    "Legibilidad e indelebilidad general": "Ambos",
    "Ubicación del rótulo (información posterior)": "Ambos",

    # 4. Particulares
    "Producto importado — rótulo complementario": "Producto terminado",
    "Producto reenvasado (en establecimiento autorizado)": "Producto terminado",
    "Venta a granel / fraccionados": "Producto terminado",
    "Envases muy pequeños (limitaciones de espacio)": "Producto terminado",
    "Multipacks o envases secundarios": "Producto terminado",
    "Promociones/obsequios adheridos": "Producto terminado",

    # 5. Documental
    "Soportes regulatorios disponibles": "Ambos",
    "Fichas técnicas y especificaciones": "Ambos",
    "Control de cambios del arte de etiqueta": "Ambos",
    "Coherencia documental vs rótulo": "Ambos",
    "Evidencia de revisión periódica de artes": "Ambos",
}

# =========================================================
# ESTADO / NOTAS / EVIDENCIAS
# =========================================================
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

# =========================================================
# RENDER DEL CHECKLIST
# =========================================================
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

        # Botonera de estado
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

        # Observación
        nota = st.text_area("Observación (opcional)", value=st.session_state.note_5109.get(titulo, ""), key=f"{titulo}_nota")
        st.session_state.note_5109[titulo] = nota

        # Evidencia (solo si No cumple)
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

# =========================================================
# MÉTRICAS
# =========================================================
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

# =========================================================
# PDF (A4 horizontal) + evidencias
# =========================================================
def split_obs_pdf(text: str, chunk: int = 110) -> str:
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

    # Tabla principal
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
                Paragraph(str(titulo),        style_cell),
                Paragraph(str(estado_humano), style_cell),
                Paragraph(obs,                style_cell),
                Paragraph(str(referencia),    style_cell),
            ])

    tbl = Table(data, colWidths=[105*mm, 25*mm, 80*mm, 55*mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f2f2f2")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",(0,0), (-1,-1), 3),
        ("RIGHTPADDING",(0,0), (-1,-1), 3),
    ]))
    story.append(tbl)

    # Evidencias (página nueva)
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

# =========================================================
# EXPORTAR PDF
# =========================================================
st.subheader("Generar informe PDF (A4 horizontal)")
if st.button("Generar PDF"):
    pdf_buffer = generar_pdf()
    file_name = (nombre_pdf.strip() or f"informe_5109_{datetime.now().strftime('%Y%m%d')}") + ".pdf"
    st.download_button("Descargar PDF", data=pdf_buffer, file_name=file_name, mime="application/pdf")


import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak

# ------------------------------------------------------------------
# APP 5109 SOLO (sin 810/2492). Con evidencia fotográfica por ítem NO CUMPLE.
# ------------------------------------------------------------------
st.set_page_config(page_title="Checklist Rotulado — Resolución 5109/2005", layout="wide")
st.title("Checklist de rotulado — Resolución 5109 de 2005 (Colombia)")

# ------------------------------------------------------------------
# SIDEBAR: Datos generales
# ------------------------------------------------------------------
st.sidebar.header("Datos de la verificación")
producto = st.sidebar.text_input("Nombre del producto")
categoria_producto = st.sidebar.selectbox("Tipo", ["Producto terminado", "Materia prima", "Ambos"])
proveedor = st.sidebar.text_input("Proveedor / Fabricante")
responsable = st.sidebar.text_input("Responsable de la verificación")
invima_num = st.sidebar.text_input("Registro sanitario INVIMA (si aplica a producto terminado)")
invima_url = st.sidebar.text_input("URL consulta INVIMA (opcional)")
invima_estado_ok = st.sidebar.checkbox("Verificación en INVIMA realizada y ACTIVO (coincide nombre/empresa)", value=False)
nombre_pdf = st.sidebar.text_input("Nombre del PDF (sin .pdf)", f"informe_5109_{datetime.now().strftime('%Y%m%d')}")
filter_no = st.sidebar.checkbox("Mostrar solo 'No cumple'", value=False)

st.sidebar.markdown("---")
st.sidebar.caption("Este recurso guía una verificación práctica según la Resolución 5109/2005 y normas generales de rotulado de alimentos en Colombia (sin incluir requisitos de tabla nutricional ni sellos frontales regulados por 810/2492).")

# ------------------------------------------------------------------
# Definición ordenada de criterios (flujo típico de revisión física)
# Solo referencias y textos en el marco de la Res. 5109/2005 y lineamientos generales sanitarios
# ------------------------------------------------------------------
CATEGORIAS = {
    "1. Identificación sanitaria y legal": [
        ("Registro sanitario INVIMA visible y vigente",
         "Verificar que el rótulo del PRODUCTO TERMINADO muestre el número de registro sanitario INVIMA, legible, indeleble y en el empaque. Confirmar en el portal del INVIMA que el registro está ACTIVO y que el nombre del producto, titular y fabricante coinciden con lo impreso.",
         "Asegurar que el número esté en el empaque, sea legible/indeleble y que su estado sea ACTIVO y coincidente en INVIMA.",
         "Res. 5109/2005 (arts. 3, 4, 5) + control sanitario general"),
        ("Nombre y dirección del fabricante, importador o reenvasador",
         "Debe indicarse la razón social y dirección física completa del fabricante nacional o importador (y del reenvasador, si aplica), legibles e indelebles.",
         "Incluir razón social y dirección completas del responsable de fabricación/importación/reenvasado.",
         "Res. 5109/2005 art. 5.8"),
        ("País de origen",
         "Declarar claramente 'Hecho en...' o 'Producto de...' según procedencia del alimento.",
         "Incluir país de origen de forma explícita y legible.",
         "Res. 5109/2005 art. 5.9"),
    ],
    "2. Denominación y composición declarada": [
        ("Denominación del alimento (verdadera naturaleza)",
         "La denominación debe describir la verdadera naturaleza del alimento (no sustituida por la marca).",
         "Usar una denominación precisa que refleje el alimento.",
         "Res. 5109/2005 art. 5.1"),
        ("Marca comercial (no sustituye denominación)",
         "La marca puede acompañar, pero no reemplazar la denominación del alimento.",
         "Conservar denominación técnica junto a la marca.",
         "Res. 5109/2005 art. 5.1.2"),
        ("Lista de ingredientes en orden decreciente de peso",
         "Listar todos los ingredientes en orden decreciente de su peso al momento de formulación. Incluir aditivos con su categoría funcional y nombre específico (p. ej., 'Conservante (Sorbato de potasio)').",
         "Completar/ordenar correctamente la lista y declarar aditivos con categoría y nombre.",
         "Res. 5109/2005 art. 5.2"),
        ("Aditivos alimentarios declarados correctamente",
         "Los aditivos deben declararse por su nombre común o categoría funcional; no usar códigos ni abreviaturas.",
         "Declarar aditivos por nombre común o categoría funcional.",
         "Res. 5109/2005 art. 5.2.1"),
        ("Contenido neto en cara principal",
         "Expresar el contenido neto en unidades del SI (g, kg, mL o L), excluyendo el envase. Debe estar en la cara frontal de exhibición, legible y con buen contraste.",
         "Ubicar el contenido neto en la cara principal y con unidad SI.",
         "Res. 5109/2005 (arts. 3, 5 y anexo de rotulado)"),
    ],
    "3. Identificación de lote y fechas": [
        ("Lote impreso sobre el empaque",
         "El código/lote debe estar impreso directamente sobre el empaque o etiqueta adherida, legible, indeleble y ubicado para lectura rápida (trazabilidad).",
         "Imprimir lote en el empaque con alta legibilidad e indelebilidad.",
         "Res. 5109/2005 art. 5.4"),
        ("Fecha de vencimiento o duración mínima impresa",
         "Imprimir en el empaque (no solo en la caja externa) la fecha de vencimiento/duración mínima en formato claro (recomendado día/mes/año) y legible. Debe corresponder al alimento ofrecido al consumidor.",
         "Asegurar impresión directa en el empaque y formato legible.",
         "Res. 5109/2005 art. 5.5"),
        ("Condiciones de conservación y almacenamiento",
         "Cuando el alimento requiera condiciones especiales (refrigeración, temperatura, luz, humedad), declararlas junto a la fecha para preservar inocuidad/calidad.",
         "Indicar claramente condiciones de conservación si aplican.",
         "Res. 5109/2005 arts. 3 y 5"),
        ("Modo de empleo / instrucciones de uso (si son necesarias)",
         "Si para el uso seguro/adecuado del alimento se requieren instrucciones (reconstitución, calentamiento, dilución), deben declararse.",
         "Agregar instrucciones de uso cuando sean necesarias.",
         "Res. 5109/2005 art. 5 (principios de información)"),
    ],
    "4. Presentación del rótulo y veracidad": [
        ("Idioma español",
         "Toda la información obligatoria debe estar en español. Para importados, puede usarse rótulo complementario adherido con la traducción.",
         "Asegurar rotulado completo en español o rótulo complementario.",
         "Res. 5109/2005 art. 5"),
        ("Legibilidad, contraste y permanencia",
         "El texto debe ser visible, legible, indeleble y con buen contraste respecto del fondo; no oculto por pliegues o cierres.",
         "Mejorar tamaño de letra/contraste y asegurar indelebilidad.",
         "Res. 5109/2005 arts. 3, 4 y 6"),
        ("Ubicación y visibilidad en cara principal",
         "La información obligatoria no debe quedar oculta; colocarla en la(s) cara(s) visible(s) al consumidor.",
         "Reubicar la información para asegurar visibilidad.",
         "Res. 5109/2005 arts. 3 y 5"),
        ("Prohibición de inducir a error o atribuir propiedades medicinales",
         "El rótulo no debe contener afirmaciones falsas, engañosas o atribuir propiedades de prevenir, tratar o curar enfermedades.",
         "Eliminar frases/elementos que induzcan a error o sean medicinales.",
         "Res. 5109/2005 art. 4"),
        ("Información del importador y rótulo complementario (si aplica)",
         "Para productos importados, además del país de origen, indicar el importador responsable en Colombia y adherir rótulo complementario en español cuando sea necesario.",
         "Incluir importador y rótulo complementario en español.",
         "Res. 5109/2005 arts. 2, 5"),
    ],
    "5. Control documental y soportes": [
        ("Soportes técnicos disponibles (fichas, especificaciones)",
         "Mantener fichas técnicas, especificaciones y documentación que respalde lo declarado (ingredientes, aditivos, condiciones).",
         "Adjuntar/solicitar soportes documentales actualizados.",
         "Res. 5109/2005 (buenas prácticas de información)"),
        ("Trazabilidad del proveedor",
         "El rótulo debe permitir rastrear el producto (lote, fabricante, dirección) para retiro en caso de no conformidades.",
         "Verificar que la información permita la trazabilidad.",
         "Res. 5109/2005 art. 5.4"),
    ],
}

# Aplicabilidad (sugerida)
APLICA = {
    # 1
    "Registro sanitario INVIMA visible y vigente": "Producto terminado",
    "Nombre y dirección del fabricante, importador o reenvasador": "Ambos",
    "País de origen": "Ambos",
    # 2
    "Denominación del alimento (verdadera naturaleza)": "Ambos",
    "Marca comercial (no sustituye denominación)": "Ambos",
    "Lista de ingredientes en orden decreciente de peso": "Producto terminado",
    "Aditivos alimentarios declarados correctamente": "Ambos",
    "Contenido neto en cara principal": "Producto terminado",
    # 3
    "Lote impreso sobre el empaque": "Ambos",
    "Fecha de vencimiento o duración mínima impresa": "Ambos",
    "Condiciones de conservación y almacenamiento": "Ambos",
    "Modo de empleo / instrucciones de uso (si son necesarias)": "Producto terminado",
    # 4
    "Idioma español": "Ambos",
    "Legibilidad, contraste y permanencia": "Ambos",
    "Ubicación y visibilidad en cara principal": "Ambos",
    "Prohibición de inducir a error o atribuir propiedades medicinales": "Ambos",
    "Información del importador y rótulo complementario (si aplica)": "Producto terminado",
    # 5
    "Soportes técnicos disponibles (fichas, especificaciones)": "Ambos",
    "Trazabilidad del proveedor": "Ambos",
}

# ------------------------------------------------------------------
# Estado y notas en sesión
# ------------------------------------------------------------------
if "status" not in st.session_state:
    st.session_state.status = {i[0]: "none" for c in CATEGORIAS.values() for i in c}
if "note" not in st.session_state:
    st.session_state.note = {i[0]: "" for c in CATEGORIAS.values() for i in c}
# Evidencia: lista de imágenes por ítem (cada elemento: dict con keys 'name', 'bytes', 'caption')
if "evidence" not in st.session_state:
    st.session_state.evidence = {i[0]: [] for c in CATEGORIAS.values() for i in c}

st.header("Checklist según flujo de revisión (5109/2005)")
st.markdown("Responde con ✅ Cumple / ❌ No cumple / ⚪ No aplica. Cuando marques **No cumple**, podrás **adjuntar evidencia fotográfica**.")

# Métrica rápida arriba (se actualiza al vuelo)
def compute_metrics():
    yes = sum(1 for v in st.session_state.status.values() if v == "yes")
    no = sum(1 for v in st.session_state.status.values() if v == "no")
    answered = yes + no
    pct = round((yes / answered * 100), 1) if answered > 0 else 0.0
    return yes, no, answered, pct

yes_count, no_count, answered_count, percent = compute_metrics()
st.metric("Cumplimiento total (sobre ítems contestados)", f"{percent}%")

for categoria, items in CATEGORIAS.items():
    st.subheader(categoria)
    for item in items:
        titulo, que_verificar, recomendacion, referencia = item

        estado = st.session_state.status.get(titulo, "none")
        if filter_no and estado != "no":
            continue

        st.markdown(f"### {titulo}")
        st.markdown(f"**Qué verificar:** {que_verificar}")
        st.markdown(f"**Referencia:** {referencia}")
        st.markdown(f"**Aplica a:** {APLICA.get(titulo, 'Ambos')}")

        c1, c2, c3, _ = st.columns([0.12, 0.12, 0.12, 0.64])
        with c1:
            if st.button("✅ Cumple", key=f"{titulo}_yes"):
                st.session_state.status[titulo] = "yes"
        with c2:
            if st.button("❌ No cumple", key=f"{titulo}_no"):
                st.session_state.status[titulo] = "no"
        with c3:
            if st.button("⚪ No aplica", key=f"{titulo}_na"):
                st.session_state.status[titulo] = "na"

        # Visualización del estado
        estado = st.session_state.status[titulo]
        if estado == "yes":
            st.markdown("<div style='background:#e6ffed;padding:6px;border-radius:5px;'>✅ Cumple</div>", unsafe_allow_html=True)
        elif estado == "no":
            st.markdown(f"<div style='background:#ffe6e6;padding:6px;border-radius:5px;'>❌ No cumple — {recomendacion}</div>", unsafe_allow_html=True)
        elif estado == "na":
            st.markdown("<div style='background:#f2f2f2;padding:6px;border-radius:5px;'>⚪ No aplica</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#fff;padding:6px;border-radius:5px;'>Sin responder</div>", unsafe_allow_html=True)

        # Observación libre
        nota = st.text_area("Observación (opcional)", value=st.session_state.note.get(titulo, ""), key=f"{titulo}_nota")
        st.session_state.note[titulo] = nota

        # ------------------------------------------------------
        # Evidencia fotográfica (se activa SOLO cuando NO CUMPLE)
        # ------------------------------------------------------
        if st.session_state.status[titulo] == "no":
            st.markdown("**Adjunta evidencia fotográfica del incumplimiento:**")
            files = st.file_uploader("Subir imágenes (JPG/PNG) — puedes cargar varias", type=["jpg","jpeg","png"], accept_multiple_files=True, key=f"uploader_{titulo}")
            if files:
                # Pedir una descripción/caption común opcional para este bloque
                caption = st.text_input("Descripción breve para estas imágenes (opcional)", key=f"caption_{titulo}")
                if st.button("Agregar evidencia", key=f"add_ev_{titulo}"):
                    for f in files:
                        st.session_state.evidence[titulo].append({
                            "name": f.name,
                            "bytes": f.read(),
                            "caption": caption or ""
                        })
                    st.success(f"Se agregaron {len(files)} imagen(es) a la evidencia de: {titulo}")

            # Mostrar miniaturas de la evidencia acumulada para el ítem
            ev_list = st.session_state.evidence.get(titulo, [])
            if ev_list:
                st.markdown("**Evidencia acumulada:**")
                cols = st.columns(4)
                for idx, ev in enumerate(ev_list):
                    with cols[idx % 4]:
                        st.image(ev["bytes"], caption=ev["caption"] or ev["name"], use_column_width=True)
                        if st.button("Eliminar esta imagen", key=f"del_{titulo}_{idx}"):
                            st.session_state.evidence[titulo].pop(idx)
                            st.experimental_rerun()

        st.markdown("---")

# ------------------------------------------------------------------
# Resumen y exportación
# ------------------------------------------------------------------
# DataFrame de resultados
rows = []
for items in CATEGORIAS.values():
    for titulo, que_verificar, recomendacion, referencia in items:
        estado_val = st.session_state.status.get(titulo, "none")
        estado_humano = (
            "Cumple" if estado_val == "yes"
            else "No cumple" if estado_val == "no"
            else "No aplica" if estado_val == "na"
            else "Sin responder"
        )
        rows.append({
            "Ítem": titulo,
            "Estado": estado_humano,
            "Recomendación": recomendacion,
            "Referencia": referencia,
            "Observación": st.session_state.note.get(titulo, ""),
        })
df = pd.DataFrame(rows, columns=["Ítem", "Estado", "Recomendación", "Referencia", "Observación"])

st.subheader("Resumen rápido")
st.write(
    f"CUMPLE: {sum(1 for v in st.session_state.status.values() if v == 'yes')} — "
    f"NO CUMPLE: {sum(1 for v in st.session_state.status.values() if v == 'no')} — "
    f"NO APLICA: {sum(1 for v in st.session_state.status.values() if v == 'na')} — "
    f"SIN RESPONDER: {sum(1 for v in st.session_state.status.values() if v == 'none')}"
)

# ------------------------------------------------------------------
# Utilidad: dividir observación a saltos de línea
# ------------------------------------------------------------------
def split_observation_text(text: str, chunk: int = 100) -> str:
    if not text:
        return ""
    s = str(text)
    if len(s) <= chunk:
        return s
    parts = [s[i:i+chunk] for i in range(0, len(s), chunk)]
    return "\\n".join(parts)

# ------------------------------------------------------------------
# PDF: Tabla resumen + bloque de evidencias (solo NO CUMPLE) al final
# ------------------------------------------------------------------
def generar_pdf(df: pd.DataFrame, producto: str, proveedor: str, responsable: str,
                categoria_producto: str, invima_num: str, invima_url: str,
                invima_estado_ok: bool, porcentaje: float, nombre_archivo: str) -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=8*mm, rightMargin=8*mm,
        topMargin=8*mm, bottomMargin=8*mm
    )
    styles = getSampleStyleSheet()
    style_header = ParagraphStyle("header", parent=styles["Normal"], fontSize=8, leading=10)
    style_cell   = ParagraphStyle("cell",   parent=styles["Normal"], fontSize=7.5, leading=9)

    story = []
    story.append(Paragraph("<b>Informe de verificación de rotulado — Resolución 5109/2005</b>", style_header))
    story.append(Spacer(1, 3*mm))
    fecha_str = datetime.now().strftime("%Y-%m-%d")
    invima_str = invima_num or "-"
    invima_estado_str = "ACTIVO y coincidente" if invima_estado_ok else "No verificado / No activo / No coincide"
    meta = (
        f"<b>Fecha:</b> {fecha_str} &nbsp;&nbsp; "
        f"<b>Producto:</b> {producto or '-'} &nbsp;&nbsp; "
        f"<b>Tipo:</b> {categoria_producto or '-'} &nbsp;&nbsp; "
        f"<b>Proveedor:</b> {proveedor or '-'} &nbsp;&nbsp; "
        f"<b>Responsable:</b> {responsable or '-'}<br/>"
        f"<b>Registro INVIMA:</b> {invima_str} &nbsp;&nbsp; "
        f"<b>Estado en portal:</b> {invima_estado_str}"
    )
    if invima_url.strip():
        meta += f" &nbsp;&nbsp; <b>Consulta:</b> {invima_url}"
    story.append(Paragraph(meta, style_header))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(f"<b>Cumplimiento (sobre ítems contestados):</b> {porcentaje}%", style_header))
    story.append(Spacer(1, 5*mm))

    # Tabla principal
    data = [["Ítem", "Estado", "Recomendación", "Referencia", "Observación"]]
    for _, r in df.iterrows():
        obs = r["Observación"] or "-"
        if obs != "-":
            obs = split_observation_text(obs, chunk=100)
        data.append([
            Paragraph(str(r["Ítem"]),          style_cell),
            Paragraph(str(r["Estado"]),        style_cell),
            Paragraph(str(r["Recomendación"]), style_cell),
            Paragraph(str(r["Referencia"]),    style_cell),
            Paragraph(obs,                     style_cell),
        ])

    col_widths = [70*mm, 25*mm, 100*mm, 45*mm, 40*mm]
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f2f2f2")),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,0), 8),
        ("GRID",       (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN",     (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",(0,0), (-1,-1), 3),
        ("RIGHTPADDING",(0,0), (-1,-1), 3),
    ]))
    story.append(tbl)

    # Bloque de evidencias fotográficas (solo para ítems 'No cumple')
    # Cada ítem inicia con un subtítulo y sus imágenes (escaladas). Se parte página si es necesario.
    evidencias_total = sum(len(v) for v in st.session_state.evidence.values())
    no_cumple_items = [k for k,v in st.session_state.status.items() if v == "no" and len(st.session_state.evidence.get(k,[]))>0]
    if evidencias_total > 0 and len(no_cumple_items)>0:
        story.append(PageBreak())
        story.append(Paragraph("<b>Evidencia fotográfica de incumplimientos</b>", style_header))
        story.append(Spacer(1, 3*mm))

        max_img_width = 120*mm  # dos por fila si se desea (aquí una por fila por claridad)
        for titulo in no_cumple_items:
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(f"<b>Ítem:</b> {titulo}", style_header))
            ev_list = st.session_state.evidence.get(titulo, [])
            for ev in ev_list:
                # Cargar la imagen desde bytes y escalar
                img_buf = BytesIO(ev["bytes"])
                try:
                    img = RLImage(img_buf)
                    # Escala manteniendo proporción al ancho fijo
                    iw, ih = img.drawWidth, img.drawHeight
                    scale = max_img_width / iw if iw > 0 else 1.0
                    img.drawWidth = max_img_width
                    img.drawHeight = ih * scale
                    story.append(img)
                except Exception:
                    # Si no se puede renderizar, se ignora esa imagen
                    story.append(Paragraph("(No se pudo renderizar la imagen adjunta)", style_cell))
                # Pie de foto
                if ev["caption"]:
                    story.append(Paragraph(ev["caption"], style_cell))
                story.append(Spacer(1, 3*mm))

    doc.build(story)
    buf.seek(0)
    return buf

# ------------------------------------------------------------------
# Botón: Generar PDF
# ------------------------------------------------------------------
st.subheader("Generar informe PDF (A4 horizontal)")
if st.button("Generar PDF"):
    yes_count = sum(1 for v in st.session_state.status.values() if v == "yes")
    no_count = sum(1 for v in st.session_state.status.values() if v == "no")
    answered_count = yes_count + no_count
    percent = round((yes_count / answered_count * 100), 1) if answered_count > 0 else 0.0

    pdf_buffer = generar_pdf(
        df, producto, proveedor, responsable, categoria_producto,
        invima_num, invima_url, invima_estado_ok, percent, nombre_pdf
    )
    file_name = (nombre_pdf.strip() or f"informe_5109_{datetime.now().strftime('%Y%m%d')}") + ".pdf"
    st.download_button("Descargar PDF", data=pdf_buffer, file_name=file_name, mime="application/pdf")


# app_5109_definitiva_v5.py
# Resolución 5109/2005 — Checklist integral (v5)
# - Flujo: INVIMA → Cara frontal → Cara posterior → Condiciones → Documentación
# - Sin herramientas/calculadoras
# - Ejemplos para Lote y Fecha en “Qué verificar”
# - Criterios de legibilidad/veracidad unificados
# - Ítem duplicado removido
# - Responsable ampliado (teléfono, web y “Elaborado para/Por”)
# - Nuevo ítem: “Modo de consumo o instrucciones de consumo”
# - PDF horizontal con portada (v5) y evidencias en página nueva

import streamlit as st
import base64
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage

# ===========================================
# CONFIG INICIAL
# ===========================================
st.set_page_config(page_title="Checklist Rotulado — Resolución 5109/2005 (v5)", layout="wide")
st.title("Checklist de Rotulado — Resolución 5109 de 2005")

# ===========================================
# SIDEBAR / DATOS GENERALES
# ===========================================
st.sidebar.header("Datos de la verificación")
producto   = st.sidebar.text_input("Nombre del producto")
proveedor  = st.sidebar.text_input("Fabricante / Importador / Reenvasador")
responsable= st.sidebar.text_input("Responsable de la verificación")
fecha_verif= st.sidebar.text_input("Fecha del informe (AAAA-MM-DD)", datetime.now().strftime("%Y-%m-%d"))
invima_registro     = st.sidebar.text_input("Registro sanitario INVIMA (producto terminado)")
invima_estado_activo= st.sidebar.checkbox("Verificado ACTIVO y coincidente en el portal INVIMA", value=False)
invima_url          = st.sidebar.text_input("URL de consulta INVIMA (opcional)")
nombre_pdf          = st.sidebar.text_input("Nombre del PDF (sin .pdf)", f"informe_5109_v5_{datetime.now().strftime('%Y%m%d')}")
solo_no             = st.sidebar.checkbox("Mostrar solo 'No cumple'", value=False)

# ===========================================
# CHECKLIST — CATEGORÍAS E ÍTEMS
#  Cada ítem: (titulo, que_verificar, referencia, aplica)
# ===========================================
CATEGORIAS = {
    # 1) INVIMA
    "1. Verificación con INVIMA (registro sanitario)": [
        ("Registro sanitario INVIMA impreso, vigente y coherente con el producto",
        "Verificar con el siguiente checklist.",
        "Resolución 5109/2005 Art. 5.8.",
        "Producto terminado")
    ],
    
    "4. Contenido neto y peso escurrido": [
         ("Contenido neto en cara principal con unidades SI",
          "Que se declare el contenido neto en la cara principal de exhibición, utilizando unidades del Sistema Internacional (g, kg, mL, L), de forma legible, clara y sin incluir el peso o volumen del envase. Cuando se trate de un producto terminado, verificar adicionalmente que se declare el número de porciones conforme a la normativa aplicable.",
          "Resolución 5109/2005 Art. 5.3", "Producto terminado y Materia Prima")
    ],

    # 5) Cara frontal
    "5. Revisión de la cara frontal": [
        ("Lote impreso en el empaque (trazabilidad)",
         "Que este impreso, legible e indeleble. Ejemplos de formato válido (referenciales): "
         "L230401, LOTE230401",
         "Resolución 5109/2005 Art. 5.5", "Producto terminado y Materia Prima"),
        ("Fecha de vencimiento o duración mínima impresa",
         "Que sea clara, legible y se encuentre en el empaque. Ejemplos de formato válido (según caso): "
         "DD/MM/AAAA, DD-MM-AAAA, o MMM/AAAA (duración mínima). "
         "Fecha límite de consumo recomendada, Fecha de caducidad, Fecha de vencimiento (F. Vto.), "
         "Vence (Ven.), Expira (Exp.), Consumase antes de.",
         "Resolución 5109/2005 Art. 5.5.", "Producto terminado y Materia Prima"),
    ],

    # 6) Cara posterior
    "6. Revisión de la cara posterior": [
        ("Lista de ingredientes, aditivos y declaración de alérgenos",
          "Con ayuda del mini checklist realizar revisión",
          "Resolución 5109/2005 Art. 5.2.", "Producto terminado y Materia Prima"),
        ("País de origen",
         "Declarar “Hecho en …” o “Producto de …” cuando aplique.",
         "Resolución 5109/2005 Art. 5.4.2.", "Producto terminado y Materia Prima"),
        ("Condiciones de conservación",
         "Declarar condiciones especiales de conservación para preservar inocuidad y vida útil (p. ej., refrigeración a 4 °C).",
         "Resolución 5109/2005 Art. 5.9.1 y 5.9.2.", "Producto terminado y Materia Prima"),
        ("Instrucciones de uso, preparación y consumo (cuando aplique)",
         "Incluir instrucciones claras y suficientes para el uso, preparación y consumo seguro y adecuado del alimento, cuando corresponda. Indicar de forma expresa la manera correcta de consumo o preparación (por ejemplo: “Agítese antes de usar”, “Listo para consumir”, “Servir frío”, “Agregar agua antes de usar”, “Porción sugerida”), asegurando que la información sea comprensible para el consumidor.",
         "Resolución 5109 de 2005, Artículos 5.9 y 5.9.2",
         "Producto terminado"),
        ("Nombre y dirección del responsable (fabricante / importador / reenvasador)",
         "Que se Declare la razón social y la dirección completa del responsable del alimento, de forma clara y legible. Utilizar exactamente las expresiones establecidas en la normativa según corresponda: “FABRICADO o ENVASADO POR”, o “FABRICADO, ENVASADO O REEMPACADO POR (FABRICANTE, ENVASADOR O REEMPACADOR) PARA: (PERSONA NATURAL O JURÍDICA AUTORIZADA PARA COMERCIALIZAR EL ALIMENTO)”. Para **producto terminado**, verificar que esta identificación coincida con el registro sanitario INVIMA, adicionalmente, que declare información de contacto la cual facilita la trazabilidad y comunicación, como teléfono, correo electrónico u otros datos de contacto del proveedor o fabricante, en coherencia con la documentación sanitaria y comercial.",
         "Resolución 5109 de 2005, Art. 5.3; Resolución 810 de 2021; Resolución 2492 de 2022; Ley 1480 de 2011", "Producto terminado y Materia Prima"),
        ("Idioma en español (o rótulo complementario si es importado)",
         "Toda la información obligatoria debe estar en español; en importados, adherir rótulo complementario traducido.",
         "Resolución 5109/2005 Art. 4.4", "Producto terminado y Materia Prima")
    ],

    # 7) Condiciones particulares
    "7. Condiciones particulares": [
        ("Producto reenvasado (establecimiento autorizado)",
         "Conservar la información original e incluir responsable del reenvasado con dirección.",
         "Resolución 5109/2005 Art. 5.4", "Producto reenvasado"),
        ("Venta a granel o fraccionados",
         "Exhibir información mínima mediante cartel/rótulo: denominación, ingredientes (si aplica), responsable, país de origen, "
         "lote y fecha en envase inmediato.",
         "Resolución 5109/2005 (principios de información al consumidor).", "Producto a granel"),
        ("Envases muy pequeños (limitación de espacio)",
         "Usar medios complementarios (insertos/etiquetas adicionales) si el espacio no permite toda la información esencial.",
         "Resolución 5109/2005 Art. 4.3 y 4.4", "Producto terminado"),
        ("Multipacks o envases secundarios",
         "El envase secundario debe repetir la información esencial o referir claramente al envase primario.",
         "Criterio práctico de información al consumidor.", "Producto terminado"),
    ],
}

# ===========================================
# ESTADO / NOTAS / EVIDENCIAS
# ===========================================
if "status_5109_v5" not in st.session_state:
    st.session_state.status_5109_v5 = {i[0]: "none" for c in CATEGORIAS.values() for i in c}
if "note_5109_v5" not in st.session_state:
    st.session_state.note_5109_v5   = {i[0]: "" for c in CATEGORIAS.values() for i in c}
if "evidence_5109_v5" not in st.session_state:
    st.session_state.evidence_5109_v5 = {i[0]: [] for c in CATEGORIAS.values() for i in c}

def _wrap(text: str, chunk: int = 110) -> str:
    if not text:
        return ""
    s = str(text)
    return "\\n".join([s[i:i+chunk] for i in range(0, len(s), chunk)])

# ===========================================
# UI — CHECKLIST
# ===========================================
st.header("Checklist — Resolución 5109/2005")
st.markdown("Responde con ✅ Cumple / ❌ No cumple / ⚪ No aplica. Si marcas **No cumple**, podrás **adjuntar evidencia**.")

for categoria, items in CATEGORIAS.items():
    st.subheader(categoria)
    for (titulo, que_verificar, referencia, aplica) in items:
        estado = st.session_state.status_5109_v5.get(titulo, "none")
        if solo_no and estado != "no":
            continue

        st.markdown(f"### {titulo}")
        st.markdown(f"**Qué verificar:** {que_verificar}")
        st.markdown(f"**Referencia normativa:** {referencia}")
        st.caption(f"Aplica a: {aplica}")

        if titulo == "Lista de ingredientes, aditivos y declaración de alérgenos":
            
            with st.expander("Desglose de verificación — Ingredientes", expanded=False):
                
                checklist_ingredientes = [
                    "Lista encabezada con la palabra “Ingredientes:”",
                    "Ingredientes declarados en orden decreciente de peso y no se omiten ingredientes presentes en la formulación",
                    "Aditivos alimentarios declarados  ej., Conservante (Sorbato de potasio)",
                    "Alérgenos declarados cuando aplique gluten (trigo/cebada/centeno/avena), huevo, leche (incl. lactosa), soya, maní, frutos secos, pescado, crustáceos, mostaza, apio, sésamo, sulfitos ≥10 mg/kg."
                ]
                
                for item in checklist_ingredientes:
                    st.checkbox(
                        item,
                        key=f"cp_ing_{item}"
                    )


        if titulo == "Registro sanitario INVIMA impreso, vigente y coherente con el producto":
            st.markdown("#### Mini checklist — Verificación INVIMA")
            checks_invima = {
               "Registro sanitario INVIMA impreso en el empaque de forma visible, legible e indeleble": False,
               "Registro sanitario vigente y en estado ACTIVO según portal INVIMA": False,
               "Marca declarada coincide con la registrada ante INVIMA (cuando aplique)": False,
               "Nombre del producto coincide con la ficha del registro sanitario": False,
               "Denominación del alimento corresponde a su verdadera naturaleza": False,
               "La marca o nombre de fantasía no sustituye la denominación del alimento": False,
               "Denominación visible en la cara principal de exhibición": False,
               "Presentaciones comerciales coinciden con las autorizadas en el registro": False,
            }
            
            for check in checks_invima:
                checks_invima[check] = st.checkbox(
                    check,
                    key=f"invima_{check}"
                )

        if titulo == "Contenido neto en cara principal con unidades SI":
            st.markdown("#### Anexo — Altura mínima de números y letras del contenido neto (Res. 5109/2005)")
            st.markdown("""
            **a) Según el área de la cara principal de exhibición**

| Área de la cara principal (cm²) | Altura mínima números y letras (impreso / adhesivo) | Altura mínima rótulo soplado, formado o moldeado |
|-------------------------------|-----------------------------------------------------|--------------------------------------------------|
| Hasta 16                      | 2 mm                                                | 3 mm                                             |
| > 16 a 100                    | 3 mm                                                | 4 mm                                             |
| > 100 a 225                   | 4 mm                                                | 6 mm                                             |
| > 225 a 400                   | 5 mm                                                | 7 mm                                             |
| > 400 a 625                   | 7 mm                                                | 8 mm                                             |
| > 625 a 900                   | 9 mm                                                | 9 mm                                             |
| > 900                         | Proporcional (≥ 9 mm)                               | Proporcional (≥ 9 mm)                            |
""")
            st.markdown("""
**b) Criterio técnico de referencia internacional — Directiva 76/211/EEC (Unión Europea)**  
*(Referencia informativa; no sustituye la Resolución 5109/2005)*

| Contenido neto | Altura mínima de números y letras |
|---------------|-----------------------------------|
| ≤ 200 g o mL  | 3 mm                              |
| > 200 g o mL hasta 1 kg o L       | 4 mm                              |
| > 1 kg o L    | 6 mm                              |
""")

        c1, c2, c3, _ = st.columns([0.12, 0.12, 0.12, 0.64])
        with c1:
            if st.button("✅ Cumple", key=f"{titulo}_yes"):
                st.session_state.status_5109_v5[titulo] = "yes"
        with c2:
            if st.button("❌ No cumple", key=f"{titulo}_no"):
                st.session_state.status_5109_v5[titulo] = "no"
        with c3:
            if st.button("⚪ No aplica", key=f"{titulo}_na"):
                st.session_state.status_5109_v5[titulo] = "na"

        estado = st.session_state.status_5109_v5[titulo]
        if estado == "yes":
            st.markdown("<div style='background:#e6ffed;padding:6px;border-radius:5px;'>✅ Cumple</div>", unsafe_allow_html=True)
        elif estado == "no":
            st.markdown("<div style='background:#ffe6e6;padding:6px;border-radius:5px;'>❌ No cumple</div>", unsafe_allow_html=True)
        elif estado == "na":
            st.markdown("<div style='background:#f2f2f2;padding:6px;border-radius:5px;'>⚪ No aplica</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#fff;padding:6px;border-radius:5px;'>Sin responder</div>", unsafe_allow_html=True)

        nota = st.text_area("Observación (opcional)", value=st.session_state.note_5109_v5.get(titulo, ""), key=f"{titulo}_nota")
        st.session_state.note_5109_v5[titulo] = nota

        if st.session_state.status_5109_v5[titulo] == "no":
            st.markdown("**Adjunta evidencia (JPG/PNG):**")
            files = st.file_uploader("Subir imágenes", type=["jpg","jpeg","png"], accept_multiple_files=True, key=f"upl_{titulo}")
            if files:
                caption = st.text_input("Descripción breve para estas imágenes (opcional)", key=f"cap_{titulo}")
                if st.button("Agregar evidencia", key=f"btn_add_{titulo}"):
                    for f in files:
                        st.session_state.evidence_5109_v5[titulo].append({
                            "name": f.name,
                            "base64": base64.b64encode(f.read()).decode("utf-8"),
                            "caption": caption or ""
                        })
                    st.success(f"Se agregaron {len(files)} imagen(es) a: {titulo}")
            ev_list = st.session_state.evidence_5109_v5.get(titulo, [])
            if ev_list:
                st.markdown("**Evidencia acumulada:**")
                cols = st.columns(4)
                for idx, ev in enumerate(ev_list):
                    img_bytes = base64.b64decode(ev["base64"])
                    with cols[idx % 4]:
                        st.image(img_bytes, caption=ev.get("caption") or ev.get("name"), use_column_width=True)

        st.markdown("---")

# ===========================================
# MÉTRICAS
# ===========================================
yes_count = sum(1 for v in st.session_state.status_5109_v5.values() if v == "yes")
no_count  = sum(1 for v in st.session_state.status_5109_v5.values() if v == "no")
answered_count = yes_count + no_count
percent = round((yes_count / answered_count * 100), 1) if answered_count > 0 else 0.0
st.metric("Cumplimiento total (sobre ítems contestados)", f"{percent}%")
st.write(
    f"CUMPLE: {yes_count} — NO CUMPLE: {no_count} — "
    f"NO APLICA: {sum(1 for v in st.session_state.status_5109_v5.values() if v == 'na')} — "
    f"SIN RESPONDER: {sum(1 for v in st.session_state.status_5109_v5.values() if v == 'none')}"
)

# ===========================================
# PDF (horizontal) — portada (v5) + evidencias
# ===========================================
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
    # Portada v5
    fecha_str = fecha_verif or datetime.now().strftime("%Y-%m-%d")
    portada = (
        f"<b>Informe de verificación — Rotulado general (Res. 5109/2005 v5)</b><br/>"
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
    story.append(Paragraph(f"<b>Cumplimiento (sobre ítems contestados):</b> {percent}%", style_header))
    story.append(Spacer(1, 4*mm))

    # Tabla
    data = [["Ítem", "Estado", "Observación", "Referencia"]]
    for items in CATEGORIAS.values():
        for (titulo, _, referencia, _) in items:
            estado_val = st.session_state.status_5109_v5.get(titulo, "none")
            estado_humano = (
                "Cumple" if estado_val == "yes"
                else "No cumple" if estado_val == "no"
                else "No aplica" if estado_val == "na"
                else "Sin responder"
            )
            obs = st.session_state.note_5109_v5.get(titulo, "") or "-"
            obs = "-" if obs.strip() == "" else _wrap(obs, 110)
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
    any_ev = any(len(v) > 0 for v in st.session_state.evidence_5109_v5.values())
    if any_ev:
        story.append(PageBreak())
        story.append(Paragraph("<b>Evidencia fotográfica</b>", style_header))
        story.append(Spacer(1, 3*mm))
        for titulo, ev_list in st.session_state.evidence_5109_v5.items():
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
            story.append(Spacer(1, 4*mm))

    doc.build(story)
    buf.seek(0)
    return buf

# ===========================================
# EXPORTAR PDF
# ===========================================
st.subheader("Generar informe PDF")
if st.button("Generar PDF"):
    pdf_buffer = generar_pdf()
    file_name = (nombre_pdf.strip() or f"informe_5109_v5_{datetime.now().strftime('%Y%m%d')}") + ".pdf"
    st.download_button("Descargar PDF", data=pdf_buffer, file_name=file_name, mime="application/pdf")

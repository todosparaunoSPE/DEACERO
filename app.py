import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from PIL import Image
import os

# Configuración de la página
st.set_page_config(
    page_title="DEACERO - Dashboard de Energía y Sustentabilidad",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar imagen DEACERO
def load_image():
    try:
        image_path = os.path.join("images", "images.png")
        deacero_logo = Image.open(image_path)
        return deacero_logo
    except FileNotFoundError:
        try:
            deacero_logo = Image.open("images.png")
            return deacero_logo
        except:
            return None

deacero_logo = load_image()

# Generador de datos de ejemplo
def generate_data():
    dates = pd.date_range(start="2023-01-01", end="2023-12-31")
    energy_data = pd.DataFrame({
        "Fecha": dates,
        "Consumo_MWh": np.random.normal(loc=500, scale=50, size=len(dates)).cumsum(),
        "Costo_MXN": np.random.normal(loc=100000, scale=5000, size=len(dates)).cumsum(),
        "Emisiones_CO2": np.random.normal(loc=200, scale=10, size=len(dates)).cumsum(),
        "Planta": np.random.choice(["Acero 1", "Acero 2", "Fundición"], size=len(dates))
    })
    
    sustainability = pd.DataFrame({
        "Metrica": ["Energía renovable", "Agua reciclada", "Material reciclado", "Eficiencia energética"],
        "Porcentaje": [15, 45, 78, 62],
        "Objetivo_2025": [30, 60, 85, 75]
    })
    
    return energy_data, sustainability

# Cargar datos
energy_df, sustainability_df = generate_data()

# Sidebar con filtros mejorados
with st.sidebar:
    if deacero_logo:
        st.image(deacero_logo, width=200)
    else:
        st.image("https://via.placeholder.com/200x50?text=DEACERO", width=200)
    
    st.title("Filtros")
    
    # Filtros de fecha
    fecha_inicio = st.date_input(
        "Fecha inicio",
        value=datetime(2023, 1, 1),
        min_value=datetime(2023, 1, 1),
        max_value=datetime(2023, 12, 31)
    )
    
    fecha_fin = st.date_input(
        "Fecha fin",
        value=datetime(2023, 12, 31),
        min_value=datetime(2023, 1, 1),
        max_value=datetime(2023, 12, 31)
    )
    
    # Filtro de plantas mejorado
    st.markdown("**Seleccionar plantas**")
    
    # Obtener plantas disponibles en el rango de fechas seleccionado
    plantas_disponibles = energy_df[
        (energy_df["Fecha"] >= pd.to_datetime(fecha_inicio)) & 
        (energy_df["Fecha"] <= pd.to_datetime(fecha_fin))
    ]["Planta"].unique().tolist()
    
    # Inicializar session_state si no existe
    if 'plantas_seleccionadas' not in st.session_state:
        st.session_state.plantas_seleccionadas = plantas_disponibles.copy()
    
    # Verificar y sincronizar plantas seleccionadas con las disponibles
    st.session_state.plantas_seleccionadas = [
        p for p in st.session_state.plantas_seleccionadas 
        if p in plantas_disponibles
    ]
    
    # Checkboxes para cada planta
    for planta in plantas_disponibles:
        if st.checkbox(
            planta,
            value=planta in st.session_state.plantas_seleccionadas,
            key=f"planta_{planta}"
        ):
            if planta not in st.session_state.plantas_seleccionadas:
                st.session_state.plantas_seleccionadas.append(planta)
        else:
            if planta in st.session_state.plantas_seleccionadas:
                st.session_state.plantas_seleccionadas.remove(planta)
    
    # Botón para resetear selección
    if st.button("Seleccionar todas"):
        st.session_state.plantas_seleccionadas = plantas_disponibles.copy()
    
    st.markdown("---")
    st.markdown("**Configuración de alertas**")
    alerta_consumo = st.slider("Umbral consumo (MWh)", 400, 600, 550)
    st.markdown("---")
    st.caption("Última actualización: " + datetime.now().strftime("%d/%m/%Y %H:%M"))

# Filtrar datos usando las plantas seleccionadas
filtered_df = energy_df[
    (energy_df["Planta"].isin(st.session_state.plantas_seleccionadas)) & 
    (energy_df["Fecha"] >= pd.to_datetime(fecha_inicio)) & 
    (energy_df["Fecha"] <= pd.to_datetime(fecha_fin))
]

# Header del dashboard
st.title("📊 Dashboard de Energía y Sustentabilidad")
st.markdown("""
<style>
.big-font {
    font-size:18px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<p class="big-font">Monitoreo operativo y métricas de sustentabilidad | {fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}</p>', 
            unsafe_allow_html=True)

# KPI Cards
st.markdown("## 📈 Indicadores Clave")
col1, col2, col3, col4 = st.columns(4)

with col1:
    consumo_total = filtered_df["Consumo_MWh"].iloc[-1] - filtered_df["Consumo_MWh"].iloc[0]
    delta_consumo = (consumo_total / filtered_df["Consumo_MWh"].iloc[0]) * 100
    st.metric("Consumo Energético", f"{consumo_total:,.0f} MWh", 
              f"{delta_consumo:+.1f}% vs periodo")

with col2:
    costo_total = filtered_df["Costo_MXN"].iloc[-1] - filtered_df["Costo_MXN"].iloc[0]
    delta_costo = (costo_total / filtered_df["Costo_MXN"].iloc[0]) * 100
    st.metric("Costo Energía", f"${costo_total:,.0f} MXN", 
              f"{delta_costo:+.1f}% vs periodo")

with col3:
    co2_total = filtered_df["Emisiones_CO2"].iloc[-1] - filtered_df["Emisiones_CO2"].iloc[0]
    delta_co2 = (co2_total / filtered_df["Emisiones_CO2"].iloc[0]) * 100
    st.metric("Emisiones CO2", f"{co2_total:,.0f} ton", 
              f"{delta_co2:+.1f}% vs periodo")

with col4:
    eficiencia = sustainability_df[sustainability_df["Metrica"] == "Eficiencia energética"]["Porcentaje"].values[0]
    objetivo = sustainability_df[sustainability_df["Metrica"] == "Eficiencia energética"]["Objetivo_2025"].values[0]
    st.metric("Eficiencia Energética", f"{eficiencia}%", 
              f"Objetivo 2025: {objetivo}%")

# Gráficos principales
tab1, tab2, tab3 = st.tabs(["📈 Tendencias", "🌱 Sustentabilidad", "🚨 Alertas"])

with tab1:
    st.markdown("### Tendencias de Consumo y Costo")
    
    fig = go.Figure()
    
    for planta in filtered_df["Planta"].unique():
        df_planta = filtered_df[filtered_df["Planta"] == planta]
        fig.add_trace(go.Scatter(
            x=df_planta["Fecha"],
            y=df_planta["Consumo_MWh"].diff().fillna(0),
            name=f"Consumo {planta}",
            yaxis="y1"
        ))
        
        fig.add_trace(go.Scatter(
            x=df_planta["Fecha"],
            y=df_planta["Costo_MXN"].diff().fillna(0) / 1000,
            name=f"Costo {planta} (Miles MXN)",
            yaxis="y2"
        ))
    
    fig.update_layout(
        title="Consumo Diario y Costo por Planta",
        yaxis=dict(title="Consumo (MWh/día)"),
        yaxis2=dict(title="Costo (Miles MXN/día)", overlaying="y", side="right"),
        hovermode="x unified",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    fig2 = px.area(
        filtered_df, 
        x="Fecha", 
        y="Emisiones_CO2", 
        color="Planta",
        title="Acumulado de Emisiones CO2 (ton)"
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("### Indicadores de Sustentabilidad")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            sustainability_df,
            x="Metrica",
            y=["Porcentaje", "Objetivo_2025"],
            barmode="group",
            title="Progreso de Metas de Sustentabilidad",
            labels={"value": "Porcentaje (%)", "variable": "Tipo"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        filtered_df["Dia_Semana"] = filtered_df["Fecha"].dt.day_name()
        filtered_df["Semana"] = filtered_df["Fecha"].dt.isocalendar().week
        
        heatmap_data = filtered_df.groupby(["Dia_Semana", "Semana"])["Consumo_MWh"].mean().unstack()
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        heatmap_data = heatmap_data.reindex(days_order)
        
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Semana", y="Día", color="Consumo (MWh)"),
            title="Consumo Promedio por Día de la Semana"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### Alertas y Oportunidades")
    
    max_consumo = filtered_df.groupby("Planta")["Consumo_MWh"].max().reset_index()
    alertas = max_consumo[max_consumo["Consumo_MWh"] > alerta_consumo]
    
    if not alertas.empty:
        st.warning("🚨 Alertas de Consumo Elevado")
        for _, row in alertas.iterrows():
            st.error(f"Planta {row['Planta']}: Consumo máximo de {row['Consumo_MWh']:,.0f} MWh (umbral: {alerta_consumo} MWh)")
    else:
        st.success("✅ Ningún consumo excede los umbrales configurados")
    
    st.markdown("---")
    
    st.markdown("💡 **Oportunidades identificadas**")
    
    oportunidades = [
        {"Tipo": "Energía", "Descripción": "Instalación de paneles solares en Planta Acero 1", "Ahorro Estimado": "15% costo energético"},
        {"Tipo": "Agua", "Descripción": "Sistema de recirculación para proceso de enfriamiento", "Ahorro Estimado": "2.5M litros/año"},
        {"Tipo": "Emisiones", "Descripción": "Actualización a hornos de alta eficiencia", "Ahorro Estimado": "8% reducción CO2"}
    ]
    
    for op in oportunidades:
        with st.expander(f"{op['Tipo']}: {op['Descripción']}"):
            st.markdown(f"**Ahorro estimado:** {op['Ahorro Estimado']}")
            st.button("Ver análisis detallado", key=f"btn_{op['Tipo']}")

# Footer con logo
st.markdown("---")
footer_col1, footer_col2 = st.columns([1, 4])

with footer_col1:
    if deacero_logo:
        st.image(deacero_logo, width=150)
    else:
        st.image("https://via.placeholder.com/150x50?text=DEACERO", width=150)

with footer_col2:
    st.markdown("""
    **Contacto:**  
    - Javier Horacio Pérez Ricárdez  
    - email: jahoperi@gmail.com  
    - Celular: +52 56 1056 4095  
    """)
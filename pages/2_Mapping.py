import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
from folium import Choropleth
from streamlit_folium import st_folium
import os

# ruta absoluta del script actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# ruta relativa de los ficheros
csv_file_path = os.path.join(current_dir, '50039bsc.csv')
shapefile_path = os.path.join(current_dir, 'SECC_CE_20230101.geojson')
# Función para cargar el DataFrame desde un archivo CSV (se ejecuta solo una vez)
@st.cache_data
def load_data():
    df = pd.read_csv(csv_file_path, delimiter=';', encoding='latin-1')
    df['Total'] = df.Total.apply(lambda x: float(x.replace(',', '.')))
    df['periodo'] = df.periodo.astype(int)
    df['NCA'] = df['Comunidades y Ciudades Autónomas']
    code = {name: str(f'{i:02d}') for i, name in enumerate(df['NCA'].unique().tolist(), start=1)}
    df['CCA'] = df.NCA.apply(lambda x:code[x])
    # df['CCA'] = df['CCA'].astype('str')
    df.drop(['Comunidades y Ciudades Autónomas'], axis=1, inplace=True)
    return df

@st.cache_data
def load_geo_data():
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf.loc[:, ['CCA', 'NCA', 'geometry']]
    gdf['CCA'] = gdf['CCA'].astype('str')
    cca_gdf = gdf.dissolve(by='CCA', aggfunc='first').reset_index()
    cca_gdf['centroid'] = cca_gdf.centroid
    cca_gdf = cca_gdf.set_crs("EPSG:4326")
    return cca_gdf

@st.cache_data
def get_unique_lists(df):
    equipamiento = df['Tipo de equipamiento'].unique().tolist()
    periodo_max = max(df['periodo'])+1
    periodo_min = min(df['periodo'])
    return equipamiento, list(range(periodo_min, periodo_max))

def display_detail_map(df, gdf, selected_equipamiento, periodo):
    st.title(f'Encuesta sobre Equipamiento y Uso de Tecnologías de Información: {selected_equipamiento}')
    filtered_df = df[df['Tipo de equipamiento'] == selected_equipamiento]
    filtered_df = filtered_df[filtered_df['periodo'] == periodo]
    m = folium.Map(location=[40.42, -3.7], zoom_start=5)
    new_gdf = gdf.copy()
    new_gdf.drop(['centroid'], axis=1, inplace=True)
    new_gdf = new_gdf.merge(filtered_df, left_on='CCA', right_on='CCA')
    tooltip = folium.features.GeoJsonTooltip(
        fields=['CCA', 'NCA_y', 'Total', 'periodo'],
        aliases=['CCA:', 'NCA:', 'Total (%):', 'Periodo:'],
        localize=True,
        sticky=False
    )
    
    folium.Choropleth(
        geo_data=new_gdf,
        data=new_gdf,
        columns=['CCA', 'Total'],
        key_on='feature.properties.CCA',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name="Tasa de equipamiento tecnológico (%)"
    ).add_to(m)
    
    folium.GeoJson(
        new_gdf,
        name='geojson',
        style_function=lambda feature: {
            'fillOpacity': 0,
            'color': 'black',
            'weight': 0.5,
            'line_opacity': 0.5
        },
        highlight_function=lambda x: {'weight': 2, 'color': 'black'},
        tooltip=tooltip
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    st_map = st_folium(m)
    # st_map

def display_map(df, gdf, selected_equipamiento, periodo):
    st.title(f'Encuesta sobre Equipamiento y Uso de Tecnologías de Información: {selected_equipamiento}')
    filtered_df = df[df['Tipo de equipamiento'] == selected_equipamiento]
    filtered_df = filtered_df[filtered_df['periodo'] == periodo]
    new_gdf = gdf.copy()
    merged_gdf = new_gdf.merge(filtered_df, left_on='CCA', right_on='CCA')

    fig, ax = plt.subplots(figsize=(25, 25))
    merged_gdf.plot(column='Total', cmap='YlOrRd', linewidth=0.8, ax=ax, edgecolor='1.0', legend=True,)
    for idx, row in merged_gdf.iterrows():
        plt.annotate(text=row['NCA_y'], xy=(row['centroid'].x, row['centroid'].y), ha='center', fontsize=12)
    ax.set_axis_off()

    st.pyplot(fig)
# Carga del DataFrame
df = load_data()
gdf = load_geo_data()
equipamiento, periodo = get_unique_lists(df)

# Título 
# st.title('Encuesta sobre Equipamiento y Uso de Tecnologías de Información y Comunicación en los Hogares, Comunidades Autónomas, Viviendas que disponen de acceso a Internet')

# Sidebar con los checkboxes de las comunidades autónomas y el equipamiento
st.sidebar.title('Filtros')
selected_equipamiento = st.sidebar.radio('Equipamiento', equipamiento)

# Control de rango de años
periodo = st.sidebar.radio('Período', periodo)

# Control de mapa
mapa = st.sidebar.radio('Mapa', ['Simple','Detallado'])

# Mostrar los filtros seleccionados
st.sidebar.markdown('---')
st.sidebar.markdown('**Filtros seleccionados:**')
st.sidebar.markdown(f'Equipamiento: {selected_equipamiento}')
st.sidebar.markdown(f'Período: {periodo}')

# Mostrar tipo mapas
if mapa=='Simple':
    display_map(df, gdf, selected_equipamiento, periodo)
else:
    display_detail_map(df, gdf, selected_equipamiento, periodo)

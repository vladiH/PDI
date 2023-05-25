import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os
# Get the absolute path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the relative file paths based on the current script location
csv_file_path = os.path.join(current_dir, '50039bsc.csv')

# Función para cargar el DataFrame desde un archivo CSV (se ejecuta solo una vez)
@st.cache_data
def load_data():
    df = pd.read_csv(csv_file_path, delimiter=';', encoding='latin-1')
    df['Total'] = df.Total.apply(lambda x: float(x.replace(',', '.')))
    df['periodo'] = df.periodo.astype(int)
    return df

@st.cache_data
def get_unique_lists(df):
    comunidades = df['Comunidades y Ciudades Autónomas'].unique() .tolist()
    equipamiento = df['Tipo de equipamiento'].unique().tolist()
    periodo_max = max(df['periodo'])
    periodo_min = min(df['periodo'])
    return comunidades, equipamiento, periodo_min, periodo_max

# Función para procesar los datos y generar el gráfico de líneas
# @st.cache_data
def process_data(df, selected_comunidades, selected_equipamiento, periodo, tipo):
    st.title(f'Encuesta sobre Equipamiento y Uso de Tecnologías de Información:{selected_equipamiento}')
    # Aplicar filtros a los datos
    filtered_df = df[df['Comunidades y Ciudades Autónomas'].isin(selected_comunidades)]
    filtered_df = filtered_df[filtered_df['Tipo de equipamiento']==selected_equipamiento]
    filtered_df = filtered_df[(filtered_df['periodo'] >= periodo[0]) & (filtered_df['periodo'] <= periodo[1])]

    # Group the data by 'Comunidades y Ciudades Autónomas' and 'Tipo de equipamiento'
    grouped_df = filtered_df.groupby(['Comunidades y Ciudades Autónomas', 'Tipo de equipamiento'])

    chart_data = None 
    for (comunidad, equipamiento), group in grouped_df:
        if chart_data is None:
            chart_data = group[['periodo', 'Total']].set_index('periodo').rename(columns={'Total': comunidad})
        else:
            chart_data = chart_data.merge(group[['periodo', 'Total']].set_index('periodo').rename(columns={'Total': comunidad}), left_index=True, right_index=True)

    if tipo=='Linea':
        st.line_chart(chart_data)
    if tipo == "Barra":
        st.bar_chart(chart_data)

# Carga del DataFrame
df = load_data()
comunidades, equipamiento, periodo_desde,  periodo_hasta = get_unique_lists(df)

# Título
# st.title('Encuesta sobre Equipamiento y Uso de Tecnologías de Información y Comunicación en los Hogares, Comunidades Autónomas, Viviendas que disponen de acceso a Internet')

# Sidebar con los checkboxes de las comunidades autónomas y el equipamiento
st.sidebar.title('Filtros')
selected_comunidades = st.sidebar.multiselect('Comunidades Autónomas', comunidades, default=comunidades[0])
selected_equipamiento = st.sidebar.radio('Equipamiento', equipamiento)

# Control de rango de años
periodo = st.sidebar.slider('Período', periodo_desde, periodo_hasta, (periodo_desde, periodo_hasta))

# Control de tipo grafico
grafica = st.sidebar.radio('Grafico', ['Linea','Barra'])
# Mostrar los filtros seleccionados
st.sidebar.markdown('---')
st.sidebar.markdown('**Filtros seleccionados:**')
st.sidebar.markdown(f'Comunidades Autónomas: {", ".join(selected_comunidades)}')
st.sidebar.markdown(f'Equipamiento: {selected_equipamiento}')
st.sidebar.markdown(f'Período: {periodo[0]} - {periodo[1]}')

# Procesar los datos y generar el gráfico de líneas
process_data(df, selected_comunidades, selected_equipamiento, periodo, grafica)

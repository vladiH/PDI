import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="PDI",
        page_icon="📊",
    )

    st.write("# Producción de Imagen Digital 📊")

    st.markdown(
        """
        Evolución de datos de Viviendas (2006-2021) por Comunidades y Ciudades Autónomas, tipo de equipamiento y periodo
        ### Tipos de graficos
        - Lineas 📈
        - Mapas 🌍
    """
    )


if __name__ == "__main__":
    run()

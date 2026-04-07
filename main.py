import streamlit as st
import json
from pathlib import Path

st.title("Optimizador de Compras")

json_path = Path("data/heb_productos.json")

if not json_path.exists():
    st.error("No existe data/heb_productos.json. Ejecuta primero el scraper de HEB.")
    st.stop()

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

if not data:
    st.warning("El JSON no contiene productos.")
    st.stop()

if isinstance(data, dict):
    busquedas = list(data.keys())
    producto_seleccionado = st.selectbox("Producto buscado", busquedas)
    productos = data.get(producto_seleccionado, [])
else:
    productos = data

st.subheader("Resultados de HEB")
st.metric("Productos encontrados", len(productos))

productos_por_fila = 3

for inicio in range(0, len(productos), productos_por_fila):
    fila = productos[inicio:inicio + productos_por_fila]
    columnas = st.columns(productos_por_fila)

    for col, producto in zip(columnas, fila):
        with col:
            imagen = producto.get("imagen")
            if imagen:
                st.image(imagen, use_container_width=True)
            else:
                st.caption("Sin imagen")

            st.markdown(f"**{producto.get('nombre', 'Sin nombre')}**")
            st.write(producto.get("precio", "N/D"))

            link = producto.get("link")
            if link:
                st.link_button("Ver producto", link)
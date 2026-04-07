import streamlit as st
import time

# configuración de la página y Estilos CSS 
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    /* titulo*/
    .title-left {
        text-align: left;
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* Estilo para categorias*/
    div[data-testid="stBaseButton-secondary"]:hover {
        background-color: #E1F564 !important; /* Amarillo */
        color: black !important;
        border: 1px solid #000000 !important;
    }
    
    /* estilo para las opciones */
    div[data-testid="stCheckbox"]:hover {
        background-color: #5DF55D; /* Verde */
        border-radius: 5px;
        padding: 4px;
        transition: 0.3s;
    }
            
    div[data-testid="stBaseButton-primary"]:hover {
        background-color: #537AF5 !important; /* Azul */
        color: white !important;
        border: 1px solid #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

#titulo
st.markdown('<div class="title-left">Compras Inteligentes</div>', unsafe_allow_html=True)

# categorías y productos
productos = {
    "🧼 Higiene personal": ["🚿 Shampoo", "🧼 Jabón corporal", "🪥 Pasta dental", "🧴 Desodorante", "🧻 Papel higiénico"],
    "🪄 Limpieza del hogar": ["👕 Detergente para ropa", "☁️ Suavizante", "🌊 Cloro", "✨ Limpiador multiusos", "🧽 Esponjas"],
    "🍳 Alimentos Básicos": ["🥛 Leche", "🥚 Huevo", "🍞 Pan", "🍚 Arroz", "🫘 Frijol"],
    "🍎 Frutas y verduras": ["🍏 Manzana", "🍌 Plátano", "🍅 Tomate", "🧅 Cebolla", "🥔 Papa"],
    "🥫 Despensa / abarrotes": ["🧉 Aceite", "🐟 Atún", "🍬 Azúcar", "☕ Café", "🍪 Galletas"]
}

# categorias
st.write("### Selecciona una categoría:")
colum = st.columns(len(productos))

# Usamos session_state para recordar qué categoría se hizo clic
if 'categoria_actual' not in st.session_state:
    st.session_state.categoria_actual = None

for i, categoria in enumerate(productos.keys()):
    if colum[i].button(categoria, use_container_width=True):
        st.session_state.categoria_actual = categoria


#despliega opciones segun la categoria
if st.session_state.categoria_actual:
    st.write(f"---")
    st.write(f"**Opciones para {st.session_state.categoria_actual}:**")
    
    # Mostrar los productos de la categoría
    opciones = productos[st.session_state.categoria_actual]
    sub_colum = st.columns(len(opciones))
    
    for j, producto in enumerate(opciones):
        sub_colum[j].checkbox(producto, key=f"prod_{producto}")

st.write("---")

# compara y descricpion del producto
productos_desc = st.text_area("Describe qué productos quieres comprar con algunas características...", 
                             placeholder="(producto, marca, sabor,...)")

def comparar():
    with st.expander("Resultados de la búsqueda"):
        st.write(f"Analizando precios para: **{productos_desc}**")
        st.info("Aquí aparecería la comparación de precios.")


if st.button("Comparar", type="primary", use_container_width=True):
    with st.spinner("Cargando...", show_time=True):
        time.sleep(2) # Simula el tiempo de espera
        st.success("¡Listo!")
    comparar()
    if st.button("Cerrar",type="secondary"):
        st.rerun()
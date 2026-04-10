#Libreria Streamlit para la interfaz de usuario
import streamlit as st
#Importar funcion para obtener los productos segun la categoria
from utils.getBestOptions import getBestOptions

# configuración de la página
st.set_page_config(
    page_title='Compras Inteligentes',
    page_icon='🛒',
    layout="wide",
)

#Estilos css personalizados
st.markdown("""
        <style>
            div.stMainBlockContainer{
                max-width: 1140px !important;
            }

            div[data-testid="stImageContainer"]{
                background: white;
            }

            span.st-ct{
                border: 1px solid #305a4b !important;
                background-color: #305a4b !important;
            }

            /* estilo para las opciones */
            div[data-testid="stCheckbox"]{
                padding: 4px;
                border-radius: 5px;
            }

            div[data-testid="stCheckbox"]:hover {
                background-color: #305a4b; /* CAMBIAR COLOR */
                transition: 0.3s;
            }
        </style>
    """,
    unsafe_allow_html=True
)



st.title('Compras Inteligentes')

# Objeto de categorías y productos
productos = {
    "🧼 Higiene personal": ["🚿 Shampoo", "🧼 Jabón corporal", "🪥 Pasta dental", "🧴 Desodorante", "🧻 Papel higiénico"],
    "🪄 Limpieza del hogar": ["👕 Detergente en polvo", "☁️ Suavizante", "🌊 Cloro", "✨ Limpiador multiusos", "🧽 Esponjas"],
    "🍳 Alimentos Básicos": ["🥛 Leche", "🥚 Huevo", "🍞 Pan blanco", "🍚 Arroz", "🫘 Frijol"],
    "🍎 Frutas y verduras": ["🍏 Manzana", "🍌 Plátano", "🍅 Tomate", "🧅 Cebolla", "🥔 Papa"],
    "🥫 Abarrotes": ["🧉 Aceite", "🐟 Atún", "🍬 Azúcar", "☕ Café", "🍪 Galletas"]
}



# categorias
st.subheader("Selecciona una categoría:")
column = st.columns(len(productos))

# session_state guarda la categoria clickeada
if 'categoria_actual' not in st.session_state:
    st.session_state.categoria_actual = None

for i, categoria in enumerate(productos.keys()):
    #Crea un botón para cada categoría
    if column[i].button(categoria, use_container_width=True):
        st.session_state.categoria_actual = categoria



subcategoria = []
#Despliegue de opciones segun la categoria
if st.session_state.categoria_actual:
    st.write(f"---")
    st.subheader(f"Opciones para {st.session_state.categoria_actual}:")
    
    # Mostrar los productos de la categoría
    opciones = productos[st.session_state.categoria_actual]
    sub_column = st.columns(len(opciones))
    
    for j, producto in enumerate(opciones):
        if(sub_column[j].checkbox(producto, key=f"prod_{producto}")):
            subcategoria.append(producto)

st.write("---")

if(len(subcategoria) > 0):
    st.subheader("Mejores resultados en HEB")

    categoria = ' '.join(st.session_state.categoria_actual.split(" ")[1:])
    subcategoria = [' '.join(sub.split(" ")[1:]) for sub in subcategoria]
    productosHEB = getBestOptions(categoria, subcategoria, "data/heb_productos.json")

    minimum_cards = []

    for sub in subcategoria:
        sub_result = productosHEB.get("bySubcategory", {}).get(sub, {})
        minimum_product = sub_result.get("minimumProduct")

        if minimum_product is not None:
            minimum_cards.append((sub, minimum_product))

    for inicio in range(0, len(minimum_cards), 5):
        fila = minimum_cards[inicio:inicio + 5]
        columnas = st.columns(5)

        for col, item in zip(columnas, fila):
            sub, producto = item
            with col:
                nombre = producto.get("nombre", "Sin nombre")
                precio = producto.get("precio", "Sin precio")
                link = producto.get("link")
                imagen = producto.get("imagen")

                st.caption(sub)
                if imagen:
                    st.image(imagen)

                st.markdown(f"**{nombre}**")
                st.write(f"Precio: {precio}")
                if link:
                    st.link_button("Ver producto", link, key=f"min_{sub}_{nombre}")

    if not productosHEB:
        st.warning("No se encontraron productos para la categoría seleccionada.")
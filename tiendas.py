#Libreria Streamlit para la interfaz de usuario
import streamlit as st
#Importar funcion para obtener los productos segun la categoria
from utils.getBestOptions import getBestOptions
import folium
from streamlit_folium import st_folium
import math
import requests
import time

# ========== FUNCIONES DEL MAPA ==========
def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """Calcula distancia en línea recta usando fórmula de Haversine (km)"""
    R = 6371
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    distancia = R * c
    return round(distancia, 2)

def calcular_tiempo_estimado(distancia_km):
    """Estima tiempo en minutos basado en distancia"""
    velocidad_promedio = 30
    tiempo_horas = distancia_km / velocidad_promedio
    return round(tiempo_horas * 60, 1)

@st.cache_data(ttl=3600)
def obtener_sucursales():
    """Sucursales con coordenadas reales"""
    return [
        {"id": 1, "nombre": "HEB San Pedro", "lat": 25.6602, "lng": -100.3700, 
         "cadena": "HEB", "horario": "7:00-23:00", "direccion": "Av. José Vasconcelos 100, San Pedro"},
        {"id": 2, "nombre": "HEB Valle Oriente", "lat": 25.6547, "lng": -100.3250, 
         "cadena": "HEB", "horario": "7:00-23:00", "direccion": "Av. Lázaro Cárdenas 2000, Valle Oriente"},
        {"id": 3, "nombre": "HEB Cumbres", "lat": 25.6938, "lng": -100.3511, 
         "cadena": "HEB", "horario": "7:00-23:00", "direccion": "Av. Cumbres 300, Cumbres"},
        {"id": 4, "nombre": "Aurrerá Lincoln", "lat": 25.6786, "lng": -100.3341, 
         "cadena": "Aurrerá", "horario": "7:00-22:00", "direccion": "Av. Lincoln 500, Lincoln"},
        {"id": 5, "nombre": "Aurrerá Cumbres", "lat": 25.6891, "lng": -100.3058, 
         "cadena": "Aurrerá", "horario": "7:00-22:00", "direccion": "Av. Cumbres 600, Cumbres"},
        {"id": 6, "nombre": "Walmart La Fe", "lat": 25.6905, "lng": -100.3150, 
         "cadena": "Walmart", "horario": "24 horas", "direccion": "Av. La Fe 100, La Fe"},
        {"id": 7, "nombre": "Walmart San Pedro", "lat": 25.6650, "lng": -100.3650, 
         "cadena": "Walmart", "horario": "24 horas", "direccion": "Av. Real de San Pedro 200, San Pedro"},
        {"id": 8, "nombre": "Soriana Valle", "lat": 25.6589, "lng": -100.3692, 
         "cadena": "Soriana", "horario": "8:00-22:00", "direccion": "Av. Vasconcelos 300, Valle"},
        {"id": 9, "nombre": "Soriana La Fe", "lat": 25.6875, "lng": -100.3100, 
         "cadena": "Soriana", "horario": "8:00-22:00", "direccion": "Av. La Fe 200, La Fe"},
        {"id": 10, "nombre": "Chedraui Constitución", "lat": 25.6700, "lng": -100.3400, 
         "cadena": "Chedraui", "horario": "7:00-23:00", "direccion": "Av. Constitución 1000, Centro"}
    ]

def obtener_colores_cadena():
    return {
        "HEB": "#2E7D32", "Aurrerá": "#E65100", 
        "Walmart": "#1565C0", "Soriana": "#F9A825", "Chedraui": "#6A1B9A"
    }

def obtener_ubicacion_automatica():
    """Obtiene ubicación automática por IP"""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('latitude') and data.get('longitude'):
                return (data['latitude'], data['longitude'])
    except:
        pass
    # Fallback: Monterrey centro
    return (25.6866, -100.3161)

def mostrar_mapa_con_ruta(sucursales, ubicacion_usuario, tienda_destino=None):
    """Crea mapa con marcadores y ruta hacia la tienda destino"""
    if not sucursales:
        return None
    
    center = ubicacion_usuario if ubicacion_usuario else [sucursales[0]["lat"], sucursales[0]["lng"]]
    colores_cadena = obtener_colores_cadena()
    
    m = folium.Map(location=center, zoom_start=13, control_scale=True, tiles='CartoDB positron')
    
    # Agregar marcadores de tiendas
    for tienda in sucursales:
        color = colores_cadena.get(tienda["cadena"], "#95a5a6")
        
        # Si es la tienda destino, marcador más grande
        if tienda_destino and tienda["nombre"] == tienda_destino:
            radius = 15
            color = "#FF9800"
            popup_text = f"🎯 **DESTINO** - {tienda['nombre']}"
        else:
            radius = 10
            popup_text = f"🛒 {tienda['nombre']}"
        
        popup_html = f"""
        <div style="min-width: 200px;">
            <strong>{popup_text}</strong><br>
            <small>{tienda['cadena']}</small><br>
            <small>{tienda['direccion']}</small><br>
            <small>⏰ {tienda['horario']}</small>
        </div>
        """
        
        folium.CircleMarker(
            location=[tienda["lat"], tienda["lng"]],
            radius=radius,
            color="white",
            weight=3,
            fill_color=color,
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{tienda['nombre']}"
        ).add_to(m)
    
    # Marcador de ubicación del usuario
    if ubicacion_usuario:
        folium.Marker(
            location=ubicacion_usuario,
            popup="📍 Tu ubicación",
            icon=folium.Icon(color="red", icon="user", prefix='fa'),
            tooltip="Estás aquí"
        ).add_to(m)
        
        # Círculos de radio
        folium.Circle(radius=1000, location=ubicacion_usuario, color='#2E7D32', 
                     weight=2, fill=True, fill_opacity=0.1, tooltip="1km").add_to(m)
        folium.Circle(radius=3000, location=ubicacion_usuario, color='#66BB6A', 
                     weight=1, fill=True, fill_opacity=0.05, tooltip="3km").add_to(m)
        
        # Dibujar ruta a la tienda destino
        if tienda_destino:
            tienda_info = next((t for t in sucursales if t["nombre"] == tienda_destino), None)
            if tienda_info:
                # Dibujar línea de ruta
                folium.PolyLine(
                    locations=[[ubicacion_usuario[0], ubicacion_usuario[1]], 
                               [tienda_info["lat"], tienda_info["lng"]]],
                    color="#FF9800",
                    weight=5,
                    opacity=0.9,
                    dash_array='10, 5',
                    popup=f"Ruta a {tienda_destino}"
                ).add_to(m)
                
                # Agregar marcador de inicio y fin
                folium.Marker(
                    location=ubicacion_usuario,
                    icon=folium.Icon(color="green", icon="play", prefix='fa'),
                    popup="Inicio"
                ).add_to(m)
                
                folium.Marker(
                    location=[tienda_info["lat"], tienda_info["lng"]],
                    icon=folium.Icon(color="orange", icon="flag-checkered", prefix='fa'),
                    popup="Destino"
                ).add_to(m)
                
                # Ajustar zoom para mostrar toda la ruta
                bounds = [[ubicacion_usuario[0], ubicacion_usuario[1]], 
                         [tienda_info["lat"], tienda_info["lng"]]]
                m.fit_bounds(bounds)
    
    return m

def encontrar_tienda_mas_cercana(sucursales, ubicacion_usuario):
    """Encuentra la tienda más cercana"""
    if not ubicacion_usuario:
        return None, None
    
    distancias = {}
    for tienda in sucursales:
        distancia = calcular_distancia_haversine(
            ubicacion_usuario[0], ubicacion_usuario[1],
            tienda["lat"], tienda["lng"]
        )
        distancias[tienda["nombre"]] = {
            'distancia': distancia,
            'tiempo': calcular_tiempo_estimado(distancia),
            'tienda': tienda
        }
    
    if distancias:
        tienda_cercana = min(distancias, key=lambda x: distancias[x]['distancia'])
        return tienda_cercana, distancias[tienda_cercana]
    return None, None

# ========== CONFIGURACIÓN DE LA PÁGINA ==========
st.set_page_config(
    page_title='Compras Inteligentes',
    page_icon='🛒',
    layout="wide",
)

# Inicializar session state
if 'productos_seleccionados' not in st.session_state:
    st.session_state.productos_seleccionados = []
if 'coords_usuario' not in st.session_state:
    st.session_state.coords_usuario = obtener_ubicacion_automatica()
if 'categoria_actual' not in st.session_state:
    st.session_state.categoria_actual = None
if 'mostrar_ruta' not in st.session_state:
    st.session_state.mostrar_ruta = False
if 'tienda_destino' not in st.session_state:
    st.session_state.tienda_destino = None
if 'compra_finalizada' not in st.session_state:
    st.session_state.compra_finalizada = False

# ========== JAVASCRIPT PARA UBICACIÓN PRECISA AUTOMÁTICA ==========
st.markdown("""
    <script>
    // Solicitar ubicación automáticamente al cargar la página
    function getAutoLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const coords = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    localStorage.setItem('user_location_precise', JSON.stringify(coords));
                    console.log('Ubicación obtenida automáticamente');
                },
                function(error) {
                    console.log("Error obteniendo ubicación:", error.message);
                }
            );
        }
    }
    
    // Ejecutar automáticamente
    getAutoLocation();
    
    // Guardar en input oculto para Streamlit
    const savedPrecise = localStorage.getItem('user_location_precise');
    if (savedPrecise) {
        const coords = JSON.parse(savedPrecise);
        const latInput = document.createElement('input');
        latInput.id = 'auto_lat';
        latInput.value = coords.lat;
        latInput.style.display = 'none';
        document.body.appendChild(latInput);
        const lngInput = document.createElement('input');
        lngInput.id = 'auto_lng';
        lngInput.value = coords.lng;
        lngInput.style.display = 'none';
        document.body.appendChild(lngInput);
    }
    </script>
""", unsafe_allow_html=True)

# Intentar leer ubicación precisa automática
try:
    import streamlit.components.v1 as components
    components.html("""
        <script>
        setTimeout(() => {
            const latInput = document.getElementById('auto_lat');
            const lngInput = document.getElementById('auto_lng');
            if (latInput && lngInput && latInput.value && lngInput.value) {
                const coords = latInput.value + ',' + lngInput.value;
                const output = document.createElement('div');
                output.id = 'auto_coords_output';
                output.innerText = coords;
                document.body.appendChild(output);
            }
        }, 1000);
        </script>
    """, height=0)
except:
    pass

# Estilos css personalizados
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

            div[data-testid="stCheckbox"]{
                padding: 4px;
                border-radius: 5px;
            }

            div[data-testid="stCheckbox"]:hover {
                background-color: #305a4b;
                transition: 0.3s;
            }
            
            [data-testid="stSidebar"] {
                min-width: 400px;
            }
            
            .ruta-info {
                background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid #FF9800;
                margin: 10px 0;
            }
        </style>
    """,
    unsafe_allow_html=True
)

# ========== SIDEBAR CON MAPA ==========
with st.sidebar:
    st.markdown("## 🗺️ **Mapa de Tiendas Cercanas**")
    st.markdown("---")
    
    # Mostrar ubicación actual
    if st.session_state.coords_usuario:
        st.success(f"📍 Ubicación detectada automáticamente")
        st.caption(f"Lat: {st.session_state.coords_usuario[0]:.4f} | Lng: {st.session_state.coords_usuario[1]:.4f}")
    
    st.markdown("---")
    
    # Leyenda de tiendas
    st.markdown("### 🏪 **Cadenas**")
    colores = obtener_colores_cadena()
    for cadena, color in colores.items():
        st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 20px; height: 20px; background: {color}; border-radius: 50%; margin-right: 10px;"></div>
                <span>{cadena}</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mostrar tienda más cercana
    sucursales = obtener_sucursales()
    if st.session_state.coords_usuario:
        tienda_cercana, info = encontrar_tienda_mas_cercana(sucursales, st.session_state.coords_usuario)
        if tienda_cercana:
            st.markdown("### 🎯 **Tienda más cercana**")
            st.markdown(f"""
                <div style="background: #E8F5E9; padding: 15px; border-radius: 10px; border-left: 4px solid #2E7D32;">
                    <strong>{tienda_cercana}</strong><br>
                    📏 {info['distancia']} km<br>
                    ⏱️ {info['tiempo']} minutos
                </div>
            """, unsafe_allow_html=True)
            
            # Guardar tienda más cercana en session state
            st.session_state.tienda_mas_cercana = tienda_cercana
            st.session_state.info_tienda = info
    
    st.markdown("---")
    
    # Mostrar el mapa (con ruta si compra finalizada)
    if st.session_state.get('compra_finalizada', False) and st.session_state.get('tienda_destino'):
        mapa = mostrar_mapa_con_ruta(sucursales, st.session_state.coords_usuario, st.session_state.tienda_destino)
        if mapa:
            st_folium(mapa, width=380, height=450, key="mapa_con_ruta")
            
            # Mostrar información de la ruta
            if st.session_state.get('info_tienda'):
                st.markdown(f"""
                    <div class="ruta-info">
                        🗺️ <strong>Ruta a {st.session_state.tienda_destino}</strong><br>
                        📏 Distancia: {st.session_state.info_tienda['distancia']} km<br>
                        ⏱️ Tiempo estimado: {st.session_state.info_tienda['tiempo']} minutos
                    </div>
                """, unsafe_allow_html=True)
    else:
        mapa = mostrar_mapa_con_ruta(sucursales, st.session_state.coords_usuario, None)
        if mapa:
            st_folium(mapa, width=380, height=450, key="mapa_normal")

# ========== CONTENIDO PRINCIPAL ==========
st.title('Compras Inteligentes')

# Mostrar resumen de productos seleccionados
if st.session_state.productos_seleccionados:
    with st.expander(f"📋 Ver lista de compras ({len(st.session_state.productos_seleccionados)} productos)", expanded=True):
        for i, prod in enumerate(st.session_state.productos_seleccionados, 1):
            st.markdown(f"{i}. {prod}")
        if st.button("🗑️ Limpiar lista"):
            st.session_state.productos_seleccionados = []
            st.session_state.compra_finalizada = False
            st.rerun()

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

for i, categoria in enumerate(productos.keys()):
    if column[i].button(categoria, use_container_width=True):
        st.session_state.categoria_actual = categoria

# Despliegue de opciones segun la categoria
if st.session_state.categoria_actual:
    st.write(f"---")
    st.subheader(f"Opciones para {st.session_state.categoria_actual}:")
    
    opciones = productos[st.session_state.categoria_actual]
    sub_column = st.columns(len(opciones))
    
    nuevos_seleccionados = []
    for j, producto in enumerate(opciones):
        ya_seleccionado = producto in st.session_state.productos_seleccionados
        if sub_column[j].checkbox(producto, value=ya_seleccionado, key=f"prod_{producto}"):
            nuevos_seleccionados.append(producto)
    
    # Actualizar lista
    for prod in opciones:
        if prod in st.session_state.productos_seleccionados and prod not in nuevos_seleccionados:
            st.session_state.productos_seleccionados.remove(prod)
    for prod in nuevos_seleccionados:
        if prod not in st.session_state.productos_seleccionados:
            st.session_state.productos_seleccionados.append(prod)

st.write("---")

# Mostrar productos seleccionados actualmente para búsqueda
subcategoria = st.session_state.productos_seleccionados

if len(subcategoria) > 0:
    st.subheader("Mejores resultados en HEB")
    
    # Mostrar tienda más cercana recomendada
    if st.session_state.coords_usuario:
        tienda_cercana, info = encontrar_tienda_mas_cercana(sucursales, st.session_state.coords_usuario)
        if tienda_cercana:
            st.info(f"🏪 **Recomendación:** La tienda más cercana es **{tienda_cercana}** a {info['distancia']} km (aprox. {info['tiempo']} min)")

    categoria = ' '.join(st.session_state.categoria_actual.split(" ")[1:]) if st.session_state.categoria_actual else ""
    subcategoria_proc = [' '.join(sub.split(" ")[1:]) for sub in subcategoria]
    
    with st.spinner("Buscando mejores precios..."):
        productosHEB = getBestOptions(categoria, subcategoria_proc, "data/heb_productos.json")

        minimum_cards = []

        for sub in subcategoria_proc:
            sub_result = productosHEB.get("bySubcategory", {}).get(sub, {})
            minimum_product = sub_result.get("minimumProduct")

            if minimum_product is not None:
                minimum_cards.append((sub, minimum_product))

        if minimum_cards:
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
                            st.link_button("Ver producto", link)

            # Botón para finalizar compra
            st.markdown("---")
            
            # Obtener la tienda más cercana
            tienda_recomendada = tienda_cercana if 'tienda_cercana' in locals() else None
            
            if st.button("✅ Finalizar compra", use_container_width=True):
                # Mostrar animación de globos
                st.balloons()
                time.sleep(1)
                
                # Marcar que la compra se finalizó
                st.session_state.compra_finalizada = True
                
                # Guardar tienda destino
                if tienda_recomendada:
                    st.session_state.tienda_destino = tienda_recomendada
                    st.session_state.info_tienda = info if 'info' in locals() else None
                
                # Mostrar mensaje de éxito
                st.success(f"🎉 ¡Compra lista!")
                
                # Mostrar información de la ruta
                if tienda_recomendada:
                    st.markdown(f"""
                        <div style="background: #FFF3E0; padding: 20px; border-radius: 10px; margin-top: 10px;">
                            <h3>🗺️ ¡Tu ruta está lista!</h3>
                            <p>📍 <strong>Destino:</strong> {tienda_recomendada}</p>
                            <p>📏 <strong>Distancia:</strong> {info['distancia']} km</p>
                            <p>⏱️ <strong>Tiempo estimado:</strong> {info['tiempo']} minutos</p>
                            <p>✅ <strong>Revisa el mapa en la barra lateral</strong> para ver la ruta trazada</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Forzar recarga para mostrar la ruta en el mapa
                    time.sleep(2)
                    st.rerun()

        if not productosHEB:
            st.warning("No se encontraron productos para la categoría seleccionada.")
else:
    if st.session_state.categoria_actual:
        st.info("💡 Selecciona productos para ver las mejores ofertas")

# Mostrar ruta activa si ya se finalizó la compra
if st.session_state.get('compra_finalizada', False) and st.session_state.get('tienda_destino'):
    st.markdown("---")
    st.subheader("🗺️ **Tu ruta activa**")
    
    # Mostrar instrucciones
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E8F5E9, #C8E6C9); padding: 20px; border-radius: 15px;">
            <h3 style="color: #2E7D32;">✅ ¡Ruta trazada con éxito!</h3>
            <p>📍 <strong>Destino:</strong> {st.session_state.tienda_destino}</p>
            <p>📏 <strong>Distancia:</strong> {st.session_state.info_tienda['distancia'] if st.session_state.info_tienda else 'N/A'} km</p>
            <p>⏱️ <strong>Tiempo estimado:</strong> {st.session_state.info_tienda['tiempo'] if st.session_state.info_tienda else 'N/A'} minutos</p>
            <hr>
            <p>🔍 <strong>Instrucciones:</strong></p>
            <ol>
                <li>Revisa el mapa en la barra lateral <strong>👈 izquierda</strong></li>
                <li>La línea <strong style="color: #FF9800;">🟠 naranja</strong> muestra tu ruta</li>
                <li>El marcador <strong>🎯 naranja</strong> es tu destino</li>
                <li>¡Buen viaje y felices compras!</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Nueva compra", use_container_width=True):
        st.session_state.compra_finalizada = False
        st.session_state.tienda_destino = None
        st.session_state.productos_seleccionados = []
        st.rerun()
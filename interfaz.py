# Librería Streamlit para la interfaz de usuario
import streamlit as st
from utils.getBestOptions import getBestOptions
import folium
from streamlit_folium import st_folium
import math
import requests
import time

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
    velocidad_promedio = 30  # km/h en zona urbana
    tiempo_horas = distancia_km / velocidad_promedio
    return round(tiempo_horas * 60, 1)

@st.cache_data(ttl=3600)
def obtener_sucursales():
    """Sucursales con coordenadas reales de Monterrey"""
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
    """Colores corporativos para cada cadena de tiendas"""
    return {
        "HEB": "#2E7D32", "Aurrerá": "#E65100", 
        "Walmart": "#1565C0", "Soriana": "#F9A825", "Chedraui": "#6A1B9A"
    }

def obtener_ubicacion_por_ip():
    """Fallback: Obtiene ubicación aproximada por IP"""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('latitude') and data.get('longitude'):
                return (data['latitude'], data['longitude'])
    except:
        pass
    return (25.6866, -100.3161)

def mostrar_mapa_con_ruta(sucursales, ubicacion_usuario, tienda_destino=None):
    """Crea mapa con marcadores y ruta hacia la tienda destino"""
    if not sucursales:
        return None
    
    center = ubicacion_usuario if ubicacion_usuario else [sucursales[0]["lat"], sucursales[0]["lng"]]
    colores_cadena = obtener_colores_cadena()
    
    m = folium.Map(location=center, zoom_start=14, control_scale=True, tiles='CartoDB positron')
    
    for tienda in sucursales:
        color = colores_cadena.get(tienda["cadena"], "#95a5a6")
        
        if tienda_destino and tienda["nombre"] == tienda_destino:
            radius = 15
            color = "#FF9800"
            popup_text = f"🎯 **DESTINO** - {tienda['nombre']}"
        else:
            radius = 10
            popup_text = f"🛒 {tienda['nombre']}"
        
        popup_html = f"""
        <div style="min-width: 220px; font-family: Arial, sans-serif;">
            <strong style="font-size: 14px;">{popup_text}</strong><br>
            <small style="color: #666;">{tienda['cadena']}</small><br>
            <small style="color: #666;">{tienda['direccion']}</small><br>
            <small style="color: #2E7D32;">⏰ {tienda['horario']}</small>
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
    
    if ubicacion_usuario:
        folium.Marker(
            location=ubicacion_usuario,
            popup="📍 Tu ubicación actual",
            icon=folium.Icon(color="red", icon="user", prefix='fa'),
            tooltip="Estás aquí"
        ).add_to(m)
        
        folium.Circle(radius=1000, location=ubicacion_usuario, color='#2E7D32', 
                     weight=2, fill=True, fill_opacity=0.1, tooltip="1 km").add_to(m)
        folium.Circle(radius=3000, location=ubicacion_usuario, color='#66BB6A', 
                     weight=1, fill=True, fill_opacity=0.05, tooltip="3 km").add_to(m)
        
        if tienda_destino:
            tienda_info = next((t for t in sucursales if t["nombre"] == tienda_destino), None)
            if tienda_info:
                folium.PolyLine(
                    locations=[[ubicacion_usuario[0], ubicacion_usuario[1]], 
                               [tienda_info["lat"], tienda_info["lng"]]],
                    color="#FF9800",
                    weight=5,
                    opacity=0.9,
                    dash_array='10, 5',
                    popup=f"Ruta hacia {tienda_destino}"
                ).add_to(m)
                
                folium.Marker(
                    location=ubicacion_usuario,
                    icon=folium.Icon(color="green", icon="play", prefix='fa'),
                    popup="🚀 Punto de partida"
                ).add_to(m)
                
                folium.Marker(
                    location=[tienda_info["lat"], tienda_info["lng"]],
                    icon=folium.Icon(color="orange", icon="flag-checkered", prefix='fa'),
                    popup="🏁 Destino"
                ).add_to(m)
                
                bounds = [[ubicacion_usuario[0], ubicacion_usuario[1]], 
                         [tienda_info["lat"], tienda_info["lng"]]]
                m.fit_bounds(bounds, padding=(50, 50))
    
    return m

def encontrar_tienda_mas_cercana(sucursales, ubicacion_usuario):
    """Encuentra la tienda más cercana al usuario"""
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


st.set_page_config(
    page_title='Compras Inteligentes',
    page_icon='🛒',
    layout="wide",
    initial_sidebar_state="expanded"
)

productos = {
    "🧼 Higiene personal": ["🚿 Shampoo", "🧼 Jabón corporal", "🪥 Pasta dental", "🧴 Desodorante", "🧻 Papel higiénico"],
    "🪄 Limpieza del hogar": ["👕 Detergente en polvo", "☁️ Suavizante", "🌊 Cloro", "✨ Limpiador multiusos", "🧽 Esponjas"],
    "🍳 Alimentos Básicos": ["🥛 Leche", "🥚 Huevo", "🍞 Pan blanco", "🍚 Arroz", "🫘 Frijol"],
    "🍎 Frutas y verduras": ["🍏 Manzana", "🍌 Plátano", "🍅 Tomate", "🧅 Cebolla", "🥔 Papa"],
    "🥫 Abarrotes": ["🧉 Aceite", "🐟 Atún", "🍬 Azúcar", "☕ Café", "🍪 Galletas"]
}

if 'categoria_actual' not in st.session_state:
    st.session_state.categoria_actual = list(productos.keys())[0]
if 'coords_usuario' not in st.session_state:
    st.session_state.coords_usuario = None
if 'compra_finalizada' not in st.session_state:
    st.session_state.compra_finalizada = False
if 'tienda_destino' not in st.session_state:
    st.session_state.tienda_destino = None
if 'info_tienda' not in st.session_state:
    st.session_state.info_tienda = None
if 'geo_status' not in st.session_state:
    st.session_state.geo_status = "pendiente"
if 'geo_attempts' not in st.session_state:
    st.session_state.geo_attempts = 0

st.markdown("""
    <style>
        /* Contenedor principal */
        div.stMainBlockContainer{
            max-width: 1140px !important;
            margin: 0 auto;
        }
        
        /* Estilo para imágenes */
        div[data-testid="stImageContainer"]{
            background: white;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        div[data-testid="stImageContainer"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        
        /* Estilo para spans especiales */
        span.st-ct{
            border: 1px solid #305a4b !important;
            background-color: #305a4b !important;
        }
        
        /* Estilo para los checkboxes */
        div[data-testid="stCheckbox"]{
            padding: 8px;
            border-radius: 10px;
            transition: all 0.3s ease;
            border: 1px solid #e0e0e0;
        }
        
        div[data-testid="stCheckbox"]:hover {
            background: linear-gradient(135deg, #305a4b, #1e3a2f);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(48, 90, 75, 0.3);
        }
        
        div[data-testid="stCheckbox"]:hover label {
            color: white !important;
        }
        
        /* Sidebar mejorado */
        [data-testid="stSidebar"] {
            min-width: 380px;
            max-width: 380px;
        }
        
        [data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(135deg, #305a4b, #1e3a2f);
            color: white;
            border: none;
            transition: all 0.3s ease;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            transform: translateX(5px);
            background: linear-gradient(135deg, #1e3a2f, #0f241d);
            box-shadow: 0 4px 12px rgba(48, 90, 75, 0.4);
        }
        
        /* Cajas de coordenadas */
        .coord-box {
            background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
            padding: 12px;
            border-radius: 10px;
            border-left: 4px solid #2E7D32;
            font-family: monospace;
            margin: 8px 0;
            color: #2E7D32 !important;
            transition: all 0.3s ease;
        }
        
        .coord-box:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2);
        }
        
        /* Caja de error */
        .error-box {
            background: linear-gradient(135deg, #ffebee, #ffcdd2);
            padding: 12px;
            border-radius: 10px;
            border-left: 4px solid #dc3545;
            margin: 8px 0;
            color: #dc3545 !important;
            transition: all 0.3s ease;
        }
        
        /* Información de ruta */
        .ruta-info {
            background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
            padding: 15px;
            border-radius: 12px;
            border-left: 4px solid #FF9800;
            margin: 10px 0;
            transition: all 0.3s ease;
            animation: slideIn 0.5s ease;
        }
        
        .ruta-info:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
        }
        
        /* Botones generales */
        .stButton > button {
            border-radius: 10px;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        }
        
        /* Pestañas mejoradas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 8px 20px;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #305a4b20;
            transform: translateY(-2px);
        }
        
        /* Tarjetas de productos */
        .stContainer {
            background: white;
            border-radius: 12px;
            padding: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stContainer:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        /* Animaciones */
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        /* Títulos con animación */
        h1, h2, h3 {
            animation: fadeIn 0.6s ease;
        }
        
        /* Footer */
        footer {
            animation: fadeIn 1s ease;
        }
        
        /* Precios destacados */
        .stSubheader {
            color: #2E7D32;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

def solicitar_ubicacion():
    """Maneja la lógica de geolocalización de forma robusta"""
    if st.session_state.geo_status == "exito" and st.session_state.coords_usuario:
        return True
    
    st.session_state.geo_status = "solicitando"
    st.session_state.geo_attempts += 1
    
    try:
        from streamlit_geolocation import streamlit_geolocation
        location = streamlit_geolocation()
        
        if location and 'latitude' in location and location['latitude'] is not None:
            st.session_state.coords_usuario = (location['latitude'], location['longitude'])
            st.session_state.geo_status = "exito"
            return True
        elif location and 'error' in location:
            st.session_state.geo_status = "error"
            return False
    except ImportError:
        st.session_state.geo_status = "error"
        return False
    except Exception:
        st.session_state.geo_status = "error"
        return False
    
    return False


with st.sidebar:
    st.markdown("# 🛒 Menú")
    
    st.markdown("## 📂 Categorías")
    for categoria in productos.keys():
        if st.button(categoria, width='stretch', key=f"sidebar_{categoria}"):
            st.session_state.categoria_actual = categoria
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📍 Tu ubicación")
    
    if st.session_state.geo_status == "pendiente":
        if st.button("📍 Activar ubicación precisa", width='stretch', type="primary"):
            solicitar_ubicacion()
            st.rerun()
    elif st.session_state.geo_status == "solicitando":
        with st.spinner("📡 Solicitando ubicación..."):
            time.sleep(0.5)
            solicitar_ubicacion()
            st.rerun()
    elif st.session_state.geo_status == "exito" and st.session_state.coords_usuario:
        st.success("✅ Ubicación activa")
        st.markdown(f"""
            <div class="coord-box">
                📍 <strong>Lat:</strong> {st.session_state.coords_usuario[0]:.6f}<br>
                📍 <strong>Lng:</strong> {st.session_state.coords_usuario[1]:.6f}
            </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Actualizar", width='stretch'):
            st.session_state.geo_status = "pendiente"
            st.rerun()
    elif st.session_state.geo_status == "error":
        st.markdown(f"""
            <div class="error-box">
                ❌ <strong>Ubicación no disponible</strong><br>
                <small>Requiere HTTPS y permiso del navegador.</small>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🌐 Usar ubicación por IP", width='stretch'):
            fallback = obtener_ubicacion_por_ip()
            st.session_state.coords_usuario = fallback
            st.session_state.geo_status = "exito"
            st.info("🌐 Ubicación aproximada activada")
            st.rerun()
    
    if st.session_state.geo_attempts >= 2 and not st.session_state.coords_usuario:
        fallback = obtener_ubicacion_por_ip()
        st.session_state.coords_usuario = fallback
        st.session_state.geo_status = "exito"
        st.rerun()
    
    st.markdown("---")

    if st.session_state.coords_usuario:
        st.markdown("### 🏪 **Cadenas disponibles**")
        colores = obtener_colores_cadena()
        for cadena, color in colores.items():
            st.markdown(f"""
                <div style="display: flex; align-items: center; margin: 6px 0; transition: all 0.3s ease;">
                    <div style="width: 18px; height: 18px; background: {color}; 
                               border-radius: 50%; margin-right: 10px; border: 2px solid white;
                               box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                    <span style="font-size: 14px; font-weight: 500;">{cadena}</span>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        sucursales = obtener_sucursales()
        tienda_cercana, info = encontrar_tienda_mas_cercana(sucursales, st.session_state.coords_usuario)
        if tienda_cercana:
            st.markdown("### 🎯 **Tienda más cercana**")
            st.info(f"""
**{tienda_cercana}**  
📏 {info['distancia']} km  
⏱️ ~{info['tiempo']} min
            """)
            st.session_state.tienda_mas_cercana = tienda_cercana
            st.session_state.info_tienda_cercana = info
        
        st.markdown("---")
        
        if st.session_state.get('compra_finalizada', False) and st.session_state.get('tienda_destino'):
            mapa = mostrar_mapa_con_ruta(sucursales, st.session_state.coords_usuario, st.session_state.tienda_destino)
            if mapa:
                st_folium(mapa, width=360, height=450, key="mapa_ruta")
        else:
            mapa = mostrar_mapa_con_ruta(sucursales, st.session_state.coords_usuario, None)
            if mapa:
                st_folium(mapa, width=360, height=450, key="mapa_normal")
    else:
        st.caption("💡 Activa tu ubicación para ver el mapa")


st.title('🛒 Compras Inteligentes')
st.markdown("*Encuentra los mejores precios y la ruta más corta*")

st.title(f"Productos de {st.session_state.categoria_actual}")
st.write("Selecciona los productos que buscas")

categoria_actual = st.session_state.categoria_actual or list(productos.keys())[0]
opciones = productos[categoria_actual]
subcategoria = []

cols_sub = st.columns(len(opciones))
for j, producto in enumerate(opciones):
    with cols_sub[j]:
        if st.checkbox(producto, key=f"check_{producto}"):
            subcategoria.append(producto)

st.divider()

def display_store_results(path: str, categoria: str, subcategoria_list: list):
    try:
        res = getBestOptions(categoria, subcategoria_list, path)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return
    
    if not res:
        st.info("No hay productos seleccionados o no se encontraron resultados.")
        return

    cards_data = []
    for sub in subcategoria_list:
        p = res.get("bySubcategory", {}).get(sub, {}).get("minimumProduct")
        if p:
            cards_data.append((sub, p))

    if not cards_data:
        st.warning("No encontramos ofertas para estos productos hoy.")
        return

    for i in range(0, len(cards_data), 5):
        fila = cards_data[i:i+5]
        columnas = st.columns(5)
        for col, item in zip(columnas, fila):
            sub_name, p_info = item
            with col:
                with st.container():
                    if p_info.get("imagen"):
                        try:
                            st.image(p_info["imagen"], width='stretch')
                        except:
                            st.image("https://via.placeholder.com/150?text=Producto", width='stretch')
                    st.caption(sub_name)
                    st.markdown(f"**{p_info.get('nombre', 'Sin nombre')}**")
                    st.subheader(f"{p_info.get('precio', '0.00')}")
                    if p_info.get("link"):
                        st.link_button("🔗 Ver", p_info["link"], width='stretch')

# Lógica principal de comparación
if subcategoria:
    cat_clean = ' '.join(categoria_actual.split(" ")[1:])
    sub_clean = [' '.join(s.split(" ")[1:]) for s in subcategoria]
    
    # Mostrar recomendación de tienda si hay ubicación
    if st.session_state.coords_usuario:
        sucursales = obtener_sucursales()
        tienda_cercana, info = encontrar_tienda_mas_cercana(sucursales, st.session_state.coords_usuario)
        if tienda_cercana:
            st.info(f"🏪 **Recomendación:** {tienda_cercana} a {info['distancia']} km (~{info['tiempo']} min)")
    
    tab_heb, tab_aurrera, tab_walmart = st.tabs(["🟢 HEB", "🟠 Aurrerá", "🔵 Walmart"])

    with tab_heb:
        display_store_results("data/heb_productos.json", cat_clean, sub_clean)

    with tab_aurrera:
        display_store_results("data/aurrera_productos.json", cat_clean, sub_clean)

    with tab_walmart:
        display_store_results("data/walmart_productos.json", cat_clean, sub_clean)
    
    st.divider()
    
    # Botón para finalizar compra
    if st.button("✅ Finalizar compra y ver ruta", width="stretch", type="primary"):
        sucursales = obtener_sucursales()
        if st.session_state.coords_usuario:
            tienda_recomendada, info_tienda = encontrar_tienda_mas_cercana(sucursales, st.session_state.coords_usuario)
            if tienda_recomendada:
                st.balloons()
                st.session_state.compra_finalizada = True
                st.session_state.tienda_destino = tienda_recomendada
                st.session_state.info_tienda = info_tienda
                st.success(f"🎉 ¡Ruta a **{tienda_recomendada}** lista en el mapa!")
                st.markdown(f"""
                    <div class="ruta-info">
                        🗺️ <strong>Tu ruta:</strong> {info_tienda['distancia']} km • ~{info_tienda['tiempo']} min
                    </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
        else:
            st.warning("⚠️ Activa tu ubicación en el sidebar para calcular la ruta.")

else:
    st.info("💡 Selecciona productos arriba para comparar precios")

# Sección final cuando la compra está finalizada
if st.session_state.get('compra_finalizada', False) and st.session_state.get('tienda_destino'):
    st.markdown("---")
    st.subheader("🗺️ **Tu ruta activa**")
    info_display = st.session_state.get('info_tienda', {})
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E8F5E9, #C8E6C9); 
                   padding: 20px; border-radius: 12px; border: 2px solid #2E7D32;
                   animation: slideIn 0.5s ease;">
            <h4 style="color: #1B5E20; margin: 0 0 15px 0;">✅ ¡Listo para ir de compras!</h4>
            <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                <div style="background: white; color: #1B5E20; padding: 12px 20px; border-radius: 8px; text-align: center; flex: 1; min-width: 120px;
                          transition: all 0.3s ease;">
                    🎯<br><strong>{st.session_state.tienda_destino}</strong>
                </div>
                <div style="background: white; color: #1B5E20; padding: 12px 20px; border-radius: 8px; text-align: center; flex: 1; min-width: 120px;
                          transition: all 0.3s ease;">
                    📏<br><strong>{info_display.get('distancia', 'N/A')} km</strong>
                </div>
                <div style="background: white; color: #1B5E20; padding: 12px 20px; border-radius: 8px; text-align: center; flex: 1; min-width: 120px;
                          transition: all 0.3s ease;">
                    ⏱️<br><strong>{info_display.get('tiempo', 'N/A')} min</strong>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Nueva compra", width='stretch'):
            st.session_state.compra_finalizada = False
            st.session_state.tienda_destino = None
            st.session_state.info_tienda = None
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 15px; font-size: 13px; animation: fadeIn 1s ease;">
        🛒 <strong>Compras Inteligentes</strong> • Comparación de precios • Rutas con GPS
    </div>
""", unsafe_allow_html=True)
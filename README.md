# Compras Inteligentes

Aplicacion web hecha con `Streamlit` para comparar precios de productos basicos entre varias cadenas de supermercado y ayudar a elegir la compra mas conveniente segun disponibilidad, distancia y ruta.

## Que hace

- Permite seleccionar una categoria de productos.
- Compara precios entre `HEB`, `Aurrera` y `Walmart`.
- Muestra el producto mas barato por subcategoria.
- Detecta la ubicacion del usuario para calcular la tienda mas cercana.
- Muestra un mapa interactivo con `Folium` y una ruta estimada hacia la tienda recomendada.
- Usa archivos JSON locales con productos scrapeados previamente.

## Estructura del proyecto

- `interfaz.py`: interfaz principal de la aplicacion.
- `tiendas.py`: logica relacionada con tiendas y seleccion de opciones.
- `utils/getProductsFromJSON.py`: carga y filtra los productos desde JSON.
- `utils/getBestOptions.py`: encuentra el producto con menor precio por subcategoria.
- `scrapping/walmart.py`: scraper de productos de Walmart.
- `scrapping/heb.py`: scraper de productos de HEB.
- `scrapping/aurrera.py`: scraper de productos de Bodega Aurrera.
- `data/*.json`: datos con los productos ya procesados para la interfaz.

## Requisitos

- Python 3.10 o superior.
- Google Chrome y/o Microsoft Edge instalados para los scrapers.
- Acceso a internet para geolocalizacion, mapas y scraping.

## Instalacion

1. Crea y activa un entorno virtual.
2. Instala las dependencias:

```bash
pip install streamlit folium streamlit-folium requests streamlit-geolocation pandas selenium undetected-chromedriver webdriver-manager
```

## Como ejecutar la app

```bash
streamlit run interfaz.py
```

La aplicacion abrira un panel donde puedes:

1. Elegir una categoria.
2. Marcar los productos que buscas.
3. Comparar precios por tienda.
4. Activar tu ubicacion.
5. Ver la tienda recomendada y la ruta en el mapa.

## Actualizar los datos

Los archivos JSON dentro de `data/` se generan con los scrapers. Si quieres refrescar la informacion, ejecuta cada script de scraping por separado:

```bash
python scrapping/heb.py
python scrapping/aurrera.py
python scrapping/walmart.py
```

Cada script actualiza su archivo correspondiente en `data/`.

## Notas

- La geolocalizacion puede pedir permiso del navegador.
- Si la ubicacion precisa no esta disponible, la app intenta usar una ubicacion aproximada por IP.
- Los scrapers dependen de la estructura actual de los sitios web, asi que pueden requerir ajustes si las tiendas cambian su HTML.

## Objetivo

Este proyecto busca hacer mas rapida la comparacion de precios y facilitar la planeacion de compras con una vista clara de tiendas, distancias y ruta.

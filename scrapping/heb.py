from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from pathlib import Path
import json
import time

options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")

def crear_driver():
    try:
        return webdriver.Edge(options=options)
    except WebDriverException:
        pass

    try:
        return webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            options=options
        )
    except Exception as e:
        raise RuntimeError("Error con EdgeDriver") from e


def cargar_data_actual(json_path: Path) -> dict:
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def scrape_subcategoria(driver, subcategoria: str) -> list:
    url = f"https://www.heb.com.mx/{subcategoria}?_q={subcategoria}&map=ft"

    driver.get(url)
    time.sleep(8)

    cards = driver.find_elements(By.CSS_SELECTOR, "div.vtex-search-result-3-x-galleryItem")

    resultados = []
    cardsFiltered = []

    for card in cards:
        patrocinado = card.find_elements(By.CSS_SELECTOR, ".hebmx-store-theme-7-x-containerSponsored")
        if patrocinado:
            continue
        cardsFiltered.append(card)

    for card in cardsFiltered[:10]:
        nombre = ""
        precio = ""
        link = ""
        imagen = ""

        for n in card.find_elements(By.CSS_SELECTOR, "h3, h2, a[title]"):
            texto = n.text.strip()
            if texto:
                nombre = texto
                break

        for p in card.find_elements(By.CSS_SELECTOR, "span.vtex-product-price-1-x-currencyContainer, div[class*='price-shelf']"):
            texto = p.text.strip()
            if texto:
                precio = texto
                break

        for a in card.find_elements(By.TAG_NAME, "a"):
            href = (a.get_attribute("href") or "").strip()
            if href:
                link = href
                break

        for img in card.find_elements(By.CSS_SELECTOR, "img.vtex-product-summary-2-x-imageNormal.vtex-product-summary-2-x-image.vtex-product-summary-2-x-image--img-shelf"):
            src = (img.get_attribute("src") or img.get_attribute("data-src") or "").strip()
            if src:
                imagen = src
                break

        #Solo agregar producto si tiene nombre y precio (campos obligatorios)
        if nombre and precio:
            resultados.append({
                "nombre": nombre,
                "precio": precio,
                "link": link,
                "imagen": imagen,
            })

    return resultados


driver = crear_driver()

# Configura aqui tus categorias y subcategorias a scrapear
productos_por_categoria = {
    "Limpieza del hogar": ["Cloro", "Detergente en polvo", "Suavizante", "Limpiador multiusos", "Esponjas"],
    "Higiene personal": ["Shampoo", "Pasta dental", "Jabón corporal", "Papel higiénico", "Desodorante"],
    "Alimentos Básicos": ["Leche", "Huevo", "Pan blanco", "Arroz", "Frijol"],
    "Frutas y verduras": ["Manzana", "Plátano", "Tomate", "Cebolla", "Papa"],
    "Abarrotes": ["Aceite", "Atún", "Azúcar", "Café", "Galletas"]
}

Path("data").mkdir(exist_ok=True)
json_path = Path("data/heb_productos.json")
data = cargar_data_actual(json_path)

try:
    for categoria, subcategorias in productos_por_categoria.items():
        bloque_categoria = {}

        for subcategoria in subcategorias:
            bloque_categoria[subcategoria] = scrape_subcategoria(driver, subcategoria)

        data[categoria] = [bloque_categoria]
finally:
    driver.quit()

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
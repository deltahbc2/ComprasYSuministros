from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from pathlib import Path
import json
import time

productos = ["Limpiador multiusos", "Esponjas"]

for producto in productos:
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")

    def crear_driver():
        # Intenta usar el EdgeDriver local/gestionado por Selenium primero.
        try:
            return webdriver.Edge(options=options)
        except WebDriverException:
            pass

        # Como respaldo, intenta webdriver-manager (requiere internet).
        try:
            return webdriver.Edge(
                service=Service(EdgeChromiumDriverManager().install()),
                options=options
            )
        except Exception as e:
            raise RuntimeError(
                "No se pudo iniciar EdgeDriver. Verifica conexion a internet o instala Edge WebDriver localmente."
            ) from e
        
    driver = crear_driver()

    url = f"https://www.heb.com.mx/{producto}?_q={producto}&map=ft"

    driver.get(url)
    time.sleep(8)

    cards = driver.find_elements(By.CSS_SELECTOR, "div.vtex-search-result-3-x-galleryItem")
    resultados = []

    cards_sin_patrocinados = []
    for card in cards:
        patrocinado = card.find_elements(By.CSS_SELECTOR, ".hebmx-store-theme-7-x-containerSponsored")
        if patrocinado:
            continue
        cards_sin_patrocinados.append(card)

    for card in cards_sin_patrocinados[:10]:
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

        for img in card.find_elements(By.TAG_NAME, "img"):
            src = (img.get_attribute("src") or img.get_attribute("data-src") or "").strip()
            if src:
                imagen = src
                break

        resultados.append({
            "nombre": nombre,
            "precio": precio,
            "link": link,
            "imagen": imagen,
        })

    driver.quit()

    Path("data").mkdir(exist_ok=True)
    json_path = Path("data/heb_productos.json")

    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}
    else:
        data = {}

    data[producto] = resultados

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
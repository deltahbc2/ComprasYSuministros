#C:\Program Files\Google\Chrome\Application

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import re
import pandas as pd
import time
import random
import json
from pathlib import Path

def walmart_captcha(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "px-captcha"))
            )
        print("Resolviendo captcha")
        captcha_element = driver.find_element(By.ID, "px-captcha")
        action = ActionChains(driver)
        action.click_and_hold(captcha_element).perform()
        time.sleep(13)
        action.release().perform()
        print("Esperando recarga")
        time.sleep(5)
    except Exception:
        print("No se detectó captcha")



def scrape_walmart(search_query):
    #configuracion
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #options.add_argument('--headless') # esconde ventana da error (?)
    chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    options.binary_location = chrome_path 

    driver = uc.Chrome(version_main=146,options=options, browser_executable_path=chrome_path) #carga ruta navegador chrome
    
    url = f"https://www.walmart.com.mx/search?q={search_query}" #Dirección de pagina a extraer
    
    try:
        driver.get(url)
        walmart_captcha(driver)

        #scroll carga objetos
        driver.execute_script(f"window.scrollTo(0, 900);")
        time.sleep(random.uniform(3,5))

        #carga productos
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-item-id]'))
        )

        productos = []
        items = driver.find_elements(By.CSS_SELECTOR, 'div[data-item-id]')

        for item in items[:10]:
            try:
                nombre = item.find_element(By.CSS_SELECTOR, 'span[data-automation-id="product-title"]').text

                precio = item.find_element(By.CSS_SELECTOR, 'div[data-automation-id="product-price"]').text
                match = re.search(r'\$\d+(?:,\d+)*(?:\.\d+)?', precio)
                if match:
                    precioreal = match.group(0)
                else:
                    print("No se encontró precio")
                    continue

                imagen = item.find_element(By.CSS_SELECTOR, 'img[data-testid="productTileImage"]').get_attribute("src")

                productos.append({
                    "Nombre": nombre,
                    "Precio": precioreal,
                    "Imagen": imagen
                })

            except Exception:
                continue

        return pd.DataFrame(productos)
    except Exception as ex:
        print("Ocurrio un error en el script")
        print(ex)
        return pd.DataFrame()

    finally:
        driver.quit()



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



productos_por_categoria = {
    "Limpieza del hogar": ["Cloro", "Detergente en polvo", "Suavizante", "Limpiador multiusos", "Esponjas"],
    "Higiene personal": ["Shampoo", "Pasta dental", "Jabón corporal", "Papel higiénico", "Desodorante"],
    "Alimentos Básicos": ["Leche", "Huevo", "Pan blanco", "Arroz", "Frijol"],
    "Frutas y verduras": ["Manzana", "Plátano", "Tomate", "Cebolla", "Papa"],
    "Abarrotes": ["Aceite", "Atún", "Azúcar", "Café", "Galletas"]
}

Path("data").mkdir(exist_ok=True)
json_path = Path("data/walmart_productos.json")
data = cargar_data_actual(json_path)

try:
    for categoria, subcategorias in productos_por_categoria.items():
        bloque_categoria = {}

        for subcategoria in subcategorias:
            print(f"Scrapeando {categoria} -> {subcategoria}")
            df = scrape_walmart(subcategoria)
            if not df.empty:
                df.drop_duplicates(subset=['Nombre'], inplace=True)

            productos = []
            for row in df.to_dict(orient="records"):
                productos.append({
                    "nombre": row.get("Nombre", ""),
                    "precio": row.get("Precio", ""),
                    "link": "",
                    "imagen": row.get("Imagen", "")
                })

            bloque_categoria[subcategoria] = productos

        data[categoria] = [bloque_categoria]
finally:
    pass

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nArchivo guardado como {json_path}")
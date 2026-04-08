#C:\Program Files\Google\Chrome\Application

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import re 
import pandas as pd
import time
import datetime
import random


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

        for item in items[:15]: 
            try:
                nombre = item.find_element(By.CSS_SELECTOR, 'span[data-automation-id="product-title"]').text

                precio = item.find_element(By.CSS_SELECTOR, 'div[data-automation-id="product-price"]').text
                match = re.search(r'\$\d+(?:,\d+)*(?:\.\d+)?', precio)
                if match:
                    precioreal = match.group(0)
                else:
                    print("No se encontró precio")
                
                productos.append({
                    "Nombre": nombre,
                    "Precio": precioreal
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

# principal
query = "laptop"
df = scrape_walmart(query)
df.drop_duplicates(subset=['Nombre'], inplace=True)

if not df.empty:
    print("Los datos se lograron extraer correctamente")
    timenow = datetime.datetime.now()
    formateo = timenow.strftime("%d/%m/%Y %H:%M:%S")


    print(f"Datos extraidos {formateo}")
    print(df)
    filename = "precios_walmart.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\nArchivo guardado como {filename} ")
else:
    print('Hubo un problema y no se recolectaron datos')

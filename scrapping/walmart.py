from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

# Configuración de Edge
options = webdriver.EdgeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")

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


def esperar_captcha_manual(driver, tiempo_maximo=180):
    inicio = time.time()
    aviso_mostrado = False

    while (time.time() - inicio) < tiempo_maximo:
        pagina = driver.page_source.lower()
        hay_captcha = (
            "no eres un robot" in pagina
            or "manten presionado" in pagina
            or "mantén presionado" in pagina
            or "verify you are human" in pagina
        )

        if hay_captcha and not aviso_mostrado:
            print("Se detecto verificacion anti-bot. Resuelvela manualmente en el navegador y espera unos segundos...")
            aviso_mostrado = True

        productos = driver.find_elements(By.CSS_SELECTOR, "div[data-automation-id='productTile']")
        if productos:
            return productos

        time.sleep(2)

    return driver.find_elements(By.CSS_SELECTOR, "div[data-automation-id='productTile']")

driver = crear_driver()

# Producto a buscar
producto = "detergente ariel"
url = f"https://www.walmart.com.mx/search?q={producto}"

resultados = []

try:
    driver.get(url)

    # Espera a que aparezcan tiles de producto en la pagina.
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-automation-id='productTile']"))
        )
    except TimeoutException:
        print("No aparecieron productos de inmediato. Revisando si hay verificacion manual...")

    productos = driver.find_elements(By.CSS_SELECTOR, "div[data-automation-id='productTile']")
    if not productos:
        productos = esperar_captcha_manual(driver)

    if not productos:
        print("No se encontraron productos. Es posible que Walmart haya cambiado los selectores o siga bloqueando el acceso.")

    for p in productos[:5]:
        try:
            nombre = p.find_element(By.CSS_SELECTOR, "span[data-automation-id='product-title']").text
            precio = p.find_element(By.CSS_SELECTOR, "span[data-automation-id='product-price']").text
            link = p.find_element(By.TAG_NAME, "a").get_attribute("href")

            resultados.append({
                "nombre": nombre,
                "precio": precio,
                "link": link
            })

        except Exception as e:
            print("Error al leer producto:", e)

except KeyboardInterrupt:
    print("Ejecucion interrumpida por el usuario.")

finally:
    try:
        driver.quit()
    except Exception:
        pass

# Mostrar resultados
for r in resultados:
    print(r)
import time
from playwright.sync_api import sync_playwright

def run(playwright):
    # Lanza un navegador (Chromium), headless=False significa que veremos la ventana.
    browser = playwright.chromium.launch(headless=False)
    
    # Crea una nueva pestaña.
    page = browser.new_page()
    
    # Va a la URL especificada.
    url = "https://app7.dge.gob.pe/maps/sala_metaxenica/"
    print(f"Navegando a: {url}")
    page.goto(url)
    
    # Espera 10 segundos para que puedas ver el resultado.
    print("Página cargada. El navegador se cerrará en 10 segundos.")
    time.sleep(10)
    
    # Cierra el navegador.
    browser.close()

# Bloque principal que ejecuta Playwright
with sync_playwright() as playwright:
    run(playwright)

print("Script finalizado.")
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
    
    # --- NUEVO CÓDIGO ---
    # Localizamos la pestaña "Tablas". Playwright es inteligente y buscará un
    # elemento que funcione como una pestaña y que contenga el texto "Tablas".
    print("Buscando y haciendo clic en la pestaña 'Tablas'...")
    tablas_button = page.get_by_role("tab", name="Tablas")
    
    # Hacemos clic en el elemento encontrado.
    tablas_button.click()
    # --- FIN DEL NUEVO CÓDIGO ---

    # Espera 5 segundos para que puedas ver el resultado.
    print("Pestaña 'Tablas' seleccionada. El navegador se cerrará en 5 segundos.")
    time.sleep(5)
    
    # Cierra el navegador.
    browser.close()

# Bloque principal que ejecuta Playwright
with sync_playwright() as playwright:
    run(playwright)

print("Script finalizado.")
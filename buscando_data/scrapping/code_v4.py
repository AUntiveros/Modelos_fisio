import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    
    url = "https://app7.dge.gob.pe/maps/sala_metaxenica/"
    print(f"Navegando a: {url}")
    page.goto(url, timeout=60000)
    
    print("\nCambiando a la pestaña 'Tablas'...")
    page.get_by_role("tab", name="Tablas").click()

    try:
        # --- PASO 1: SELECCIONAR AÑO (YA FUNCIONA) ---
        print("Esperando a que la tabla '#ten-tbl04-tbl' cargue...")
        table_locator = page.locator("#ten-tbl04-tbl")
        table_locator.wait_for(state='visible', timeout=30000)
        print("Tabla cargada. El DOM es estable.")

        print("\nHaciendo clic en el <input> del menú 'Año'...")
        page.locator("#ten-fyear-selectized").click()
        
        print("Seleccionando el año '2025'...")
        page.get_by_role("option", name="2025").click()
        print("Año seleccionado con éxito.")

        # --- NUEVO CÓDIGO: SELECCIONAR ENFERMEDAD ---
        # La página se actualiza después de seleccionar el año.
        # Volvemos a esperar a que la tabla esté visible para asegurar estabilidad.
        print("\nEsperando a que la tabla se actualice después de cambiar el año...")
        table_locator.wait_for(state='visible', timeout=30000)

        print("Haciendo clic en el <input> del menú 'Enfermedad'...")
        # Aplicamos nuestro aprendizaje: usamos el ID directo del input.
        page.locator("#ten-fenfe-selectized").click()
        
        print("Seleccionando la enfermedad 'DENGUE'...")
        # Hacemos clic en la opción para cerrar el menú.
        page.get_by_role("option", name="DENGUE").click()
        print("Enfermedad seleccionada con éxito.")
        # --- FIN DEL NUEVO CÓDIGO ---

    except PlaywrightTimeoutError:
        print("\n--- FALLO ---")
        print("La operación excedió el tiempo de espera.")
        print("Revisa los selectores o el tiempo de carga de la página.")

    print("\nFlujo completado. El navegador se cerrará en 7 segundos.")
    time.sleep(7)
    
    browser.close()

with sync_playwright() as playwright:
    run(playwright)

print("Script finalizado.")
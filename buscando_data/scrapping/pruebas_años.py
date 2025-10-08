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
        # --- APLICANDO TUS DESCUBRIMIENTOS ---

        # LECCIÓN #2: Esperar por el ID de tabla correcto.
        print("Esperando a que la tabla correcta ('#ten-tbl04-tbl') cargue...")
        table_locator = page.locator("#ten-tbl04-tbl")
        table_locator.wait_for(state='visible', timeout=30000)
        print("¡Tabla cargada! El DOM es ahora estable.")

        # LECCIÓN #1: Hacer clic en el <input> específico, no en el <div>.
        print("\nHaciendo clic en el <input> del menú 'Año'...")
        year_dropdown_input = page.locator("#ten-fyear-selectized")
        year_dropdown_input.click()
        
        # Ahora, el resto del flujo debería funcionar.
        print("Leyendo las opciones disponibles...")
        option_elements = page.locator(".selectize-dropdown-content .option")
        option_elements.first.wait_for() # Esperar a que aparezcan
        
        all_options = option_elements.all_text_contents()
        print(f"Opciones encontradas: {all_options}")
        
        print("Seleccionando el año '2025'...")
        page.get_by_role("option", name="2025").click()
        print("¡ÉXITO! El año fue seleccionado correctamente.")

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
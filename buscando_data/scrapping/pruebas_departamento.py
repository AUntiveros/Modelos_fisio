import time
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

def wait_for_load_indicator_to_disappear(page: Page):
    print("Esperando a que el indicador de 'Cargando' desaparezca...")
    loading_indicator = page.locator("div.shiny-busy")
    loading_indicator.wait_for(state='hidden', timeout=60000)
    print("Indicador de carga desaparecido. La página está lista.")

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    
    url = "https://app7.dge.gob.pe/maps/sala_metaxenica/"
    print(f"Navegando a: {url}")
    page.goto(url, timeout=60000)
    
    print("\nCambiando a la pestaña 'Tablas'...")
    page.get_by_role("tab", name="Tablas").click()

    try:
        print("Esperando a que la tabla inicial '#ten-tbl04-tbl' cargue...")
        page.locator("#ten-tbl04-tbl").wait_for(state='visible', timeout=30000)
        
        # --- PASO 1: AÑO ---
        print("\nHaciendo clic en el menú 'Año'...")
        page.locator("#ten-fyear-selectized").click()
        page.get_by_role("option", name="2025").click()
        wait_for_load_indicator_to_disappear(page)

        # --- PASO 2: ENFERMEDAD ---
        print("\nHaciendo clic en el menú 'Enfermedad'...")
        page.locator("#ten-fenfe-selectized").click()
        page.get_by_role("option", name="DENGUE").click()
        wait_for_load_indicator_to_disappear(page)

        # --- PASO 3: DEPARTAMENTO ---
        print("\nHaciendo clic en el menú 'Departamento'...")
        page.locator("#ten-fdepa-filter-selectized").click()
        
        # --- LA CORRECCIÓN DEFINITIVA ---
        # Selector específico: Busca opciones DENTRO del contenedor de dropdown VISIBLE.
        visible_options = page.locator(".selectize-dropdown-content:visible .option")
        
        # Ahora esperamos por el primer elemento de ESTA lista visible.
        visible_options.first.wait_for()

        second_option = visible_options.nth(1)
        department_to_select = second_option.text_content()
        print(f"Seleccionando '{department_to_select}'...")
        second_option.click()
        wait_for_load_indicator_to_disappear(page)

    except PlaywrightTimeoutError as e:
        print(f"\n--- FALLO ---")
        print(f"La operación excedió el tiempo de espera. Detalles: {e}")

    print("\n¡Flujo de selección completado con éxito! El navegador se cerrará en 7 segundos.")
    time.sleep(7)
    
    browser.close()

with sync_playwright() as playwright:
    run(playwright)

print("Script finalizado.")
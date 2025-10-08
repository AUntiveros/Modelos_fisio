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
        
        # --- PASOS ANTERIORES (YA FUNCIONAN) ---
        print("\nSeleccionando Año '2025'...")
        page.locator("#ten-fyear-selectized").click()
        page.get_by_role("option", name="2025").click()
        wait_for_load_indicator_to_disappear(page)

        print("\nSeleccionando Enfermedad 'DENGUE'...")
        page.locator("#ten-fenfe-selectized").click()
        page.get_by_role("option", name="DENGUE").click()
        wait_for_load_indicator_to_disappear(page)

        print("\nSeleccionando segundo Departamento en la lista...")
        page.locator("#ten-fdepa-filter-selectized").click()
        visible_dept_options = page.locator(".selectize-dropdown-content:visible .option")
        visible_dept_options.first.wait_for()
        second_dept_option = visible_dept_options.nth(1)
        department_to_select = second_dept_option.text_content()
        print(f"Seleccionando '{department_to_select}'...")
        second_dept_option.click()
        wait_for_load_indicator_to_disappear(page)

        # --- SELECCIÓN DE PROVINCIA CON BUCLE DE REINTENTO (TU IDEA) ---
        print("\nSeleccionando Provincia con lógica de reintento...")
        max_retries = 3
        success = False
        for attempt in range(max_retries):
            print(f"Intento {attempt + 1}/{max_retries} para cargar las provincias...")
            page.locator("#ten-fprov-filter-selectized").click()
            
            visible_prov_options = page.locator(".selectize-dropdown-content:visible .option")
            print("-------------------Antes del try: ", visible_prov_options.all_text_contents())
            print("-------------------Total de elementos: ", visible_prov_options.count())
            
            try:
                # Primero, esperamos a que el dropdown al menos se abra (tenga 1 opción)
                visible_prov_options.first.wait_for(timeout=5000)
                print("Entramos a condicional")
                
                # Ahora, comprobamos si tiene MÁS de una opción
                if visible_prov_options.count() > 1:
                    print("¡Lista de provincias poblada con éxito!")
                    second_prov_option = visible_prov_options.nth(1)
                    province_to_select = second_prov_option.text_content()
                    print(f"Seleccionando '{province_to_select}'...")
                    second_prov_option.click()
                    wait_for_load_indicator_to_disappear(page)
                    success = True
                    break # Salimos del bucle si tenemos éxito
                else:
                    print("La lista aún no contiene provincias. Reintentando...")
                    # Cerramos el menú para el siguiente intento
                    page.locator("#ten-fprov-filter-selectized").click() 
                    time.sleep(1) # Pequeña pausa antes de reintentar

            except PlaywrightTimeoutError:
                print("El menú de Provincia no se abrió a tiempo en este intento.")
                # No es necesario hacer nada, el bucle continuará con el siguiente intento.
        
        if not success:
            raise Exception("No se pudieron cargar las opciones de Provincia después de varios intentos.")
        # --- FIN DEL NUEVO CÓDIGO ---

    except Exception as e:
        print(f"\n--- FALLO ---")
        print(f"Ocurrió un error: {e}")

    print("\n¡Flujo de selección completado con éxito! El navegador se cerrará en 10 segundos.")
    time.sleep(1)
    browser.close()

with sync_playwright() as playwright:
    run(playwright)

print("Script finalizado.")
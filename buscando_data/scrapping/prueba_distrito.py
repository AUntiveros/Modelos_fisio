import time
import os
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

def wait_for_processing_to_finish(page: Page):
    print("Verificando estado de carga y esperando si es necesario...")
    page.locator("html.shiny-busy").wait_for(state='hidden', timeout=60000)
    print("La página está lista para la siguiente acción.")

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
        
        selected_year = "2025"
        selected_disease = "DENGUE"
        selected_department = ""
        selected_province = ""
        selected_district = ""

        print("\nSeleccionando Año '2025'...")
        page.locator("#ten-fyear-selectized").click()
        page.get_by_role("option", name=selected_year).click()
        wait_for_processing_to_finish(page)

        print(f"\nSeleccionando Enfermedad '{selected_disease}'...")
        page.locator("#ten-fenfe-selectized").click()
        page.get_by_role("option", name=selected_disease).click()
        wait_for_processing_to_finish(page)

        print("\nSeleccionando segundo Departamento en la lista...")
        page.locator("#ten-fdepa-filter-selectized").click()
        visible_dept_options = page.locator(".selectize-dropdown-content:visible .option")
        visible_dept_options.first.wait_for()
        second_dept_option = visible_dept_options.nth(1)
        selected_department = second_dept_option.text_content()
        print(f"Seleccionando '{selected_department}'...")
        second_dept_option.click()
        wait_for_processing_to_finish(page)

        print("\nSeleccionando Provincia con lógica de reintento...")
        # ... (código de provincia con tus prints de depuración)
        max_retries_prov = 3
        success_prov = False
        for attempt in range(max_retries_prov):
            page.locator("#ten-fprov-filter-selectized").click()
            visible_prov_options = page.locator(".selectize-dropdown-content:visible .option")
            print("-------------------(Provincia) Antes del try: ", visible_prov_options.all_text_contents())
            print("-------------------(Provincia) Total de elementos: ", visible_prov_options.count())
            try:
                visible_prov_options.first.wait_for(timeout=5000)
                if visible_prov_options.count() > 1:
                    second_prov_option = visible_prov_options.nth(1)
                    selected_province = second_prov_option.text_content()
                    print(f"Seleccionando '{selected_province}'...")
                    second_prov_option.click()
                    wait_for_processing_to_finish(page)
                    success_prov = True
                    break
                else:
                    page.locator("#ten-fprov-filter-selectized").click() 
                    time.sleep(1)
            except PlaywrightTimeoutError:
                pass
        if not success_prov:
            raise Exception("No se pudieron cargar las opciones de Provincia.")
        
        print("\nHaciendo clic en el botón 'Procesar' (primera vez)...")
        page.locator("#ten-run").click()
        wait_for_processing_to_finish(page)
        
        print("\nCambiando a la pestaña 'Tabla: Casos y defunciones'...")
        page.get_by_role("tab", name="Tabla: Casos y defunciones").click()
        wait_for_processing_to_finish(page)
        page.locator("#ten-tbl06b-tbl").wait_for(state="visible", timeout=10000)
        
        print("\nPreparando para la primera descarga...")
        download_folder = "datas"
        os.makedirs(download_folder, exist_ok=True)
        filename_1 = (f"{selected_year}-{selected_disease}-{selected_department.replace(' ', '-')}"
                      f"-{selected_province.replace(' ', '-')}-CasoDefuncion.xlsx")
        with page.expect_download() as download_info_1:
            page.locator("#ten-tbl06b-download").click()
        download_1 = download_info_1.value
        download_1.save_as(os.path.join(download_folder, filename_1))
        print(f"¡Descarga 1 completa! Archivo guardado como: {filename_1}")

        print("\nCambiando a la pestaña 'Tabla: Casos según diagnóstico'...")
        page.get_by_role("tab", name="Tabla: Casos según diagnóstico").click()
        wait_for_processing_to_finish(page)
        page.locator("#ten-tbl06c-tbl").wait_for(state="visible", timeout=10000)

        print("\nPreparando para la segunda descarga...")
        filename_2 = (f"{selected_year}-{selected_disease}-{selected_department.replace(' ', '-')}"
                      f"-{selected_province.replace(' ', '-')}-CasoClinico.xlsx")
        with page.expect_download() as download_info_2:
            page.locator("#ten-tbl06c-download").click()
        download_2 = download_info_2.value
        download_2.save_as(os.path.join(download_folder, filename_2))
        print(f"¡Descarga 2 completa! Archivo guardado como: {filename_2}")
        
        # --- LÓGICA DE DISTRITO MOVIDA AQUÍ (DENTRO DEL TRY...EXCEPT) ---
        print("\nSeleccionando Distrito con lógica de reintento...")
        max_retries_dist = 3
        success_dist = False
        for attempt in range(max_retries_dist):
            print(f"Intento {attempt + 1}/{max_retries_dist} para cargar los distritos...")
            page.locator("#ten-fdist-filter-selectized").click()
            visible_dist_options = page.locator(".selectize-dropdown-content:visible .option")
            print("-------------------(Distrito) Antes del try: ", visible_dist_options.all_text_contents())
            print("-------------------(Distrito) Total de elementos: ", visible_dist_options.count())
            try:
                visible_dist_options.first.wait_for(timeout=5000)
                if visible_dist_options.count() > 1:
                    second_dist_option = visible_dist_options.nth(1)
                    selected_district = second_dist_option.text_content()
                    print(f"Seleccionando '{selected_district}'...")
                    second_dist_option.click()
                    wait_for_processing_to_finish(page)
                    success_dist = True
                    break
                else:
                    page.locator("#ten-fdist-filter-selectized").click() 
                    time.sleep(1)
            except PlaywrightTimeoutError:
                pass
        if not success_dist:
            raise Exception("No se pudieron cargar las opciones de Distrito.")

        # --- NUEVO PASO: PROCESAR POR SEGUNDA VEZ ---
        print("\nHaciendo clic en el botón 'Procesar' (segunda vez, con Distrito)...")
        page.locator("#ten-run").click()
        
        print("Procesando nuevos filtros, esperando que el contenido se actualice...")
        wait_for_processing_to_finish(page)
        print("Contenido actualizado con el filtro de distrito.")
        # --- FIN DEL NUEVO PASO ---

    except Exception as e:
        print(f"\n--- FALLO ---")
        print(f"Ocurrió un error: {e}")

    print("\n¡Flujo completo finalizado! El navegador se cerrará en 10 segundos.")
    time.sleep(10)
    browser.close()

with sync_playwright() as playwright:
    run(playwright)

print("Script finalizado.")
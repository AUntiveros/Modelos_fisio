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
        
        selected_year = ""
        selected_disease = ""
        selected_department = ""
        selected_province = ""

        print("\nSeleccionando Año '2025'...")
        page.locator("#ten-fyear-selectized").click()
        page.get_by_role("option", name="2025").click()
        selected_year = "2025"
        wait_for_processing_to_finish(page)

        print("\nSeleccionando Enfermedad 'DENGUE'...")
        page.locator("#ten-fenfe-selectized").click()
        page.get_by_role("option", name="DENGUE").click()
        selected_disease = "DENGUE"
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
        max_retries = 3
        success = False
        for attempt in range(max_retries):
            # ... (código de provincia con tus prints)
            print(f"Intento {attempt + 1}/{max_retries} para cargar las provincias...")
            page.locator("#ten-fprov-filter-selectized").click()
            visible_prov_options = page.locator(".selectize-dropdown-content:visible .option")
            print("-------------------Antes del try: ", visible_prov_options.all_text_contents())
            print("-------------------Total de elementos: ", visible_prov_options.count())
            try:
                visible_prov_options.first.wait_for(timeout=5000)
                if visible_prov_options.count() > 1:
                    print("¡Lista de provincias poblada con éxito!")
                    second_prov_option = visible_prov_options.nth(1)
                    selected_province = second_prov_option.text_content()
                    print(f"Seleccionando '{selected_province}'...")
                    second_prov_option.click()
                    wait_for_processing_to_finish(page)
                    success = True
                    break
                else:
                    print("La lista aún no contiene provincias. Reintentando...")
                    page.locator("#ten-fprov-filter-selectized").click() 
                    time.sleep(1)
            except PlaywrightTimeoutError:
                print("El menú de Provincia no se abrió a tiempo en este intento.")
        if not success:
            raise Exception("No se pudieron cargar las opciones de Provincia.")
        
        print("\nHaciendo clic en el botón 'Procesar'...")
        page.locator("#ten-run").click()
        wait_for_processing_to_finish(page)
        
        print("\nCambiando a la pestaña 'Tabla: Casos y defunciones'...")
        page.get_by_role("tab", name="Tabla: Casos y defunciones").click()
        wait_for_processing_to_finish(page)
        page.locator("#ten-tbl06b-tbl").wait_for(state="visible", timeout=10000)
        print("Pestaña de 'Casos y defunciones' cargada.")

        # --- PRIMERA DESCARGA ---
        print("\nPreparando para la primera descarga...")
        download_folder = "datas"
        os.makedirs(download_folder, exist_ok=True)
        filename_1 = (f"{selected_year}-{selected_disease}-{selected_department.replace(' ', '-')}"
                      f"-{selected_province.replace(' ', '-')}-CasoDefuncion.xlsx")
        with page.expect_download() as download_info_1:
            print(f"Haciendo clic en el botón de descarga 1...")
            page.locator("#ten-tbl06b-download").click()
        download_1 = download_info_1.value
        save_path_1 = os.path.join(download_folder, filename_1)
        download_1.save_as(save_path_1)
        print(f"¡Descarga 1 completa! Archivo guardado en: {save_path_1}")

        # --- CAMBIO DE PESTAÑA ---
        print("\nCambiando a la pestaña 'Tabla: Casos según diagnóstico'...")
        page.get_by_role("tab", name="Tabla: Casos según diagnóstico").click()
        wait_for_processing_to_finish(page)
        page.locator("#ten-tbl06c-tbl").wait_for(state="visible", timeout=10000)
        print("Pestaña y tabla de 'Casos según diagnóstico' cargadas con éxito.")

        # --- NUEVO CÓDIGO: SEGUNDA DESCARGA ---
        print("\nPreparando para la segunda descarga...")
        
        # Construimos el nuevo nombre de archivo.
        filename_2 = (f"{selected_year}-{selected_disease}-{selected_department.replace(' ', '-')}"
                      f"-{selected_province.replace(' ', '-')}-CasoClinico.xlsx")
                      
        # Repetimos el proceso de descarga.
        with page.expect_download() as download_info_2:
            print(f"Haciendo clic en el botón de descarga 2...")
            page.locator("#ten-tbl06c-download").click()
            
        download_2 = download_info_2.value
        
        save_path_2 = os.path.join(download_folder, filename_2)
        download_2.save_as(save_path_2)
        print(f"¡Descarga 2 completa! Archivo guardado en: {save_path_2}")
        # --- FIN DEL NUEVO CÓDIGO ---

    except Exception as e:
        print(f"\n--- FALLO ---")
        print(f"Ocurrió un error: {e}")

    print("\n¡Flujo completo con ambas descargas finalizado con éxito! El navegador se cerrará en 10 segundos.")
    time.sleep(10)
    browser.close()

with sync_playwright() as playwright:
    run(playwright)

print("Script finalizado.")
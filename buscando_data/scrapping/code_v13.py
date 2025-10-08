import time
import os
import re # ¡Importante! Añadimos la librería para expresiones regulares
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

        # ... [Selecciones iniciales hasta Departamento se mantienen igual]
        print(f"\nSeleccionando Año '{selected_year}'...")
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

        # --- PREPARACIÓN PARA EL BUCLE DE PROVINCIAS ---
        print("\nObteniendo la lista de todas las provincias disponibles...")
        page.locator("#ten-fprov-filter-selectized").click()
        visible_prov_options = page.locator(".selectize-dropdown-content:visible .option")
        visible_prov_options.first.wait_for()
        all_province_names = visible_prov_options.all_text_contents()
        valid_provinces = [name for name in all_province_names if name != "..."]
        print(f"Se procesarán {len(valid_provinces)} provincias: {valid_provinces}")
        visible_prov_options.first.click()
        wait_for_processing_to_finish(page)

        # --- BUCLE EXTERIOR PARA CADA PROVINCIA ---
        for province_to_process in valid_provinces:
            print(f"\n================== INICIANDO PROVINCIA: {province_to_process} ==================")
            
            success_prov = False
            for attempt in range(3):
                print(f"Intento {attempt + 1}/3 para seleccionar la provincia '{province_to_process}'...")
                page.locator("#ten-fprov-filter-selectized").click()
                try:
                    # --- CORRECCIÓN AQUÍ: Usamos regex para una coincidencia exacta ---
                    exact_province_selector = re.compile(f"^{re.escape(province_to_process)}$")
                    page.locator(".selectize-dropdown-content:visible .option", has_text=exact_province_selector).wait_for(timeout=5000)
                    page.locator(".selectize-dropdown-content:visible .option", has_text=exact_province_selector).click()
                    wait_for_processing_to_finish(page)
                    success_prov = True
                    break
                except PlaywrightTimeoutError:
                    print(f"Intento {attempt + 1} fallido. Reintentando...")
                    page.locator("#ten-fprov-filter-selectized").click()
                    time.sleep(1)
            if not success_prov:
                print(f"!!! FALLO CRÍTICO: No se pudo seleccionar la provincia {province_to_process}. Omitiendo.")
                continue

            # ... [Descargas a nivel de provincia se mantienen igual]
            print(f"\nHaciendo clic en 'Procesar' para la provincia {province_to_process}...")
            page.locator("#ten-run").click()
            wait_for_processing_to_finish(page)
            # 2. PROCESAR Y DESCARGAR LOS DOS ARCHIVOS DE LA PROVINCIA
            print(f"\nHaciendo clic en 'Procesar' para la provincia {province_to_process}...")
            page.locator("#ten-run").click()
            wait_for_processing_to_finish(page)
            
            print("\nCambiando a la pestaña 'Tabla: Casos y defunciones'...")
            page.get_by_role("tab", name="Tabla: Casos y defunciones").click()
            wait_for_processing_to_finish(page)
            
            download_folder = "datas"
            os.makedirs(download_folder, exist_ok=True)
            filename_1 = (f"{selected_year}-{selected_disease}-{selected_department.replace(' ', '_')}"
                          f"-{province_to_process.replace(' ', '_')}-CasoDefuncion.xlsx")
            with page.expect_download() as download_info_1:
                page.locator("#ten-tbl06b-download").click()
            download_1 = download_info_1.value
            download_1.save_as(os.path.join(download_folder, filename_1))
            print(f"¡Descarga 1/2 para {province_to_process} completa!")

            print("\nCambiando a la pestaña 'Tabla: Casos según diagnóstico'...")
            page.get_by_role("tab", name="Tabla: Casos según diagnóstico").click()
            wait_for_processing_to_finish(page)

            filename_2 = (f"{selected_year}-{selected_disease}-{selected_department.replace(' ', '_')}"
                          f"-{province_to_process.replace(' ', '_')}-CasoClinico.xlsx")
            with page.expect_download() as download_info_2:
                page.locator("#ten-tbl06c-download").click()
            download_2 = download_info_2.value
            download_2.save_as(os.path.join(download_folder, filename_2))
            print(f"¡Descarga 2/2 para {province_to_process} completa!")

            # --- BUCLE INTERIOR PARA CADA DISTRITO ---
            print(f"\nObteniendo distritos para la provincia {province_to_process}...")
            # ... [Obtención de lista de distritos se mantiene igual]
            page.locator("#ten-fdist-filter-selectized").click()
            visible_dist_options = page.locator(".selectize-dropdown-content:visible .option")
            visible_dist_options.first.wait_for()
            all_district_names = visible_dist_options.all_text_contents()
            valid_districts = [name for name in all_district_names if name != "..."]
            print(f"Se procesarán {len(valid_districts)} distritos: {valid_districts}")
            visible_dist_options.first.click()
            wait_for_processing_to_finish(page)
            for district_to_process in valid_districts:
                print(f"\n--- INICIANDO PROCESO PARA EL DISTRITO: {district_to_process} ---")
                success_dist = False
                for attempt in range(3):
                    print(f"Intento {attempt + 1}/3 para seleccionar '{district_to_process}'...")
                    page.locator("#ten-fdist-filter-selectized").click()
                    try:
                        # --- CORRECCIÓN AQUÍ: Usamos regex para una coincidencia exacta ---
                        exact_district_selector = re.compile(f"^{re.escape(district_to_process)}$")
                        page.locator(".selectize-dropdown-content:visible .option", has_text=exact_district_selector).wait_for(timeout=5000)
                        page.locator(".selectize-dropdown-content:visible .option", has_text=exact_district_selector).click()
                        wait_for_processing_to_finish(page)
                        success_dist = True
                        break
                    except PlaywrightTimeoutError:
                        print(f"Intento {attempt + 1} fallido. Reintentando...")
                        page.locator("#ten-fdist-filter-selectized").click()
                        time.sleep(1)
                
                if not success_dist:
                    print(f"!!! FALLO CRÍTICO: No se pudo seleccionar el distrito {district_to_process}. Omitiendo.")
                    continue

                # ... [Procesar y descargar a nivel de distrito se mantiene igual]
                print("Haciendo clic en 'Procesar'...")
                page.locator("#ten-run").click()
                print("Procesando, esperando que el contenido se actualice...")
                page.locator("html.shiny-busy").wait_for(state='visible', timeout=15000)
                page.locator("html.shiny-busy").wait_for(state='hidden', timeout=60000)
                print("Contenido actualizado.")

                print(f"Preparando descarga para '{district_to_process}'...")
                download_folder = "datas"
                os.makedirs(download_folder, exist_ok=True)
                filename = (f"{selected_year}-{selected_disease}-{selected_department.replace(' ', '_')}"
                            f"-{province_to_process.replace(' ', '_')}-{district_to_process.replace(' ', '_')}.xlsx")
                with page.expect_download() as download_info:
                    page.locator("#ten-tbl05b-download").click()
                download = download_info.value
                save_path = os.path.join(download_folder, filename)
                download.save_as(save_path)
                print(f"¡Descarga para '{district_to_process}' completa! Guardado como: {filename}")
    except Exception as e:
        print(f"\n--- FALLO ---")
        print(f"Ocurrió un error: {e}")

    print("\n¡Proceso de iteración por provincias y distritos finalizado! El navegador se cerrará en 10 segundos.")
    time.sleep(10)
    browser.close()

with sync_playwright() as playwright:
    run(playwright)

print("Script finalizado.")
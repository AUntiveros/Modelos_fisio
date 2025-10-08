import time
import os
import re
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError

# --- FUNCIONES DE AYUDA MEJORADAS ---

def wait_for_processing_to_finish(page: Page):
    """
    Espera a que el selector 'html.shiny-busy' deje de existir.
    - Si la página está cargando, espera a que termine.
    - Si la página NO está cargando, continúa inmediatamente.
    """
    print("Verificando estado de carga y esperando si es necesario...")
    page.locator("html.shiny-busy").wait_for(state='hidden', timeout=60000)
    print("La página está lista para la siguiente acción.")

# --- DESPUÉS (La Versión Corregida y Más Inteligente) ---

def get_options_from_dropdown(page: Page, dropdown_selector: str, dropdown_name: str) -> list[str] | None:
    """
    Función robusta que intenta abrir un dropdown y leer sus opciones.
    Solo considera éxito si el dropdown se abre Y contiene opciones válidas (más que solo '...').
    """
    for attempt in range(3):
        print(f"Intento {attempt + 1}/3 para obtener la lista de '{dropdown_name}'...")
        page.locator(dropdown_selector).click()
        visible_options_locator = page.locator(".selectize-dropdown-content:visible .option")
        try:
            visible_options_locator.first.wait_for(timeout=5000)
            all_option_names = visible_options_locator.all_text_contents()
            
            # ¡LA NUEVA LÓGICA! Verificamos si la lista es válida.
            if len(all_option_names) > 1 or (len(all_option_names) == 1 and all_option_names[0] != "..."):
                print(f"Opciones válidas encontradas para '{dropdown_name}'.")
                visible_options_locator.first.click() # Cerramos el dropdown
                wait_for_processing_to_finish(page)
                return all_option_names
            else:
                # Si solo encontramos '...', lo consideramos un fallo para forzar un reintento.
                print(f"El dropdown solo contiene '...'. Considerado un fallo. Reintentando...")
                visible_options_locator.first.click() # Cerramos para reintentar
                time.sleep(2) # Pausa
                continue # Pasa al siguiente intento del bucle
                
        except PlaywrightTimeoutError:
            print(f"El dropdown de '{dropdown_name}' no se abrió en el intento {attempt + 1}. Reintentando...")
            time.sleep(2) # Pausa antes del siguiente intento
            
    print(f"!!! FALLO CRÍTICO: No se pudo obtener la lista de '{dropdown_name}' después de 3 intentos.")
    return None

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    
    # --- CONFIGURACIÓN DE EJECUCIÓN ---
    # Cambia estos valores para controlar el script.
    # Pon START_DEPARTMENT en None para empezar desde el principio.
    START_YEAR = "2025"
    START_DISEASE = "DENGUE"
    START_DEPARTMENT = "LIMA" # Ejemplo: "SAN MARTIN" o None
    #START_DEPARTMENT = None

    # --- PREPARACIÓN PARA LA ROBUSTEZ ---
    download_folder = "datas"
    screenshots_folder = os.path.join(download_folder, "screenshots")
    os.makedirs(screenshots_folder, exist_ok=True)
    failed_downloads = []
    
    start_point_reached = START_DEPARTMENT is None

    try:
        url = "https://app7.dge.gob.pe/maps/sala_metaxenica/"
        print(f"Navegando a: {url}")
        page.goto(url, timeout=60000)
        
        print("\nCambiando a la pestaña 'Tablas'...")
        page.get_by_role("tab", name="Tablas").click()
        page.locator("#ten-tbl04-tbl").wait_for(state='visible', timeout=30000)
        
        # --- SELECCIONES GLOBALES (AÑO Y ENFERMEDAD) ---
        print(f"\nSeleccionando Año '{START_YEAR}'...")
        page.locator("#ten-fyear-selectized").click()
        page.get_by_role("option", name=START_YEAR).click()
        wait_for_processing_to_finish(page)

        print(f"\nSeleccionando Enfermedad '{START_DISEASE}'...")
        page.locator("#ten-fenfe-selectized").click()
        page.get_by_role("option", name=START_DISEASE).click()
        wait_for_processing_to_finish(page)

        # --- PREPARACIÓN PARA EL BUCLE DE DEPARTAMENTOS ---
        all_department_names = get_options_from_dropdown(page, "#ten-fdepa-filter-selectized", "Departamento")
        if not all_department_names:
            raise Exception("No se pudo obtener la lista de departamentos para iniciar el proceso.")
        
        valid_departments = [name for name in all_department_names if name != "NACIONAL"]
        print(f"Se procesarán {len(valid_departments)} departamentos en total.")

        # --- BUCLE MÁS EXTERNO PARA CADA DEPARTAMENTO ---
        for department_to_process in valid_departments:
            
            # Lógica para saltar hasta el departamento de inicio
            if not start_point_reached:
                if department_to_process == START_DEPARTMENT:
                    start_point_reached = True
                    print(f"\n--- Punto de inicio encontrado. Reanudando desde el departamento: {START_DEPARTMENT} ---")
                else:
                    print(f"--- Omitiendo departamento: {department_to_process} (antes del punto de inicio) ---")
                    continue

            print(f"\n################## INICIANDO DEPARTAMENTO: {department_to_process} ##################")
            
            # 1. SELECCIONAR EL DEPARTAMENTO ACTUAL CON LÓGICA DE REINTENTO
            success_dept = False
            for attempt in range(3):
                print(f"Intento {attempt + 1}/3 para seleccionar el departamento '{department_to_process}'...")
                page.locator("#ten-fdepa-filter-selectized").click()
                try:
                    exact_dept_selector = re.compile(f"^{re.escape(department_to_process)}$")
                    page.locator(".selectize-dropdown-content:visible .option", has_text=exact_dept_selector).wait_for(timeout=5000)
                    page.locator(".selectize-dropdown-content:visible .option", has_text=exact_dept_selector).click()
                    wait_for_processing_to_finish(page)
                    success_dept = True
                    break
                except PlaywrightTimeoutError:
                    print(f"Intento {attempt + 1} fallido. Reintentando...")
                    if attempt < 2: 
                        try:
                            # Intenta cerrar el dropdown si está abierto
                            page.locator(".selectize-dropdown-content:visible .option").first.click()
                        except:
                            pass # Si no está abierto, no hagas nada
                        time.sleep(1)
            if not success_dept:
                print(f"!!! FALLO CRÍTICO: No se pudo seleccionar el departamento {department_to_process}. Omitiendo.")
                failed_downloads.append({'filename': f"{START_YEAR}-{START_DISEASE}-{department_to_process}", 'error': 'No se pudo seleccionar el departamento.'})
                continue

# --- BUCLE EXTERIOR PARA CADA PROVINCIA ---
            all_province_names = get_options_from_dropdown(page, "#ten-fprov-filter-selectized", f"Provincia de {department_to_process}")
            if not all_province_names:
                print(f"!!! FALLO CRÍTICO: No se pudo obtener la lista de provincias para {department_to_process}. Omitiendo este departamento.")
                failed_downloads.append({'filename': f"{START_YEAR}-{START_DISEASE}-{department_to_process}", 'error': 'No se pudo obtener la lista de provincias.'})
                continue

            valid_provinces = [name for name in all_province_names if name != "..."]
            print(f"Se procesarán {len(valid_provinces)} provincias: {valid_provinces}")

            for province_to_process in valid_provinces:
                print(f"\n================== INICIANDO PROVINCIA: {province_to_process} ==================")
                
                # SELECCIONAR LA PROVINCIA ACTUAL CON LÓGICA DE REINTENTO
                success_prov = False
                for attempt in range(3):
                    print(f"Intento {attempt + 1}/3 para seleccionar la provincia '{province_to_process}'...")
                    page.locator("#ten-fprov-filter-selectized").click()
                    try:
                        exact_province_selector = re.compile(f"^{re.escape(province_to_process)}$")
                        page.locator(".selectize-dropdown-content:visible .option", has_text=exact_province_selector).wait_for(timeout=5000)
                        page.locator(".selectize-dropdown-content:visible .option", has_text=exact_province_selector).click()
                        wait_for_processing_to_finish(page)
                        success_prov = True
                        break
                    except PlaywrightTimeoutError:
                        print(f"Intento {attempt + 1} fallido. Reintentando...")
                        if attempt < 2: 
                            try:
                                page.locator(".selectize-dropdown-content:visible .option").first.click()
                            except:
                                pass
                            time.sleep(1)
                if not success_prov:
                    print(f"!!! FALLO CRÍTICO: No se pudo seleccionar la provincia {province_to_process}. Omitiendo.")
                    failed_downloads.append({'filename': f"{START_YEAR}-{START_DISEASE}-{department_to_process}-{province_to_process}", 'error': 'No se pudo seleccionar la provincia.'})
                    continue

                # --- DESCARGAS A NIVEL DE PROVINCIA ---
                print(f"\nHaciendo clic en 'Procesar' para la provincia {province_to_process}...")
                page.locator("#ten-run").click()


                # APLICAMOS LA LÓGICA ROBUSTA DE DOS PASOS AQUÍ TAMBIÉN
                print("Procesando, esperando que el contenido se actualice...")
                # Paso 1: Esperamos a que la página RECONOZCA que está trabajando
                page.locator("html.shiny-busy").wait_for(state='visible', timeout=15000)
                print("¡La página ha empezado a cargar!")
                # Paso 2: AHORA SÍ, esperamos a que termine de trabajar
                page.locator("html.shiny-busy").wait_for(state='hidden', timeout=60000)
                print("Contenido actualizado para la provincia.")
                
                # --- DESCARGA 1 (CASO DEFUNCION) ---
                filename_1 = ""
                try:
                    filename_1 = (f"{START_YEAR}-{START_DISEASE}-{department_to_process.replace(' ', '_')}"
                                  f"-{province_to_process.replace(' ', '_')}-CasoDefuncion")
                    page.get_by_role("tab", name="Tabla: Casos y defunciones").click()
                    wait_for_processing_to_finish(page)
                    with page.expect_download(timeout=90000) as download_info:
                        page.locator("#ten-tbl06b-download").click()
                    download = download_info.value
                    download.save_as(os.path.join(download_folder, f"{filename_1}.xlsx"))
                    print(f"¡Descarga 1/2 para {province_to_process} completa!")
                except PlaywrightTimeoutError as e:
                    screenshot_path = os.path.join(screenshots_folder, f"{filename_1}.png")
                    page.screenshot(path=screenshot_path)
                    failed_downloads.append({'filename': filename_1, 'error': str(e)})
                    print(f"!!! FALLO EN DESCARGA 1: Timeout. Captura guardada en {screenshot_path}")

                # --- DESCARGA 2 (CASO CLINICO) ---
                filename_2 = ""
                try:
                    filename_2 = (f"{START_YEAR}-{START_DISEASE}-{department_to_process.replace(' ', '_')}"
                                  f"-{province_to_process.replace(' ', '_')}-CasoClinico")
                    page.get_by_role("tab", name="Tabla: Casos según diagnóstico").click()
                    wait_for_processing_to_finish(page)
                    with page.expect_download(timeout=90000) as download_info:
                        page.locator("#ten-tbl06c-download").click()
                    download = download_info.value
                    download.save_as(os.path.join(download_folder, f"{filename_2}.xlsx"))
                    print(f"¡Descarga 2/2 para {province_to_process} completa!")
                except PlaywrightTimeoutError as e:
                    screenshot_path = os.path.join(screenshots_folder, f"{filename_2}.png")
                    page.screenshot(path=screenshot_path)
                    failed_downloads.append({'filename': filename_2, 'error': str(e)})
                    print(f"!!! FALLO EN DESCARGA 2: Timeout. Captura guardada en {screenshot_path}")

                # --- BUCLE INTERIOR PARA CADA DISTRITO ---
                all_district_names = get_options_from_dropdown(page, "#ten-fdist-filter-selectized", f"Distrito de {province_to_process}")
                if not all_district_names:
                    print(f"!!! FALLO CRÍTICO: No se pudo obtener la lista de distritos para {province_to_process}. Omitiendo sus distritos.")
                    failed_downloads.append({'filename': f"{START_YEAR}-{START_DISEASE}-{department_to_process}-{province_to_process}", 'error': 'No se pudo obtener la lista de distritos.'})
                    continue

                valid_districts = [name for name in all_district_names if name != "..."]
                print(f"Se procesarán {len(valid_districts)} distritos: {valid_districts}")



                for district_to_process in valid_districts:
                    print(f"\n--- INICIANDO PROCESO PARA EL DISTRITO: {district_to_process} ---")
                    
                    # SELECCIONAR EL DISTRITO ACTUAL CON LÓGICA DE REINTENTO
                    success_dist = False
                    for attempt in range(3):
                        print(f"Intento {attempt + 1}/3 para seleccionar '{district_to_process}'...")
                        page.locator("#ten-fdist-filter-selectized").click()
                        try:
                            exact_district_selector = re.compile(f"^{re.escape(district_to_process)}$")
                            page.locator(".selectize-dropdown-content:visible .option", has_text=exact_district_selector).wait_for(timeout=5000)
                            page.locator(".selectize-dropdown-content:visible .option", has_text=exact_district_selector).click()
                            wait_for_processing_to_finish(page)
                            success_dist = True
                            break
                        except PlaywrightTimeoutError:
                            print(f"Intento {attempt + 1} fallido. Reintentando...")
                            if attempt < 2:
                                try:
                                    page.locator(".selectize-dropdown-content:visible .option").first.click()
                                except:
                                    pass
                                time.sleep(1)
                    
                    if not success_dist:
                        print(f"!!! FALLO CRÍTICO: No se pudo seleccionar el distrito {district_to_process}. Omitiendo.")
                        failed_downloads.append({'filename': f"{START_YEAR}-{START_DISEASE}-{department_to_process}-{province_to_process}-{district_to_process}", 'error': 'No se pudo seleccionar el distrito.'})
                        continue
                    
                    # --- DESCARGA A NIVEL DE DISTRITO ---
                    filename_3 = ""
                    try:
                        filename_3 = (f"{START_YEAR}-{START_DISEASE}-{department_to_process.replace(' ', '_')}"
                                      f"-{province_to_process.replace(' ', '_')}-{district_to_process.replace(' ', '_')}")
                        print("Haciendo clic en 'Procesar'...")
                        page.locator("#ten-run").click()
                        print("Procesando, esperando que el contenido se actualice...")
                        page.locator("html.shiny-busy").wait_for(state='visible', timeout=15000)
                        page.locator("html.shiny-busy").wait_for(state='hidden', timeout=60000)
                        
                        with page.expect_download(timeout=90000) as download_info:
                            page.locator("#ten-tbl05b-download").click()
                        download = download_info.value
                        download.save_as(os.path.join(download_folder, f"{filename_3}.xlsx"))
                        print(f"¡Descarga para '{district_to_process}' completa!")
                    except PlaywrightTimeoutError as e:
                        screenshot_path = os.path.join(screenshots_folder, f"{filename_3}.png")
                        page.screenshot(path=screenshot_path)
                        failed_downloads.append({'filename': filename_3, 'error': str(e)})
                        print(f"!!! FALLO EN DESCARGA 3: Timeout para {district_to_process}. Captura guardada.")
                        continue

    except Exception as e:
        print(f"\n--- FALLO GENERAL ---")
        print(f"Ocurrió un error inesperado en el flujo principal: {e}")
        page.screenshot(path=os.path.join(screenshots_folder, "fallo_general.png"))

    finally:
        # --- REPORTE FINAL DE FALLOS ---
        print("\n\n==================== REPORTE FINAL ====================")
        if not failed_downloads:
            print("¡Todas las descargas se completaron con éxito!")
        else:
            print(f"Se encontraron {len(failed_downloads)} fallos durante la ejecución:")
            for failed in failed_downloads:
                print(f"  - Archivo/Contexto: {failed['filename']}")
                print(f"    Error: {failed['error']}\n")
        print("======================================================")

        print("\n¡Proceso de iteración finalizado! El navegador se cerrará en 15 segundos.")
        time.sleep(15)
        browser.close()

with sync_playwright() as playwright:
    run(playwright)

print("Script finalizado.")                
import asyncio
import re
import os
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, expect

async def wait_for_specific_table(page, table_id, description):
    """
    Función genérica para esperar a que una tabla con un ID específico se haga visible.
    """
    print(f"Esperando a que la tabla '{description}' (#{table_id}) aparezca...")
    table_locator = page.locator(f"#{table_id}")
    await table_locator.wait_for(state="visible", timeout=30000)
    print(f"Tabla '{description}' visible.")

async def scrape_and_select_option(page, dropdown_selector, dropdown_name, option_to_select=None, selection_index=0):
    """
    Función resiliente: Intenta cargar las opciones hasta 3 veces.
    Si falla, cierra el menú, espera y reintenta SIN recargar la página.
    """
    max_retries = 3
    retry_delay_ms = 3000

    for attempt in range(max_retries):
        print(f"\n--- Obteniendo opciones de '{dropdown_name}' (Intento {attempt + 1}/{max_retries}) ---")
        
        await page.click(dropdown_selector)
        
        visible_dropdown_locator = page.locator(".selectize-dropdown-content:visible")
        
        try:
            await visible_dropdown_locator.locator(".option").first.wait_for(timeout=5000)
        except PlaywrightTimeoutError:
             raise Exception(f"El menú desplegable para '{dropdown_name}' no apareció.")

        options = await visible_dropdown_locator.locator(".option").all()
        option_texts = [await opt.inner_text() for opt in options]

        if len(option_texts) > 1 or (len(option_texts) == 1 and option_texts[0] != "..."):
            print("Opciones cargadas correctamente.")
            for text in option_texts:
                print(f"- {text}")
            print("-------------------------------------------------")
            
            selection_text = ""
            if option_to_select:
                selection_text = option_to_select
            elif len(option_texts) > selection_index:
                selection_text = option_texts[selection_index]
            else:
                raise ValueError("Índice de selección fuera de rango.")

            print(f"Seleccionando '{selection_text}' para cerrar el menú...")
            option_to_click = visible_dropdown_locator.locator(".option", has_text=re.compile(f"^{re.escape(selection_text)}$"))
            await option_to_click.click()
            
            await wait_for_specific_table(page, "ten-tbl04-tbl", "principal")
            
            return selection_text
        else:
            print(f"Datos no válidos encontrados. La red puede estar lenta. Reintentando en {retry_delay_ms / 1000} segundos...")
            await visible_dropdown_locator.locator(".option").first.click()
            await page.wait_for_timeout(retry_delay_ms)
    
    raise Exception(f"No se pudieron cargar las opciones válidas para '{dropdown_name}' después de {max_retries} intentos.")


async def main():
    """
    Función principal que orquesta todo el proceso de scraping.
    """
    print("Iniciando el scraper...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) 
        page = await browser.new_page()

        try:
            print("Navegando al sitio web...")
            await page.goto("https://app7.dge.gob.pe/maps/sala_metaxenica/", timeout=60000)
            print("Página cargada con éxito.")

            print("\nCambiando a la pestaña 'Tablas'...")
            await page.click("a[data-value='Tablas']")
            await wait_for_specific_table(page, "ten-tbl04-tbl", "principal inicial")
            
            selected_year = await scrape_and_select_option(page, "#ten-fyear-selectized", "Año de análisis", option_to_select="2025")
            selected_disease = await scrape_and_select_option(page, "#ten-fenfe-selectized", "Enfermedad", option_to_select="DENGUE")
            selected_department = await scrape_and_select_option(page, "#ten-fdepa-filter-selectized", "Departamento", option_to_select="AMAZONAS")
            selected_province = await scrape_and_select_option(page, "#ten-fprov-filter-selectized", "Provincia", selection_index=1)
            
            print("\nPresionando el botón 'Procesar'...")
            await page.click("#ten-run")
            
            await wait_for_specific_table(page, "ten-tbl06a-tbl", "Tabla: Casos según años")
            print("Contenido post-procesamiento cargado.")
            
            # --- Primera Descarga ---
            print("\nCambiando a la pestaña 'Tabla: Casos y defunciones'...")
            # <<< LA CORRECCIÓN DEFINITIVA: Selector contextual y robusto
            await page.locator('div.card-header a[data-value="Tabla: Casos y defunciones"]').click()
            await wait_for_specific_table(page, "ten-tbl06b-tbl", "Casos y defunciones")
            
            print("Iniciando la primera descarga...")
            async with page.expect_download() as download_info_1:
                await page.click("#ten-tbl06b-download")
            download_1 = await download_info_1.value
            
            download_folder = "descargas"
            os.makedirs(download_folder, exist_ok=True)
            
            base_filename = (f"{selected_year}-{selected_disease}-{selected_department}-{selected_province}").replace(' ', '-')
            filename_1 = f"{base_filename}-CasosDefunciones.xlsx"
            path_1 = os.path.join(download_folder, filename_1)
            await download_1.save_as(path_1)
            print(f"Descarga 1 completa. Archivo guardado como: {path_1}")

            # --- Segunda Descarga ---
            print("\nCambiando a la pestaña 'Tabla: Casos según diagnóstico'...")
            await page.locator('div.card-header a[data-value="Tabla: Casos según diagnóstico"]').click()
            await wait_for_specific_table(page, "ten-tbl06c-tbl", "Casos según diagnóstico")
            
            print("Iniciando la segunda descarga...")
            async with page.expect_download() as download_info_2:
                await page.click("#ten-tbl06c-download")
            download_2 = await download_info_2.value

            filename_2 = f"{base_filename}-CasosDiagnostico.xlsx"
            path_2 = os.path.join(download_folder, filename_2)
            await download_2.save_as(path_2)
            print(f"Descarga 2 completa. Archivo guardado como: {path_2}")
            
            print("\nFlujo de trabajo y ambas descargas completados con éxito.")

        except PlaywrightTimeoutError as e:
            print(f"\nERROR: La operación excedió el tiempo de espera. Detalles: {e}")
        except Exception as e:
            print(f"\nERROR: Ocurrió un error inesperado: {e}")
        finally:
            print("El script ha finalizado. El navegador se cerrará en 15 segundos...")
            await page.wait_for_timeout(15000)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
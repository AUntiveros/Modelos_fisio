#import time
#from playwright.sync_api import sync_playwright
#
#def run(playwright):
#    browser = playwright.chromium.launch(headless=False)
#    page = browser.new_page()
#    
#    url = "https://app7.dge.gob.pe/maps/sala_metaxenica/"
#    print(f"Navegando a: {url}")
#    page.goto(url)
#    
#    print("Haciendo clic en la pestaña 'Tablas'...")
#    page.get_by_role("tab", name="Tablas").click()
#    
#    # --- NUEVO CÓDIGO ---
#    # 1. Hacemos clic en el control del menú desplegable de Año para abrirlo.
#    #    Usamos un selector que apunta al div específico del año.
#    print("Abriendo el menú desplegable de 'Año'...")
#    year_dropdown = page.locator("#ten-fyear .selectize-input")
#    year_dropdown.click()
#
#    # 2. Esperamos un momento a que las opciones carguen y las leemos.
#    #    Las opciones están en un contenedor diferente que aparece al hacer clic.
#    print("Leyendo las opciones disponibles...")
#    # Buscamos elementos con la clase 'option' dentro del desplegable que se abrió.
#    option_elements = page.locator(".selectize-dropdown-content .option")
#    
#    # Esperamos a que el primer elemento sea visible para asegurar que cargaron.
#    option_elements.first.wait_for()
#    
#    # Extraemos el texto de todas las opciones y lo imprimimos.
#    all_options = option_elements.all_text_contents()
#    print(f"Opciones encontradas: {all_options}")
#
#    # 3. Hacemos clic en la opción "2025".
#    #    Playwright tiene un localizador muy útil para esto.
#    print("Seleccionando el año '2025'...")
#    page.get_by_role("option", name="2025").click()
#    # --- FIN DEL NUEVO CÓDIGO ---
#
#    print("Año seleccionado. El navegador se cerrará en 7 segundos.")
#    time.sleep(7)
#    
#    browser.close()
#
#with sync_playwright() as playwright:
#    run(playwright)
#
#print("Script finalizado.")


#-------------------------------------------------------
#import time
#from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
#
#def run(playwright):
#    browser = playwright.chromium.launch(headless=False)
#    page = browser.new_page()
#    
#    url = "https://app7.dge.gob.pe/maps/sala_metaxenica/"
#    print(f"Navegando a: {url}")
#    page.goto(url)
#    
#    print("Haciendo clic en la pestaña 'Tablas'...")
#    page.get_by_role("tab", name="Tablas").click()
#    
#    # --- CÓDIGO CORREGIDO ---
#    try:
#        # Tu diagnóstico es correcto. El contenido de la pestaña tarda en cargar.
#        # En lugar de un delay fijo, le decimos a Playwright que espere ACTIVAMENTE
#        # hasta que el selector del año sea VISIBLE.
#        print("Esperando a que el menú del año sea visible...")
#        year_dropdown = page.locator("#ten-fyear .selectize-input")
#        
#        # Esta es la línea clave: espera hasta 30 segundos a que el elemento
#        # aparezca y sea visible antes de continuar.
#        year_dropdown.wait_for(state='visible')
#        
#        print("El menú es visible. Procediendo a hacer clic...")
#        year_dropdown.click()
#        
#        # El resto del código para leer las opciones...
#        print("Leyendo las opciones disponibles...")
#        option_elements = page.locator(".selectize-dropdown-content .option")
#        option_elements.first.wait_for() # Esperar a que las opciones aparezcan
#        
#        all_options = option_elements.all_text_contents()
#        print(f"Opciones encontradas: {all_options}")
#        
#        print("Seleccionando el año '2025'...")
#        page.get_by_role("option", name="2025").click()
#
#    except PlaywrightTimeoutError:
#        print("Error: El menú desplegable del año no apareció a tiempo.")
#        print("Es posible que la página haya cambiado o haya tardado demasiado en cargar.")
#    # --- FIN DEL CÓDIGO CORREGIDO ---
#
#    print("Año seleccionado. El navegador se cerrará en 7 segundos.")
#    time.sleep(7)
#    
#    browser.close()
#
#with sync_playwright() as playwright:
#    run(playwright)
#
#print("Script finalizado.")

#-------------------------------------------------------

"""
Tener cuidado con los selectores. DEntro de su "div" hay que buscar un "input"
que es el que realmente se puede clicar. Se estaba trabajando con el marco, en lugar del contenido.

"""


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
Versión final a usar:
- code_v14.py
   - Se puede insertar manualmente: Año, Enfermedad, Departamento (para iniciar desde ahí, caso contrario, None)
   - Se reportará en caso haya errores, esos se descarga manualmente (ver que se haya hecho hasta el último)
      - En caso el mensaje antes de "Reporte de fallos" sea un error, entonces se ha cortado durante el proceso (error desconocido)
Scraping [en proceso]:
- Dengue:
   - 2025 [completo]
   - 2024 [completo]
   - 2023
   - 2022
- Malaria:
   - 2025
   - 2024
   - 2023
   - 2022


Falta:
    - Acceder a una provincia (poner condicional)  [completo]
    - Procesar [completo] + [inclusión de un sistema para evaluar si la página está ocupada] [completo]
    - Seleccionar las tablas esas de casos y defunciones ; casos y clínicos [completo]
    - Descargar cada uno [completo]
    - Acceder a un distrito [completo]
    - Procesar [completo]
    - descargar la tabla [completo]
    - Iterar por distritos [completo]
    - Iterar por provincias [completo]
    - Iterar por departamentos [completo]
    - Iterar por años (opcional) [no, son solo pocos]

Ojo con el nombre del archivo:
Año-Enfermedad-Departamento-Provincia-CasoDefuncion
Año-Enfermedad-Departamento-Provincia-CasoClinico
Año-Enfermedad-Departamento-Provincia-Distrito

Nombres:
- v1 -> solo ingreso a la página
- v2 -> seleccionar Tablas
- v3 -> seleccionar año
- v4 -> seleccionar enfermedad
- v5 -> seleccionar departamento
- v6 -> seleccionar provincia 
   - (por probar el método en caso de error: no cargaron los elementos de provincia)
- v7 -> Procesar (+ esperar a que cargue)
- v8 -> Presionar Tabla:Casos y defunciones + descargar (con nombre definido)
   - Ojo: no se ha esperado luego de presionar "Procesar", en caso de error, puede que sea esto. Pero de momento, está funcionando bien
- v9 -> Presionar Tabla: Casos según diagnóstico + descargar (con el nombre definido)
- v10 -> seleccionar distrito + procesar (la lógica de manejo de eror de provincia funciona)
- v11 -> Descargar y renombrar (con la lógica de espera de carga del paso anterior)
- v12 -> Iterar por distritos (se mantiene la lógica de intentos para distritos y provincia)
- v13 -> Iterar por provincia (se mantiene lógica de intentos)
   - Problema resuelto de nombres iguales
- v14 -> Iterar por departamentos (se mantiene varias lógicas)
   - Hubo error 
      * Solucionando con manejo de error para apertura de lista desplegable
      * Agregando detalles de error en el reporte final
      * Aumentando el tiempo de descarga (60 -> 90 s)
   - OJO: los que no se pudieron descargar (ver los logs) se descargarán a mano
      - Se imprimirá un log con los que hubo un fallo en descarga
   - A veces da error: se procede con descarga manual (error: desconocido)
   - Se ha seteado variables para inicio (se puede seleccionar desde qué departamento iniciar)

Se hace manual lo de años (pero se puede setear), también las enfermedades
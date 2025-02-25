import subprocess

# Ruta de los scripts
script1 = "C:\\Users\\albar\\Desktop\\Proyecto de Investigación\\versiones buenas\\sacar_enlaces_varias_paginas_bien.py"
script2 = "C:\\Users\\albar\\Desktop\\Proyecto de Investigación\\versiones buenas\\subveciones_mas_datos.py"
script3 = "C:\\Users\\albar\\Desktop\\Proyecto de Investigación\\prueba_descarhas.py"

def ejecutar_script(script):
    try:
        print(f"Ejecutando {script}...")
        resultado = subprocess.run(["python", script], capture_output=True, text=True)
        print(resultado.stdout)
        print(resultado.stderr)
    except Exception as e:
        print(f"Error al ejecutar {script}: {e}")

# Ejecutar los scripts en orden
ejecutar_script(script1)
ejecutar_script(script2)
ejecutar_script(script3)

print("Todos los scripts se han ejecutado correctamente.")

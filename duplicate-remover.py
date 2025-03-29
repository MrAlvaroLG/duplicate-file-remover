import os
import sys
import hashlib
import time
import shutil
from argparse import ArgumentParser
from collections import defaultdict

def barra_progreso(actual, total, longitud=50):
    """Muestra una barra de progreso en la consola."""
    porcentaje = int(100 * (actual / total))
    completado = int(longitud * actual // total)
    barra = "█" * completado + "-" * (longitud - completado)
    return f"\r[{barra}] {porcentaje}% ({actual}/{total})"

def calcular_hash(archivo, bloque=65536):
    hasher = hashlib.md5()
    with open(archivo, 'rb') as f:
        bloque_bytes = f.read(bloque)
        while len(bloque_bytes) > 0:
            hasher.update(bloque_bytes)
            bloque_bytes = f.read(bloque)
    return hasher.hexdigest()

def encontrar_duplicados(directorio):
    hashes = {}
    rutas_directorios = set()
    
    # Primero contamos cuántos archivos hay para la barra de progreso
    print("Contando archivos...")
    total_archivos = 0
    for raiz, dirs, archivos in os.walk(directorio):
        total_archivos += len(archivos)
        # Guardamos las rutas de los directorios para análisis posterior
        for dir_nombre in dirs:
            ruta_dir = os.path.join(raiz, dir_nombre)
            rutas_directorios.add(ruta_dir)
    
    if total_archivos == 0:
        print("No se encontraron archivos para analizar.")
        return hashes, {}
    
    print(f"Analizando {total_archivos} archivos...")
    
    # Procesamos los archivos con barra de progreso
    archivo_actual = 0
    archivos_por_directorio = defaultdict(list)
    
    for raiz, dirs, archivos in os.walk(directorio):
        for archivo in archivos:
            ruta_completa = os.path.join(raiz, archivo)
            try:
                file_hash = calcular_hash(ruta_completa)
                if file_hash in hashes:
                    hashes[file_hash].append(ruta_completa)
                else:
                    hashes[file_hash] = [ruta_completa]
                
                # Registramos este archivo en su directorio padre
                archivos_por_directorio[raiz].append((archivo, file_hash))
            except (IOError, PermissionError):
                print(f"\nError accediendo: {ruta_completa}")
            
            archivo_actual += 1
            sys.stdout.write(barra_progreso(archivo_actual, total_archivos))
            sys.stdout.flush()
    
    print("\nAnálisis completo!")
    
    # Ahora analizamos directorios para encontrar duplicados
    print("Analizando directorios duplicados...")
    directorios_hash = {}
    
    # Solo consideramos directorios que tienen archivos
    directorios_validos = list(rutas_directorios.intersection(archivos_por_directorio.keys()))
    total_dirs = len(directorios_validos)
    
    if total_dirs > 0:
        print(f"Analizando {total_dirs} directorios...")
        for idx, dir_path in enumerate(directorios_validos):
            # Creamos una firma para el directorio basada en nombres de archivos y hashes
            contenido = sorted(archivos_por_directorio[dir_path])
            if contenido:  # Solo consideramos directorios no vacíos
                dir_hash = hashlib.md5(str(contenido).encode()).hexdigest()
                if dir_hash in directorios_hash:
                    directorios_hash[dir_hash].append(dir_path)
                else:
                    directorios_hash[dir_hash] = [dir_path]
            
            sys.stdout.write(barra_progreso(idx + 1, total_dirs))
            sys.stdout.flush()
        
        print("\nAnálisis de directorios completo!")
    
    # Filtramos solo los directorios con duplicados
    directorios_duplicados = {h: dirs for h, dirs in directorios_hash.items() if len(dirs) > 1}
    return hashes, directorios_duplicados

def eliminar_duplicados(hashes, directorios_duplicados, eliminar_sin_preguntar=False):
    # Lista para registrar archivos que han sido eliminados como parte de carpetas
    archivos_ya_eliminados = set()
    
    # Primero procesamos los directorios duplicados
    total_grupos_dir = len(directorios_duplicados)
    
    if total_grupos_dir > 0:
        print(f"\nSe encontraron {total_grupos_dir} grupos de directorios duplicados.")
        
        grupo_actual = 0
        for hash_value, directorios in directorios_duplicados.items():
            grupo_actual += 1
            sys.stdout.write(f"\nGrupo de directorios {grupo_actual}/{total_grupos_dir} - ")
            
            print(f"\nDirectorios duplicados:")
            for i, directorio in enumerate(directorios, 1):
                print(f"{i}. {directorio}")
            
            if eliminar_sin_preguntar:
                eliminar = directorios[1:]
            else:
                respuesta = input("¿Qué directorios completos quieres eliminar? (ej: 2,3 o 'todos' o 'ninguno'): ")
                if respuesta.lower() == 'todos':
                    eliminar = directorios[1:]
                elif respuesta.lower() == 'ninguno':
                    continue
                else:
                    try:
                        indices = list(map(int, respuesta.split(',')))
                        eliminar = [directorios[i-1] for i in indices if 0 < i <= len(directorios)]
                    except:
                        print("Entrada inválida, saltando...")
                        continue
            
            for directorio in eliminar:
                try:
                    # Registramos todos los archivos en el directorio que vamos a eliminar
                    for raiz, _, archivos in os.walk(directorio):
                        for archivo in archivos:
                            ruta_completa = os.path.join(raiz, archivo)
                            archivos_ya_eliminados.add(ruta_completa)
                    
                    shutil.rmtree(directorio)
                    print(f"Eliminado directorio completo: {directorio}")
                except Exception as e:
                    print(f"Error eliminando directorio {directorio}: {str(e)}")
    
    # Luego procesamos los archivos duplicados individuales
    # Identificamos grupos de duplicados
    duplicados = {h: archivos for h, archivos in hashes.items() if len(archivos) > 1}
    
    # Limpiamos las listas de archivos duplicados, excluyendo los que ya han sido eliminados
    for hash_value, archivos in list(duplicados.items()):
        # Filtramos los archivos que ya han sido eliminados o que ya no existen
        archivos_existentes = [a for a in archivos if a not in archivos_ya_eliminados and os.path.exists(a)]
        
        if len(archivos_existentes) <= 1:
            # Si no quedan duplicados (0 o 1 archivo), eliminamos el grupo
            del duplicados[hash_value]
        else:
            # Actualizamos la lista con solo los archivos existentes
            duplicados[hash_value] = archivos_existentes
    
    total_grupos = len(duplicados)
    
    if total_grupos == 0:
        if total_grupos_dir == 0:
            print("No se encontraron archivos ni directorios duplicados.")
        else:
            print("No se encontraron archivos duplicados adicionales.")
        return
    
    print(f"\nSe encontraron {total_grupos} grupos de archivos duplicados.")
    
    # Procesamos los duplicados con barra de progreso
    grupo_actual = 0
    for hash_value, archivos in duplicados.items():
        grupo_actual += 1
        sys.stdout.write(f"\nGrupo de archivos {grupo_actual}/{total_grupos} - ")
        
        print(f"\nArchivos duplicados (Hash: {hash_value}):")
        for i, archivo in enumerate(archivos, 1):
            print(f"{i}. {archivo}")
        
        if eliminar_sin_preguntar:
            eliminar = archivos[1:]
        else:
            respuesta = input("¿Qué archivos quieres eliminar? (ej: 2,3 o 'todos' o 'ninguno'): ")
            if respuesta.lower() == 'todos':
                eliminar = archivos[1:]
            elif respuesta.lower() == 'ninguno':
                continue
            else:
                try:
                    indices = list(map(int, respuesta.split(',')))
                    eliminar = [archivos[i-1] for i in indices if 0 < i <= len(archivos)]
                except:
                    print("Entrada inválida, saltando...")
                    continue
        
        for archivo in eliminar:
            try:
                os.remove(archivo)
                print(f"Eliminado: {archivo}")
            except Exception as e:
                print(f"Error eliminando {archivo}: {str(e)}")
    
    print("\nProceso completado.")

def main():
    parser = ArgumentParser(description='Elimina archivos y directorios duplicados')
    parser.add_argument('directorio', help='Directorio a analizar')
    parser.add_argument('-y', action='store_true', help='Eliminar automáticamente sin confirmar')
    args = parser.parse_args()

    if not os.path.isdir(args.directorio):
        print("Error: El directorio especificado no existe")
        sys.exit(1)

    tiempo_inicio = time.time()
    print("Buscando duplicados...")
    hashes, directorios_duplicados = encontrar_duplicados(args.directorio)
    
    # Calcular y mostrar el tiempo transcurrido
    tiempo_busqueda = time.time() - tiempo_inicio
    print(f"Tiempo de búsqueda: {tiempo_busqueda:.2f} segundos")
    
    eliminar_duplicados(hashes, directorios_duplicados, args.y)

if __name__ == '__main__':
    main()
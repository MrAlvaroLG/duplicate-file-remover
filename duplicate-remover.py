import os
import sys
import hashlib
from argparse import ArgumentParser

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
    for raiz, dirs, archivos in os.walk(directorio):
        for archivo in archivos:
            ruta_completa = os.path.join(raiz, archivo)
            try:
                file_hash = calcular_hash(ruta_completa)
                if file_hash in hashes:
                    hashes[file_hash].append(ruta_completa)
                else:
                    hashes[file_hash] = [ruta_completa]
            except (IOError, PermissionError):
                print(f"Error accediendo: {ruta_completa}")
    return hashes

def eliminar_duplicados(hashes, eliminar_sin_preguntar=False):
    for hash_value, archivos in hashes.items():
        if len(archivos) > 1:
            print(f"\nDuplicados encontrados (Hash: {hash_value}):")
            for i, archivo in enumerate(archivos, 1):
                print(f"{i}. {archivo}")
            
            if eliminar_sin_preguntar:
                eliminar = archivos[1:]
            else:
                respuesta = input("¿Qué archivos quieres eliminar? (ej: 2,3 o 'todos'): ")
                if respuesta.lower() == 'todos':
                    eliminar = archivos[1:]
                else:
                    try:
                        indices = list(map(int, respuesta.split(',')))
                        eliminar = [archivos[i-1] for i in indices if i > 0]
                    except:
                        print("Entrada inválida, saltando...")
                        continue
            
            for archivo in eliminar:
                try:
                    os.remove(archivo)
                    print(f"Eliminado: {archivo}")
                except Exception as e:
                    print(f"Error eliminando {archivo}: {str(e)}")

def main():
    parser = ArgumentParser(description='Elimina archivos duplicados')
    parser.add_argument('directorio', help='Directorio a analizar')
    parser.add_argument('-y', action='store_true', help='Eliminar automáticamente sin confirmar')
    args = parser.parse_args()

    if not os.path.isdir(args.directorio):
        print("Error: El directorio especificado no existe")
        sys.exit(1)

    print("Buscando duplicados...")
    hashes = encontrar_duplicados(args.directorio)
    eliminar_duplicados(hashes, args.y)

if __name__ == '__main__':
    main()
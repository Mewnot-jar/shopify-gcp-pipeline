from extract import paginar_todos, QUERY_PRODUCTOS, QUERY_ORDENES, QUERY_CLIENTES
from ingest_raw import guardar_como_json, subir_a_gcs 
from datetime import date

ENTIDADES = {
    "products": QUERY_PRODUCTOS,
    "orders": QUERY_ORDENES,
    "customers": QUERY_CLIENTES,
}

def main():
    fecha = date.today().isoformat()
    resumen = {"nuevo":0, "actualizado":0, "sin_cambios":0}

    for nombre_entidad, query in ENTIDADES.items():
        print(f"\nExtrayendo: {nombre_entidad}...")
        datos = paginar_todos(query, nombre_entidad)

        ruta_local = guardar_como_json(datos, nombre_entidad, fecha)
        _, estado = subir_a_gcs(ruta_local, nombre_entidad, fecha)
        resumen[estado] += 1

    print(f"\nResumen: {resumen['nuevo']} nuevos, {resumen['actualizado']} actualizados, {resumen['sin_cambios']} sin cambios.")

        

if __name__ == "__main__":
    main()
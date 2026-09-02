from extract import paginar_todos, guardar_como_json, subir_a_gcs, QUERY_PRODUCTOS, QUERY_ORDENES, QUERY_CLIENTES
from datetime import date

ENTIDADES = {
    "products": QUERY_PRODUCTOS,
    "orders": QUERY_ORDENES,
    "customers": QUERY_CLIENTES,
}

def main():
    fecha = date.today().isoformat()

    for nombre_entidad, query in ENTIDADES.items():
        print(f"\nExtrayendo: {nombre_entidad}...")
        datos = paginar_todos(query, nombre_entidad)

        ruta_local = guardar_como_json(datos, nombre_entidad, fecha)
        subir_a_gcs(ruta_local, nombre_entidad, fecha)

        

if __name__ == "__main__":
    main()
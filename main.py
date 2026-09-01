from extract import paginar_todos, guardar_como_json, subir_a_gcs, QUERY_PRODUCTOS, QUERY_ORDENES, QUERY_CLIENTES

ENTIDADES = {
    "products": QUERY_PRODUCTOS,
    "orders": QUERY_ORDENES,
    "customers": QUERY_CLIENTES,
}

def main():
    for nombre_entidad, query in ENTIDADES.items():
        print(f"\nExtrayendo: {nombre_entidad}...")
        datos = paginar_todos(query, nombre_entidad)

        ruta_local = guardar_como_json(datos, nombre_entidad)
        subir_a_gcs(ruta_local)

        

if __name__ == "__main__":
    main()
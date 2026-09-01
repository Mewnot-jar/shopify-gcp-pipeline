from extract import paginar_todos, QUERY_PRODUCTOS, QUERY_ORDENES, QUERY_CLIENTES

def main():
    productos = paginar_todos(QUERY_PRODUCTOS, "products")
    print(f"\nTotal productos: {len(productos)} productos.")

    ordenes = paginar_todos(QUERY_ORDENES, "orders")
    print(f"\nTotal ordenes: {len(ordenes)} ordenes.")

    clientes = paginar_todos(QUERY_CLIENTES, "customers")
    print(f"\nTotal clientes: {len(clientes)} clientes.")

if __name__ == "__main__":
    main()
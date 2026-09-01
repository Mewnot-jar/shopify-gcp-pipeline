from extract import paginar_todos, QUERY_PRODUCTOS

def main():
    productos = paginar_todos(QUERY_PRODUCTOS, "products")
    print(f"\nTotal final: {len(productos)} productos.")

if __name__ == "__main__":
    main()
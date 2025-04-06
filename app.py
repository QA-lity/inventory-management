import sqlite3
import hashlib

# Conectar a la base de datos
def conectar_bd():
    return sqlite3.connect("inventario.db")

# Crear las tablas si no existen
def inicializar_bd():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Función para hashear contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Verificar si hay usuarios existentes
def hay_usuarios():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    cantidad = cursor.fetchone()[0]
    conn.close()
    return cantidad > 0

# Crear un nuevo usuario
def crear_usuario():
    print("\n=== Crear usuario administrador ===")
    username = input("Nombre de usuario: ").strip()
    password = input("Contraseña: ").strip()
    password_hash = hash_password(password)

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (username, password_hash) VALUES (?, ?)", (username, password_hash))
    conn.commit()
    conn.close()
    print("Usuario creado con éxito.")

# Verificar credenciales
def autenticar_usuario():
    print("\n=== Inicio de Sesión ===")
    username = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()
    password_hash = hash_password(password)

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password_hash = ?", (username, password_hash))
    usuario = cursor.fetchone()
    conn.close()
    return usuario is not None

# Función para agregar un producto
def agregar_producto(nombre, descripcion, cantidad, precio, categoria):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria) VALUES (?, ?, ?, ?, ?)", 
                   (nombre, descripcion, cantidad, precio, categoria))
    conn.commit()
    conn.close()
    print(f"Producto '{nombre}' agregado con éxito.")

# Función para mostrar todos los productos
def mostrar_productos():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()

    if not productos:
        print("No hay productos en el inventario.")
        return

    print("\nInventario de productos:")
    for producto in productos:
        print(f"ID: {producto[0]} | Nombre: {producto[1]} | Cantidad: {producto[3]} | Precio: ${producto[4]} | Categoría: {producto[5]}")

# Función para actualizar la cantidad de un producto
def actualizar_cantidad(id_producto, nueva_cantidad):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, id_producto))
    conn.commit()
    conn.close()
    print(f"Cantidad del producto ID {id_producto} actualizada a {nueva_cantidad}.")

# Función para eliminar un producto
def eliminar_producto(id_producto):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
    conn.commit()
    conn.close()
    print(f"Producto ID {id_producto} eliminado.")

# Función de búsqueda por nombre
def buscar_producto(nombre):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE nombre LIKE ?", ('%' + nombre + '%',))
    productos = cursor.fetchall()
    conn.close()

    if not productos:
        print(f"No se encontraron productos con el nombre '{nombre}'.")
        return

    print("\nResultados de búsqueda:")
    for producto in productos:
        print(f"ID: {producto[0]} | Nombre: {producto[1]} | Cantidad: {producto[3]} | Precio: ${producto[4]} | Categoría: {producto[5]}")

# Función para registrar un nuevo usuario
def registrar_usuario():
    print("\n=== Registrar nuevo usuario ===")
    username = input("Nuevo nombre de usuario: ").strip()
    password = input("Contraseña: ").strip()
    password_hash = hash_password(password)

    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        print(f"Usuario '{username}' registrado con éxito.")
    except sqlite3.IntegrityError:
        print("Error: El nombre de usuario ya existe.")
    finally:
        conn.close()

# Menú interactivo
def menu():
    while True:
        print("\n--- Sistema de Inventario ---")
        print("1. Agregar producto")
        print("2. Mostrar inventario")
        print("3. Actualizar cantidad de producto")
        print("4. Eliminar producto")
        print("5. Buscar producto por nombre")
        print("6. Registrar nuevo usuario")
        print("7. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombre = input("Nombre del producto: ")
            descripcion = input("Descripción: ")
            cantidad = int(input("Cantidad: "))
            precio = float(input("Precio: "))
            categoria = input("Categoría: ")
            agregar_producto(nombre, descripcion, cantidad, precio, categoria)

        elif opcion == "2":
            mostrar_productos()

        elif opcion == "3":
            id_producto = int(input("Ingrese el ID del producto a actualizar: "))
            nueva_cantidad = int(input("Nueva cantidad: "))
            actualizar_cantidad(id_producto, nueva_cantidad)

        elif opcion == "4":
            id_producto = int(input("Ingrese el ID del producto a eliminar: "))
            eliminar_producto(id_producto)

        elif opcion == "5":
            nombre = input("Ingrese el nombre del producto a buscar: ")
            buscar_producto(nombre)

        elif opcion == "6":
            registrar_usuario()

        elif opcion == "7":
            print("Saliendo del sistema de inventario.")
            break

        else:
            print("Opción inválida. Intente nuevamente.")

# Inicialización y autenticación
inicializar_bd()

if not hay_usuarios():
    crear_usuario()

if autenticar_usuario():
    menu()
else:
    print("Usuario o contraseña incorrectos. No se pudo iniciar sesión. Terminando ejecución.")


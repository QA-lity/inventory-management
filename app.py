import sqlite3
import hashlib
import getpass
import logging

# Configuración de logging
logging.basicConfig(
    filename="inventario.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Conectar a la base de datos
def conectar_bd():
    try:
        return sqlite3.connect("inventario.db")
    except sqlite3.Error as e:
        logging.error(f"Error al conectar a la base de datos: {e}")
        print("Error al conectar a la base de datos. Verifique los registros para más detalles.")
        exit(1)

# Crear las tablas si no existen
def inicializar_bd():
    try:
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
        logging.info("Base de datos inicializada.")
    except sqlite3.Error as e:
        logging.error(f"Error al inicializar la base de datos: {e}")
        print("Error al inicializar la base de datos. Verifique los registros para más detalles.")
        exit(1)

# Función para hashear contraseñas
def hash_password(password):
    try:
        return hashlib.sha256(password.encode()).hexdigest()
    except Exception as e:
        logging.error(f"Error al hashear la contraseña: {e}")
        print("Error al procesar la contraseña. Verifique los registros para más detalles.")
        exit(1)

def hay_usuarios():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        cantidad = cursor.fetchone()[0]
        conn.close()
        return cantidad > 0
    except sqlite3.Error as e:
        logging.error(f"Error al verificar usuarios: {e}")
        print("Error al verificar los usuarios. Verifique los registros para más detalles.")
        exit(1)

def crear_usuario():
    print("\n=== Crear usuario administrador ===")
    username = input("Nombre de usuario: ").strip()
    password = getpass.getpass("Contraseña: ").strip()

    if not username or not password:
        logging.warning("Intento de crear usuario con datos vacíos.")
        print("El nombre de usuario y la contraseña no pueden estar vacíos.")
        return

    password_hash = hash_password(password)

    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        conn.close()
        logging.info(f"Usuario administrador creado: {username}")
        print("Usuario creado con éxito.")
    except sqlite3.IntegrityError:
        logging.warning(f"Intento fallido: el nombre de usuario '{username}' ya existe.")
        print("Error: El nombre de usuario ya existe.")
    except sqlite3.Error as e:
        logging.error(f"Error al crear usuario: {e}")
        print("Error al crear el usuario. Verifique los registros para más detalles.")

def autenticar_usuario():
    print("\n=== Inicio de Sesión ===")
    username = input("Usuario: ").strip()
    password = getpass.getpass("Contraseña: ").strip()

    if not username or not password:
        logging.warning("Intento de inicio de sesión con datos vacíos.")
        print("El nombre de usuario y la contraseña no pueden estar vacíos.")
        return False

    password_hash = hash_password(password)

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password_hash = ?", (username, password_hash))
    usuario = cursor.fetchone()
    conn.close()
    return usuario is not None

# Función de búsqueda por nombre
def busqueda_por_nombre(nombre):
    if not nombre.strip():
        logging.warning("Intento de búsqueda con nombre vacío.")
        print("\nEl nombre no puede estar vacío.")
        return

    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE nombre LIKE ?", ('%' + nombre + '%',))
        productos = cursor.fetchall()
        conn.close()

        if not productos:
            logging.info(f"No se encontraron productos con el nombre '{nombre}'.")
            print(f"\nNo se encontraron productos con el nombre '{nombre}'.")
            return

        print("\nResultados de búsqueda:")
        for producto in productos:
            print(f"ID: {producto[0]} | Nombre: {producto[1]} | Cantidad: {producto[3]} | Precio: ${producto[4]} | Categoría: {producto[5]}")
    except sqlite3.Error as e:
        logging.error(f"Error al buscar por nombre: {e}")
        print("\nError al realizar la búsqueda. Verifique los registros para más detalles.")

# Función de búsqueda por categoría
def busqueda_por_categoria(categoria):
    if not categoria.strip():
        logging.warning("Intento de búsqueda con categoría vacía.")
        print("\nLa categoría no puede estar vacía.")
        return

    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE categoria LIKE ?", ('%' + categoria + '%',))
        productos = cursor.fetchall()
        conn.close()

        if not productos:
            logging.info(f"No se encontraron productos de la categoría '{categoria}'.")
            print(f"\nNo se encontraron productos de la categoría '{categoria}'.")
            return

        print("\nResultados de búsqueda:")
        for producto in productos:
            print(f"ID: {producto[0]} | Nombre: {producto[1]} | Cantidad: {producto[3]} | Precio: ${producto[4]} | Categoría: {producto[5]}")
    except sqlite3.Error as e:
        logging.error(f"Error al buscar por categoría: {e}")
        print("\nError al realizar la búsqueda. Verifique los registros para más detalles.")

# Función de búsqueda por rango de precios
def busqueda_por_precios(inferior, superior):
    try:
        inferior = float(inferior)
        superior = float(superior)

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE precio BETWEEN ? AND ?", (inferior, superior))
        productos = cursor.fetchall()
        conn.close()

        if not productos:
            logging.info(f"No se encontraron productos entre el rango de precios '{inferior}' y '{superior}'.")
            print(f"\nNo se encontraron productos entre el rango de precios '{inferior}' y '{superior}'.")
            return

        print("\nResultados de búsqueda:")
        for producto in productos:
            print(f"ID: {producto[0]} | Nombre: {producto[1]} | Cantidad: {producto[3]} | Precio: ${producto[4]} | Categoría: {producto[5]}")

    except ValueError:
        logging.warning("El usuario ingresó un valor no numérico para los rangos de precios.")
        print("\nError: Ingrese valores numéricos válidos para los rangos de precios.")
    except sqlite3.Error as e:
        logging.error(f"Error al realizar búsqueda por rango de precios: {e}")
        print("\nError al realizar la búsqueda. Verifique los registros para más detalles.")
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")

# Función para registrar un nuevo usuario
def registrar_usuario():
    print("\n=== Registrar nuevo usuario ===")
    username = input("Nuevo nombre de usuario: ").strip()
    password = getpass.getpass("Contraseña: ").strip()
    password_hash = hash_password(password)

    conn = conectar_bd()
    cursor = conn.cursor()
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password_hash = ?", (username, password_hash))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            logging.info(f"Inicio de sesión exitoso: {username}")
            return True
        else:
            logging.warning(f"Intento fallido de inicio de sesión: {username}")
            return False
    except sqlite3.Error as e:
        logging.error(f"Error al autenticar usuario: {e}")
        print("Error al autenticar usuario. Verifique los registros para más detalles.")
        return False

def agregar_producto(nombre, descripcion, cantidad, precio, categoria):
    if not nombre.strip() or not descripcion.strip() or not categoria.strip():
        logging.warning("Intento de agregar producto con campos vacíos.")
        print("Todos los campos son obligatorios.")
        return

    if cantidad < 0 or precio < 0:
        logging.warning(f"Intento de agregar producto con cantidad o precio negativo: {nombre}")
        print("La cantidad y el precio no pueden ser negativos.")
        return

    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria) VALUES (?, ?, ?, ?, ?)", 
                       (nombre, descripcion, cantidad, precio, categoria))
        conn.commit()
        conn.close()
        logging.info(f"Producto agregado: {nombre} ({cantidad} unidades, ${precio}, {categoria})")
        print(f"Producto '{nombre}' agregado con éxito.")
    except sqlite3.Error as e:
        logging.error(f"Error al agregar producto: {e}")
        print("Error al agregar el producto. Verifique los registros para más detalles.")

def mostrar_productos():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        conn.close()

        if not productos:
            logging.info("No hay productos en el inventario.")
            print("No hay productos en el inventario.")
            return

        print("\nInventario de productos:")
        for producto in productos:
            print(f"ID: {producto[0]} | Nombre: {producto[1]} | Cantidad: {producto[3]} | Precio: ${producto[4]} | Categoría: {producto[5]}")
    except sqlite3.Error as e:
        logging.error(f"Error al mostrar productos: {e}")
        print("Error al mostrar los productos. Verifique los registros para más detalles.")

def actualizar_cantidad(id_producto, nueva_cantidad):
    if nueva_cantidad < 0:
        logging.warning(f"Intento de actualizar cantidad a un valor negativo para el producto ID {id_producto}.")
        print("La cantidad no puede ser negativa.")
        return

    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, id_producto))
        conn.commit()
        conn.close()
        logging.info(f"Cantidad actualizada para producto ID {id_producto} a {nueva_cantidad}.")
        print(f"Cantidad del producto ID {id_producto} actualizada a {nueva_cantidad}.")
    except sqlite3.Error as e:
        logging.error(f"Error al actualizar cantidad del producto ID {id_producto}: {e}")
        print("Error al actualizar la cantidad. Verifique los registros para más detalles.")

def eliminar_producto(id_producto):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
        producto = cursor.fetchone()
        
        if not producto:
            logging.warning(f"Intento de eliminar un producto que no existe: ID {id_producto}")
            print(f"Error: El producto con ID {id_producto} no existe.")
            return
        
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conn.commit()
        conn.close()
        logging.info(f"Producto eliminado: ID {id_producto}")
        print(f"Producto ID {id_producto} eliminado.")
    except sqlite3.Error as e:
        logging.error(f"Error al eliminar producto ID {id_producto}: {e}")
        print("Error al eliminar el producto. Verifique los registros para más detalles.")

def buscar_producto(nombre):
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos WHERE nombre LIKE ?", ('%' + nombre + '%',))
        productos = cursor.fetchall()
        conn.close()

        if not productos:
            logging.info(f"No se encontraron productos con el nombre '{nombre}'.")
            print(f"No se encontraron productos con el nombre '{nombre}'.")
            return

        print("\nResultados de búsqueda:")
        for producto in productos:
            print(f"ID: {producto[0]} | Nombre: {producto[1]} | Cantidad: {producto[3]} | Precio: ${producto[4]} | Categoría: {producto[5]}")
    except sqlite3.Error as e:
        logging.error(f"Error al buscar producto: {e}")
        print("Error al buscar el producto. Verifique los registros para más detalles.")

def reporte_inventario():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*), SUM(cantidad * precio) FROM productos WHERE cantidad > 0")
        total_disponibles, valor_total = cursor.fetchone()

        cursor.execute("SELECT nombre, cantidad FROM productos WHERE cantidad > 0")
        disponibles = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM productos WHERE cantidad = 0")
        total_agotados = cursor.fetchone()[0]

        cursor.execute("SELECT nombre FROM productos WHERE cantidad = 0")
        agotados = cursor.fetchall()

        conn.commit()
        conn.close()

        logging.info("Reporte de inventario generado.")

        print("\n--- Reporte de Inventario ---")
        if disponibles:
            print(f"\nProductos disponibles: {total_disponibles}")
            for nombre, cantidad in disponibles:
                print(f"- {nombre}: {cantidad} unidades")
        else:
            print("\nProductos disponibles: 0")

        if agotados:
            print(f"\nProductos agotados: {total_agotados}")
            for nombre in agotados:
                print(f"- {nombre}")
        else:
            print("\nProductos agotados: 0")

        print(f"\nValor total del inventario disponible: ${valor_total}")
    except sqlite3.Error as e:
        logging.error(f"Error al generar el reporte de inventario: {e}")
        print("Error al generar el reporte. Verifique los registros para más detalles.")

# Menú interactivo
def menu():
    while True:
        print("\n--- Sistema de Inventario ---")
        print("1. Agregar producto")
        print("2. Mostrar inventario")
        print("3. Actualizar cantidad de producto")
        print("4. Eliminar producto")
        print("5. Filtrado y búsqueda")
        print("6. Registrar nuevo usuario")
        print("7. Reporte de inventario")
        print("8. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombre = input("Nombre del producto: ")
            descripcion = input("Descripción: ")
            try:
                cantidad = int(input("Cantidad: "))
                precio = float(input("Precio: "))
            except ValueError as e:
                logging.error(f"Error al convertir la cantidad o el precio: {e}")
                print("Error: Ingrese valores numéricos válidos para la cantidad y el precio.")
                return
            categoria = input("Categoría: ")
            agregar_producto(nombre, descripcion, cantidad, precio, categoria)

        elif opcion == "2":
            mostrar_productos()

        elif opcion == "3":
            try:
                id_producto = int(input("Ingrese el ID del producto a actualizar: "))
                nueva_cantidad = int(input("Nueva cantidad: "))
            except ValueError as e:
                logging.error(f"Error al convertir el ID del producto o la nueva cantidad: {e}")
                print("Error: Ingrese valores numéricos válidos para el ID del producto y la nueva cantidad.")
                return
            actualizar_cantidad(id_producto, nueva_cantidad)

        elif opcion == "4":
            try:
                id_producto = int(input("Ingrese el ID del producto a eliminar: "))
            except ValueError as e:
                logging.error(f"Error al convertir el ID del producto: {e}")
                print("Error: Ingrese un valor numérico válido para el ID del producto.")
                return
            eliminar_producto(id_producto)

        elif opcion == "5":
            print("\n1. Búsqueda por nombre")
            print("2. Búsqueda por categoría")
            print("3. Búsqueda por rango de precios")
            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                nombre = input("\nIngrese el nombre del producto a buscar: ")
                busqueda_por_nombre(nombre)

            elif opcion == "2":
                categoria = input("\nIngrese la categoría del producto a buscar: ")
                busqueda_por_categoria(categoria)

            elif opcion == "3":
                inferior = input("\nIngrese el rango inferior: ")
                superior = input("Ingrese el rango superior: ")
                busqueda_por_precios(inferior, superior)

        elif opcion == "6":
            registrar_usuario()

        elif opcion == "7":
            reporte_inventario()

        elif opcion == "8":
            logging.info("Sesión finalizada por el usuario.")
            print("Saliendo del sistema de inventario.")
            break

        else:
            print("Opción inválida. Intente nuevamente.")

# Inicialización y autenticación
if __name__ == "__main__":
    inicializar_bd()

    if not hay_usuarios():
        crear_usuario()

    if autenticar_usuario():
        menu()
    else:
        print("Usuario o contraseña incorrectos. No se pudo iniciar sesión. Terminando ejecución.")


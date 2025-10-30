import mariadb
from sqlalchemy import text

def dbConectar():
    try:
        conn = mariadb.connect (
            user = "root",
            password = "12345", 
            host = "localhost",
            port = 3306,
            database = "orders_db"
        )

        print ("----Conexión con MariaDB realizada correctamente----")

        cursor = conn.cursor()
        consulta = "SELECT DATABASE()"
        cursor.execute(consulta)
        db_nombre = cursor.fetchone()

        print(f"----Conectado a la base de datos: {db_nombre}----")

        cursor.close()

    except mariadb.Exception as e:
        print(f"Error al conectarnos a mariadb: {e}")


def verify_connection(flask_app, db):
    with flask_app.app_context():
        try:
            result = db.session.execute(text("SELECT DATABASE() as db_name"))
            db_name = result.scalar()
            print(f"✅ SQLAlchemy conectado a: {db_name}")
            
            # ✅ SOLO verificar que las tablas existen (no crearlas)
            result = db.session.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Tablas en la base de datos: {tables}")
            
        except Exception as e:
            print(f"❌ Error de SQLAlchemy: {e}")
            return        

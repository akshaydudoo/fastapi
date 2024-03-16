import mysql.connector

# Establish a connection to the database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="api"
        )
        print("Connected to the MySQL database")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    
def close_connection(connection):
    if connection:
        connection.close()
        print("Connection closed")
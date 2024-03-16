import mysql.connector

# Establish a connection to the database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="193.203.184.9",
            user="u862584388_aadish",
            password="Aadish@1008",
            database="u862584388_aadish"
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

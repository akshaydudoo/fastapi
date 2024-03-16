
from mysql.connector import Error

def add_transaction(connection, cursor, transaction_data):
    try:
        sql = """INSERT INTO transactions 
                 (status, message, transid, optransid, referenceid, 
                 number, amount, balance, margin, updated_margin, 
                 user_name, state, gst, category) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        cursor.execute(sql, transaction_data)
        connection.commit()
        print("Transaction added successfully.")
    except Error as e:
        print(f"Error adding transaction: {e}")

def update_transaction(connection, cursor,status,message,balance,optrid,refid,mergin,transid,updated_margin):
    try:
        sql = "UPDATE transactions SET status= %s,message= %s,referenceid= %s,  balance =%s, margin =%s,updated_margin = %s WHERE transid = %s"
        cursor.execute(sql, (status,message,refid ,balance,mergin,updated_margin,transid))
        connection.commit()
        print("Transaction updated successfully.")
    except Error as e:
        print(f"Error updating transaction: {e}")




# def main():
#     try:
#         # Connect to MySQL database
#         connection = mysql.connector.connect(
#             host="your_host",
#             user="your_username",
#             password="your_password",
#             database="your_database"
#         )
        
#         if connection.is_connected():
#             print("Connected to MySQL database")

#             cursor = connection.cursor()

#             # Example data for updating a transaction
#             transid = '12345647'
#             updated_margin = 3.5
            
#             # Update transaction
#             update_transaction(connection, cursor, transid, updated_margin)

#     except Error as e:
#         print(f"Error connecting to MySQL database: {e}")

#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()
#             print("MySQL connection closed")

# if __name__ == "__main__":
#     main()

import requests
import mysql.connector
from db import create_connection
def initiate_transaction(userid, token, opcode, number, amount, transid):
    url = f"https://api.RechargeExchange.com/API.asmx/Transaction"
    payload = {
        'userid': userid,
        'token': token,
        'opcode': opcode,
        'number': number,
        'amount': amount,
        'transid': transid
    }
    try:
        response = requests.get(url, params=payload)
        data = response.json()

        if response.status_code == 200:
            if data['status'] == 'SUCCESS':      
                return data
            else:
                return data
        else:
            
            return response.status_code
    except Exception as e:
        print("An error occurred:", str(e))
        return {"error": "An error occurred"}



# Retrieve user information
def get_user_info(connection, username, apitoken):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT username, api_token, balance,account_status FROM users WHERE username = %s AND api_token = %s", (username, apitoken))
        user_info = cursor.fetchone()
        if user_info:
            return user_info
        else:
            print(f"User '{username}' not found or invalid API token or inactive")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return err

# Update user balance if sufficient funds
def update_user_balance(connection, username, new_balance):
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (new_balance, username))
        connection.commit()
        print(f"User '{username}' balance updated successfully")
        return (f"User '{username}' balance updated successfully '{new_balance}'")
    except mysql.connector.Error as err:
        print(f"Error: {err}")






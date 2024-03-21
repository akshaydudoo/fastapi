
import json
from fastapi import Header,FastAPI, Form, Request,HTTPException,Query
import requests
from mybalance import check_balance_re,check_mobile_balance
from recharge import initiate_transaction,get_user_info,update_user_balance
from db import create_connection,close_connection
from updatetrx import add_transaction,update_transaction

from mysql.connector import Error


userid_re = 12680
token_re = 'oxPSU4oRn2xSAx6Gs9hE'

mobile_number = "9923801801"  # payone
api_key = "jZMxyKv84VAHBdCYFPwrzVWb4CKhFeJfQid"     # payone


app = FastAPI()
# templates = Jinja2Templates(directory="templates")  # Assuming your HTML files are stored in a folder named 'templates'
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root(request: Request):
    client_host = request.client.host
    return client_host

@app.get("/balance_Admin_re")
async def check_balance_html():
    balance = {"Recherge exchenge":check_balance_re(userid_re, token_re),"PayOne" : check_mobile_balance(mobile_number, api_key)}
    return {"balance": balance}

@app.get('/operator_codes/{operator_type}')
async def get_operator_codes(operator_type: str):
    file_mapping = {
        'dth': 'dth.json',
        'postpaid': 'postpaid.json',
        'landline': 'landline.json',
        'electricity': 'electricity.json',
        'water': 'water.json',
        'gas': 'gas.json',
        'mobile': 'mobile.json'
    }
    if operator_type not in file_mapping:
        raise HTTPException(status_code=404, detail="Operator type not found")
    
    return load_json_file(file_mapping[operator_type])

def fetch_bill_info(service_code: str, consumer_number: str, customer_mobile_number: str, is_stv: bool, field1: str, field2: str, pin_code: str, latitude: str, longitude: str):
    url = f"https://www.payoneapi.com/RechargeAPI/RechargeAPI.aspx?MobileNo={mobile_number}&APIKey={api_key}&REQTYPE=BILLINFO&SERCODE={service_code}&CUSTNO={consumer_number}&REFMOBILENO={customer_mobile_number}&AMT=0&STV={'true' if is_stv else 'false'}&FIELD1={field1}&FIELD2={field2}&PCODE={pin_code}&LAT={latitude}&LONG={longitude}&RESPTYPE=JSON"
    response = requests.get(url)
    return response.json()

@app.get("/bill_info/")
async def get_bill_info(service_code: str, consumer_number: str, customer_mobile_number: str, is_stv: bool, field1: str, field2: str, pin_code: str, latitude: str, longitude: str):
    response = fetch_bill_info(service_code, consumer_number, customer_mobile_number, is_stv, field1, field2, pin_code, latitude, longitude)
    return response

@app.get("/recharge")
async def recharge(username: str, apitocken:str, operator_code:int, number: str, amount:int,transid: int):
    connection=create_connection()
    user_info = get_user_info(connection, username,apitocken)
    cursor = connection.cursor()
    # Example data for adding a transaction
    transaction_data = ('Pending', 'Pending', transid, operator_code, '', number, amount,"",0, 0, username, "Maharastra", "GST", "Roffer")
    add_transaction(connection, cursor, transaction_data)

    if  user_info:
        # Example: Check if the balance is sufficient
        if user_info['balance'] >= amount and user_info['account_status']=='active':
            recharge = initiate_transaction(userid_re, token_re, operator_code, number, amount, transid)
            if recharge['status'] == 'SUCCESS':
                new_balance = user_info['balance'] - amount
                # Update user balance
                update_user_balance(connection, username, new_balance)

                updated_margin=recharge['margin']-(recharge['margin']*0.1)
                status=recharge['status']
                message=recharge['message']
                optrid=recharge['optransid']
                refid=recharge['referenceid']
                mergin=recharge['margin']
                balance=recharge['balance']
                update_transaction(connection, cursor,status,message,balance,optrid,refid,mergin,transid,updated_margin)

                close_connection(connection)
                print(recharge)
                return {"success":recharge}
            else:
                
                updated_margin=recharge['margin']-(recharge['margin']*0.1)
                status=recharge['status']
                message=recharge['message']
                optrid=recharge['optransid']
                refid=recharge['referenceid']
                mergin=recharge['margin']
                balance=recharge['balance']
                update_transaction(connection, cursor,status,message,balance,optrid,refid,mergin,transid,updated_margin)
                close_connection(connection)
                print(recharge)
                return {"error" : recharge}
        else:
            return{"error":{"status": "FAIL","message": "Insufficient balance","transid":transid}}
    else:            
        return {"error":{"status": "FAIL","message": "User Account is in Active","transid":transid}}
    

@app.get('/ip')
def index(real_ip: str = Header(None, alias='Forwarded')):
    return real_ip

@app.post("/signin")
async def sign_in(username: str = Form(...), password: str = Form(...)):
    # Establish a connection to the MySQL database
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Query the database to check if the provided username and password match any user record
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        
        if user:
            # User authentication successful
            return {"message": "Sign-in successful"}
        else:
            # Invalid username or password
            raise HTTPException(status_code=401, detail="Invalid username or password")
    except Error as e:
        # Handle database error
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        # Close the database connection
        close_connection(connection)

@app.get("/user_transitions/")
async def get_user_transitions(user: str = Query(..., description="User name"), 
                               limit: int = Query(..., description="Number of records to retrieve")):
    # Connect to the database
    connection = create_connection()
    if not connection:
        return {"error": "Failed to connect to the database"}
    
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM transactions WHERE user_name = %s ORDER BY id DESC LIMIT %s"
    cursor.execute(query, (user, limit))
    transitions = cursor.fetchall()
    
    close_connection(connection)

    return transitions


@app.get("/utility-bill-payment/")
async def utility_bill_payment(
    username :str,
    apitocken : str,
    ref_no: str = Query(..., description="API Reference No (Unique)"),
    service_code: str = Query(..., description="Service Code (Please check Appendix)"),
    cust_no: str = Query(..., description="Customer No"),
    ref_mobile_no: str = Query(..., description="Reference Mobile No (Used for BBPS)"),
    amt: float = Query(..., description="Amount"),
    field1: str = Query("", description="Other input (FIELD1)"),
    field2: str = Query("", description="Other input (FIELD2)"),
    field3: str = Query("", description="Other input (FIELD3)"),
    field4: str = Query("", description="Other input (FIELD4)"),
    field5: str = Query("", description="Other input (FIELD5)"),
):
    url = "https://www.payoneapi.com/RechargeAPI/RechargeAPI.aspx"
    params = {
        "MobileNo": mobile_number,
        "APIKey": api_key,
        "REQTYPE": "BILLPAY",
        "REFNO": ref_no,
        "SERCODE": service_code,
        "CUSTNO": cust_no,
        "REFMOBILENO": ref_mobile_no,
        "AMT": amt,
        "STV": 0,
        "FIELD1": field1,
        "FIELD2": field2,
        "FIELD3": field3,
        "FIELD4": field4,
        "FIELD5": field5,
        "PCODE": 413109,
        "LAT": 23.1003804,
        "LONG": 72.5500481,
        "RESPTYPE": "JSON"
    }

    print(params)
    connection=create_connection()
    user_info = get_user_info(connection, username,apitocken)
    cursor = connection.cursor()
    # Example data for adding a transaction
    transaction_data = ('Pending', 'Pending', ref_no, service_code, '', cust_no, amt,"",0, 0, username, field1, field2, "BBPS")
    add_transaction(connection, cursor, transaction_data)

    if  user_info:
        # Example: Check if the balance is sufficient
        if user_info['balance'] >= amt and user_info['account_status']=='active':
            try:
           
                response = requests.get(url, params=params)
                response.raise_for_status()
                response=response.json()

                print (response)
                if response['STATUSCODE'] == '0':
                    updated_margin= 1
                    new_balance = float(user_info['balance']) - float(amt)
                    # Update user balance
                    update_user_balance(connection, username, new_balance)
                    status=response['STATUSMSG']
                    message=response['TRNID']
                    optrid=response['OPRID']
                    refid=response['REFNO']
                    mergin= 1
                    balance=response['BAL']
                    update_transaction(connection, cursor,status,message,new_balance,optrid,refid,mergin,ref_no,updated_margin)
                    close_connection(connection)
                    print(recharge)
                    return {"success":response}
                else:
                    updated_margin= 1
                    status=response['STATUSMSG']
                    message=response['TRNID']
                    optrid=response['OPRID']
                    refid=response['REFNO']
                    mergin= 1
                    balance=response['BAL']
                    update_transaction(connection, cursor,status,message,balance,optrid,refid,mergin,ref_no,updated_margin)
                    close_connection(connection)
                    print(recharge)
                    return {"error" : response}
            except requests.RequestException as e:
                raise HTTPException(status_code=500, detail=f"Error connecting to PayOneApi: {e}")
        else:
            return{"error":{"status": "FAIL","message": "Insufficient balance","transid":ref_no}}
    else:            
        return {"error":{"status": "FAIL","message": "User Account is in Active","transid":ref_no}}

    


# API endpoint to add balance
@app.get("/add_balance/")
async def add_balance(username: str,amount: int,payment_method: str,trx_id: str,status: str,updated_by: str):

    connection = create_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            # Insert balance into balances table
            balance_query = "INSERT INTO add_balance (username, amount, payment_method, trx_id, status, updated_by) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(balance_query, (username, amount, payment_method, trx_id, status, updated_by))
            # Update user_info table with new balance
            if status=="Success":
                update_query = """UPDATE users SET balance = balance + %s WHERE username = %s"""
                cursor.execute(update_query, (amount, username))
                connection.commit()
                print("Balance added successfully")
                return {"message": "Balance added successfully", "transaction_id": trx_id}
            else :
                error_message = {"message":"Payment Failed", "transaction id": trx_id}
                connection.commit()
                return  error_message
            
        except Error as e:
            print(f"Error: {e}")
            return {"error": "Failed to add balance"}
        finally:
            close_connection(connection)
    else:
        return {"error": "Failed to establish database connection"}

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

@app.get("/user_balance/")
async def get_user_balance(username:str,apitocken:str):
    connection=create_connection()
    user_info = get_user_info(connection, username,apitocken)
    return { "balance" : user_info['balance']}

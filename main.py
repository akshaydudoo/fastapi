from typing import Union
from fastapi import Header,FastAPI, Form, Request,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from mybalance import check_balance
from recharge import initiate_transaction,get_user_info,update_user_balance
from db import create_connection,close_connection
from updatetrx import add_transaction,update_transaction
from fastapi.staticfiles import StaticFiles
from mysql.connector import Error

import uuid


userid = 12680
token = 'oxPSU4oRn2xSAx6Gs9hE'

app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Assuming your HTML files are stored in a folder named 'templates'
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    client_host = request.client.host

    connection=create_connection()
    # Retrieve the last 50 records from the transactions table
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 10")
    transactions = cursor.fetchall()
    balance = check_balance(userid, token)
    return templates.TemplateResponse("index.html", {"request": request, "balance": balance['balance'],"transactions": transactions,"host":client_host})

@app.get("/balance")
async def check_balance_html(request: Request):
    client_host = request.client.host
    print(client_host)
    balance = check_balance(userid, token)
    return {"balance": balance}

@app.get("/recharge")
async def recharge(username: str, apitocken:str, operator_code:int, number: str, amount:int,transid: int):
    connection=create_connection()
    user_info = get_user_info(connection, username,apitocken)
    cursor = connection.cursor()
    # Example data for adding a transaction
    transaction_data = ('Pending', 'Pending', transid, operator_code, '', number, 
                                amount,"",0, 0, username, "Maharastra", "GST", "Roffer")     
            # Add transaction
    add_transaction(connection, cursor, transaction_data)

    if  user_info:
        # Example: Check if the balance is sufficient
        if user_info['balance'] >= amount and user_info['account_status']=='active':
            recharge = initiate_transaction(userid, token, operator_code, number, amount, transid)
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
            return{"error": "Insufficient balance","TrxID" : transid}
    else:            
        return {"error":"User account is inactive"}
    
@app.get("/report", response_class=HTMLResponse)
async def report(request: Request):
    connection=create_connection()

    # Retrieve the last 50 records from the transactions table
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 50")
    transactions = cursor.fetchall()

    return templates.TemplateResponse("report.html", {"request": request, "transactions": transactions})

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
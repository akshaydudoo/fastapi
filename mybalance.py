import requests

def check_balance_re(userid, token):
    url = f"https://status.rechargeexchange.com/API.asmx/BalanceNew?userid={userid}&token={token}"
    
    try:
        # Make GET request to the API endpoint
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            if data['status'] == 'SUCCESS':
                return data
            else:
                print(f"Failed to retrieve balance. Message: {data['message']}")
        else:
            print(f"Failed to retrieve balance. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def check_mobile_balance(mobile_number, api_key):
    url = f"https://www.payoneapi.com/RechargeAPI/RechargeAPI.aspx?MobileNo={mobile_number}&APIKey={api_key}&REQTYPE=BAL&RESPTYPE=JSON"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        # Handle errors
        return {"error": f"Failed to fetch balance. Status code: {response.status_code}"}

# Example usage:



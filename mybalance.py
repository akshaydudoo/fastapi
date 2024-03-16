import requests

def check_balance(userid, token):
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
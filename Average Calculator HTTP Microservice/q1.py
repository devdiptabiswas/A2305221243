import requests
from flask import Flask, jsonify, request
from collections import deque
import logging
import time

app = Flask(_name_)
logging.basicConfig(level=logging.INFO)

WINDOW_SIZE = 10
numbers_queue = deque(maxlen=WINDOW_SIZE)
TOKEN_EXPIRY_TIME = 600  # 10 minutes, adjust as needed
token = None
token_expiry = 0

def get_new_token():
    global token, token_expiry
    # Replace with actual token endpoint and credentials
    auth_url = "http://20.244.56.144/auth"
    credentials ={'companyName': 'Amity University', 'clientID': '850692d1-b5db-4b53-9d75-4f5353998eab', 'clientSecret': 'epxlshyODfjKFReq', 'ownerName': 'Devdipta Biswas', 'ownerEmail': 'devdiptabiswas@gmail.com', 'rollNo': 'A2305221243'}


    try:
        response = requests.post(auth_url, json=credentials)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['token']
            token_expiry = time.time() + TOKEN_EXPIRY_TIME
            logging.info("New token obtained")
        else:
            logging.error(f"Failed to obtain token: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error obtaining token: {e}")

def get_valid_token():
    if token is None or time.time() > token_expiry:
        get_new_token()
    return token

def fetch_numbers(number_type):
    url = f"http://20.244.56.144/numbers/{number_type}"
    headers = {"Authorization": f"Bearer {get_valid_token()}"}
    try:
        response = requests.get(url, headers=headers, timeout=0.5)
        if response.status_code == 200:
            return response.json()['numbers']
        else:
            logging.error(f"Error fetching numbers: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Request exception: {e}")
        return []

@app.route('/numbers/<number_type>')
def get_numbers(number_type):
    if number_type not in ['primes', 'fibo', 'odd', 'rand']:
        return jsonify({"error": "Invalid number type"}), 400

    new_numbers = fetch_numbers(number_type)
    logging.info(f"Fetched numbers: {new_numbers}")
    
    window_prev_state = list(numbers_queue)
    
    for num in new_numbers:
        if num not in numbers_queue:
            if len(numbers_queue) == WINDOW_SIZE:
                numbers_queue.popleft()
            numbers_queue.append(num)

    window_curr_state = list(numbers_queue)
    
    avg = sum(window_curr_state) / len(window_curr_state) if window_curr_state else 0

    response = {
        "windowPrevState": window_prev_state,
        "windowCurrState": window_curr_state,
        "numbers": new_numbers,
        "avg": round(avg, 2)
    }
    logging.info(f"Response: {response}")
    return jsonify(response)

@app.route('/')
def home():
    return "Average Calculator Microservice is running!"

if _name_ == '_main_':
    app.run(debug=True, host='0.0.0.0', port=1243)
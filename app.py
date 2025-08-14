from flask import Flask, request, jsonify, render_template
import requests
import datetime
import json
import os
app = Flask(__name__)

def get_held_inscriptions(address, api_key, from_date=None, to_date=None):
    """
    Fetches held inscription IDs for a given Bitcoin address from Ordiscan API,
    filtered by creation date range if specified.
    
    :param address: Bitcoin address
    :param api_key: Ordiscan API key
    :param from_date: datetime.date, optional start date (inclusive)
    :param to_date: datetime.date, optional end date (inclusive)
    :return: list of inscription IDs or dict with error
    """
    inscriptions = []
    page = 1
    base_url = "https://api.ordiscan.com/v1/address/{}/inscriptions".format(address)
    
    while True:
        url = "{}?page={}".format(base_url, page)
        headers = {
            "Authorization": "Bearer {}".format(api_key),
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return {"error": f"API request failed: {response.status_code} - {response.text}"}
        
        data = response.json().get('data', [])
        if not data:
            break
        
        for insc in data:
            ts_str = insc.get('timestamp', '').rstrip('Z')
            if not ts_str:
                continue
            ts = datetime.datetime.fromisoformat(ts_str)
            insc_date = ts.date()
            
            if from_date and insc_date < from_date:
                continue
            if to_date and insc_date > to_date:
                continue
            
            inscriptions.append(insc['inscription_id'])
        
        page += 1
    
    return inscriptions

def get_transferred_inscriptions(address, api_key, from_date=None, to_date=None):
    """
    Fetches transferred (sent) inscription IDs for a given Bitcoin address from Ordiscan API,
    filtered by transfer date range if specified.
    
    :param address: Bitcoin address
    :param api_key: Ordiscan API key
    :param from_date: datetime.date, optional start date (inclusive)
    :param to_date: datetime.date, optional end date (inclusive)
    :return: list of inscription IDs or dict with error
    """
    transferred = []
    page = 1
    base_url = "https://api.ordiscan.com/v1/address/{}/activity?type=transfer".format(address)
    
    while True:
        url = "{}&page={}".format(base_url, page)
        headers = {
            "Authorization": "Bearer {}".format(api_key),
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return {"error": f"API request failed: {response.status_code} - {response.text}"}
        
        data = response.json().get('data', [])
        if not data:
            break
        
        for event in data:
            ts_str = event.get('timestamp', '').rstrip('Z')
            if not ts_str:
                continue
            ts = datetime.datetime.fromisoformat(ts_str)
            event_date = ts.date()
            
            if from_date and event_date < from_date:
                continue
            if to_date and event_date > to_date:
                continue
            
            if event['type'] == 'SEND':
                transferred.append(event['inscription_id'])
        
        page += 1
    
    return transferred

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_inscriptions', methods=['POST'])
def fetch_inscriptions():
    api_key = "373a1e27-947f-4bd8-80c6-639a03014a16"  # Your provided placeholder Ordiscan API key
    data = request.get_json()
    addresses = data.get('addresses', '').split('\n')
    addresses = [addr.strip() for addr in addresses if addr.strip()]
    from_date_str = data.get('from_date')
    to_date_str = data.get('to_date')
    
    from_date = None
    to_date = None
    try:
        if from_date_str:
            from_date = datetime.date.fromisoformat(from_date_str)
        if to_date_str:
            to_date = datetime.date.fromisoformat(to_date_str)
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
    
    results = {}
    for address in addresses:
        try:
            held = get_held_inscriptions(address, api_key, from_date, to_date)
            transferred = get_transferred_inscriptions(address, api_key, from_date, to_date)
            
            if isinstance(held, dict) and "error" in held:
                results[address] = {"held": {"error": held["error"]}, "transferred": transferred}
            elif isinstance(transferred, dict) and "error" in transferred:
                results[address] = {"held": held, "transferred": {"error": transferred["error"]}}
            else:
                results[address] = {"held": held, "transferred": transferred}
        except Exception as e:
            results[address] = {"error": str(e)}
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
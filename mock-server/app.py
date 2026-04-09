import json
import os
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from dotenv import load_dotenv

# --- Configuration Management ---
load_dotenv()
DATA_PATH = os.getenv('CUSTOMERS_DATA_PATH', os.path.join(os.path.dirname(__file__), 'data', 'customers.json'))
PORT = int(os.getenv('MOCK_SERVER_PORT', 5000))
MAX_LIMIT = int(os.getenv('MAX_LIMIT', 50))

app = Flask(__name__)
CORS(app)

with open(DATA_PATH, 'r') as f:
    customers = json.load(f)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# --- Filtering & Sorting ---
def filter_and_sort(customers, last_name=None, sort_by=None, sort_order='asc'):
    result = customers
    if last_name:
        result = [c for c in result if c['last_name'].lower() == last_name.lower()]
    if sort_by:
        reverse = sort_order == 'desc'
        result = sorted(result, key=lambda x: x.get(sort_by, ''), reverse=reverse)
    return result

@app.route('/api/customers', methods=['GET'])
def get_customers():
    # --- Pagination Validation ---
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        if page < 1 or limit < 1 or limit > MAX_LIMIT:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid 'page' or 'limit' parameter. 'page' >= 1, 1 <= 'limit' <= %d." % MAX_LIMIT}), 400

    # --- Filtering & Sorting ---
    last_name = request.args.get('last_name')
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')
    filtered = filter_and_sort(customers, last_name, sort_by, sort_order)

    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]
    return jsonify({
        "data": paginated,
        "total": len(filtered),
        "page": page,
        "limit": limit
    })

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = next((c for c in customers if c['customer_id'] == customer_id), None)
    if not customer:
        abort(404, description="Customer not found")
    return jsonify(customer)

# --- Testing (pytest) ---
def create_app():
    return app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)

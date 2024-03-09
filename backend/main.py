from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/endpoint', methods=['GET'])
def handle_request():
    # Handle the request and return a response
    return jsonify({'annotations': 'value'})

if __name__ == '__main__':
    app.run(port=5000)
# debug_routes.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/routes')
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        output.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'route': str(rule)
        })
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
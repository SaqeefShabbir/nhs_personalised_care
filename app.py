import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from flask import Flask, jsonify, request
    logger.info("Flask imported successfully")
except ImportError as e:
    logger.error(f"Failed to import Flask: {e}")
    raise

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "NHS Personalised Care API",
        "status": "running",
        "version": "1.0.0",
        "environment": "vercel"
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "deployment": "vercel",
        "python_version": sys.version
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "status": 404}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "status": 500}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
else:
    logger.info("App loaded successfully for Vercel")
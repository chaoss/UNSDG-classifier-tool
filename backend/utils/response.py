from flask import jsonify

def success(data, status=200):
    return jsonify({
        "success": True,
        "data": data
    }), status


def error(message, error_type="API_ERROR", status=500):
    return jsonify({
        "success": False,
        "error": message,
        "type": error_type
    }), status
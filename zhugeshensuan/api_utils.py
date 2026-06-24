from flask import jsonify


def success(data=None, status=200, **legacy_fields):
    payload = {"success": True, "data": data, "error": None}
    payload.update(legacy_fields)
    return jsonify(payload), status


def failure(code, message, status=400, details=None, **legacy_fields):
    error = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    payload = {"success": False, "data": None, "error": error, "message": message}
    payload.update(legacy_fields)
    return jsonify(payload), status

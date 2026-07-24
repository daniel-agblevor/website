import datetime
from functools import wraps
import jwt
import requests
from flask import request, jsonify, current_app

def generate_admin_token(user_id: str, email: str) -> str:
    """Generate a JWT token for authorized admin sessions"""
    payload = {
        "sub": user_id,
        "email": email,
        "role": "admin",
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def verify_supabase_user(email: str, password: str) -> dict:
    """
    Authenticates user credentials against Supabase Auth endpoint.
    If Supabase URL or Anon Key is missing, falls back to environment/dev credentials check.
    """
    supabase_url = current_app.config.get("SUPABASE_URL")
    supabase_anon_key = current_app.config.get("SUPABASE_ANON_KEY")

    if supabase_url and supabase_anon_key:
        auth_url = f"{supabase_url.rstrip('/')}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": supabase_anon_key,
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "password": password
        }
        try:
            response = requests.post(auth_url, json=data, headers=headers, timeout=10)
            if response.status_code == 200:
                res_data = response.json()
                return {
                    "success": True,
                    "user_id": res_data.get("user", {}).get("id", "supabase_admin"),
                    "email": email,
                    "access_token": res_data.get("access_token")
                }
            else:
                return {"success": False, "error": "Invalid email or password"}
        except Exception as e:
            current_app.logger.error(f"Supabase auth request failed: {e}")
            return {"success": False, "error": f"Supabase auth error: {str(e)}"}
    
    # Dev / Local fallback authentication when Supabase is not yet configured
    # In development mode, allow admin login with admin / admin123 or defined env vars
    dev_email = current_app.config.get("ADMIN_EMAIL", "admin@example.com")
    dev_pass = current_app.config.get("ADMIN_PASSWORD", "admin123")
    
    if email.lower() == dev_email.lower() and password == dev_pass:
        return {
            "success": True,
            "user_id": "dev_admin_1",
            "email": email
        }
    
    return {"success": False, "error": "Invalid login credentials"}


def admin_required(f):
    """Decorator to require a valid admin JWT token on protected API routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header:
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 401

        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"]
            )
            request.admin_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated

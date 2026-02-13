import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

routes = Blueprint("routes", __name__)

# temporary storage (later DB)
users = {
    "university": [],
    "verifier": []
}

# ---------- SIGNUP ----------
@routes.route("/signup", methods=["POST"])
def signup():
    data = request.json
    role = data.get("role")
    email = data.get("email")
    password = data.get("password")

    if role not in users:
        return jsonify({"message": "Invalid role"}), 400

    for u in users[role]:
        if u["email"] == email:
            return jsonify({"message": "User already exists"}), 409

    users[role].append({
        "email": email,
        "password": password
    })

    return jsonify({"message": f"{role} signup successful"})


# ---------- SIGNIN ----------
@routes.route("/signin", methods=["POST"])
def signin():
    data = request.json
    role = data.get("role")
    email = data.get("email")
    password = data.get("password")

    for u in users.get(role, []):
        if u["email"] == email and u["password"] == password:
            return jsonify({"message": "Login successful", "role": role})

    return jsonify({"message": "Invalid credentials"}), 401


# ---------- FILE UPLOAD (WRITE YOUR CODE HERE) ----------
@routes.route("/upload", methods=["POST"])
def upload_file():
    role = request.form.get("role")

    if role not in ["university", "verifier"]:
        return jsonify({"message": "Invalid role"}), 400

    if "file" not in request.files:
        return jsonify({"message": "No file provided"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)

    path = os.path.join("uploads", role)
    os.makedirs(path, exist_ok=True)

    file.save(os.path.join(path, filename))

    return jsonify({
        "message": "File uploaded successfully",
        "file": filename,
        "role": role
    })

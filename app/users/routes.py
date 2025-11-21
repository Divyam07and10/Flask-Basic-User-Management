from flask import Blueprint, request, jsonify, render_template, abort, make_response, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies
from .services import *
from app.models.user import User

users_bp = Blueprint("users", __name__, url_prefix="/users")


# --------------------------
# LIST USERS (TEMPLATE)
# --------------------------
@users_bp.get("/list")
@jwt_required()
def list_users_template():
    # Filters & sorting from query params
    status = request.args.get("status", "all")
    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")

    # Normalise values
    if status not in ("all", "active", "inactive"):
        status = "all"
    if sort_by not in ("id", "name", "created", "last_login"):
        sort_by = "id"
    if order not in ("asc", "desc"):
        order = "asc"

    users = get_all_users(status=None if status == "all" else status, sort_by=sort_by, order=order)
    current = get_jwt_identity()
    return render_template(
        "users/list.html",
        users=users,
        current_user=current,
        status=status,
        sort_by=sort_by,
        order=order,
    )


# --------------------------
# EDIT USER (HTML FORM)
# --------------------------
@users_bp.get("/<int:id>/edit")
@jwt_required()
def edit_user_page(id):
    current = get_jwt_identity()
    if current != id:
        abort(403)

    user = get_user_by_id(id)
    if not user:
        abort(404)

    return render_template("users/edit.html", user=user)


# --------------------------
# EDIT CURRENT USER GATE (PASSWORD FIRST)
# --------------------------
@users_bp.route("/me/edit", methods=["GET", "POST"])
@jwt_required()
def edit_me_redirect():
    current = get_jwt_identity()
    user = get_user_by_id(current)
    if not user:
        abort(404)

    if request.method == "POST":
        pwd = request.form.get("password") or ""
        if not user.check_password(pwd):
            flash("Incorrect password", "danger")
            return redirect(url_for("users.edit_me_redirect"))
        return redirect(url_for("users.edit_user_page", id=current))

    return render_template("users/edit_auth.html")


# --------------------------
# CREATE USER
# --------------------------
@users_bp.post("/")
@jwt_required()
def create_user_route():
    data = request.json
    dob = data.get("dob")
    user = create_user(data["name"], data["email"], data["password"], dob)
    return jsonify({"message": "User created", "id": user.id}), 201


# --------------------------
# UPDATE USER (PATCH)
# --------------------------
@users_bp.patch("/<int:id>")
@jwt_required()
def update_user_route(id):
    current_user = get_jwt_identity()
    if current_user != id:
        return jsonify({"message": "You can update only your own data"}), 403

    user = get_user_by_id(id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.is_active:
        return jsonify({"message": "Account inactive"}), 403

    data = request.json
    updated = update_user(user, data)

    if updated is False:
        return jsonify({"message": "Old password incorrect"}), 400

    return jsonify({"message": "Updated"})


# --------------------------
# SOFT DELETE USER
# --------------------------
@users_bp.delete("/<int:id>")
@jwt_required()
def delete_user_route(id):
    current_user = get_jwt_identity()
    if current_user != id:
        return jsonify({"message": "You can delete only your own account"}), 403

    user = get_user_by_id(id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    soft_delete_user(user)
    resp = make_response(jsonify({"message": "Account deactivated. You have been logged out."}))
    unset_jwt_cookies(resp)
    return resp

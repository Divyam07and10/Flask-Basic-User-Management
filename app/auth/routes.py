from flask import Blueprint, request, jsonify, render_template, make_response, redirect, url_for, flash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies
)
from app.extensions import db
from app.models.user import User
from datetime import datetime

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# --------------------------
# LOGIN (HTML FORM)
# --------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""

    user = User.query.filter_by(email=email).first()

    # Invalid credentials
    if not user or not user.check_password(password):
        flash("Invalid email or password", "danger")
        return redirect(url_for("auth.login"))

    # Deactivated account -> send to reactivation flow
    if not user.is_active:
        return redirect(url_for("auth.reactivate_account", email=user.email))

    # Stamp last_login_datetime on every successful login
    user.last_login_datetime = datetime.utcnow()
    db.session.commit()

    # Issue JWT access token in a cookie and redirect to dashboard
    token = create_access_token(identity=user.id)
    response = redirect(url_for("auth.dashboard_page"))
    set_access_cookies(response, token)
    return response


# --------------------------
# REGISTER (HTML FORM)
# --------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    password = request.form.get("password") or ""
    dob_raw = (request.form.get("dob") or "").strip()

    if not name or not email or not password:
        flash("All fields are required", "danger")
        return redirect(url_for("auth.register"))

    if User.query.filter_by(email=email).first():
        flash("Email already exists", "danger")
        return redirect(url_for("auth.register"))

    # Optional DOB parsing (YYYY-MM-DD from <input type="date">)
    dob_value = None
    if dob_raw:
        try:
            dob_value = datetime.strptime(dob_raw, "%Y-%m-%d").date()
        except Exception:
            dob_value = None

    user = User(name=name, email=email, dob=dob_value)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    flash("Account created. Please log in.", "success")
    return redirect(url_for("auth.login"))


# --------------------------
# DASHBOARD (JWT COOKIE REQUIRED)
# --------------------------
@auth_bp.get("/dashboard")
@jwt_required()
def dashboard_page():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_active:
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        user=user,
        last_login=user.last_login_datetime,
        created_at=user.created_at
    )


# --------------------------
# LOGOUT (CLEAR COOKIE + UPDATE LAST LOGIN)
# --------------------------
@auth_bp.route("/logout", methods=["GET", "POST"])
@jwt_required(optional=True)
def logout():
    """Clear auth cookie. If a user is logged in, stamp last_login_datetime to now."""
    current_id = get_jwt_identity()
    if current_id is not None:
        user = User.query.get(current_id)
        if user is not None:
            user.last_login_datetime = datetime.utcnow()
            db.session.commit()

    response = make_response(redirect(url_for("auth.login")))
    unset_jwt_cookies(response)
    flash("Logged out successfully!", "success")
    return response

@auth_bp.get("/check")
def check_login():
    from flask import request
    token = request.cookies.get('access_token')
    return jsonify({"logged_in": bool(token)})


# --------------------------
# ACCOUNT REACTIVATION
# --------------------------
@auth_bp.route("/reactivate", methods=["GET", "POST"])
def reactivate_account():
    """Let a deactivated user reactivate their account by confirming password."""
    email = (request.args.get("email") or request.form.get("email") or "").strip()

    # ---------------- GET: decide which step to show ----------------
    if request.method == "GET":
        # Step 1: no email yet -> ask for email
        if not email:
            return render_template("reactivate.html", step="email", email="")

        # Step 2: have email -> validate and show password form only for inactive users
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Account not found", "danger")
            return redirect(url_for("auth.reactivate_account"))

        if user.is_active:
            # Already active – do not even show the reactivation form
            flash("This account is already active. Please log in directly.", "info")
            return redirect(url_for("auth.login"))

        return render_template("reactivate.html", step="password", email=email)

    # ---------------- POST ----------------
    password = request.form.get("password") or ""
    user = User.query.filter_by(email=email).first()

    # If this POST only had an email field (no password), treat it as Step 1 submit
    if not password:
        email_only = (request.form.get("email") or "").strip()
        if not email_only:
            flash("Please enter your email", "danger")
            return redirect(url_for("auth.reactivate_account"))

        user = User.query.filter_by(email=email_only).first()
        if not user:
            flash("Account not found", "danger")
            return redirect(url_for("auth.reactivate_account"))

        if user.is_active:
            flash("This account is already active. Please log in directly.", "info")
            return redirect(url_for("auth.login"))

        # Email is valid and account is inactive -> go to password step
        return redirect(url_for("auth.reactivate_account", email=email_only))

    # From here on we require a real user and password
    if not user:
        flash("Account not found", "danger")
        return redirect(url_for("auth.reactivate_account"))

    if user.is_active:
        # Already active – send to login with a helpful toast
        flash("This account is already active. Please log in directly.", "info")
        return redirect(url_for("auth.login"))

    if not user.check_password(password):
        flash("Incorrect password", "danger")
        return redirect(url_for("auth.reactivate_account", email=email))

    # Reactivate account
    user.is_active = True
    user.updated_at = datetime.utcnow()
    db.session.commit()

    message = "Your account has been reactivated successfully. Please log in to continue."
    flash(message, "success")
    return render_template("reactivate.html", email=email, success=message)

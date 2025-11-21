from flask import Flask, render_template, redirect, url_for
from .config import Config
from .extensions import db, migrate, bcrypt, jwt
from flask_cors import CORS
from .auth.routes import auth_bp
from .users.routes import users_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return redirect(url_for('auth.login'))

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for('auth.login'))

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return redirect(url_for('auth.login'))

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    @app.get("/")
    def home():
        return render_template("home.html")

    return app

from datetime import datetime
from app.extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    dob = db.Column(db.Date, nullable=True)

    password_hash = db.Column(db.String(255), nullable=False)

    last_login_datetime = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # updated_at is only changed explicitly in business logic (e.g., profile edits),
    # not on every DB update like login/logout.
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, raw_password):
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password_hash, raw_password)

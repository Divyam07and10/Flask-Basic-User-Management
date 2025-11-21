from app.models.user import User
from app.extensions import db
from datetime import datetime

def get_all_users(status=None, sort_by="id", order="asc"):
    """Return users with optional status filter and sorting.

    status: None/'all' | 'active' | 'inactive'
    sort_by: 'id' | 'name' | 'created' | 'last_login'
    order: 'asc' | 'desc'
    """

    query = User.query

    # Status filter
    if status == "active":
        query = query.filter_by(is_active=True)
    elif status == "inactive":
        query = query.filter_by(is_active=False)

    # Sorting
    sort_map = {
        "id": User.id,
        "name": User.name,
        "created": User.created_at,
        "last_login": User.last_login_datetime,
    }
    sort_col = sort_map.get(sort_by, User.id)

    if order == "desc":
        sort_col = sort_col.desc()
    else:
        sort_col = sort_col.asc()

    return query.order_by(sort_col).all()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def create_user(name, email, password, dob=None):
    user = User(name=name, email=email, dob=dob)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def update_user(user, data):
    """PATCH update — only update fields provided"""

    if "name" in data:
        user.name = data["name"]

    if "email" in data:
        user.email = data["email"]

    if "dob" in data:
        try:
            user.dob = datetime.strptime(data["dob"], "%Y-%m-%d").date()
        except:
            pass

    # password update requires old_password + new_password
    if "old_password" in data and "new_password" in data:
        if user.check_password(data["old_password"]):
            user.set_password(data["new_password"])
        else:
            return False  # old password incorrect

    if "is_active" in data:
        user.is_active = data["is_active"]

    # This function represents a real profile/account update, so bump updated_at
    user.updated_at = datetime.utcnow()
    db.session.commit()
    return user

def soft_delete_user(user):
    """Deactivate instead of delete"""
    user.is_active = False
    # Treat deactivation as "last time this account was in use"
    now = datetime.utcnow()
    user.last_login_datetime = now
    user.updated_at = now
    db.session.commit()
    return user

from app.db.models import db, User
from sqlalchemy.exc import IntegrityError
from uuid import UUID

class UserCrud:

    def create_user(self, data: dict):
        try:
            user = User(
                username=data.get("username"),
                email=data.get("email"),
                password_hash=data.get("password_hash"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                role=data.get("role"),
                is_active=data.get("is_active", True),
                is_verified=data.get("is_verified", False)
            )

            db.session.add(user)
            db.session.commit()
            return user

        except IntegrityError:
            db.session.rollback()
            return None

    def get_user_by_id(self, user_id: UUID):
        return User.query.get(user_id)


    def get_user_by_username(self, username: str):
        return User.query.filter_by(username=username).first()


    def get_user_by_email(self, email: str):
        return User.query.filter_by(email=email).first()


    def get_all_users(self):
        return User.query.all()

    def update_user(self, user_id: UUID, data: dict):
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        try:
            for key, value in data.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)

            db.session.commit()
            return user

        except IntegrityError:
            db.session.rollback()
            return None


    def delete_user(self, user_id: UUID):
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        db.session.delete(user)
        db.session.commit()
        return True

    def resetDb(self):
        try:
            # Reiniciamos la base de datos
            db.session.query(User).delete()
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise e
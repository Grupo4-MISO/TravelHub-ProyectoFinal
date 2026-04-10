from app.db.models import Manager, db
from sqlalchemy.exc import IntegrityError
from uuid import UUID

class ManagerCrud:

    def create_manager(self, data: dict):
        try:
            raw_hospedaje_id = data.get("hospedajeId")
            manager = Manager(
                hospedajeId=UUID(str(raw_hospedaje_id)) if raw_hospedaje_id else None,
                userId=UUID(str(data.get("userId"))),
                userName=data.get("userName"),
                email=data.get("email"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name")
            )

            db.session.add(manager)
            db.session.commit()
            return manager

        except IntegrityError:
            db.session.rollback()
            return None

        except Exception:
            db.session.rollback()
            return None

    def get_manager_by_id(self, manager_id: UUID):
        return Manager.query.get(manager_id)

    def get_all_managers_by_hospedaje_id(self, hospedaje_id: UUID):
        return Manager.query.filter(Manager.hospedajeId == hospedaje_id).all()

    def update_manager(self, manager_id: UUID, data: dict):
        manager = self.get_manager_by_id(manager_id)
        if not manager:
            return None

        try:
            for key, value in data.items():
                if hasattr(manager, key) and value is not None:
                    setattr(manager, key, value)

            db.session.commit()
            return manager

        except IntegrityError:
            db.session.rollback()
            return None

    def delete_manager(self, manager_id: UUID):
        manager = self.get_manager_by_id(manager_id)
        if not manager:
            return False

        db.session.delete(manager)
        db.session.commit()
        return True


manager_crud = ManagerCrud()

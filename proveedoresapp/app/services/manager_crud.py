from app.db.models import Manager, Provider, ProviderAddress, ProviderStatus, db
from sqlalchemy.exc import IntegrityError
from uuid import UUID

class ManagerCrud:

    def create_manager(self, data: dict):
        try:
            raw_status = str(data.get("status", "Pending")).strip().lower()
            status_map = {
                "pending": ProviderStatus.Pending,
                "active": ProviderStatus.Active,
                "suspended": ProviderStatus.Suspended,
                "blocked": ProviderStatus.Blocked,
            }

            provider = Provider(
                Name=data.get("name"),
                DocumentNumber=data.get("DocumentNumber"),
                ProviderStatus=status_map.get(raw_status, ProviderStatus.Pending),
            )

            db.session.add(provider)
            db.session.flush()

            manager = Manager(
                provider_id=provider.id,
                userId=UUID(str(data.get("userId"))),
                email=data.get("email"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                phone=data.get("phone"),
            )

            db.session.add(manager)
            db.session.flush()

            address_data = data.get("address") or {}
            if address_data and any(address_data.values()):
                provider_address = ProviderAddress(
                    provider_id=provider.id,
                    line1=address_data.get("line1"),
                    line2=address_data.get("line2"),
                    city=address_data.get("city"),
                    state=address_data.get("state"),
                    country=address_data.get("country"),
                    countryCode=address_data.get("countryCode"),
                    postal_code=address_data.get("postal_code"),
                )
                db.session.add(provider_address)

            db.session.commit()
            return provider, manager

        except IntegrityError:
            db.session.rollback()
            return None

        except Exception:
            db.session.rollback()
            return None

    def get_manager_by_id(self, manager_id: UUID):
        return Manager.query.get(manager_id)

    def get_manager_by_userid(self, userid: UUID):
        return Manager.query.filter(Manager.userId == userid).first()
    
    def get_all_managers_by_provider_id(self, provider_id: UUID):
        return Manager.query.filter(Manager.provider_id == provider_id).all()

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
    
    def create_provider_address(self, provider_id: UUID, address: dict):
        provider = Provider.query.get(provider_id)
        if not provider:
            return None
        try:
            provider.address = address
            db.session.commit()
            return provider

        except IntegrityError:
            db.session.rollback()
            return None

manager_crud = ManagerCrud()

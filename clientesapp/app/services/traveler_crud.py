from app.db.models import Traveler, TravelerAddress, TravelerStatus, db
from sqlalchemy.exc import IntegrityError
from uuid import UUID

class TravelerCrud:

    def create_traveler(self, data: dict):
        try:
            raw_status = str(data.get("travelerStatus") or "Pending").strip().lower()
            status_map = {
                "pending": TravelerStatus.Pending,
                "active": TravelerStatus.Active,
                "suspended": TravelerStatus.Suspended,
                "blocked": TravelerStatus.Blocked,
            }

            traveler = Traveler(
                userId=UUID(str(data.get("userId"))),
                documentNumber=data.get("documentNumber"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                phone=data.get("phone"),
                gender=data.get("gender"),
                photo=data.get("photo"),
                email=data.get("email"),
                travelerStatus=status_map.get(raw_status, TravelerStatus.Pending),
            )

            db.session.add(traveler)
            db.session.flush()

            address_data = data.get("address") or {}
            if address_data and any(address_data.values()):
                traveler_address = TravelerAddress(
                    traveler_id=traveler.id,
                    line1=address_data.get("line1"),
                    line2=address_data.get("line2"),
                    city=address_data.get("city"),
                    state=address_data.get("state"),
                    country=address_data.get("country"),
                    countryCode=address_data.get("countryCode"),
                    postal_code=address_data.get("postal_code"),
                )
                db.session.add(traveler_address)

            db.session.commit()
            return traveler

        except IntegrityError:
            db.session.rollback()
            return None

        except Exception:
            db.session.rollback()
            return None

    def get_traveler_by_id(self, traveler_id: UUID):
        return Traveler.query.get(traveler_id)

    def get_traveler_by_userid(self, userid: UUID):
        traveler = Traveler.query.filter(Traveler.userId == userid).first()
        if not traveler:
            return None
        addresses = TravelerAddress.query.filter(TravelerAddress.traveler_id == traveler.id).all()
        return traveler, addresses

    def update_traveler(self, traveler_id: UUID, data: dict):
        traveler = self.get_traveler_by_id(traveler_id)
        if not traveler:
            return None

        try:
            for key, value in data.items():
                if hasattr(traveler, key) and value is not None:
                    setattr(traveler, key, value)

            db.session.commit()
            return traveler

        except IntegrityError:
            db.session.rollback()
            return None

    def delete_traveler(self, traveler_id: UUID):
        traveler = self.get_traveler_by_id(traveler_id)
        if not traveler:
            return False

        db.session.delete(traveler)
        db.session.commit()
        return True

    def create_traveler_address(self, traveler_id: UUID, address: dict):
        traveler = Traveler.query.get(traveler_id)
        if not traveler:
            return None
        try:
            traveler.address = address
            db.session.commit()
            return traveler

        except IntegrityError:
            db.session.rollback()
            return None

traveler_crud = TravelerCrud()

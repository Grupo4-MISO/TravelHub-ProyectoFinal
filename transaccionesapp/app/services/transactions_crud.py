from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.db.models import Payment, PaymentProvider, PaymentTransaction, db


class PaymentProviderCrud:
    def create_payment_provider(self, data: dict):
        try:
            payment_provider = PaymentProvider(
                name=data.get("name"),
                config=data.get("config"),
                is_active=data.get("is_active", True),
                logo=data.get("logo")
            )

            db.session.add(payment_provider)
            db.session.commit()
            return payment_provider

        except IntegrityError:
            db.session.rollback()
            return None

    def get_payment_provider_by_id(self, provider_id: UUID):
        return PaymentProvider.query.get(provider_id)

    def get_all_payment_providers(self):
        return PaymentProvider.query.all()

    def get_active_payment_providers(self):
        return PaymentProvider.query.filter_by(is_active=True).all()

    def update_payment_provider(self, provider_id: UUID, data: dict):
        payment_provider = self.get_payment_provider_by_id(provider_id)
        if not payment_provider:
            return None

        try:
            for key, value in data.items():
                if hasattr(payment_provider, key) and value is not None:
                    setattr(payment_provider, key, value)

            db.session.commit()
            return payment_provider

        except IntegrityError:
            db.session.rollback()
            return None

    def delete_payment_provider(self, provider_id: UUID):
        payment_provider = self.get_payment_provider_by_id(provider_id)
        if not payment_provider:
            return False

        db.session.delete(payment_provider)
        db.session.commit()
        return True


class PaymentCrud:
    def create_payment(self, data: dict):
        try:
            payment = Payment(
                reserva_id=UUID(str(data.get("reserva_id"))),
                provider_id=UUID(str(data.get("provider_id"))) if data.get("provider_id") else None,
                amount=data.get("amount"),
                currency=data.get("currency"),
                status=data.get("status"),
                provider_payment_id=data.get("provider_payment_id"),
                description=data.get("description"),
                payment_metadata=data.get("metadata")
            )

            db.session.add(payment)
            db.session.commit()
            return payment

        except (IntegrityError, ValueError, TypeError):
            db.session.rollback()
            return None

    def get_payment_by_id(self, payment_id: UUID):
        return Payment.query.get(payment_id)

    def get_all_payments(self):
        return Payment.query.all()

    def get_all_payments_by_reserva_id(self, reserva_id: UUID):
        return Payment.query.filter(Payment.reserva_id == reserva_id).all()

    def get_all_payments_by_provider_id(self, provider_id: UUID):
        return Payment.query.filter(Payment.provider_id == provider_id).all()

    def update_payment(self, payment_id: UUID, data: dict):
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            return None

        try:
            for key, value in data.items():
                if key == "metadata":
                    key = "payment_metadata"

                if not hasattr(payment, key) or value is None:
                    continue

                if key in {"reserva_id", "provider_id"}:
                    value = UUID(str(value)) if value else None

                setattr(payment, key, value)

            db.session.commit()
            return payment

        except (IntegrityError, ValueError, TypeError):
            db.session.rollback()
            return None

    def delete_payment(self, payment_id: UUID):
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            return False

        db.session.delete(payment)
        db.session.commit()
        return True


class PaymentTransactionCrud:
    def create_payment_transaction(self, data: dict):
        try:
            payment_transaction = PaymentTransaction(
                payment_id=UUID(str(data.get("payment_id"))),
                status=data.get("status"),
                provider_transaction_id=data.get("provider_transaction_id"),
                url=data.get("url"),
                response=data.get("response")
            )

            db.session.add(payment_transaction)
            db.session.commit()
            return payment_transaction

        except (IntegrityError, ValueError, TypeError):
            db.session.rollback()
            return None

    def get_payment_transaction_by_id(self, transaction_id: UUID):
        return PaymentTransaction.query.get(transaction_id)

    def get_all_payment_transactions(self):
        return PaymentTransaction.query.all()

    def get_all_transactions_by_payment_id(self, payment_id: UUID):
        return PaymentTransaction.query.filter(PaymentTransaction.payment_id == payment_id).all()

    def update_payment_transaction(self, transaction_id: UUID, data: dict):
        payment_transaction = self.get_payment_transaction_by_id(transaction_id)
        if not payment_transaction:
            return None

        try:
            for key, value in data.items():
                if not hasattr(payment_transaction, key) or value is None:
                    continue

                if key == "payment_id":
                    value = UUID(str(value))

                setattr(payment_transaction, key, value)

            db.session.commit()
            return payment_transaction

        except (IntegrityError, ValueError, TypeError):
            db.session.rollback()
            return None

    def delete_payment_transaction(self, transaction_id: UUID):
        payment_transaction = self.get_payment_transaction_by_id(transaction_id)
        if not payment_transaction:
            return False

        db.session.delete(payment_transaction)
        db.session.commit()
        return True


payment_provider_crud = PaymentProviderCrud()
payment_crud = PaymentCrud()
payment_transaction_crud = PaymentTransactionCrud()
from app.db.models import Payment, PaymentProvider, PaymentTransaction, db
import uuid
import random
import calendar
from datetime import date

# ---------------------------------------------------------------------------
# Fallback: Proveedores locales 
# ---------------------------------------------------------------------------
PAYMENT_PROVIDERS_FALLBACK = [
    {"id": uuid.UUID("9a4a97e8-7f0e-46fb-a451-d7de8ef19ba5"), "name": "Stripe", "config": {"apiKey": "sk_test_123", "secretKey": "sk_test_123"}, "logo": "https://logos-world.net/wp-content/uploads/2021/03/Stripe-Logo.png"},
    {"id": uuid.UUID("7f93f279-130f-4231-9458-b976925d40eb"), "name": "PayPal", "config": {"apiKey": "sk_test_456", "secretKey": "sk_test_456"}, "logo": "https://upload.wikimedia.org/wikipedia/commons/3/31/PayPal_Logo2014.svg"},
    {"id": uuid.UUID("c1b2d3e4-5678-90ab-cdef-1234567890ab"), "name": "MercadoPago", "config": {"apiKey": "sk_test_789", "secretKey": "sk_test_789"}, "logo": "https://images.seeklogo.com/logo-png/19/1/mercado-pago-logo-png_seeklogo-198430.png"}
]

ACCOMODATIONS_FALLBACK = [
    {"id": uuid.UUID("7a4aa60c-fab5-43c4-b234-e1c72f249b18")},
    {"id": uuid.UUID("0fedea59-bcc4-4b90-b703-b8613d93c415")},
    {"id": uuid.UUID("09e1229e-7832-5cb5-a9e7-e39f32c5d31b")},
    {"id": uuid.UUID("286c7159-2e57-595c-ae72-094772c88bc6")},
    {"id": uuid.UUID("a4c44c5f-b17d-5eed-a388-37cf96e3e431")},
    {"id": uuid.UUID("808dd541-8767-57d9-88fa-83ffda9ed6b6")},
    {"id": uuid.UUID("67d2ad02-4793-54f8-b4fa-0c4ace7683b3")},
    {"id": uuid.UUID("8180f5b3-0f0d-5dcc-b659-06ff8c804ebe")},
    {"id": uuid.UUID("a875d943-3fc4-53f2-adce-b2c760d18d79")},
    {"id": uuid.UUID("6d350755-fc82-557c-9e09-a9d88ad7bf01")},
    {"id": uuid.UUID("920ae6a3-537b-576d-9a0e-c0ac74460088")},
    {"id": uuid.UUID("e142b65f-8b48-53ae-8610-2d2324c364ed")}
]


class SeedHelper:
    """Herramienta para poblar y restablecer los proveedores de pago."""

    @staticmethod
    def reset_and_seed():
        """
        Elimina todos los registros existentes de proveedores de pago y transacciones, y luego inserta los proveedores definidos en PAYMENT_PROVIDERS_FALLBACK.

        Returns:
            dict con el resumen de registros insertados o un mensaje de error.
        """
        try:
            # Limpiar tablas existentes
            PaymentTransaction.query.delete()
            Payment.query.delete()
            PaymentProvider.query.delete()
            
            db.session.flush()

            payment_providers_procesados = 0

            # Recorrer cada provider
            for provider in PAYMENT_PROVIDERS_FALLBACK:

                # Crear el PaymentProvider
                provider_obj = PaymentProvider(
                    id=provider["id"],
                    name=provider["name"],
                    config=provider["config"],  
                    is_active=provider.get("is_active", True),
                    logo=provider.get("logo")
                )
                
                db.session.add(provider_obj)
                payment_providers_procesados += 1

            
            for acomodacion in ACCOMODATIONS_FALLBACK:
                for mes in range(1, 5):
                    for n in range(0,300):
                        random_provider = random.choice(PAYMENT_PROVIDERS_FALLBACK)
                        random_amount = round(random.uniform(500000.0, 2000000.0), 2)
                        fecha_pago = fecha_aleatoria(mes, 2026)
                        payment = Payment(
                            id=uuid.uuid4(),
                            reserva_id=uuid.uuid4(),
                            propiedad_id=acomodacion["id"],
                            provider_id=random_provider["id"],
                            amount=random_amount,
                            currency="COP",
                            payment_metadata={"habitacion_id": "historico-mock"},
                            created_at=fecha_pago
                        )
                        db.session.add(payment)

            db.session.commit()

            return {
                "ok": True,
                "payment_providers_procesados": payment_providers_procesados,
                "payment_providers": len(PAYMENT_PROVIDERS_FALLBACK),
                "payments_creados": len(ACCOMODATIONS_FALLBACK) * 4 * 300
            }

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}


def fecha_aleatoria(mes: int, anio: int) -> date:
    dias_del_mes = calendar.monthrange(anio, mes)[1]
    dia = random.randint(1, dias_del_mes)

    return date(anio, mes, dia)
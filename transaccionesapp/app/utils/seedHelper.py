from app.db.models import Payment, PaymentProvider, PaymentTransaction, db
import uuid

# ---------------------------------------------------------------------------
# Fallback: Proveedores locales 
# ---------------------------------------------------------------------------
PAYMENT_PROVIDERS_FALLBACK = [
    {"id": uuid.UUID("9a4a97e8-7f0e-46fb-a451-d7de8ef19ba5"), "name": "Stripe", "config": {"apiKey": "sk_test_123", "secretKey": "sk_test_123"}, "logo": "https://logos-world.net/wp-content/uploads/2021/03/Stripe-Logo.png"},
    {"id": uuid.UUID("7f93f279-130f-4231-9458-b976925d40eb"), "name": "PayPal", "config": {"apiKey": "sk_test_456", "secretKey": "sk_test_456"}, "logo": "https://upload.wikimedia.org/wikipedia/commons/3/31/PayPal_Logo2014.svg"},
    {"id": uuid.UUID("c1b2d3e4-5678-90ab-cdef-1234567890ab"), "name": "MercadoPago", "config": {"apiKey": "sk_test_789", "secretKey": "sk_test_789"}, "logo": "https://images.seeklogo.com/logo-png/19/1/mercado-pago-logo-png_seeklogo-198430.png"}
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

            db.session.commit()

            return {
                "ok": True,
                "payment_providers_procesados": payment_providers_procesados,
                "payment_providers": len(PAYMENT_PROVIDERS_FALLBACK)
            }

        except Exception as e:
            db.session.rollback()
            return {"ok": False, "error": str(e)}

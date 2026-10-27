from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings


def kes_to_usd(amount_kes):
    """Convert a KES amount to USD using the configured rate."""
    rate = Decimal(str(getattr(settings, "KES_PER_USD", "129.00")))
    if rate <= 0:
        return None
    return (Decimal(str(amount_kes)) / rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

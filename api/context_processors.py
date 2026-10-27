from django.conf import settings

from .pricing import kes_to_usd


def training_pricing(request):
    rate_kes = settings.DEFAULT_TRAINING_RATE_KES
    return {
        "training_rate_kes": rate_kes,
        "training_rate_kes_display": f"{rate_kes:,}",
        "training_rate_usd": kes_to_usd(rate_kes),
    }

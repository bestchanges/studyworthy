from . import logic


def periodic():
    logic.update_status_yandex_payments(days=3)

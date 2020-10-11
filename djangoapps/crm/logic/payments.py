from djangoapps.erp.models import Invoice

PAYMENT_GATEWAYS = {}

class PaymentGateway(object):

    code = None
    name = None
    # def __init__(self, code: str, name: str) -> None:
    #     """
    #     :param code: slug-like str
    #     :param name: name for human reads
    #     """
    #     assert code and len(code)
    #     assert name and len(name)
    #     self.code = code
    #     self.name = name

    @classmethod
    def assert_can_pay_invocie(self, invoice: Invoice) -> None:
        """
        raises AssertionError is this invoice cannot be payed
        :param invoice:
        :return: None if this invoice payable
        """
        raise NotImplemented()

    @classmethod
    def pay_invoice(self, invoice):
        """
        Start payment process for invoice.
        This involves status updates, payments create
        and so on.

        :param invoice: invoice shoult be payeble.
        :return: redirect location for browser
        """
        raise NotImplemented()


def register_gateway(gateway_class) -> None:
    global PAYMENT_GATEWAYS
    PAYMENT_GATEWAYS[gateway_class.code] = gateway_class

def list_gateways():
    global PAYMENT_GATEWAYS
    return PAYMENT_GATEWAYS.values()

def get_gateway(code: str) -> PaymentGateway:
    global PAYMENT_GATEWAYS
    return PAYMENT_GATEWAYS[code]

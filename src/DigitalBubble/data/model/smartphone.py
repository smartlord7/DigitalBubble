from data.model.product import Product


class Smartphone(Product):
    def __init__(self):
        super(Smartphone, self).__init__()
        self.model = None
        self.operative_system = None

        self.fields["model"] = \
            {
                "required": True,
                "type": int
            }

        self.fields["operating_system"] = \
            {
                "required": True,
                "type": int
            }

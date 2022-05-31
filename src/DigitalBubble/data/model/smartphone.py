from data.model.product import Product


class Smartphone(Product):
    def __init__(self):
        super(Smartphone, self).__init__()
        self.model = None
        self.operative_system = None

        self.fields["model"] = \
            {
                "required": True,
                "type": str
            }

        self.fields["operative_system"] = \
            {
                "required": True,
                "type": str
            }

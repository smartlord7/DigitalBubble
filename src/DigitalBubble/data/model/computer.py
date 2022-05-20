from data.model.product import Product


class Computer(Product):
    def __init__(self):
        super(Computer, self).__init__()
        self.cpu = None
        self.gpu = None

        self.fields["cpu"] = \
            {
                "required": True,
                "type": str
            }

        self.fields["gpu"] = \
            {
                    "required": True,
                    "type": str
            }

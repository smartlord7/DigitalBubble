from data.model.product import Product


class Television(Product):
    def __init__(self):
        super(Television, self).__init__()
        self.size = None
        self.technology = None

        self.fields["size"] = \
            {
                "required": True,
                "type": int
            }

        self.fields["technology"] = \
            {
                "required": True,
                "type": int
            }

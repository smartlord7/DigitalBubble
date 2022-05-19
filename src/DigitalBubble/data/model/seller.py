from data.model.user import User


class Seller(User):
    def __init__(self):
        super(Seller, self).__init__()
        self.company_name = None

        self.fields["company_name"] = {
            "required": True,
            "type": str
        }

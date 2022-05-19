from data.model.base_model import BaseModel


class User(BaseModel):
    def __init__(self):
        super().__init__()
        self.zip_code = None
        self.state = None
        self.city = None
        self.street_name = None
        self.last_name = None
        self.house_no = None
        self.phone_number = None
        self.tin = None
        self.email = None
        self.first_name = None
        self.user_name = None
        self.role = None

        self.fields = {
            "user_name":
                {
                    "required": True,
                    "type": str
                },
            "email":
                {
                    "required": True,
                    "type": str
                },
            "password":
                {
                    "required": True,
                    "type": str
                },
            "first_name":
                {
                    "required": True,
                    "type": str
                },
            "last_name":
                {
                    "required": True,
                    "type": str
                },
            "tin":
                {
                    "required": True,
                    "type": str
                },
            "phone_number":
                {
                    "required": True,
                    "type": str
                },
            "house_no":
                {
                    "required": True,
                    "type": int
                },
            "street_name":
                {
                    "required": True,
                    "type": str
                },
            "state":
                {
                    "required": True,
                    "type": str
                },
            "city":
                {
                    "required": True,
                    "type": str
                },
            "zip_code":
                {
                    "required": True,
                    "type": str
                },
            "role":
                {
                    "required": True,
                    "type": int
                },
        }
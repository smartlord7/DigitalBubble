from data.model.base_model import BaseModel


class Product(BaseModel):
    def __init__(self):
        super().__init__()
        self.name = None
        self.price = None
        self.stock = None
        self.category = None
        self.type = None
        self.description = None

        self.fields = {
            "name":
                {
                    "required": True,
                    "type": str
                },
            "price":
                {
                    "required": True,
                    "type": float
                },
            "stock":
                {
                    "required": True,
                    "type": int
                },
            "category":
                {
                    "required": True,
                    "type": str
                },
            "type":
                {
                    "required": True,
                    "type": int
                },
            "description":
                {
                    "required": True,
                    "type": str
                },
        }

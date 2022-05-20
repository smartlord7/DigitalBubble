from data.model.base_model import BaseModel


class Classification(BaseModel):
    def __init__(self):
        super(Classification, self).__init__()
        self.rating = None
        self.comment = None

        self.fields["rating"] = \
            {
                "required": True,
                "type": int
            }

        self.fields["comment"] = \
            {
                    "required": True,
                    "type": str
            }

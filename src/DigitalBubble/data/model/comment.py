from data.model.base_model import BaseModel


class Comment(BaseModel):
    def __init__(self):
        super(Comment, self).__init__()
        self.text = None

        self.fields["text"] = \
            {
                "required": True,
                "type": str
            }

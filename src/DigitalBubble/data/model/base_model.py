import flask


class BaseModel:
    def __init__(self):
        self.fields = dict()

    def from_json(self, json: dict):
        missing_fields = list()
        wrong_type_fields = list()

        for field in self.fields.keys():
            if "required" in self.fields[field]:
                field_metadata = self.fields[field]

                if field_metadata["required"] and field not in json:
                    missing_fields.append(field)
                    continue

            if field in json:
                field_metadata = self.fields[field]

                if field_metadata["type"] != type(json[field]):
                    wrong_type_fields.append((field, field_metadata["type"], type(json[field])))
                    continue

                self.__setattr__(field, json[field])

        return missing_fields, wrong_type_fields

    def bind_json(self, json: dict):
        missing_fields, wrong_type_fields = self.from_json(json)
        response = dict()
        response['errors'] = list()
        valid = len(missing_fields) == 0 and len(wrong_type_fields) == 0

        if len(missing_fields) != 0:
            for field in missing_fields:
                response['errors'].append("Field %s is missing" % field)

        if len(wrong_type_fields) != 0:
            for field in wrong_type_fields:
                response['errors'].append("Wrong type for %s: expected %s, have %s" % (field[0], field[1], field[2]))

        if not valid:
            return flask.jsonify(response)

        return False

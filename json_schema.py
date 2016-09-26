# type: int, list, object


class DictParser(object):
    @staticmethod
    def must_attr(_dict, attr):
        r = _dict.get(attr)
        if r is None:
            raise ValueError("Invalid json {} is missing".format(attr))
        return r


class TypeValidator(DictParser):
    _type = None
    # to define

    def __init__(self, schema):
        self.schema = schema

    def validate(self, value):
        if self._type is None:
            raise NotImplementedError
        if not isinstance(value, self._type):
            return False
        return True


class IntegerValidator(TypeValidator):
    _type = int

    def __init__(self, dictionary):
        self.minValue = dictionary.get("minValue")
        super(IntegerValidator, self).__init__(dictionary)

    def validate(self, value):
        if not super(IntegerValidator, self).validate(value):
            return False
        if self.minValue is not None:
            return value >= self.minValue
        else:
            return True


class StringValidator(TypeValidator):
    _type = str


class ArrayValidator(TypeValidator):
    _type = list


def get_non_object_validator(string, value):
    if string == "integer":
        return IntegerValidator(value)
    elif string == "string":
        return StringValidator(value)
    elif string == "array":
        return ArrayValidator(value)


class ObjectValidator(TypeValidator):
    _type = dict

    def validate(self, value):
        if not super(ObjectValidator, self).validate(value):
            return False
        for k, v in self.schema.get('properties', {}):
            if v.get("type") is not None:
                validator = get_non_object_validator(v.get("type"))
                k_value = value.get(k)
                if k_value is not None:
                    if not validator.validate(k_value):
                        return False
        return True


def get_validator(string, value):
    v = get_non_object_validator(string, value)
    if v is not None:
        return v
    if string == "object":
        return ObjectValidator(value)
    raise NotImplementedError


class JsonSchema(DictParser):
    def __init__(self, jsons):
        self.jsons = jsons

    def validate(self, jsons):
        if not self.jsons:
            return True
        validator = get_validator(self.must_attr(self.jsons, "type"),
                                  self.jsons)
        return validator.validate(jsons)

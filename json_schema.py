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


def get_leaf_validator(string, value):
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
        for prop_name, prop_schema in self.schema.get('properties', {}).iteritems():
            typestr = prop_schema.get("type")
            if typestr is not None:
                validator = self.get_validator(typestr, prop_schema)
                prop_value = value.get(prop_name)
                if prop_value is not None:
                    if not validator.validate(prop_value):
                        return False
        return True

    @staticmethod
    def get_validator(typestr, value):
        v = get_leaf_validator(typestr, value)
        if v is not None:
            return v
        if typestr == "object":
            return ObjectValidator(value)
        raise NotImplementedError


class JsonSchema(DictParser):
    def __init__(self, jsons):
        self.jsons = jsons

    @staticmethod
    def find_in_schema(_dict, path):
        prefix = "#/"
        if not path.startswith(prefix):
            raise ValueError("Invalid path {}".format(path))
        path = path[len(prefix):].split('/')
        node = _dict
        for p in path:
            node = node.get(p)
            if node is None:
                raise ValueError("Invalid path: {} does not exist".format(path))
        return node

    def validate(self, jsonval):
        if not self.jsons:
            return True
        validator = ObjectValidator.get_validator(self.must_attr(self.jsons,
                                                                 "type"),
                                                  self.jsons)
        return validator.validate(jsonval)

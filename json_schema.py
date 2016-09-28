class DictParser(object):
    @staticmethod
    def must_attr(_dict, attr):
        r = _dict.get(attr)
        if r is None:
            raise ValueError("Invalid json {} is missing".format(attr))
        return r


class TypeValidator(DictParser):
    _type = None

    def __init__(self, schema):
        self.schema = schema

    def validate(self, value, get_validator):
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

    def validate(self, value, get_validator):
        if not super(IntegerValidator, self).validate(value, get_validator):
            return False
        if self.minValue is not None:
            return value >= self.minValue
        else:
            return True


class StringValidator(TypeValidator):
    _type = str


class ArrayValidator(TypeValidator):
    _type = list


class ObjectValidator(TypeValidator):
    _type = dict

    def validate(self, value, get_validator):
        if not super(ObjectValidator, self).validate(value, get_validator):
            return False
        for prop_name, prop_schema in self.schema.get('properties', {}).iteritems():
            validator = get_validator(prop_schema)
            if validator is not None:
                prop_value = value.get(prop_name)
                if prop_value is not None:
                    if not validator.validate(prop_value, get_validator):
                        return False
        return True


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

    @staticmethod
    def get_non_ref_validator(typestr, value):
        if typestr == "integer":
            return IntegerValidator(value)
        elif typestr == "string":
            return StringValidator(value)
        elif typestr == "array":
            return ArrayValidator(value)
        elif typestr == "object":
            return ObjectValidator(value)
        raise NotImplementedError

    def get_validator(self, node):
        typestr = node.get("type")
        if typestr is not None:
            return self.get_non_ref_validator(typestr, node)
        ref = node.get("$ref")
        if ref is not None:
            node = self.find_in_schema(self.jsons, ref)
            return self.get_validator(node)

    def validate(self, jsonval):
        if not self.jsons:
            return True

        validator = self.get_validator(self.jsons)
        return validator.validate(jsonval, self.get_validator)

import unittest
from json_schema import JsonSchema


class TestJsonSchema(unittest.TestCase):

    def test_empty_loadjs(self):
        j = JsonSchema({})
        for ex in [{}, 1, [1, 2], None]:
            self.assertTrue(j.validate(ex))

    def test_must_attr(self):
        self.assertEquals(JsonSchema.must_attr({"type": "integer"}, "type"),
                          "integer")

    # @unittest.skip
    def test_integer_loadjs(self):
        j = JsonSchema({"type": "integer"})
        self.assertTrue(j.validate(1))
        for ex in [{}, [1, 2], None]:
            self.assertFalse(j.validate(ex))

    # @unittest.skip
    def test_integer_min_value(self):
        j = JsonSchema({"type": "integer",
                        "minValue": 1})
        self.assertTrue(j.validate(1))
        self.assertFalse(j.validate(0))

    # @unittest.skip
    def test_string_loadjs(self):
        j = JsonSchema({"type": "string"})
        self.assertTrue(j.validate("1"))
        for ex in [{}, 1, [1, 2], None]:
            self.assertFalse(j.validate(ex))

    # @unittest.skip
    def test_object_loadjs(self):
        j = JsonSchema({"type": "object"})
        self.assertTrue(j.validate({"1": 2}))
        for ex in [[1, 2], 1, "1", None]:
            self.assertFalse(j.validate(ex))

    def test_object_properties(self):
        j = JsonSchema({"type": "object",
                        "properties": {
                            "firstName": {
                                "type": "string"},
                            "lastName": {
                                "type": "string"}
                        }})
        self.assertTrue(j.validate({"firstName": "myFirstName",
                                    "lastName": "myLastName"}))
        self.assertFalse(j.validate({"firstName": 1,
                                    "lastName": "myLastName"}))

    def test_rec_object_properties(self):
        j = JsonSchema({"type": "object",
                        "properties": {
                            "name": {
                                "type": "object",
                                "properties": {
                                    "firstName": {
                                        "type": "string"},
                                    "lastName": {
                                        "type": "string"}
                                }
                            }
                        }})
        self.assertTrue(j.validate({"name": {"firstName": "myFirstName",
                                             "lastName": "myLastName"}}))
        self.assertFalse(j.validate({"name":
                                     {"firstName": 1,
                                      "lastName": "myLastName"}}))

    def test_find_in_schema(self):
        self.assertEquals(JsonSchema.find_in_schema({"definitions":
                                                     {"def_1":
                                                      {"subdef_1": "1_val"}}},
                                                    "#/definitions/def_1/subdef_1"),
                          "1_val")

    def test_ref(self):
        j = JsonSchema({"type": "object",
                        "properties": {
                            "name": {
                                "type": "object",
                                "properties": {
                                    "firstName": {
                                        "type": "string"},
                                    "lastName": {
                                        "type": "string"}
                                }
                            },
                            "age": {
                                "$ref": "#/definitions/positive_integer"
                            }
                        },
                        "definitions":
                        {"positive_integer":
                         {"type": "integer",
                          "minValue": 0
                          }}})
        self.assertTrue(j.validate({"name": {"firstName": "someFirstName",
                                             "lastName": "someLastName"},
                                    "age": 1}))
        self.assertFalse(j.validate({"name": {"firstName": "someFirstName",
                                              "lastName": "someLastName"},
                                     "age": -1}))

if __name__ == '__main__':
    unittest.main()

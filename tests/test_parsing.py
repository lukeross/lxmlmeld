from io import StringIO
from unittest import TestCase

from lxmlmeld import parse_xml, parse_xmlstring


class XMLTests(TestCase):
    def as_expected(self, handler):
        scenarios = (
            (
                "<xml />",
                "<?xml version='1.0' encoding='ASCII'?>\n<xml/>"
            ),
            (
                "<?xml version='1.0' ?><xml />",
                "<?xml version='1.0' encoding='ASCII'?>\n<xml/>"
            ),
            (
                "<xml><a /><b /></xml>",
                "<?xml version='1.0' encoding='ASCII'?>\n<xml><a/><b/></xml>"
            ),
        )
        for ip, op in scenarios:
            doc = handler(ip)
            self.assertEqual(doc.write_xmlstring(), op.encode("ascii"))

    def test_parse_string(self):
        self.as_expected(parse_xmlstring)

    def test_parse_handle(self):
        self.as_expected(lambda i: parse_xml(StringIO(i)))

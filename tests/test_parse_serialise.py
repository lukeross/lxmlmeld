from io import StringIO
from unittest import TestCase

from lxmlmeld import parse_xml, parse_xmlstring, parse_html, parse_htmlstring


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


class HTMLTests(TestCase):
    def as_expected(self, handler):
        scenarios = (
            (
                "<html><body><br></body></html>",
                "<html><body><br></body></html>"
            ),
            (
                "<html><body><script></script></body></html>",
                "<html><body><script></script></body></html>"
            ),
        )
        for ip, op in scenarios:
            doc = handler(ip)
            self.assertEqual(
                doc.write_htmlstring(doctype=None),
                op.encode("ascii")
            )

    def test_parse_string(self):
        self.as_expected(parse_htmlstring)

    def test_parse_handle(self):
        self.as_expected(lambda i: parse_html(StringIO(i)))

    def test_find_meld(self):
        doc = parse_htmlstring("<html><body meld:id='a'><br></body></html>")
        ele = doc.findmeld('a')
        self.assertEqual(ele.tag, 'body')


class XHTMLTests(TestCase):
    DT = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" " \
        "\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n"

    def as_expected(self, handler):
        scenarios = (
            (
                self.DT + "<html xmlns='http://www.w3.org/1999/xhtml' "
                "xmlns:meld='http://www.plope.com/software/meld3'>"
                "<body meld:id='b'><br/></body></html>",
                self.DT + "<html xmlns=\"http://www.w3.org/1999/xhtml\">"
                "<body><br /></body></html>"
            ),
            (
                self.DT + "<html xmlns='http://www.w3.org/1999/xhtml' "
                "xmlns:meld='http://www.plope.com/software/meld3'>"
                "<body meld:id='b'><p/></body></html>",
                self.DT + "<html xmlns=\"http://www.w3.org/1999/xhtml\">"
                "<body><p></p></body></html>"
            ),
        )
        for ip, op in scenarios:
            doc = handler(ip)
            self.assertEqual(
                doc.write_xhtmlstring(),
                op.encode("ascii")
            )

    def test_parse_string(self):
        self.as_expected(parse_xmlstring)

    def test_parse_handle(self):
        self.as_expected(lambda i: parse_xml(StringIO(i)))

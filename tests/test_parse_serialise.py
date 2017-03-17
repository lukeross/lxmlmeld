from io import BytesIO, StringIO
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

    def test_write_handle(self):
        doc = parse_xmlstring("<a />")
        io = BytesIO()
        doc.write_xml(io, declaration=False)
        self.assertEqual(io.getvalue(), b"<a/>")

    def test_serialise_options(self):
        tests = (
            (
                {'encoding': 'ASCII', 'declaration': True},
                b"<?xml version='1.0' encoding='ASCII'?>",
                {'encoding': 'ASCII', 'declaration': False},
                b"<?xml",
                True
            ),
            (
                {'pipeline': True},
                b"meld:id=",
                {'pipeline': False},
                b"meld:id=",
                False
            ),
            (
                {'doctype': '<!DOCTYPE note SYSTEM "Note.dtd">'},
                b'<!DOCTYPE note SYSTEM "Note.dtd">',
                {'doctype': None},
                b"DOCTYPE",
                False
            ),
            (
                {'fragment': False, 'declaration': True},
                b"<?xml version='1.0'",
                {'fragment': True, 'declaration': True},
                b"<?xml",
                True
            ),
        )

        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3' "
            "meld:id='r' />"
        )
        for turn_on, match_on, turn_off, absent, default in tests:
            serialised_on = doc.write_xmlstring(**turn_on)
            self.assertIn(match_on, serialised_on)
            serialised_off = doc.write_xmlstring(**turn_off)
            self.assertNotIn(absent, serialised_off)
            serialised_default = doc.write_xmlstring()
            if default:
                self.assertIn(match_on, serialised_default)
            else:
                self.assertNotIn(absent, serialised_default)
            for txt in (serialised_on, serialised_off, serialised_default):
                self.assertIn(b"<a", txt)

    def test_duplicate_melds(self):
        with self.assertRaises(ValueError):
            parse_xmlstring(
                "<body xmlns:meld='http://www.plope.com/software/meld3' "
                "meld:id='a'><br meld:id='a'/></body>"
            )


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

    def test_write_handle(self):
        doc = parse_xmlstring("<html><body/></html>")
        io = BytesIO()
        doc.write_html(io, doctype=None)
        self.assertEqual(io.getvalue(), b"<html><body></body></html>")

    def test_duplicate_melds(self):
        with self.assertRaises(ValueError):
            parse_htmlstring("<body meld:id='a'><br meld:id='a'/></body>")

    def test_find_meld(self):
        doc = parse_htmlstring("<html><body meld:id='a'><br></body></html>")
        ele = doc.findmeld('a')
        self.assertEqual(ele.tag, 'body')

    def test_serialise_options(self):
        html_dtd = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">'

        tests = (
            (
                {'doctype': html_dtd},
                b'<!DOCTYPE HTML PUBLIC ',
                {'doctype': None},
                b"DOCTYPE",
                True
            ),
            (
                {'fragment': False, 'doctype': html_dtd},
                b'<!DOCTYPE HTML PUBLIC ',
                {'fragment': True, 'doctype': html_dtd},
                b"DOCTYPE",
                True
            ),
        )

        doc = parse_htmlstring(
            "<html><body><br><p></p></body></html>"
        )
        for turn_on, match_on, turn_off, absent, default in tests:
            serialised_on = doc.write_htmlstring(**turn_on)
            self.assertIn(match_on, serialised_on, repr(turn_on))
            serialised_off = doc.write_htmlstring(**turn_off)
            self.assertNotIn(absent, serialised_off, repr(turn_off))
            serialised_default = doc.write_htmlstring()
            if default:
                self.assertIn(match_on, serialised_default)
            else:
                self.assertNotIn(absent, serialised_default)
            for txt in (serialised_on, serialised_off, serialised_default):
                self.assertIn(b"<html><body><br><p></p></body></html>", txt)


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

    def test_write_handle(self):
        doc = parse_xmlstring("<a />")
        io = BytesIO()
        doc.write_xhtml(io, fragment=True)
        self.assertEqual(io.getvalue(), b"<a></a>")

    def test_serialise_options(self):
        xhtml_strict_dt = '<!DOCTYPE html PUBLIC ' \
            '"-//W3C//DTD XHTML 1.0 Strict//EN" ' \
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'

        tests = (
            (
                {'encoding': 'ASCII', 'declaration': True},
                b"<?xml version='1.0' encoding='ASCII'?>",
                {'encoding': 'ASCII', 'declaration': False},
                b"<?xml",
                False
            ),
            (
                {'pipeline': True},
                b"meld:id=",
                {'pipeline': False},
                b"meld:id=",
                False
            ),
            (
                {'doctype': xhtml_strict_dt},
                xhtml_strict_dt.encode("ascii"),
                {},
                b"Strict",
                False
            ),
            (
                {'fragment': False, 'declaration': True},
                b"<?xml version='1.0'",
                {'fragment': True, 'declaration': True},
                b"<?xml",
                False
            ),
        )

        doc = parse_xmlstring(
            self.DT + "<html xmlns='http://www.w3.org/1999/xhtml' "
            "xmlns:meld='http://www.plope.com/software/meld3'>"
            "<body meld:id='b'><br/><p/></body></html>",
        )
        for turn_on, match_on, turn_off, absent, default in tests:
            serialised_on = doc.write_xhtmlstring(**turn_on)
            self.assertIn(match_on, serialised_on, repr(turn_on))
            serialised_off = doc.write_xhtmlstring(**turn_off)
            self.assertNotIn(absent, serialised_off, repr(turn_off))
            serialised_default = doc.write_xhtmlstring()
            if default:
                self.assertIn(match_on, serialised_default)
            else:
                self.assertNotIn(absent, serialised_default)
            for txt in (serialised_on, serialised_off, serialised_default):
                self.assertIn(b"<br /><p></p></body></html>", txt)

        with self.assertRaises(ValueError):
            doc.write_xhtmlstring(doctype='<!DOCTYPE note SYSTEM "Note.dtd">')
        with self.assertRaises(ValueError):
            doc.write_xhtmlstring(doctype=None)

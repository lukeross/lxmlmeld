import unittest
from copy import deepcopy
from lxml.builder import E
from unittest import TestCase

from lxmlmeld import parse_xmlstring


class ReplaceTests(TestCase):
    def as_expected(self, arg, expected_in_output, **kwargs):
        docs = (
            (  # Naked
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "<replaceme meld:id='r' /></foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo>{}</foo>"
            ),
            (  # Surrounded by elements
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "<bar /><replaceme meld:id='r' /><baz /></foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n"
                "<foo><bar/>{}<baz/></foo>"
            ),
            (  # Surrounded by text
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "bar <replaceme meld:id='r' />baz</foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo>bar {}baz</foo>"
            ),
            (  # Surrounded by mixed
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "<bar />bar <replaceme meld:id='r' />baz</foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n"
                "<foo><bar/>bar {}baz</foo>"
            ),
        )
        for ip, op in docs:
            doc = parse_xmlstring(ip)
            doc.findmeld("r").replace(deepcopy(arg), **kwargs)
            self.assertEqual(
                doc.write_xmlstring(),
                op.format(expected_in_output).encode("ascii"),
                op.format(expected_in_output)
            )

    def test_replace_with_plain_text(self):
        self.as_expected("<hello world!>", "&lt;hello world!&gt;")

    def test_replace_with_structure(self):
        self.as_expected("<hello word='world' /><a />",
                         '<hello word="world"/><a/>', structure=True)

    def test_replace_with_nodes(self):
        replacement = E("awesome")
        replacement.tail = "!"
        self.as_expected(replacement, "<awesome/>!")

    def test_replace_with_nodelist(self):
        replacements = [E("so", {"completely": "yes"}), E("awesome")]
        replacements[0].tail = "-"
        replacements[1].tail = "!"
        self.as_expected(replacements, '<so completely="yes"/>-<awesome/>!')

    def test_replace_no_parent(self):
        doc = parse_xmlstring("<a/>")
        doc.replace("nooo")
        self.assertEqual(
            doc.write_xmlstring(declaration=False),
            b'<a/>'
        )


class ContentTests(TestCase):
    def as_expected(self, arg, expected_in_output, **kwargs):
        docs = (
            (  # Empty
                "<foo xmlns:meld='http://www.plope.com/software/meld3'"
                " meld:id='r' />",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo>{}</foo>"
            ),
            (  # Contains text
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "<bar meld:id='r'>placeholder</bar></foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n"
                "<foo><bar>{}</bar></foo>"
            ),
            (  # Contains node
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "<bar meld:id='r'><gone /></bar></foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n"
                "<foo><bar>{}</bar></foo>"
            ),
            (  # Contains mixed
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "<bar meld:id='r'>and it's <gone /></bar></foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n"
                "<foo><bar>{}</bar></foo>"
            ),
        )
        for ip, op in docs:
            doc = parse_xmlstring(ip)
            doc.findmeld("r").content(deepcopy(arg), **kwargs)
            self.assertEqual(
                doc.write_xmlstring(),
                op.format(expected_in_output).encode("ascii"),
                op.format(expected_in_output)
            )

    def test_plain_text_content(self):
        self.as_expected("<hello world!>", "&lt;hello world!&gt;")

    def test_structured_content(self):
        self.as_expected("<hello word='world' /><a />",
                         '<hello word="world"/><a/>', structure=True)

    def test_content_nodes(self):
        replacement = E("awesome")
        replacement.tail = "!"
        self.as_expected(replacement, "<awesome/>!")

    def test_content_nodelist(self):
        replacements = [E("so", {"completely": "yes"}), E("awesome")]
        replacements[0].tail = "-"
        replacements[1].tail = "!"
        self.as_expected(replacements, '<so completely="yes"/>-<awesome/>!')


class RepeatTests(TestCase):
    def as_expected(self, arg, expected_in_output):
        docs = (
            (  # Text before
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "yo<bar meld:id='r' /></foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo>yo{}</foo>"
            ),
            (  # Text after
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "<bar meld:id='r' />yo</foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo>{}yo</foo>"
            ),
            (  # Text both sides
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "oy<bar meld:id='r' />yo</foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo>oy{}yo</foo>"
            ),
            (  # Elements both sides
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "<oy/><bar meld:id='r' /><yo/></foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n"
                "<foo><oy/>{}<yo/></foo>"
            ),
            (  # Mixed
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>"
                "<oy/><bar meld:id='r' />yo</foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo><oy/>{}yo</foo>"
            ),
        )
        for ip, op in docs:
            doc = parse_xmlstring(ip)
            for ele, data in doc.findmeld("r").repeat(deepcopy(arg), 'r'):
                ele.set("a", data)
            self.assertEqual(
                doc.write_xmlstring(),
                op.format(expected_in_output).encode("ascii"),
                op.format(expected_in_output)
            )

    def test_repeat_zero(self):
        self.as_expected([], '')

    def test_repeat_one(self):
        self.as_expected(['q'], '<bar a="q"/>')

    def test_repeat_multi(self):
        self.as_expected(['q', 'z'], '<bar a="q"/><bar a="z"/>')


class MeldFindingTests(TestCase):
    def test_findmeld_exists(self):
        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3'>"
            "<b meld:id='q'/></a>"
        )
        found = doc.findmeld('q')
        self.assertIsNotNone(found)
        self.assertEqual(found.tag, 'b')
        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3'"
            " meld:id='q' />"
        )
        found = doc.findmeld('q')
        self.assertIsNotNone(found)
        self.assertEqual(found.tag, 'a')

    def test_findmeld_missing(self):
        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3'>"
            "<b meld:id='q'/></a>"
        )
        found = doc.findmeld('z')
        self.assertIsNone(found)
        found = doc.findmeld('z', '')
        self.assertEqual(found, '')

    def test_meldid(self):
        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3'>"
            "<b meld:id='q'/></a>"
        )
        found = doc.findmeld('q')
        self.assertEqual(found.meldid(), 'q')

    def test_findmelds(self):
        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3' "
            "meld:id='z'><b meld:id='q'/></a>"
        )
        found = list(doc.findmelds())
        self.assertEqual(len(found), 2)
        self.assertEqual(set(['q', 'z']), set([
            e.meldid() for e in found
        ]))


class FillMeldsTests(TestCase):
    def test_fill_melds(self):
        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3'> "
            "<b meld:id='z'/><b meld:id='q'/></a>"
        )
        ret = doc.fillmelds(z='foo', q='bar', a='ohno')
        self.assertEqual(
            doc.write_xmlstring(declaration=False),
            b'<a> <b>foo</b><b>bar</b></a>'
        )
        self.assertEqual(ret, ['a'])


class AttributesTests(TestCase):
    def test_fill_attributes(self):
        doc = parse_xmlstring("<a/>")
        doc.attributes(foo='q', bar='z')
        op = doc.write_xmlstring(declaration=False)
        self.assertTrue(op.startswith(b"<a "))
        self.assertTrue(op.endswith(b"/>"))
        self.assertIn(b'foo="q"', op)
        self.assertIn(b'bar="z"', op)


class CloneTests(TestCase):
    def test_no_parent(self):
        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3'>"
            "<b meld:id='z'/></a>"
        )
        new = doc.findmeld('z').clone()
        new.attributes(foo='bar')
        self.assertEqual(
            new.write_xmlstring(declaration=False),
            b'<b foo="bar"/>'
        )
        self.assertEqual(
            doc.write_xmlstring(declaration=False),
            b'<a><b/></a>'
        )

    def test_with_parent(self):
        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3'>"
            "<b meld:id='z'/><c meld:id='q'/></a>"
        )
        new = doc.findmeld('z').clone(doc.findmeld('q'))
        new.attributes(foo='bar')
        self.assertEqual(
            new.write_xmlstring(declaration=False),
            b'<b foo="bar"/>'
        )
        self.assertEqual(
            doc.write_xmlstring(declaration=False),
            b'<a><b/><c><b foo="bar"/></c></a>'
        )


class DeparentTests(TestCase):
    def test_deparent(self):
        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3'>"
            "<b meld:id='z'/></a>"
        )
        doc.findmeld('z').deparent()
        self.assertEqual(
            doc.write_xmlstring(declaration=False),
            b'<a/>'
        )
        doc.deparent()  # no-op
        self.assertEqual(
            doc.write_xmlstring(declaration=False),
            b'<a/>'
        )

    def test_deparent_preserves_tail(self):
        doc = parse_xmlstring(
            "<a xmlns:meld='http://www.plope.com/software/meld3'>atail"
            "<b meld:id='z'/>btail</a>"
        )
        doc.findmeld('z').deparent()
        self.assertEqual(
            doc.write_xmlstring(declaration=False),
            b'<a>atailbtail</a>'
        )
        doc.deparent()  # no-op
        self.assertEqual(
            doc.write_xmlstring(declaration=False),
            b'<a>atailbtail</a>'
        )


if __name__ == '__main__':
    unittest.main()

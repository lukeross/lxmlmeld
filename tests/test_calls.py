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

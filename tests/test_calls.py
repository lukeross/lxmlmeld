from unittest import TestCase

from lxmlmeld import parse_xmlstring


class ReplaceTests(TestCase):
    def as_expected(self, arg, expected_in_output, **kwargs):
        docs = (
            (  # Naked
                "<foo xmlns:meld='http://www.plope.com/software/meld3'><replaceme meld:id='r' /></foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo>{}</foo>",
            ),
            (  # Surrounded by elements
                "<foo xmlns:meld='http://www.plope.com/software/meld3'><bar /><replaceme meld:id='r' /><baz /></foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo><bar/>{}<baz/></foo>",
            ),
            (  # Surrounded by text
                "<foo xmlns:meld='http://www.plope.com/software/meld3'>bar <replaceme meld:id='r' />baz</foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo>bar {}baz</foo>",
            ),
            (  # Surrounded by mixed
                "<foo xmlns:meld='http://www.plope.com/software/meld3'><bar />bar <replaceme meld:id='r' />baz</foo>",
                "<?xml version='1.0' encoding='ASCII'?>\n<foo><bar/>bar {}baz</foo>",
            ),
        )
        for ip, op in docs:
            doc = parse_xmlstring(ip)
            doc.findmeld("r").replace(arg, **kwargs)
            self.assertEqual(doc.write_xmlstring(), op.format(expected_in_output).encode("ascii"), op.format(expected_in_output))

    def test_replace_with_plain_text(self):
        self.as_expected("<hello world!>", "&lt;hello world!&gt;")

    def test_replace_with_structure(self):
        self.as_expected("<hello word='world' /><a />",
                         '<hello word="world"/><a/>', structure=True)

    def test_replace_with_nodes(self):
        pass

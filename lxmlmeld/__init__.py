from copy import deepcopy
from lxml import etree

NS = "http://www.plope.com/software/meld3"
_html_doctype = (
    "HTML", "-//W3C//DTD HTML 4.01 Transitional//EN",
    "http://www.w3.org/TR/html4/loose.dtd"
)
_xhtml_doctype = (
    "html", "-//W3C//DTD XHTML 1.0 Transitional//EN",
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
)


class Element(etree.ElementBase):
    def __repr__(self):
        return "<{} {} at {}>".format(
            self.__class__.__name__, self.tag, id(self)
        )

    def clone(self, parent=None):
        ret = deepcopy(self)
        if parent is not None:
            parent.append(ret)
        return ret

    def findmeld(self, name, default=None):
        ret = self.xpath(
            "descendant-or-self::*[@meld:id='{}']".format(name),
            namespaces={"meld": NS}
        )
        return ret[0] if ret else default

    def findmelds(self):
        return self.xpath(
            "descendant-or-self::*[@meld:id]", namespaces={"meld": NS}
        )

    def meldid(self):
        return self.get(etree.QName(NS, "id").text)

    def repeat(self, iterable, childname=None):
        thing = self.findmeld(childname) if childname else self
        for data in iterable:
            next_thing = thing.clone()
            yield thing, data
            thing.addnext(next_thing)
            thing = next_thing
        thing.getparent().remove(thing)

    def replace(self, text):
        parent = self.getparent()
        if not parent:
            return

        if isinstance(text, etree._Element):
            parent.replace(self, text)
        else:
            self.getprevious().tail += text
            parent.remove(self)

    def content(self, text):
        if isinstance(text, etree._Element):
            self[:] = [text]
        else:
            self[:] = []
            self.text = text

    def attributes(self, **kwargs):
        for k, v in kwargs.items():
            self.set(k, v)

    def fillmelds(self, **kwargs):
        missing = set()
        for k, v in kwargs.items():
            ele = self.findmeld(k)
            if ele is not None:
                ele.content(v)
            else:
                missing.add(k)
        return missing

    def _clone_without_own_ns(self):
        new = self.clone()
        for node in new.xpath("//meld:*", namespaces={"meld": NS}):
            node.getparent().remove(node)
        for node in new.xpath("//*[@*[namespace-uri()='{}']]".format(NS)):
            to_remove = [
                k for k in node.attrib.keys() if etree.QName(k).namespace == NS
            ]
            for k in to_remove:
                del node.attrib[k]
        etree.cleanup_namespaces(new)
        return new

    @staticmethod
    def _get_doctype(doctype):
        name, public, system = doctype
        return '<!DOCTYPE {} PUBLIC "{}" "{}">'.format(*doctype)

    def write_xml(self, file, encoding=None, doctype=None, fragment=False,
                  declaration=True, pipeline=False, _kwargs={"method": "xml"}):
        kwargs = {k: v for k, v in _kwargs.items()}
        kwargs.update(xml_declaration=declaration)
        if doctype:
            kwargs.update(doctype=self._get_doctype(doctype))
        if fragment:
            kwargs.update(doctype=None, xml_declaration=False)

        doc = self if pipeline else self._clone_without_own_ns()
        if file:
            # ElementTree.write() doesn't support doctype
            file.write(etree.tostring(doc, **kwargs))
        else:
            return etree.tostring(doc, **kwargs)

    def write_xhtml(self, file, encoding=None, declaration=False,
                    pipeline=False):
        return self.write_xml(file, encoding=encoding, doctype=_xhtml_doctype)

    def write_html(self, file, encoding=None, doctype=_html_doctype,
                   fragment=False):
        return self.write_xml(
            file, encoding=encoding, doctype=doctype, fragment=fragment,
            _kwargs={"method": "html"}
        )


def _parser(parser_cls=etree.XMLParser):
    parser = parser_cls()
    parser.set_element_class_lookup(
        etree.ElementDefaultClassLookup(element=Element)
    )
    return parser


def _check_tree(tree):
    seen = set()
    for id in tree.xpath("//@meld:id", namespaces={"meld": NS}):
        if id in seen:
            raise ValueError("Duplicate meld:id: {}".format(id))
        seen.add(id)


def parse_xml(file):
    t = etree.parse(xml, _parser())
    _check_tree(t)
    return t


def parse_xmlstring(xml):
    t = etree.fromstring(xml, _parser())
    _check_tree(t)
    return t


def _fix_html(tree):
    qn = etree.QName(NS, "id").text
    for ele in tree.iter():
        if "meld:id" in ele.attrib:
            ele.set(qn, ele.attrib.pop("meld:id"))


def parse_html(file):
    t = etree.parse(xml, _parser(etree.HTMLParser))
    _fix_html(t)
    _check_tree(t)
    return t


def parse_htmlstring(html):
    t = etree.fromstring(html, _parser(etree.HTMLParser))
    _fix_html(t)
    _check_tree(t)
    return t

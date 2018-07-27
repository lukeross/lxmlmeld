from copy import deepcopy
from lxml import etree

NS = "http://www.plope.com/software/meld3"


class _DoctypeDict(object):
    def __init__(self, **kwargs):
        self._doctypes = kwargs

    def __getattr__(self, name):
        try:
            return self._doctypes[name]
        except KeyError:
            raise AttributeError(name)

    def __getitem__(self, name):
        return self._doctypes[name]

    def keys(self):
        return self._doctypes.keys()

    def items(self):
        return self._doctypes.items()

    def __iter__(self):
        return iter(self._doctypes)

    def __repr__(self):
        return repr(self._doctypes)

    def get(self, *args, **kwargs):
        return self._doctypes.get(*args, **kwargs)


doctypes = _DoctypeDict(
    html='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" '
         '"http://www.w3.org/TR/html4/loose.dtd">',
    html_strict='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                '"http://www.w3.org/TR/html4/strict.dtd">',
    xhtml='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
          '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
    xhtml_strict='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
                 '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
)


class Element(etree.ElementBase):
    def __repr__(self):
        return "<{} {} at {}>".format(
            self.__class__.__name__, self.tag, id(self)
        )

    def clone(self, parent=None):
        """
        Copy a element, including all of its children. The new element
        initially is not associated with the document, but if an element
        is passed in as parent the newly-copied element will be appended
        to this parent element. Returns the new element.
        """
        ret = deepcopy(self)
        if parent is not None:
            parent.append(ret)
        return ret

    def findmeld(self, name, default=None):
        """
        Searches this element and all children for any with a meld:id
        attribute with value equal to the name parameter. Returns
        default (None if not supplied) if the node account be found.
        """
        ret = self.xpath(
            "descendant-or-self::*[@meld:id='{}']".format(name),
            namespaces={"meld": NS}
        )
        return ret[0] if ret else default

    def findmelds(self):
        """
        Returns an iterable of all elements (this one or children) with a
        meld:id attribute (of any value).
        """
        return self.xpath(
            "descendant-or-self::*[@meld:id]", namespaces={"meld": NS}
        )

    def meldid(self):
        """
        Returns the value of the meld:id attribute of this element, or None
        if this element does not have a meld:id attribute.
        """
        return self.get(etree.QName(NS, "id").text)

    def repeat(self, iterable, childname=None):
        """
        Given an iterable, repeat the target element the same number of times
        as the length of the iterable. Returns an iterable of (new_element,
        iterable_data_item) pairs, from which you can mutate new_element as
        desired.

        The target element is by default this element, but if a meld:id is pass
        in as childname then this element will be found and used instead.
        """
        thing = self.findmeld(childname) if childname else self
        tail = thing.tail
        thing.tail = None
        prev_thing = None
        for data in iterable:
            next_thing = thing.clone()
            prev_thing = thing
            yield thing, data
            thing.addnext(next_thing)
            thing = next_thing
        if tail:
            if prev_thing is not None:
                prev_thing.tail = tail
            elif thing.getprevious() is not None:
                prev = thing.getprevious()
                prev.tail = (prev.tail or "") + tail
            elif thing.getparent() is not None:
                parent = thing.getparent()
                if parent.text:
                    parent.text += tail
                else:
                    parent.text = tail
        thing.getparent().remove(thing)

    def replace_child(self, old_element, new_element):
        """
        Looks for this old_element as a direct child of this element, removes
        it and replaces it in the same position with new_element. This
        is lxml's Element.replace()
        """
        super(Element, self).replace(old_element, new_element)

    def replace(self, text, structure=False):
        """
        Replace the element with argument given.

        If the argument is text and structure is False (the default), argument
        is treated as a plain-text string (and is escaped if required).

        If the argument is text and structure is True, the argument is treated
        as text containing some XML elements and inserted as part of the
        document. The text needs to be parseable as XML.

        If the argument is an lxml Element node it is used as the replacement.

        If the argument is a list or tuple it is expected to be a list of
        lxml Element nodes which will all be used as the replacement.

        If the element had no parent to update this call does nothing and
        returns None.
        """
        parent = self.getparent()
        if parent is None:
            return None

        idx = self.parentindex()
        if isinstance(text, (list, tuple)):
            for node in text:
                parent.insert(self.parentindex(), node)
            if self.tail:
                prev = self.getprevious()
                prev.tail = (prev.tail or "") + self.tail
            parent.remove(self)
        elif isinstance(text, etree._Element):
            if self.tail:
                text.tail = (text.tail or "") + self.tail
            parent.replace_child(self, text)
        elif structure:
            xml = etree.XML("<dispose>{}</dispose>".format(text))
            self.replace(list(xml) or xml.text)
        else:
            if self.tail:
                text += self.tail
            prev = self.getprevious()
            if prev is not None:
                prev.tail = (prev.tail or '') + text
            else:
                if parent.text:
                    parent.text += text
                else:
                    parent.text = text
            parent.remove(self)

        return idx

    def content(self, text, structure=False):
        """
        Sets the content of this element. It removes all of the text and child
        elements before doing so. You can pass in text, an lxml element or list
        of lxml elements to use as the new contents. If you pass in text and
        set structure to true then the text will be treated as a fragment of
        XML, parsed and inserted. Returns nothing.
        """
        if isinstance(text, (list, tuple)):
            self.text = None
            self[:] = list(text)
        elif isinstance(text, etree._Element):
            self.text = None
            self[:] = [text]
        elif structure:
            xml = etree.XML("<dispose>{}</dispose>".format(text))
            self.content(list(xml) or xml.text)
        else:
            self[:] = []
            self.text = text

    def attributes(self, **kwargs):
        """
        Attributes are set on the node using the argument names given.
        Existing attributes with the same name are overwritten. Returns
        nothing.
        """
        for k, v in kwargs.items():
            self.set(k, v)

    def fillmelds(self, **kwargs):
        """
        For each kwarg find the element with the meld:id with that argument
        name and set the content of the element to the value of the argument.
        Anything that can be passed to content() can be used as an argument
        value.

        Any arguments with names that don't correspond meld:ids in the
        document are returned as a list of argument names.
        """
        missing = set()
        for k, v in kwargs.items():
            ele = self.findmeld(k)
            if ele is not None:
                ele.content(v)
            else:
                missing.add(k)
        return list(missing)

    def __mod__(self, **kwargs):
        """
        Alias for fillmelds.
        """
        self.fillmelds(**kwargs)

    def parentindex(self):
        """
        Gives the array index of this node on it's parent. Returns None
        if this element has no parent.
        """
        parent = self.getparent()
        return parent.index(self) if parent is not None else None

    def deparent(self):
        """
        Removes this element from it's parent (ie. it removes it from the
        document). If this element is already unparented it silently does
        nothing. Returns the old index.
        """
        idx = self.parentindex()
        parent = self.getparent()
        if parent is not None:
            if self.tail:
                parent.text = (parent.text or "") + self.tail
            parent.remove(self)
        return idx

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

    def write_xml(self, file, encoding=None, doctype=None, fragment=False,
                  declaration=True, pipeline=False, _kwargs={"method": "xml"},
                  _doc=None):
        """
        Writes this document as XML to a file (filename or file-like object).
        The document will use the encoding and doctype specified. Doctype
        can be a string or tuple, and none is emitted if set to None (the
        default). An XML declaration is emitted by default but can be omitted
        if declaration is set to False.  If fragment is true then no doctype
        or XML declaration is emitted regardless of their values. By default
        all meld:ids are stripped from the serialised output, but if pipeline
        is set to true then they are serialised.
        """
        kwargs = {k: v for k, v in _kwargs.items()}
        kwargs.update(xml_declaration=declaration, encoding=encoding)
        if doctype:
            if isinstance(doctype, (tuple, list)):
                doctype = '<!DOCTYPE {} PUBLIC "{}" "{}">'.format(*doctype)
            kwargs.update(doctype=doctype)
        if fragment:
            kwargs.update(doctype=None, xml_declaration=False)

        if _doc is not None:
            doc = _doc
        elif pipeline:
            doc = self
        else:
            doc = self._clone_without_own_ns()

        ret = etree.tostring(doc, **kwargs)
        if file:
            # ElementTree.write() doesn't support doctype
            try:
                file.write(ret)
            except AttributeError:
                with open(file, "wb") as fh:
                    fh.write(ret)
            return None
        else:
            return ret

    def write_xhtml(self, file, encoding=None, doctype=doctypes.xhtml,
                    fragment=False, declaration=False, pipeline=False):
        """
        Writes this document as XHTML to a file (filename or file-like object).
        The document will use the encoding and doctype specified. Doctype
        can be a string or tuple. It defaults to XHTML 1.0 Transitional. An XML
        declaration is not emitted by default but can be if declaration is set
        to true.  If fragment is true then no doctype or XML declaration is
        emitted regardless of their values. By default all meld:ids are
        stripped from the serialised output, but if pipeline is set to true
        then they are serialised.
        """

        # libxml2/lxml is seriously finicky about XHTML and does it based on
        # sniffing the doctype, apparently at parse time. Furthermore
        # _cleanup_namespacesStart is enough to break the magic. Start by
        # serialising as XML with an XHTML doctype and then re-parsing to get
        # the magic before emitting with the correct options.
        intermediate = self.write_xml(
            None, encoding=encoding, doctype=doctypes.xhtml,
            fragment=False, declaration=True, pipeline=pipeline
        )
        intermediate = etree.fromstring(intermediate)
        return self.write_xml(
            file, encoding=encoding, doctype=doctype, pipeline=True,
            declaration=declaration, fragment=fragment, _doc=intermediate
        )

    def write_html(self, file, encoding=None, doctype=doctypes.html,
                   fragment=False):
        """
        Writes this document as HTML to a file (filename or file-like object).
        The document will use the encoding and doctype specified. Doctype
        can be a string or tuple. It defaults to HTML 4.01 Transitional.
        If fragment is true then no doctype is emitted regardless of the
        doctype parameter value.
        """
        return self.write_xml(
            file, encoding=encoding, doctype=doctype, fragment=fragment,
            _kwargs={"method": "html"}
        )

    def write_xmlstring(self, *args, **kwargs):
        """
        Returns the document as a bytes string, formatted as XML. See
        write_xml for the options you can specify to this call.
        """
        return self.write_xml(None, *args, **kwargs)

    def write_xhtmlstring(self, *args, **kwargs):
        """
        Returns the document as a bytes string, formatted as XHTML. See
        write_xhtml for the options you can specify to this call.
        """
        return self.write_xhtml(None, *args, **kwargs)

    def write_htmlstring(self, *args, **kwargs):
        """
        Returns the document as a bytes string, formatted as HTML. See
        write_html for the options you can specify to this call.
        """
        return self.write_html(None, *args, **kwargs)


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


def parse_xml(xml):
    """
    Parses XML from a file-like object. Returns the root element.
    """
    t = etree.parse(xml, _parser()).getroot()
    _check_tree(t)
    return t


def parse_xmlstring(xml):
    """
    Parses a str or unicode of XML. Returns the root element.
    """
    t = etree.fromstring(xml, _parser())
    _check_tree(t)
    return t


def _fix_html(tree):
    # The HTML parser deliberately doesn't parse namespaces, so this phase
    # moves the meld:id attributes into the correct namespace.
    qn = etree.QName(NS, "id").text
    for ele in tree.iter():
        if "meld:id" in ele.attrib:
            ele.set(qn, ele.attrib.pop("meld:id"))


def parse_html(html):
    """
    Parses HTML from a file-like object. Returns the root element.
    """
    t = etree.parse(html, _parser(etree.HTMLParser)).getroot()
    _fix_html(t)
    _check_tree(t)
    return t


def parse_htmlstring(html):
    """
    Parses a str or unicode of HTML. Returns the root element.
    """
    t = etree.fromstring(html, _parser(etree.HTMLParser))
    _fix_html(t)
    _check_tree(t)
    return t

# lxmlmeld

A mostly-compatible  implementation of Meld3
(https://github.com/supervisor/meld3) using lxml (http://lxml.de/) as the
parsing and serialisation engine.

I previously forked Meld3 and made it use lxml, but the code wasn't elegant
as it didn't use much of lxml's additional features. This version is a
from-the-ground-up rewrite based on the Meld3 documentation and test suite.

## Key Differences

 - `fillmeldhtmlform()` is not implemented (it's rather too magic)
 - `findwithattrib` is not implemented (as unclear how it interacts with
   namespaces; use lxml's finders or xpath)
 - replace() follows the meld3 syntax; the lxml call of the same name is
   renamed `replace_child()`
 - The property `parent` doesn't exist; use `getparent()`
 - You can pass lxml Elements or lists of Elements to `replace()`,
   `content()` and `fillmelds()`
 - When using `structure=True` the content must be broadly parsable as XML
 - `repeat` inserts adjacent to the original node, not at the end of the
   parent
 - doctypes to the `write_*` functions can be plain strings

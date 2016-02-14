# lxmlmeld

A mostly-compatible  implementation of Meld3
(https://github.com/supervisor/meld3) using lxml (http://lxml.de/) as the
parsing and serialisation engine.

I previously forked Meld3 and made it use lxml, but the code wasn't elegant
as it didn't use much of lxml's additional features. This version is a
from-the-ground-up rewrite based on the Meld3 documentation and test suite.
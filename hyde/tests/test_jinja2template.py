# -*- coding: utf-8 -*-
"""
Use nose
`$ pip install nose`
`$ nosetests`

Code borrowed from rwbench.py from the jinja2 examples
"""
from datetime import datetime
from hyde.ext.templates.jinja import Jinja2Template
from hyde.fs import File, Folder
from hyde.model import Config

import jinja2
from jinja2.utils import generate_lorem_ipsum
from random import choice, randrange
from util import assert_html_equals
import yaml

ROOT = File(__file__).parent
JINJA2 = ROOT.child_folder('templates/jinja2')

class Article(object):

    def __init__(self, id):
        self.id = id
        self.href = '/article/%d' % self.id
        self.title = generate_lorem_ipsum(1, False, 5, 10)
        self.user = choice(users)
        self.body = generate_lorem_ipsum()
        self.pub_date = datetime.utcfromtimestamp(randrange(10 ** 9, 2 * 10 ** 9))
        self.published = True

def dateformat(x):
    return x.strftime('%Y-%m-%d')

class User(object):

    def __init__(self, username):
        self.href = '/user/%s' % username
        self.username = username


users = map(User, [u'John Doe', u'Jane Doe', u'Peter Somewhat'])
articles = map(Article, range(20))
navigation = [
    ('index',           'Index'),
    ('about',           'About'),
    ('foo?bar=1',       'Foo with Bar'),
    ('foo?bar=2&s=x',   'Foo with X'),
    ('blah',            'Blub Blah'),
    ('hehe',            'Haha'),
] * 5

context = dict(users=users, articles=articles, page_navigation=navigation)

def test_render():
    """
    Uses pyquery to test the html structure for validity
    """
    t = Jinja2Template(JINJA2.path)
    t.configure(None)
    t.env.filters['dateformat'] = dateformat
    source = File(JINJA2.child('index.html')).read_all()

    html = t.render(source, context)
    from pyquery import PyQuery
    actual = PyQuery(html)
    assert actual(".navigation li").length == 30
    assert actual("div.article").length == 20
    assert actual("div.article h2").length == 20
    assert actual("div.article h2 a").length == 20
    assert actual("div.article p.meta").length == 20
    assert actual("div.article div.text").length == 20

def test_depends():
    t = Jinja2Template(JINJA2.path)
    t.configure(None)
    source = File(JINJA2.child('index.html')).read_all()
    deps = list(t.get_dependencies(source))

    assert len(deps) == 2

    assert 'helpers.html' in deps
    assert 'layout.html' in deps

def test_depends_multi_level():
    t = Jinja2Template(JINJA2.path)
    t.configure(None)

    source = "{% extends 'index.html' %}"
    deps = list(t.get_dependencies(source))

    assert len(deps) == 3

    assert 'helpers.html' in deps
    assert 'layout.html' in deps
    assert 'index.html' in deps


def test_typogrify():
    source = """
    {%filter typogrify%}
    One & two
    {%endfilter%}
    """
    t = Jinja2Template(JINJA2.path)
    t.configure(None)
    html = t.render(source, {}).strip()
    assert html == u'One <span class="amp">&amp;</span>&nbsp;two'

def test_markdown():
    source = """
    {%markdown%}
    ### Heading 3
    {%endmarkdown%}
    """
    t = Jinja2Template(JINJA2.path)
    t.configure(None)
    html = t.render(source, {}).strip()
    assert html == u'<h3>Heading 3</h3>'

def test_markdown_with_extensions():
    source = """
    {%markdown%}
    ### Heading 3

    {%endmarkdown%}
    """
    t = Jinja2Template(JINJA2.path)
    c = Config(JINJA2.path, dict(markdown=dict(extensions=['headerid'])))
    t.configure(c)
    html = t.render(source, {}).strip()
    assert html == u'<h3 id="heading_3">Heading 3</h3>'

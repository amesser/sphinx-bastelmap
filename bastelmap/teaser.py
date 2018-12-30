# bastelmap.de's sphinx extension to support blog style teasers
# Copyright (C) 2017 Andreas Messer <andi@bastelmap.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives import images
from sphinx.transforms import SphinxTransform, SphinxContentsFilter
from sphinx.util.osutil import ensuredir, copyfile
from sphinx.util.console import brown
from sphinx.util import status_iterator
from sphinx.environment.collectors import EnvironmentCollector
from sphinx import addnodes
from sphinx.directives import TocTree

import posixpath
import os.path
import re

class teaser_list(nodes.enumerated_list):
    pass

class Teaser(TocTree):
    has_content = True

    def run(self):
        ret = super(Teaser,self).run()

        wrapper_node = ret[-1]

        wrapper_node['classes'] = ['teaser-wrapper']

        teaser_list_node = teaser_list()
        teaser_list_node.__dict__ = wrapper_node[0].__dict__

        wrapper_node[0].replace_self(teaser_list_node)

        return ret

class TeaserTextCollector(EnvironmentCollector):
    def clear_doc(self, app, env, docname):
        app.env.teasers.pop(docname, None)

    def process_doc(self, app, doctree):
        docname = app.env.docname

        # only document names starting with a date are
        # regarded as an article
        basename = os.path.basename(docname)
        m = re.match(r'([0-9]+-[0-9]+-[0-9]+)-', basename)

        if not m:
            return

        date = m.group(0)

        title_node = None
        text_node  = None
        for x in doctree.traverse():
            if isinstance(x, nodes.title):
                title_node = title_node or x
            elif isinstance(x, nodes.paragraph):
                text_node = x
                break

        visitor = SphinxContentsFilter(doctree)
        title_node.walkabout(visitor)

        article_title = visitor.get_entry_text()

        title = nodes.paragraph('', *article_title, classes=['teaser-title'])

        ref  = nodes.reference('', '', internal=True, refuri=docname)
        para = addnodes.compact_paragraph('','', ref)
        item = nodes.list_item('', para)

        item['article_date'] = date

        ref += title
        if text_node is not None:
            ref += text_node
        ref += nodes.paragraph('', 'Weiterlesen...', classes=['teaser-readmore'])

        teasers = app.env.teasers
        teasers[docname] = item

class TeaserListTransform(SphinxTransform):
    default_priority = 100

    def apply(self):
        for node in self.document.traverse(teaser_list):
            list_node = nodes.enumerated_list('')
            node.replace_self(list_node)

            teasers = self.app.env.teasers

            entries = ((title,ref) for title,ref in node['entries'] if ref in teasers)

            for title, ref in reversed(sorted(entries, key = lambda x : os.path.basename(x[1]))):
                list_item = self.app.env.teasers[ref]
                list_node += list_item

                ref = list_item[0][0]
                ref['refuri'] = self.app.builder.get_relative_uri(self.env.docname, ref['refuri'])

                if len(list_node) >= 5:
                    break
                                                                                            
def init_teasers(app):
    if not getattr(app.env, 'teasers', None):
        app.env.teasers = {}

def setup(app):
    app.add_env_collector(TeaserTextCollector)
    app.add_directive('teaser', Teaser)
    app.add_post_transform(TeaserListTransform)
    app.connect('builder-inited', init_teasers)



      

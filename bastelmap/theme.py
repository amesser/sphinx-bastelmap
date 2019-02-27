# bastelmap.de's sphinx theme based on alabaster original theme
# Copyright (C) 2019 Andreas Messer <andi@bastelmap.de>
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

from sphinx.transforms import SphinxTransform
from sphinx.writers.html import HTMLTranslator
import docutils.transforms.frontmatter
from docutils import nodes
import os
import re

class DumpTreeTransform(SphinxTransform):
    default_priority = 1000

    def apply(self):
        docname  = self.env.docname
        metadata = self.env.metadata[docname]

        authors  = metadata.get('Authors', None)
        date     = metadata.get('Date', None)

        # only document names from sphinx.writers.html import HTMLWriter, HTMLTranslatorstarting with a date are
        # regarded as an articfrom sphinx.writers.html import HTMLWriter, HTMLTranslatorle
        if date is None:
            basename = os.path.basename(docname)
            m = re.match(r'([0-9]+-[0-9]+-[0-9]+)-', basename)

            if not m and authors is None:
                return;

            date = m.group(0)

        # check if at least author or date meta information is available
        if all([date is None, authors is None]):
            return

        title_node = self.document.next_node(nodes.title)

        title_node = self.document.next_node(nodes.title)
        parent = title_node.parent

        info = nodes.docinfo()
        parent.insert(parent.index(title_node)+1, info)

        if authors is not None:
            authors_node = nodes.authors()
            info += authors_node

            author_node = nodes.author(text=authors)
            authors_node += author_node

        if date is not None:
            date_node = nodes.date(text=date)
            info += date_node



            #print(dir(node))
        #    print(type(node))

class FixedHTMLTranslator(HTMLTranslator):
    def depart_docinfo(self, node):
        '''Fix broken docutils node'''
        self.body.append('</tbody>\n</table>\n')
        self.in_docinfo = False
        start = self.context.pop()
        self.docinfo = self.body[start:]
        del self.body[start:]

class DocTitle(docutils.transforms.frontmatter.TitlePromoter):
    ''' Renable promotion of first document section to document itself 
        
        Must use a very high priority to not confuse remaining sphinx stuff'''

    default_priority = 1000
    def apply(self):
        self.promote_title(self.document)

def setup(app):
    # register theme with sphinx
    app.add_html_theme('bastelmap', os.path.abspath(os.path.dirname(__file__) + os.sep + 'theme'))
    #app.config.html_translator_class = 'sphinx_confluence.HTMLConfluenceTranslator'
    # only for newer sphinx versions
    #app.set_translator('html', FixedHTMLTranslator)

    app.add_post_transform(DocTitle)


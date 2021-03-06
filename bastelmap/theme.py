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

from sphinx.writers.html import HTMLTranslator
import docutils.transforms.frontmatter
import datetime
from docutils import nodes
import os
import re

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

def env_updated_handler(app, env):
    date_formats = (
        '%d.%m.%Y',
        '%Y-%m-%d',
    )

    for doc, meta in env.metadata.items():
        if 'Date' in meta:
            if isinstance(meta['Date'], str):
                for f in date_formats:
                    try:
                        meta['Date'] = datetime.datetime.strptime(meta['Date'],f)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError(u'Failed to parse date {!r}'.format(meta['Date']))

def setup(app):
    # register theme with sphinx
    app.add_html_theme('bastelmap', os.path.abspath(os.path.dirname(__file__) + os.sep + 'theme'))

    # setup some transformations
    app.add_post_transform(DocTitle)
    app.connect('env-updated', env_updated_handler)

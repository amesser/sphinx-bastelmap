# bastelmap.de's sphinx extension to support lightbx2 slideshows for images/figures
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
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives import images
from sphinx.transforms import SphinxTransform
from sphinx.util.osutil import ensuredir, copyfile
from sphinx.util.console import brown
from sphinx.util import status_iterator
import posixpath
import os.path

class lightbox2_reference(nodes.reference):
    pass

class LightBox2Transform(SphinxTransform):
    default_priority = 2000

    def apply(self):
        for node in self.document.traverse(nodes.image):
            if 'group' not in node:
                continue

            reference_node = lightbox2_reference()
            reference_node['group']  = node['group']

            node.replace_self(reference_node)
            reference_node.append(node)


def visit_lightbox2_reference_html(self,node):
    # unfortunately sphinx changes the image url's when the 'ImageCollector' 
    # is running. As a result we can not extract the correct uri when the Transform
    # above is applied because the collector runs at some time later and it is not
    # ensured in which order the collectors are run
    image_node = node[0]
    uri = image_node['uri']

    # rewrite the URI if the environment knows about it
    if uri in self.builder.images:
       uri = posixpath.join(self.builder.imgpath, self.builder.images[uri])

    # type: (nodes.Node) -> None
    atts = {'class': 'reference'}
    
    atts['class'] += ' internal'
    atts['href'] = uri
    atts['class'] += ' image-reference'

    if 'reftitle' in node: 
        atts['title'] = node['reftitle']
    
    if 'group' in node:
        atts['data-lightbox'] = node['group']
    else:
        atts['data-lightbox'] = 'uri' 

    self.body.append(self.starttag(node, 'a', '', **atts)) 
    

def depart_lightbox2_reference_html(self,node):
    self.depart_reference(node)

STATIC_FILES = (
  'lightbox2/css/lightbox.css',
  'lightbox2/js/jquery-1.11.0.min.js',
  'lightbox2/js/lightbox.min.js',
  'jquery-noconflict.js',
  'lightbox2/js/lightbox.min.map',
  'lightbox2/img/close.png',
  'lightbox2/img/next.png',
  'lightbox2/img/prev.png',
  'lightbox2/img/loading.gif',
)

def install_static_files(app, env):
  base_dir = os.path.dirname(__file__)
  files_to_copy = STATIC_FILES

  dest_path = os.path.join(app.outdir, '_static')

  for x in status_iterator(files_to_copy,
                           'Copying static files for lightbox2...',
                           brown, len(files_to_copy)):


      source_file_path = os.path.join(base_dir,x)
      dest_file_path = os.path.join(dest_path, x)

      if not os.path.exists(os.path.dirname(dest_file_path)):
          ensuredir(os.path.dirname(dest_file_path))

      copyfile(source_file_path, dest_file_path)
      
      if dest_file_path.endswith('.js'):
          app.add_javascript(x)
      elif dest_file_path.endswith('.css'):
          app.add_stylesheet(x)

def setup(app):
    # add a group option to image/figure directives which is used to enable the
    # lightbox feature itself and to group the images

    images.Image.option_spec['group'] = directives.unchanged_required
    images.Figure.option_spec['group'] = directives.unchanged_required

    # Add transform which inserts the lightbox reference nodes 
    app.add_transform(LightBox2Transform)

    # define new node which implements the lightbox reference
    app.add_node(lightbox2_reference,
      html=(visit_lightbox2_reference_html, depart_lightbox2_reference_html))

    # setup install handler
    app.connect('env-updated', install_static_files)


      

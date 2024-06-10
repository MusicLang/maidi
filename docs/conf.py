# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'M(AI)DI'
copyright = '2024, GARDIN Florian, ZATAR Mehdi'
author = 'GARDIN Florian, ZATAR Mehdi'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx_rtd_theme',
              'sphinx.ext.duration',
              'sphinx.ext.doctest',
              'sphinx.ext.autodoc',
              'sphinx.ext.napoleon',
              'sphinx.ext.autosummary',
              'sphinx_gallery.gen_gallery',
              'numpydoc'
              ]


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = "furo"
html_static_path = ['_static']


from sphinx.ext.autosummary import Autosummary
from sphinx.ext.autosummary import get_documenter
from docutils.parsers.rst import directives
from sphinx.util.inspect import safe_getattr
class AutoAutoSummary(Autosummary):

    option_spec = {
        'methods': directives.unchanged,
        'attributes': directives.unchanged
    }

    required_arguments = 1

    @staticmethod
    def get_members(obj, typ, include_public=None):
        if not include_public:
            include_public = []
        items = []
        for name in dir(obj):
            try:
                documenter = get_documenter(safe_getattr(obj, name), obj)
            except AttributeError:
                continue
            if documenter.objtype == typ:
                items.append(name)
        public = [x for x in items if x in include_public or not x.startswith('_')]
        return public, items

    def run(self):
        clazz = str(self.arguments[0])
        try:
            (module_name, class_name) = clazz.rsplit('.', 1)
            m = __import__(module_name, globals(), locals(), [class_name])
            c = getattr(m, class_name)
            if 'methods' in self.options:
                _, methods = self.get_members(c, 'method', ['__init__'])

                self.content = ["~%s.%s" % (clazz, method) for method in methods if not method.startswith('_')]
            if 'attributes' in self.options:
                _, attribs = self.get_members(c, 'attribute')
                self.content = ["~%s.%s" % (clazz, attrib) for attrib in attribs if not attrib.startswith('_')]
        finally:
            return super(AutoAutoSummary, self).run()

autosummary_generate = True
numpydoc_show_class_members = False  # If you don't want to show class members by default
numpydoc_class_members_toctree = False  # If you don't want to create separate toctrees for class members

def skip_undocumented_members(app, what, name, obj, skip, options):
    # Skip members that have no docstring
    if not obj.__doc__:
        return True
    return skip



# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'inherited-members': True,
    'show-inheritance': False,
    'special-members': '__init__',  # include __init__ method
    'exclude-members': '__weakref__'
}
# Add napoleon settings if you use numpy or google style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True



def setup(app):
    app.add_css_file('css/custom_css.css')
    app.add_directive('autoautosummary', AutoAutoSummary)
    app.connect('autodoc-skip-member', skip_undocumented_members)
    # If you are using recommonmark for Markdown
    app.add_config_value('recommonmark_config', {
        'auto_toc_tree_section': 'Contents',
    }, True)

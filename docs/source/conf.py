"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Project information ---------------------------------------------------

project = 'syndantic'
copyright = '2024, Thomas Reiter'  # pylint: disable=redefined-builtin
author = 'Thomas Reiter'
release = '0.1.3'

# -- General configuration -------------------------------------------------

extensions = [
    'autoapi.extension',
    'sphinx_copybutton',
    'sphinx_tabs.tabs',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
    'sphinx_tabs.tabs',
    'sphinx-prompt',
    'sphinx_toolbox',
    'sphinx_toolbox.decorators',
    'sphinx_toolbox.installation',
    'sphinx_toolbox.sidebar_links',
]

templates_path = ['_templates']
exclude_patterns = []

intersphinx_mapping = {
    'python': ('https://docs.python.org/3.12/', None),
    'lark': ('https://lark-parser.readthedocs.io/en/stable/', None),
    'pydantic': ('https://docs.pydantic.dev/latest/objects.inv', None),
}

github_username = 'tom65536'
github_repository = 'syndantic'

# -- Configure autoapi -----------------------------------------------------
autoapi_dirs = ['../../src']

# -- Configure Napoleon -- -------------------------------------------------
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True

# -- Options for HTML output -----------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

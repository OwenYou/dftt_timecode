# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DFTT Timecode'
copyright = '2025, You Ziyuan'
author = 'You Ziyuan'
release = '0.0.15a1'

# HTML title
html_title = 'DFTT Timecode'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Master document
master_doc = 'index'
root_doc = 'index'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

# PyData theme specific options
html_theme_options = {
    "github_url": "https://github.com/OwenYou/dftt_timecode",
    "use_edit_page_button": True,
    "show_toc_level": 2,
    "navbar_align": "left",
    "navigation_with_keys": False,
    "show_nav_level": 1,  # Show from top level
    "navigation_depth": 4,
    "collapse_navigation": True,
    "sidebar_includehidden": True,  # Include hidden toctree items in sidebar
    "logo": {
        "text": "DFTT Timecode",
    },
    "navbar_end": ["navbar-icon-links"],
    "primary_sidebar_end": ["sidebar-ethical-ads"],
}

# Enable the global table of contents in sidebar
html_sidebars = {
    "**": ["search-field", "sidebar-nav-bs"]
}

html_context = {
    "github_user": "OwenYou",
    "github_repo": "dftt_timecode",
    "github_version": "main",
    "doc_path": "docs",
}

# -- Options for autodoc ----------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# -- Options for autosummary ------------------------------------------------
autosummary_generate = True

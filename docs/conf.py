# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import tomllib

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.
sys.path.insert(0, os.path.abspath('..'))

# -- Read project metadata from pyproject.toml -------------------------------
# Get the path to pyproject.toml (one level up from docs/)
docs_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(docs_dir)
pyproject_path = os.path.join(project_root, 'pyproject.toml')

with open(pyproject_path, 'rb') as f:
    pyproject_data = tomllib.load(f)

project_info = pyproject_data['project']

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'DFTT Timecode'
copyright = '2025, You Ziyuan'
author = ', '.join(a['name'] for a in project_info['authors'])
release = project_info['version']
version = release  # Short version

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
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Internationalization (i18n) configuration -------------------------------
# https://www.sphinx-doc.org/en/master/usage/advanced/intl.html

# Default language (English)
language = 'en'

# Directory path for message catalogs
locale_dirs = ['locale/']

# Generate .pot files with message catalogs for each document
gettext_compact = False

# Additional languages for documentation
# This is used by the language switcher
gettext_additional_targets = ['index']

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
    "navigation_depth": 4,
    "collapse_navigation": False,  # Keep navigation expanded
    "logo": {
        "text": "DFTT Timecode",
    },
    "navbar_end": ["navbar-icon-links", "language-switcher"],
    "primary_sidebar_end": [],  # Remove primary sidebar content
    "show_nav_level": 0,  # Hide navigation levels
    "switcher": {
        "json_url": "https://owenyou.github.io/dftt_timecode/_static/switcher.json",
        "version_match": os.environ.get("READTHEDOCS_LANGUAGE", language),
    },
}

# Disable the left sidebar navigation
html_sidebars = {
    "**": []
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

# Avoid documenting imports as duplicates
autodoc_typehints = 'description'
autodoc_class_signature = 'separated'

# Control which module path to use for imported members
# This prevents duplicate documentation when a class is imported into __init__.py
add_module_names = False

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
# Disable autosummary generation to avoid duplicate documentation
autosummary_generate = False

# -- Options for MyST-Parser ------------------------------------------------
# Enable markdown files to be parsed by Sphinx
myst_enable_extensions = [
    "colon_fence",  # ::: syntax for directives
    "deflist",      # Definition lists
    "html_image",   # HTML image syntax
]
myst_heading_anchors = 3  # Auto-generate anchors for headings up to level 3

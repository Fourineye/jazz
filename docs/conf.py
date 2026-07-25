import os
import sys

# Add root directory to sys.path so autodoc can find the jazz package
sys.path.insert(0, os.path.abspath(".."))

import jazz

# Project information
project = "Jazz Engine"
copyright = "2026, Paul Smith"
author = "Paul Smith"
release = jazz.__version__
version = jazz.__version__

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "myst_parser",
]

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
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

# Autodoc settings
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Templates & Patterns
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML Output Options
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_title = f"Jazz Engine v{version} Documentation"

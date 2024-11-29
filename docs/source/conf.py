# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup -------------------------------------------------------------- # If extensions (or modules to document with autodoc) are in another directory, # add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here. #
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ecommerce project'
copyright = '2024, IhabNael'
author = 'IhabNael'

# The full version, including alpha/beta/rc tags
release = '00.00.01'
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',  # For Google/NumPy style docstrings
    'sphinx_rtd_theme'
]


templates_path = ['_templates']
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files. # This pattern also affects html_static_path and html_extra_path. 
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes. #
html_theme = 'sphinx_rtd_theme'
# Add any paths that contain custom static files (such as style sheets) here, # relative to this directory. They are copied after the builtin static files, # so a file named "default.css" will overwrite the builtin "default.css". 
html_static_path = ['_static']
Documentation Guide
===================

The documentation is dynamically generated using Sphinx and is publish using Readthedoc
Documentation pages are written in __reStructuredText__ RST

The main page is `index.rst`, this is the landing page and this is where the menu is defined in the `toctree` section.
All .rst files listed under toctree are expected to be present in the same directory.

Dynamic generation of the documentation
---------------------------------------
The documentation generation is triggered by the python script `conf.py`.
It's possible to add our own logic to this file.
For example, I added a quick example to generate the file `jet.rst` dynamically based on a Jinja2 template.


Theme customization
-------------------
The main theme used is provided by readthedoc but can be customized using a custom CSS file
The project has been configured to load the file my_theme.css in the directory `docs/_static/css/my_theme.css`

Resources
---------

RST Table generator
http://www.tablesgenerator.com/text_tables
http://stackoverflow.com/questions/11347505/what-are-some-approaches-to-outputting-a-python-data-structure-to-restructuredte


RST documentation
http://www.sphinx-doc.org/en/stable/rest.html

How to configure sphinx to use custom CSS file
http://stackoverflow.com/questions/23211695/modifying-sphinx-theme-read-the-docs

To run: 

> python qtsimiam.py

or

> ./qtsimiampy

Load your own supervisors and controllers into the development folders following the supervisor and controller templates.

To compile the documentation, you will need Sphinx. Get it at http://sphinx-doc.org/install.html.
After that, go into the ./docs folder and type:
 
> make html
 
If you don't have make, the following command should work as well:

> sphinx-build -b html . _build

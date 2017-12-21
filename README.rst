sphinx-selenium-screenshots
===========================
Pretty much what it says on the box - adds a Sphinx directive, to take screen shots of HTML pages from Selenium

**Caveat**: You need to have `PhantomJS`_ installed for this to work, which means for now this won't work on 
readthedocs (unless we can convince them to install it when building documentation).
You can get around that by building the images locally, and checking them into wherever your documentation is.

.. _PhantomJS: http://phantomjs.org/

How to use
----------

1. Install ``sphinx`` and ``sphinx-selenium-screenshots``
2. Add ``selenium_screenshots.screener`` to the extensions in your configuration file::

      extensions = [
      # ... ,
      'selenium_screenshots.screener',
      # ... ,
      ]

3. Add the configuration parameters::

      screenshots_server_path = 'http://127.0.0.1:8080'
      screenshots_read_path = '/_static/screenshots'
      screenshots_save_path = os.path.abspath(os.path.join('.',screenshots_read_path[1:]))

4. Insert screenshots into your documentation with the ``screenshot`` directive::

      .. screenshot:: 
         :server_path: /path/to/a/file.html
         :alt: Here is how your page looks.

Advanced usage of the ``screenshot`` directive
----------------------------------------------

The ``screenshot`` directive is a subclass of the built-in Image directive, so any parameters that work on that
also work on ``screenshot``.

Basic usage
+++++++++++

This is the basic directive::

    .. screenshot::
       :server_path: /path/to/a/file.html

With a custom filename
......................

By default, ``screenshot`` gives each page load a generated filename, however if you want to
reuse the generated file you can add a filename as the first (and only) argument like so::

    .. screenshot:: my_file.jpg
       :server_path: /path/to/a/file.html

And reuse it by loading it from ``screenshots_read_path``  ::

    ..image:: /_static/screenshots/my_file.jpg

Cropping
++++++++

... to a specific part of the page
..................................

Crop to a section by passing a pair of tuples in a list with opposite corners of the bounding box to the ``crop`` parameter::

  .. screenshot::
     :server_path: /path/to/a/file.html
     :crop: [(0,0),(100,100)]

... to a particular element
...........................

You can pass any valid css selector to the ``crop_element`` parameter to capture just a particular element::

  .. screenshot::
     :server_path: /path/to/a/file.html
     :alt: The login button
     :crop_element: a[href^=/login/]

By default a padding of 50px on all edges, this padding can be changed with ``crop_element_padding``.

This argument can be 1, 2 or 4 entries long, as a python array, where:

* 1 element sets the padding for all edges uniformly in pixels - eg. ``[60]`` sets all edges to 60px of padding
* 2 entries sets the padding for top and bottom, and left and right respectively - eg. ``[20, 40]`` sets the topp and bottom padding to 20px, and left and right to 40px.
* 4 entries sets the padding as top, right, bottom and left (i.e clockwise from the top) - eg. ``[10, 20, 30, 40]`` set the top padding to 10px, right to 20px, bottom to 30px and left to 40px

For example::

  .. screenshot::
     :server_path: /path/to/a/file.html
     :alt: The login button
     :crop_element: a[href^=/login/]
     :crop_element_padding: [50, 50]


Using sessions to show how pages react
++++++++++++++++++++++++++++++++++++++

How to login
............

To login quickly, you can use the ``login`` parameter. The screen shot will be taken *after* the user has logged in.
The ``login`` parameter takes a dictionary with 3 arguments:

* ``url`` - the url the login page is at
* ``username`` - the user name of the user to login as
* ``password`` - the password for the user -- **Note:** Do not use the password of an actual account, this is stored in plain text.

This works, as long as the login page has two form elements with the HTML form names ``username`` and ``password``::

  .. screenshot::
     :server_path: /path/to/a/file.html
     :login: {'url': '/login', "username": "vicky", "password": "Viewer"}

... then log back out after the screenshot
..........................................

Just pass the url of the logout page as the ``logout`` directive to log out after the screen shot is taken::

  .. screenshot::
     :server_path: /path/to/a/file.html
     :login: {'url': '/login', "username": "vicky", "password": "Viewer"}
     :logout: {'url': '/logout'}

Filling in forms to show how pages change
+++++++++++++++++++++++++++++++++++++++++

Use the ``form_data`` parameter to show the actions of filling in a form before taking a screenshot.
The ``form_data`` parameter takes an array of dictionaries that describe which fields in a form to fill in.
This works on all field types, including ``<input>``, ``<textarea>`` and ``<select>`` elements.

This example expects a form with ``name`` and ``address`` inputs available::

  .. screenshot::
     :server_path: /path/to/a/file.html
     :form_data: [
        {'name': 'John Citizen', 'address': '123 Fake St'},
     ]

Preventing a form from being submitted
......................................

Just add the ``__submit__`` key and set it to False, like so:

  .. screenshot::
     :server_path: /path/to/a/file.html
     :form_data: [
        {'name': 'John Citizen', 'address': '123 Fake St', '__submit__': False},
     ]

Now we can see what the page looks like before the form is submitted.

Submitting multiple forms
.........................

Adding multiple dictionaries in the list given as the ``form_data`` parameter will cause the browser
to attempt to pass each form and submit it. This is useful when showing transitions or end states for form wizards::

  .. screenshot::
     :server_path: /path/to/a/file.html
     :form_data: [
        {'name': 'John Citizen', 'address': '123 Fake St'},
        {'date_of_birth': '01/01/1970',},
        {'eye_colour': 'Blue'},
     ]
     
     
Recapturing the same page
+++++++++++++++++++++++++

The ``screenshot``directive just directly captures whats happening on the virtual browser screen,
so page loads aren't necessary when capturing different parts of the same page. This can speed up
the build time, as pages don't have to be reloaded and rerendered.

To prevent a page reloading, just leave off the ``server_path`` directive. This example submits the same forms as
above, but captures a screenshot when the first page loads and after submitting each successive form::

  .. screenshot::
     :server_path: /some/form/to/submit.html

  .. screenshot::
     :form_data: [
        {'name': 'John Citizen', 'address': '123 Fake St'},
     ]

  .. screenshot::
     :form_data: [
        {'date_of_birth': '01/01/1970',},
     ]

Highlighting page elements
++++++++++++++++++++++++++

There are two ways to highlight page elements, boxes and clickers which can be used in the same screenshot.

... with clickers
.................

A clicker is an icon that shows where a user would want to click on a regular interface.
The default (and currently only) style is a transparent yellow circle in the center of the HTML element.
It can be called with the ``clicker`` parameter which accepts a css selector and only hightlights the first matching element found::

  .. screenshot::
     :server_path: /some/page.html
     :clicker: #element_of_interest

... with boxes
..............

Alternatively, you can insert a hightlighting box to bring attention to an element of interest.
The default (and currently only) style is a red rectangle around the HTML element.
It can be called with the ``box`` parameter which accepts a css selector and only hightlights the first matching element found::

  .. screenshot::
     :server_path: /some/page.html
     :box: #element_of_interest

Using the content of the directive to run arbitrary python
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Everything after the parameters is interpreted as python code run by the screenshot directive, *before* the screenshot
is taken. This makes for a very powerful but also *very dangerous tool* for capturing screenshots.

Variables available in this scope are:

* ``browser`` the selenium browser at that point in time.

Delaying a screenshot while waiting for a page to load extra content
....................................................................

This is especially useful when there is additional javascript that is loaded that changes the user interface.
For example, CKEditor will update parts of the user interface after page load to insert its WYSIWYG editor.
An example of how to cause the delay is::

  .. screenshot:: 
     :server_path: /a/page/with/slow/javascript.html

     import time
     time.sleep(2)

Using selenium to click on an element to show a change in state
...............................................................

Do this by accessing the local browser element::

  .. screenshot::
     :server_path: /path/to/a/file.html

     browser.find_element_by_css_selector('a#some_button').click()


Gotchas
-------
All documents start with a fresh virtual browser, but tTo reduce running time, the selenium browser in the background
keeps sessions logged in (or out) when processing a document.
This can mean that if you need to access a page with an anonymous user, you need to make sure to ``logout`` in the previous screenshot.

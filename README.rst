=======
LAC2018
=======

This is a |nikola| based static website.

Refer to its |handbook| to see how it works and how to add new content as blog
posts or static pages.

   .. note::

    This website is now readonly and the below steps (especially the dynamic way
    of adding information from the calendar with the python script) are not
    valid anymore. The website can now only be changed by editing the rst files
    directly and re-rendering the html.


Currently, parts of the pages (*pages/event/** and *pages/schedule.rst*) are
generated from public ics calendars. Metadata from those calendar files is used
to populate the pages and to create a fahrplan.csv file (compatible to
|voctosched|).

To pull in the latest changes:

  .. code:: bash

    # requires icalendar
    ./calendar2schedule.py

To generate a valid fahrplan XML from fahrplan.csv (assumes, that the
|voctosched| repository is located at the same level as this repository) run
from the root of this repository:

  .. code:: bash

    ../voctosched/schedule.py -vvv -c lac2018.ini

The created *files/lac2018.xml* can be validated, using the official schema
validator of the voc (this assumes, that the |schedule| repository is located
at the same level as this repository):

  .. code:: bash

    ../schedule/validator/xsd/validate_schedule_xml.sh files/lac2018.xml

Build the website:

  .. code:: bash

    nikola build

To run the website locally:

  .. code:: bash

    nikola serve

To deploy the website to its webserver destination:

  .. code:: bash

    nikola deploy

| You need to have a valid ssh key on the remote host machine.
| Please make sure to add the latest deploy and push it to the repository:

  .. code:: bash

    git add state_data.json
    git commit -m "state_data.json: Deployed website."
    git push

.. |nikola| raw:: html

  <a href="https://getnikola.com/" target="_blank">Nikola</a>

.. |handbook| raw:: html

  <a href="https://getnikola.com/handbook.html" target="_blank">handbook</a>

.. |voctosched| raw:: html

  <a href="https://github.com/voc/voctosched" target="_blank">voctosched</a>

.. |schedule| raw:: html

  <a href="https://github.com/voc/schedule" target="_blank">schedule</a>

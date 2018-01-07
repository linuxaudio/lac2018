=======
LAC2018
=======

This is a |nikola| based static website.

Refer to its |handbook| to see how it works and how to add new content as blog
posts or static pages.

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

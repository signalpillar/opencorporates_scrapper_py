.. contents::


Project goal
------------

Repository contains simple **Python** project structure to develop scrapper for [OpenCorporates](https://missions.opencorporates.com) missions.

Run scrapper
------------

Run scrapper in scope of venv created by tox::

   tox -- scrapper.py


Docker image
------------

Project also contains ``Dockerfile`` to build an image with ``turbot`` client preinstalled.

To build the image::

    make build-docker-image

To run container::

    make sandbox

To get the latest requirements for the Python runtime, run the following in the container::

    make init-turbot-deps


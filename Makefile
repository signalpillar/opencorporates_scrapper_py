init-turbot-deps:
	pip install -r http://turbot.opencorporates.com/pip_requirements.txt

turbot-new:
	turbot bots:generate --bot demo --language python

turbot-auth:
	turbot auth:login

temporary-sandbox:
	docker run --rm -it -v `pwd`:/code turbotclient /bin/bash

sandbox:
	docker run -it -v `pwd`:/code turbotclient /bin/bash

build-docker-image:
	docker build --rm -t turbotclient docker


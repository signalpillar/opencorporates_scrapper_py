FROM ubuntu:latest

RUN echo "deb http://packages.opencorporates.com wheezy main" | sudo tee /etc/apt/sources.list.d/opencorporates.list
# Trust our signing key
RUN /usr/bin/apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C15723A0
RUN apt-get update
RUN apt-get install -y turbot-client

RUN apt-get install - y make

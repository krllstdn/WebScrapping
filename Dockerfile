FROM selenium/standalone-chrome:latest

# Install necessary packages
USER root
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# install python dependencies from requirements.txt
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

RUN apt-get update

# Set up work directory
WORKDIR /app

# Copy the Scrapy project into the container
COPY . /app/

RUN cd sreality/sreality

# # after building the image, run the spider
# RUN scrapy crawl sreality
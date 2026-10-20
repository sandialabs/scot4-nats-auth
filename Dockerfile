FROM python:3.14-trixie

WORKDIR /code

# Add necessary groups and users
RUN groupadd -g 3000 scot4nats
RUN useradd -M -r -u 3000 -g 3000 -s /bin/bash scot4nats

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    curl \
    vim \
    python3-dev 

# Copy over the required files
COPY requirements.txt /code/requirements.txt
COPY ./app /code/app

# Install requirements and pip
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set deployment user and give correct permissions
RUN chown -R scot4nats /code
USER scot4nats

# Start option
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8001"]


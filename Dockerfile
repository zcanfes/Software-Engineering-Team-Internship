FROM python:3.8-alpine

WORKDIR /app

# Install Python requirements
ADD requirements.txt /app/requirements.txt
COPY dependencies ./dependencies

# Install requirements
RUN pip3 install -r requirements.txt

# Copy content of app to image
COPY . /app

RUN mkdir analysis
RUN touch analysis.txt

# Run
CMD ["python", "application.py"]
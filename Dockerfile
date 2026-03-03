# using lightweight alpine image for python 3.11
FROM python:3.11-slim

# setting working directory
WORKDIR /app

# install system dependencies
RUN apk add --no-cache gcc musl-dev

# copy requirements
COPY requirements.txt .

# install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .

# expose port
EXPOSE 5000

# run flask app with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
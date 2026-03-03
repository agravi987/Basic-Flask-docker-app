#using lightweight alpine image for python 3.11
FROM python:3.11-alpine

#setting working directory
WORKDIR /app

# Install system dependencies (if needed later)
RUN apk add --no-cache gcc musl-dev

#copying requirements file to the working directory
COPY requirements.txt .

#installing dependencies from requirements file
RUN pip install --no-cache-dir -r requirements.txt

#copying the rest of the application code to the working directory
COPY . .

#exposing the port that the flask app will run on
EXPOSE 5000

#command to run the flask app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0:5000", "app:app"]

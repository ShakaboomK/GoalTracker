# FROM python:3.9

# WORKDIR /home/app

# # Install dependencies first to leverage Docker cache
# COPY requirements.txt /home/app
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application code
# COPY . /home/app

# # Expose the port
# EXPOSE 3000

# # Command to run the application (including migration)
# CMD python manage.py migrate && python manage.py runserver 0.0.0.0:3000
FROM python:3.9

WORKDIR /home/app

# Install dependencies
COPY requirements.txt /home/app
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Copy the rest of the application code
COPY . /home/app

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port (Render will override this, but it's good practice)
EXPOSE 8000

# Command to run the application
CMD gunicorn webappexample.wsgi:application --bind 0.0.0.0:$PORT

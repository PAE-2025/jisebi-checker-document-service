# Use the official Python image
FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    fontconfig \
    libreoffice \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Create a fonts directory and copy project fonts
COPY files/fonts/ /usr/share/fonts/truetype/custom/

# Update font cache to make fonts available
RUN fc-cache -f -v

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

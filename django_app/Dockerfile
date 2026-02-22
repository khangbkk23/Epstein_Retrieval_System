# Use the exact Python version matching your local environment
FROM python:3.11.13-slim

# Set environment variables for optimized Python execution in Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/user/.local/bin:$PATH"

# Create a non-root user required by Hugging Face Spaces security policies
RUN useradd -m -u 1000 user

# Install system dependencies (C++ Compiler) required for FAISS
RUN apt-get update && apt-get install -y \
    build-essential \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Switch to the non-root user and set the working directory
USER user
WORKDIR /home/user/app

# Copy requirements and install dependencies
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire source code AND the data/faiss_index directory
COPY --chown=user:user . .

# Expose the default Hugging Face Spaces port
EXPOSE 7860

# Command to run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:7860"]
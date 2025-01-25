FROM quay.io/astronomer/astro-runtime:9.1.0

# Install additional packages
COPY packages.txt .
RUN apt-get update && \
    cat packages.txt | xargs apt-get install -y && \
    apt-get clean

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

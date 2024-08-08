# Webook

**Webook** is a platform designed for book enthusiasts to manage and share reviews, track sales, and explore statistics about books and authors.

## Getting Started

To set up and run Webook, follow these instructions:

### Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.

### Setting Up the Project


1. **To build and start the application, use Docker Compose:**

```bash
    docker-compose up --build
```
    
Note: The first build may take some time as Docker downloads and installs the necessary dependencies.

2. **Populate Keyspace:**
Once the application is running, you need to populate the keyspace. This process might also take some time.
Run the following command to populate the keyspace:
```bash
    python populate_keyspace.py
```
Note: You can use the application while the keyspace is being populated. Just wait until the population process is complete for full functionality.

In case that this steps fails, try changing the following in line 11 of this file:
```python
    cluster = Cluster(['127.0.0.1'])
```
This needs to change to this line:

```python
    cluster = Cluster(['cassandra'])
```
Some systems doesn't work propertly with the one that we have written.

# Accessing the Application

Once the application is running and the keyspace is populated, you can access Webook through your web browser at [http://localhost:8000](http://localhost:8000).


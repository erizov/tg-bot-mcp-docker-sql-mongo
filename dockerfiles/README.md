# Dockerfiles for Different Database Backends

This folder contains specialized Dockerfiles for each database backend supported by the Telegram Notes Bot.

## Available Dockerfiles

- **`Dockerfile.sqlite`** - SQLite backend (file-based database)
- **`Dockerfile.mongo`** - MongoDB backend (document database)
- **`Dockerfile.neo4j`** - Neo4j backend (graph database)
- **`Dockerfile.postgresql`** - PostgreSQL backend (relational database)
- **`Dockerfile.cassandra`** - Cassandra backend (wide-column database)
- **`Dockerfile.progress`** - Progress backend (in-memory database)
- **`Dockerfile.progress-server`** - Progress Server backend (HTTP API)
- **`Dockerfile.base`** - Base template (original Dockerfile)

## Usage Examples

### Build and run with SQLite (default):
```bash
docker build -f dockerfiles/Dockerfile.sqlite -t tg-notes-bot:sqlite .
docker run -p 8001:8001 tg-notes-bot:sqlite
```

### Build and run with MongoDB:
```bash
# Start MongoDB first
docker compose -f mongo.docker-compose.yml up -d

# Build and run bot
docker build -f dockerfiles/Dockerfile.mongo -t tg-notes-bot:mongo .
docker run -p 8001:8001 --network neuroqc-net tg-notes-bot:mongo
```

### Build and run with Neo4j:
```bash
# Start Neo4j first
docker compose -f neo4j.docker-compose.yml up -d

# Build and run bot
docker build -f dockerfiles/Dockerfile.neo4j -t tg-notes-bot:neo4j .
docker run -p 8001:8001 --network neuroqc-net tg-notes-bot:neo4j
```

### Build and run with PostgreSQL:
```bash
# Start PostgreSQL first
docker compose -f postgresql.docker-compose.yml up -d

# Build and run bot
docker build -f dockerfiles/Dockerfile.postgresql -t tg-notes-bot:postgresql .
docker run -p 8001:8001 --network neuroqc-net tg-notes-bot:postgresql
```

### Build and run with Cassandra:
```bash
# Start Cassandra first
docker compose -f cassandra.docker-compose.yml up -d

# Build and run bot
docker build -f dockerfiles/Dockerfile.cassandra -t tg-notes-bot:cassandra .
docker run -p 8001:8001 --network neuroqc-net tg-notes-bot:cassandra
```

### Build and run with Progress (in-memory):
```bash
docker build -f dockerfiles/Dockerfile.progress -t tg-notes-bot:progress .
docker run -p 8001:8001 tg-notes-bot:progress
```

## Environment Variables

Each Dockerfile sets appropriate environment variables for its backend:

- **SQLite**: `USE_DB_BACKEND=sqlite`
- **MongoDB**: `USE_DB_BACKEND=mongo`, `MONGODB_URI`, `MONGODB_DB`
- **Neo4j**: `USE_DB_BACKEND=neo4j`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **PostgreSQL**: `USE_DB_BACKEND=postgresql`, `POSTGRESQL_HOST`, `POSTGRESQL_PORT`, `POSTGRESQL_DB`, `POSTGRESQL_USER`, `POSTGRESQL_PASSWORD`
- **Cassandra**: `USE_DB_BACKEND=cassandra`, `CASSANDRA_HOSTS`, `CASSANDRA_PORT`, `CASSANDRA_KEYSPACE`, `CASSANDRA_USER`, `CASSANDRA_PASSWORD`
- **Progress**: `USE_DB_BACKEND=progress`

## Network Requirements

For database backends that require external services (MongoDB, Neo4j, PostgreSQL, Cassandra), make sure to:

1. Create the network: `docker network create neuroqc-net`
2. Use `--network neuroqc-net` when running the bot container
3. Ensure the database service is running and accessible

## Monitoring

All Dockerfiles expose port 8001 for the FastAPI monitoring service. Access the monitoring dashboard at:
- Health check: `http://localhost:8001/health`
- Stats: `http://localhost:8001/count`
- Dashboard: `http://localhost:8001/count/html`

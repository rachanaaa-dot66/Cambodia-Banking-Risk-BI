# Docker Setup — Cambodia Banking Risk BI Platform

## What's inside

| Container | Image | Purpose | Port |
|---|---|---|---|
| `banking_postgres` | postgres:16 | PostgreSQL database | `5432` |
| `banking_pgadmin` | pgadmin4 | Web-based DB browser | `8080` |

---

## Quick Start

### Step 1 — Start the containers

```bash
cd Banking-Risk-BI-Platform/docker
docker compose up -d
```

Wait about 10 seconds for PostgreSQL to be ready.

### Step 2 — Generate the data (if you haven't yet)

```bash
cd ../python
pip install pandas numpy python-dateutil sqlalchemy psycopg2-binary
python main.py --skip-load
```

### Step 3 — Load CSVs into PostgreSQL

```bash
cd ../docker
python load_to_docker.py
```

That's it. Your database is ready.

---

## Connection Details

| Field | Value |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| Database | `banking_risk_bi` |
| User | `banking_user` |
| Password | `banking2024` |

---

## pgAdmin (web browser)

Open: **http://localhost:8080**

Login:
- Email: `admin@banking.local`
- Password: `admin2024`

Add a new server in pgAdmin:
- Name: `Banking BI`
- Host: `postgres` ← use the service name, not localhost
- Port: `5432`
- Database: `banking_risk_bi`
- User: `banking_user`
- Password: `banking2024`

---

## Power BI Connection

In Power BI Desktop → Get Data → PostgreSQL:

| Field | Value |
|---|---|
| Server | `localhost:5432` |
| Database | `banking_risk_bi` |

Enter user `banking_user` / password `banking2024` when prompted.

---

## Useful Commands

```bash
# Start containers
docker compose up -d

# Stop containers (data is preserved)
docker compose stop

# Stop and delete everything including data
docker compose down -v

# Check container status
docker compose ps

# View PostgreSQL logs
docker compose logs postgres

# Open a psql shell directly
docker exec -it banking_postgres psql -U banking_user -d banking_risk_bi
```

---

## Folder Structure

```
docker/
├── Dockerfile              ← PostgreSQL image config
├── docker-compose.yml      ← Starts postgres + pgadmin
├── load_to_docker.py       ← Loads CSVs into the DB
├── README.md               ← This file
└── init/
    ├── 01_create_tables.sql   ← Runs on first container start
    └── 02_constraints.sql     ← PKs, FKs, indexes
```

> **Note:** The `init/` scripts only run once on the very first startup
> when the volume is empty. If you need to re-run them, do:
> `docker compose down -v` then `docker compose up -d`

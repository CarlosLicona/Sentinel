# Sentinel 🛡️

> Infrastructure security monitoring with real-time packet analysis, service health checks, and intelligent alerting.

Sentinel is a self-hosted network and infrastructure monitoring system built for detection of anomalous behavior across services, ports, and system logs. It captures and analyzes network traffic at the packet level using Scapy, exposes a structured REST API via FastAPI, and delivers alerts through email, Slack, and webhooks. Designed to run locally via Docker Compose with a clear path to AWS deployment using Terraform.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Modules](#modules)
- [Data Models](#data-models)
- [API Reference](#api-reference)
- [Alert System](#alert-system)
- [Deployment](#deployment)
  - [Phase 1 — Local (Docker Compose)](#phase-1--local-docker-compose)
  - [Phase 2 — AWS (Terraform)](#phase-2--aws-terraform)
- [Roadmap](#roadmap)
- [Author](#author)

---

## Overview

Sentinel addresses a real operational problem: understanding what is happening inside your infrastructure without relying on expensive SaaS monitoring tools. It sits close to the network layer, collects data from three sources — raw packet traffic, service/port probes, and system logs — and correlates that data into a unified event stream that can trigger alerts when something looks wrong.

It is intentionally minimal and auditable. Every alert has a traceable cause. Every detection rule is readable code, not a black box.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        SENTINEL                          │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Packet      │  │  Service     │  │  Log         │  │
│  │  Collector   │  │  Prober      │  │  Watcher     │  │
│  │  (Scapy)     │  │  (asyncio)   │  │  (watchdog)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┼──────────────────┘          │
│                           ▼                             │
│                  ┌────────────────┐                     │
│                  │  Event Engine  │                     │
│                  │  (detection +  │                     │
│                  │   correlation) │                     │
│                  └───────┬────────┘                     │
│                          │                              │
│            ┌─────────────┼─────────────┐               │
│            ▼             ▼             ▼               │
│     ┌────────────┐ ┌──────────┐ ┌───────────┐         │
│     │ PostgreSQL │ │  Redis   │ │  Alert    │         │
│     │ (storage)  │ │ (queue)  │ │  Dispatch │         │
│     └────────────┘ └──────────┘ └─────┬─────┘         │
│                                        │               │
│                          ┌─────────────┼────────────┐  │
│                          ▼             ▼            ▼  │
│                      Email         Slack        Webhook │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              FastAPI REST API                   │   │
│  │         /events  /services  /alerts             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Data flow:**

1. Three collectors run concurrently as background workers.
2. Raw observations are normalized into `Event` objects and written to PostgreSQL.
3. The Event Engine evaluates each event against detection rules and flags anomalies.
4. Flagged events are pushed to a Redis queue for async alert dispatch.
5. Alert workers consume the queue and deliver notifications without blocking the API.
6. The FastAPI layer exposes all collected data and configuration via REST endpoints.

---

## Features

### Network Traffic Analysis
- Packet capture and protocol parsing with Scapy (TCP, UDP, ICMP)
- Detection of port scans, SYN floods, and unusual traffic volumes
- Per-host connection tracking and baseline comparison

### Service & Port Monitoring
- Configurable probes for HTTP, HTTPS, SSH, and custom TCP ports
- Latency tracking and availability history per service
- Automatic status transitions (UP → DEGRADED → DOWN)

### Log Analysis
- Real-time tail of auth logs, syslog, and application log files
- Pattern matching for failed logins, sudo escalations, and error spikes
- Correlation of log events with network anomalies on the same host

### Alert System
- Multi-channel delivery: email (SMTP), Slack (Incoming Webhooks), generic webhooks
- Configurable severity levels: INFO, WARNING, CRITICAL
- Alert deduplication with cooldown windows to prevent noise
- Per-rule enable/disable and threshold configuration via API

### REST API
- Full CRUD for monitored targets (hosts, services, log sources)
- Event query with filtering by host, type, severity, and time range
- Alert history and acknowledgment endpoints
- OpenAPI docs at `/docs`

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| API | FastAPI + Uvicorn | REST interface, OpenAPI |
| Packet capture | Scapy | Raw network inspection |
| Async workers | asyncio + BackgroundTasks | Concurrent collectors |
| Task queue | Redis + RQ | Async alert dispatch |
| Database | PostgreSQL | Persistent event/alert storage |
| ORM | SQLAlchemy 2.0 + Alembic | Models and migrations |
| Validation | Pydantic v2 | Request/response schemas |
| Containers | Docker + Docker Compose | Local orchestration |
| IaC | Terraform | AWS infrastructure definition |
| Cloud | AWS (EC2, RDS, ElastiCache) | Phase 2 deployment |
| Notifications | SMTP, Slack Webhooks, HTTP | Alert delivery |

---

## Project Structure

```
sentinel/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Settings from environment variables
│   ├── database.py              # SQLAlchemy engine and session
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── host.py
│   │   ├── service.py
│   │   ├── event.py
│   │   ├── alert.py
│   │   └── log_source.py
│   │
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── host.py
│   │   ├── service.py
│   │   ├── event.py
│   │   └── alert.py
│   │
│   ├── routers/                 # API route handlers
│   │   ├── hosts.py
│   │   ├── services.py
│   │   ├── events.py
│   │   └── alerts.py
│   │
│   ├── collectors/              # Background data collectors
│   │   ├── packet_collector.py  # Scapy-based packet capture
│   │   ├── service_prober.py    # TCP/HTTP service probes
│   │   └── log_watcher.py       # Log file tail and parsing
│   │
│   ├── engine/                  # Detection and correlation logic
│   │   ├── detector.py          # Rule evaluation
│   │   ├── rules.py             # Detection rule definitions
│   │   └── correlator.py        # Cross-source event correlation
│   │
│   └── alerts/                  # Alert dispatch
│       ├── dispatcher.py        # Queue consumer and router
│       ├── email_channel.py
│       ├── slack_channel.py
│       └── webhook_channel.py
│
├── migrations/                  # Alembic migration scripts
├── tests/                       # Pytest test suite
│   ├── test_collectors/
│   ├── test_engine/
│   └── test_api/
│
├── terraform/                   # AWS infrastructure (Phase 2)
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│       ├── ec2/
│       ├── rds/
│       └── elasticache/
│
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
└── README.md
```

---

## Modules

### Packet Collector (`collectors/packet_collector.py`)

Uses Scapy's `AsyncSniffer` to capture packets on a configurable interface. Each packet is parsed to extract source/destination IPs, ports, and protocol. Observations are aggregated per-host over rolling time windows and compared against baselines to detect anomalies (e.g., port scan signatures, volumetric spikes).

Runs as a background task on application startup. Requires `NET_ADMIN` capability in Docker.

### Service Prober (`collectors/service_prober.py`)

Async loop that probes registered services at configurable intervals. Supports:
- **TCP connect** — checks if a port accepts connections
- **HTTP/HTTPS** — checks status code and optional response body pattern
- **SSH** — checks banner response on port 22

Probe results update the service's `status` and `latency_ms` fields and generate Events on status transitions.

### Log Watcher (`collectors/log_watcher.py`)

Uses `watchdog` to tail registered log files in real time. Each new line is matched against a set of configurable regex patterns (e.g., `Failed password`, `sudo:`, `CRITICAL`). Matches produce Events with the matched line as payload.

### Event Engine (`engine/detector.py`)

Evaluates each incoming Event against the rule set defined in `rules.py`. A rule specifies:
- Which event types it applies to
- A threshold or pattern condition
- The severity of the resulting alert
- A cooldown window to suppress repeated alerts

The correlator cross-references events from different sources (e.g., a port scan followed by a failed SSH login on the same host) to produce higher-confidence composite alerts.

### Alert Dispatcher (`alerts/dispatcher.py`)

Consumes alert jobs from the Redis queue using RQ workers. Routes each alert to the configured channels based on severity. Implements exponential backoff on delivery failures and marks alerts as `DELIVERED` or `FAILED` in the database.

---

## Data Models

### Host
```
id            UUID
ip_address    string (unique)
hostname      string (optional)
label         string
active        boolean
created_at    datetime
```

### Service
```
id            UUID
host_id       FK → Host
name          string
protocol      enum: TCP | HTTP | HTTPS | SSH
port          integer
check_interval_seconds  integer
status        enum: UP | DEGRADED | DOWN | UNKNOWN
latency_ms    float (nullable)
last_checked  datetime
```

### Event
```
id            UUID
host_id       FK → Host (nullable)
source        enum: PACKET | SERVICE | LOG
event_type    string  (e.g., PORT_SCAN, SERVICE_DOWN, AUTH_FAILURE)
severity      enum: INFO | WARNING | CRITICAL
payload       JSONB
detected_at   datetime
```

### Alert
```
id            UUID
event_id      FK → Event
rule_name     string
message       string
severity      enum: INFO | WARNING | CRITICAL
status        enum: PENDING | DELIVERED | FAILED | ACKNOWLEDGED
channels      JSONB  (list of channels used)
created_at    datetime
acknowledged_at datetime (nullable)
```

### LogSource
```
id            UUID
host_id       FK → Host
file_path     string
description   string
active        boolean
```

---

## API Reference

Base URL (local): `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs`

### Hosts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/hosts` | List all monitored hosts |
| POST | `/hosts` | Register a new host |
| GET | `/hosts/{id}` | Get host details |
| PATCH | `/hosts/{id}` | Update host label or active state |
| DELETE | `/hosts/{id}` | Remove host and its data |

### Services

| Method | Endpoint | Description |
|---|---|---|
| GET | `/services` | List all services |
| POST | `/services` | Register a new service probe |
| GET | `/services/{id}` | Get service status and history |
| PATCH | `/services/{id}` | Update probe config |
| DELETE | `/services/{id}` | Remove service |

### Events

| Method | Endpoint | Description |
|---|---|---|
| GET | `/events` | List events (filter: host, type, severity, from, to) |
| GET | `/events/{id}` | Get event detail and payload |

### Alerts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/alerts` | List alerts (filter: status, severity) |
| GET | `/alerts/{id}` | Get alert detail |
| POST | `/alerts/{id}/acknowledge` | Mark alert as acknowledged |

---

## Alert System

Alerts are triggered by the Event Engine when a detection rule fires. They are delivered asynchronously so that detection latency is never affected by notification delivery.

### Channels

**Email (SMTP)**
Configured via `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and `ALERT_EMAIL_TO` environment variables. Sends a formatted message with event details, host info, and a timestamp.

**Slack**
Configured via `SLACK_WEBHOOK_URL`. Posts a structured Block Kit message to the target channel with color-coded severity.

**Webhook**
Configured via `ALERT_WEBHOOK_URL`. Sends a POST request with a JSON body containing the full alert object. Compatible with any HTTP endpoint (PagerDuty, custom receivers, etc.).

### Severity Routing

By default, all channels receive all severities. This is configurable per-channel:

```
INFO     → webhook only
WARNING  → webhook + slack
CRITICAL → webhook + slack + email
```

### Deduplication

Each rule carries a `cooldown_seconds` value. If an identical alert (same rule + same host) fires within the cooldown window, it is suppressed at the dispatcher level. The suppression count is tracked in Redis.

---

## Deployment

### Phase 1 — Local (Docker Compose)

**Requirements:** Docker Desktop or Docker Engine with Compose v2, and `NET_ADMIN` capability available for packet capture.

```bash
# Clone the repo
git clone https://github.com/CarlosLicona/Sentinel.git
cd Sentinel

# Configure environment
cp .env.example .env
# Edit .env with your SMTP, Slack, and database credentials

# Start all services
docker compose up --build
```

Services started:
- `api` — FastAPI on port 8000
- `db` — PostgreSQL on port 5432
- `redis` — Redis on port 6379
- `worker` — RQ alert worker

Run database migrations:
```bash
docker compose exec api alembic upgrade head
```

### Phase 2 — AWS (Terraform)

Target infrastructure:

```
VPC
├── Public subnet
│   └── EC2 (t3.small) — Sentinel API + collectors
├── Private subnet
│   ├── RDS (PostgreSQL) — managed database
│   └── ElastiCache (Redis) — managed queue
└── Security Groups
    ├── Allow 8000 inbound (API)
    └── Allow internal traffic between services
```

```bash
cd terraform/
terraform init
terraform plan -var-file="prod.tfvars"
terraform apply
```

Terraform provisions: VPC, subnets, security groups, EC2 instance, RDS instance, ElastiCache cluster, and IAM role with least-privilege policy.

---

## Roadmap

**v0.1 — Foundation**
- [x] Project structure and Docker Compose setup
- [ ] PostgreSQL models and Alembic migrations
- [ ] FastAPI skeleton with all routers

**v0.2 — Collectors**
- [ ] Service Prober (TCP + HTTP)
- [ ] Log Watcher
- [ ] Packet Collector (Scapy)

**v0.3 — Detection**
- [ ] Event Engine with initial rule set
- [ ] Basic correlator (same-host cross-source)

**v0.4 — Alerts**
- [ ] Redis queue + RQ worker
- [ ] Email channel
- [ ] Slack channel
- [ ] Webhook channel

**v0.5 — AWS**
- [ ] Terraform infrastructure
- [ ] EC2 deployment with user-data script
- [ ] RDS + ElastiCache integration

**v1.0 — Portfolio release**
- [ ] Full test coverage (collectors, engine, API)
- [ ] README finalized
- [ ] Demo video / screenshots

---

## Author

**Carlos Daniel Licona Alfonso**
Redes y Servicios de Cómputo — Universidad Veracruzana

[GitHub](https://github.com/CarlosLicona) · [LinkedIn](#)

---

*Sentinel is a portfolio project demonstrating applied knowledge of network security monitoring, backend API design, containerization, and cloud infrastructure.*

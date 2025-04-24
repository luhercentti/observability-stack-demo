docker-compose down
docker-compose build
docker-compose up -d

To avoid issues with minikube open telemetry already using port 4317 I :

Changed the external port for OpenTelemetry Collector from 4317 to 4319
Changed the external port for Tempo from 4317 to 4327
Kept the internal ports the same (4317) so services can communicate inside the Docker network

# Make some requests to your Python app
# Send a variety of requests over a minute to create graph-worthy data
for i in {1..30}; do
  curl http://localhost:5000/
  sleep 1
  curl http://localhost:5000/slow
  sleep 2
  if [ $((i % 5)) -eq 0 ]; then
    curl http://localhost:5000/error
  fi
done

Access Grafana:
Open your browser and navigate to http://localhost:3000. You should already have the preconfigured datasources and a sample dashboard.

OpenTelemetry Collector to handle and route telemetry data

The application has three endpoints:

/ - A simple homepage
/slow - Simulates a slow operation with nested spans
/error - Deliberately causes an error to demonstrate error tracking

Check log of each component, go to path where the docker-compose is and:
# Check OpenTelemetry Collector logs
docker-compose logs otel-collector

# Check Loki logs
docker-compose logs loki

# Check Tempo logs
docker-compose logs tempo

# Check Prometheus logs
docker-compose logs prometheus

# Check Grafana logs
docker-compose logs grafana


////////////////////////////////////

Architecture Overview
Your setup consists of a full observability pipeline with these key components:

Application (Python App) - The source of telemetry data
OpenTelemetry Collector - Collection and routing of telemetry data
Prometheus - Metrics storage and querying
Loki - Log storage and querying
Tempo - Distributed tracing storage and querying
Grafana - Visualization platform for all data sources

Here's how they interconnect:
                                 ┌─────────────┐  
                                 │             │  
                                 │  Grafana    │  
                                 │ (Visualize) │  
                                 │             │  
                                 └──────┬──────┘  
                                        │         
                                        ▼         
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│             │    │             │    │             │    │             │
│ Python App  │───▶│ OpenTele-   │───▶│ Prometheus  │    │ Loki        │
│ (Source)    │    │ metry       │    │ (Metrics)   │    │ (Logs)      │
│             │    │ Collector   │───▶│             │    │             │
└─────────────┘    │             │    └─────────────┘    └─────────────┘
                   │             │                              ▲
                   │             │                              │
                   │             │─────────────────────────────┘
                   │             │                              
                   │             │    ┌─────────────┐           
                   │             │───▶│ Tempo       │           
                   └─────────────┘    │ (Traces)    │           
                                      │             │           
                                      └─────────────┘
Data Flow

Your Python Application generates:

Metrics (application performance, business metrics)
Logs (application events, errors)
Traces (request paths through the application)


OpenTelemetry Collector:

Receives telemetry data from your application via OTLP protocol
Acts as a central hub that processes and routes data to appropriate backends
Forwards metrics to Prometheus
Forwards logs to Loki
Forwards traces to Tempo


Storage and Query Systems:

Prometheus stores and allows querying of time-series metrics data
Loki stores and allows querying of log data
Tempo stores and allows querying of distributed trace data


Grafana:

Connects to all three backends (Prometheus, Loki, Tempo)
Provides unified visualization and dashboarding
Enables correlation between metrics, logs, and traces



Port Mapping and Communication Channels

Python App → OpenTelemetry: OTLP protocol (gRPC on port 4317)
OpenTelemetry → Prometheus: Local scrape endpoint (port 8889)
OpenTelemetry → Loki: HTTP push API (port 3100)
OpenTelemetry → Tempo: OTLP protocol (port 4317)
Grafana → All backends: Their respective HTTP APIs


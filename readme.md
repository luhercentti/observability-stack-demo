docker-compose down
docker-compose build
docker-compose up -d


OpenTelemetry Collector metrics: http://localhost:8889/metrics
Python app metrics: http://localhost:5000/metrics
Prometheus targets: http://localhost:9090/targets

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

What You Get
This setup provides:

A simple Python Flask application with OpenTelemetry instrumentation
Complete observability stack:

Metrics: Prometheus
Logs: Loki
Traces: Tempo
Visualization: Grafana


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


////

2. Data Sources in Grafana
The configuration I provided includes auto-provisioning of data sources, so they should be automatically set up when Grafana starts. To verify:

Open Grafana at http://localhost:3000 (default login is admin/admin)
Go to Configuration → Data Sources
You should see these preconfigured data sources:

Prometheus (metrics)
Loki (logs)
Tempo (traces)

3. Viewing Data in Grafana
For Metrics (Prometheus)

Click on "Explore" in the left sidebar
Select "Prometheus" as your data source
Try queries like:

up (shows which targets are up)
rate(http_server_request_duration_seconds_count[5m]) (if your app exports these metrics)


For Logs (Loki)

Click on "Explore"
Select "Loki" as your data source
Use a query like: {job="python-app"} or {service_name="demo-python-app"}

For Traces (Tempo)

Click on "Explore"
Select "Tempo" as your data source
You can search by trace ID or use the search tab to find traces

4. Generating Test Data
Make sure you've generated some data with your Python app:
bash# Make multiple requests to different endpoints

5. Checking Specific Components
OpenTelemetry Collector

Metrics endpoint: http://localhost:8888/metrics

Prometheus

UI: http://localhost:9090
Check status of targets: http://localhost:9090/targets

Loki

Ready status: http://localhost:3100/ready

Tempo

API status: http://localhost:3200/api/echo

6. Creating a Dashboard
The configuration includes a sample dashboard. To access it:

Go to Dashboards → Browse
Look for "Python App Dashboard"

If you want to create a new dashboard:

Click on "Create" (+ icon) → Dashboard
Click "Add visualization"
Select a data source and build panels for metrics, logs, and traces

Troubleshooting
If you're not seeing data:

Check connections: Verify all services can communicate with each other
Check app instrumentation: Make sure the Python app is sending telemetry data
Check collector config: Ensure ports and endpoints are properly configured
Review logs: Check component logs for errors

Remember that telemetry data is time-based - make sure your time range in Grafana includes when you generated the test data (use the time picker in the top right).ReintentarClaude aún no tiene la capacidad de ejecutar el código que genera.Claude puede cometer errores. Verifique las respuestas.
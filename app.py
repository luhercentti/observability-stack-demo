# app.py
from flask import Flask, Response
import logging
import random
import time
import prometheus_client
from prometheus_client import Counter, Histogram, generate_latest

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Prometheus metrics
REQUEST_COUNT = Counter('app_request_count', 'Application Request Count', ['endpoint'])
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Application Request Latency', ['endpoint'])
ERROR_COUNT = Counter('app_error_count', 'Application Error Count')

# Initialize tracing
resource = Resource(attributes={SERVICE_NAME: "demo-python-app"})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Initialize Flask app
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/')
def home():
    REQUEST_COUNT.labels(endpoint='/').inc()
    with REQUEST_LATENCY.labels(endpoint='/').time():
        logger.info("Processing request to home endpoint")
        return "Hello from OpenTelemetry instrumented app!"

@app.route('/slow')
def slow():
    REQUEST_COUNT.labels(endpoint='/slow').inc()
    with REQUEST_LATENCY.labels(endpoint='/slow').time():
        with tracer.start_as_current_span("slow-operation"):
            logger.info("Starting slow operation")
            time.sleep(random.uniform(0.1, 0.5))
            for i in range(3):
                with tracer.start_as_current_span(f"subtask-{i}"):
                    logger.info(f"Processing subtask {i}")
                    time.sleep(random.uniform(0.05, 0.2))
            logger.info("Completed slow operation")
        
        return "Slow operation completed"

@app.route('/error')
def error():
    REQUEST_COUNT.labels(endpoint='/error').inc()
    ERROR_COUNT.inc()
    logger.error("This endpoint generates an error")
    try:
        # Generate division by zero error
        1 / 0
    except Exception as e:
        with tracer.start_as_current_span("error-handler") as span:
            span.set_attribute("error", True)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            logger.exception("Division by zero error occurred")
        return "Error occurred and was captured by OpenTelemetry", 500

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
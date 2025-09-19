import subprocess
import os
import signal

# Paths
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
backend_host = "0.0.0.0"
backend_port = 8000

# Start frontend (Vite dev server)
frontend_process = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd=frontend_dir,
)

# Start backend (Uvicorn)
backend_process = subprocess.Popen(
    ["uvicorn", "app.api.app:app", "--host", backend_host, "--port", str(backend_port)],
)

try:
    frontend_process.wait()
    backend_process.wait()
except KeyboardInterrupt:
    # Gracefully kill both on Ctrl+C
    frontend_process.send_signal(signal.SIGINT)
    backend_process.send_signal(signal.SIGINT)

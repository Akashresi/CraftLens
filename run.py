"""
CraftLens 2.0 - Single Command Multi-Service Runner
Starts both the FastAPI Backend and Next.js Web Portal simultaneously.
Handles logging, health checks, and graceful shutdown on Ctrl+C.
"""

import sys
import os
import subprocess
import threading
import time
import signal
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
BUYER_WEB_DIR = os.path.join(ROOT_DIR, "buyer-web")
ADMIN_WEB_DIR = os.path.join(ROOT_DIR, "admin-web")

processes = []
is_shutting_down = False


def print_banner():
    banner = """
\033[1;32m╔════════════════════════════════════════════════════════════════════════╗
║                     CRAFTLENS 2.0 UNIFIED RUNNER                       ║
║    AI-Powered Artisan Business Management & Global Marketplace         ║
╚════════════════════════════════════════════════════════════════════════╝\033[0m

  \033[1;36m🌐 Service Endpoints:\033[0m
     • \033[1;37mBuyer & Artisan Web:\033[0m    \033[1;34mhttp://localhost:3000\033[0m
     • \033[1;37mBackend REST API:\033[0m        \033[1;34mhttp://127.0.0.1:8000/api/v1/docs\033[0m
     • \033[1;37mBackend Health Check:\033[0m    \033[1;34mhttp://127.0.0.1:8000/api/v1/health\033[0m
     • \033[1;37mAdmin Governance:\033[0m        \033[1;34mhttp://localhost:3001\033[0m (with --admin flag)

  \033[1;33m[Press Ctrl+C anytime to stop all running services cleanly]\033[0m
"""
    print(banner)


def stream_logs(process, prefix, color_code):
    try:
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            if is_shutting_down:
                break
            clean_line = line.rstrip()
            if clean_line:
                print(f"{color_code}[{prefix}]\033[0m {clean_line}", flush=True)
    except Exception:
        pass


def get_node_cmd():
    if shutil.which("pnpm") or shutil.which("pnpm.cmd"):
        return "pnpm"
    return "npm"


def init_database_if_needed():
    print("\033[1;33m[Setup]\033[0m Verifying database schema & seeds...")
    cmd = [sys.executable, os.path.join(BACKEND_DIR, "app", "db", "init_db.py")]
    try:
        res = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, check=True)
        print("\033[1;32m[Setup]\033[0m Database initialized successfully.")
    except Exception as e:
        print(f"\033[1;31m[Setup]\033[0m Note on database init: {e}")


def terminate_all(sig=None, frame=None):
    global is_shutting_down
    if is_shutting_down:
        return
    is_shutting_down = True
    print("\n\033[1;33m[Shutdown]\033[0m Stopping all CraftLens services...")
    for p in processes:
        try:
            if sys.platform == "win32":
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                p.terminate()
        except Exception:
            pass
    print("\033[1;32m[Shutdown]\033[0m All services stopped. Goodbye!")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, terminate_all)
    signal.signal(signal.SIGTERM, terminate_all)

    print_banner()
    init_database_if_needed()

    node_cli = get_node_cmd()
    run_admin = "--admin" in sys.argv
    run_mobile = "--mobile" in sys.argv

    # 1. Start Backend FastAPI
    print(f"\033[1;36m[Backend]\033[0m Launching FastAPI Uvicorn server on port 8000...")
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload",
    ]
    p_backend = subprocess.Popen(
        backend_cmd,
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    processes.append(p_backend)

    t_backend = threading.Thread(target=stream_logs, args=(p_backend, "Backend", "\033[36m"), daemon=True)
    t_backend.start()

    # 2. Start Buyer Web Next.js
    print(f"\033[1;32m[Frontend]\033[0m Launching Next.js Buyer Web server on port 3000 ({node_cli})...")
    frontend_cmd = [node_cli, "run", "dev"] if sys.platform != "win32" else f"{node_cli}.cmd run dev"
    p_frontend = subprocess.Popen(
        frontend_cmd,
        cwd=BUYER_WEB_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        shell=True if sys.platform == "win32" else False,
    )
    processes.append(p_frontend)

    t_frontend = threading.Thread(target=stream_logs, args=(p_frontend, "Web", "\033[32m"), daemon=True)
    t_frontend.start()

    # 3. Optional Admin Web
    if run_admin:
        print(f"\033[1;35m[Admin]\033[0m Launching Admin Web server on port 3001...")
        admin_cmd = f"{node_cli}.cmd run dev -- -p 3001" if sys.platform == "win32" else f"{node_cli} run dev -- -p 3001"
        p_admin = subprocess.Popen(
            admin_cmd,
            cwd=ADMIN_WEB_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=True if sys.platform == "win32" else False,
        )
        processes.append(p_admin)
        t_admin = threading.Thread(target=stream_logs, args=(p_admin, "Admin", "\033[35m"), daemon=True)
        t_admin.start()

    # 4. Optional Mobile
    if run_mobile:
        print(f"\033[1;33m[Mobile]\033[0m Launching Expo dev server...")
        mobile_cmd = "npx.cmd expo start" if sys.platform == "win32" else "npx expo start"
        p_mobile = subprocess.Popen(
            mobile_cmd,
            cwd=os.path.join(ROOT_DIR, "mobile"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=True if sys.platform == "win32" else False,
        )
        processes.append(p_mobile)
        t_mobile = threading.Thread(target=stream_logs, args=(p_mobile, "Mobile", "\033[33m"), daemon=True)
        t_mobile.start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(0.5)
            # Check if critical processes died unexpectedly
            if p_backend.poll() is not None:
                print(f"\033[1;31m[Backend]\033[0m Process exited with code {p_backend.returncode}")
                break
            if p_frontend.poll() is not None:
                print(f"\033[1;31m[Frontend]\033[0m Process exited with code {p_frontend.returncode}")
                break
    except KeyboardInterrupt:
        pass
    finally:
        terminate_all()


if __name__ == "__main__":
    main()

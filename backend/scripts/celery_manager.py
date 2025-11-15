#!/usr/bin/env python
"""
Celery Worker Management Script

Utility script to start/stop Celery workers and beat scheduler.
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def start_worker(concurrency=2, loglevel="info"):
    """Start Celery worker."""
    print(f"🚀 Starting Celery worker (concurrency={concurrency}, loglevel={loglevel})...")
    cmd = [
        "celery",
        "-A", "app.celery_app",
        "worker",
        f"--loglevel={loglevel}",
        f"--concurrency={concurrency}",
    ]
    subprocess.run(cmd)


def start_beat(loglevel="info"):
    """Start Celery beat scheduler."""
    print(f"⏰ Starting Celery beat scheduler (loglevel={loglevel})...")
    cmd = [
        "celery",
        "-A", "app.celery_app",
        "beat",
        f"--loglevel={loglevel}",
    ]
    subprocess.run(cmd)


def start_flower(port=5555):
    """Start Flower monitoring tool."""
    print(f"🌸 Starting Flower monitoring on port {port}...")
    cmd = [
        "celery",
        "-A", "app.celery_app",
        "flower",
        f"--port={port}",
    ]
    subprocess.run(cmd)


def purge_tasks():
    """Purge all pending tasks from the queue."""
    print("🧹 Purging all pending tasks...")
    cmd = [
        "celery",
        "-A", "app.celery_app",
        "purge",
        "-f",  # Force without confirmation
    ]
    subprocess.run(cmd)


def inspect_active():
    """Show active tasks."""
    print("📋 Active tasks:")
    cmd = [
        "celery",
        "-A", "app.celery_app",
        "inspect",
        "active",
    ]
    subprocess.run(cmd)


def inspect_scheduled():
    """Show scheduled tasks."""
    print("⏳ Scheduled tasks:")
    cmd = [
        "celery",
        "-A", "app.celery_app",
        "inspect",
        "scheduled",
    ]
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description="Celery Worker Management")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Worker command
    worker_parser = subparsers.add_parser("worker", help="Start Celery worker")
    worker_parser.add_argument("-c", "--concurrency", type=int, default=2, help="Number of worker processes")
    worker_parser.add_argument("-l", "--loglevel", default="info", help="Log level")
    
    # Beat command
    beat_parser = subparsers.add_parser("beat", help="Start Celery beat scheduler")
    beat_parser.add_argument("-l", "--loglevel", default="info", help="Log level")
    
    # Flower command
    flower_parser = subparsers.add_parser("flower", help="Start Flower monitoring")
    flower_parser.add_argument("-p", "--port", type=int, default=5555, help="Port number")
    
    # Inspect commands
    subparsers.add_parser("active", help="Show active tasks")
    subparsers.add_parser("scheduled", help="Show scheduled tasks")
    subparsers.add_parser("purge", help="Purge all pending tasks")
    
    args = parser.parse_args()
    
    if args.command == "worker":
        start_worker(concurrency=args.concurrency, loglevel=args.loglevel)
    elif args.command == "beat":
        start_beat(loglevel=args.loglevel)
    elif args.command == "flower":
        start_flower(port=args.port)
    elif args.command == "active":
        inspect_active()
    elif args.command == "scheduled":
        inspect_scheduled()
    elif args.command == "purge":
        purge_tasks()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

import reflex as rx
import httpx
import os
import asyncio
from typing import List, Dict, Any

INSIGHT_API_URL = os.getenv("INSIGHT_API_URL", os.getenv("API_URL", "http://localhost:8000"))

class AppState(rx.State):
    """The base state for the app."""

    # Overview Data
    overview_data: Dict[str, Any] = {
        "active_workers": 0,
        "failed_tasks": 0,
        "total_tasks": 0,
        "queue_backlog": 0,
        "avg_runtime": 0.0,
    }

    # Task Data
    tasks: List[Dict[str, Any]] = []

    # Worker Data
    workers: List[Dict[str, Any]] = []

    # Individual Task Detail Data
    current_task_details: Dict[str, Any] = {"task": {}, "timeline": []}

    # Queue Data
    queues: List[Dict[str, Any]] = []

    # Chart Data
    throughput_data: List[Dict[str, Any]] = []
    period_range: str = "30m"

    # Loading states
    is_loading: bool = False

    @rx.event(background=True)
    async def fetch_overview(self):
        async with self:
            self.is_loading = True

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{INSIGHT_API_URL}/metrics/overview")
                if res.status_code == 200:
                    async with self:
                        self.overview_data = res.json()
        except Exception as e:
            print(f"Error fetching overview: {e}")

        async with self:
            self.is_loading = False

    @rx.event(background=True)
    async def fetch_tasks(self):
        async with self:
            self.is_loading = True

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{INSIGHT_API_URL}/tasks/?limit=20")
                if res.status_code == 200:
                    async with self:
                        self.tasks = res.json()
        except Exception as e:
            print(f"Error fetching tasks: {e}")

        async with self:
            self.is_loading = False

    @rx.event(background=True)
    async def fetch_workers(self):
        async with self:
            self.is_loading = True

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{INSIGHT_API_URL}/workers/")
                if res.status_code == 200:
                    async with self:
                        self.workers = res.json()
        except Exception as e:
            print(f"Error fetching workers: {e}")

        async with self:
            self.is_loading = False

    @rx.event(background=True)
    async def fetch_task_detail(self):
        """Fetch details for a specific task based on the URL parameter."""
        task_id = self.router.page.params.get("task_id", "")
        if not task_id:
            return

        async with self:
            self.is_loading = True
            # Reset previous state to avoid flashing old data
            self.current_task_details = {"task": {}, "timeline": []}

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{INSIGHT_API_URL}/tasks/{task_id}")
                if res.status_code == 200:
                    async with self:
                        self.current_task_details = res.json()
        except Exception as e:
            print(f"Error fetching task details for {task_id}: {e}")

        async with self:
            self.is_loading = False

    @rx.event(background=True)
    async def fetch_queues(self):
        """Fetch per-queue statistics from the API."""
        async with self:
            self.is_loading = True

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{INSIGHT_API_URL}/queues/")
                if res.status_code == 200:
                    async with self:
                        self.queues = res.json()
        except Exception as e:
            print(f"Error fetching queues: {e}")

        async with self:
            self.is_loading = False

    @rx.event(background=True)
    async def fetch_throughput(self):
        """Fetch throughput metrics from the API."""
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{INSIGHT_API_URL}/metrics/throughput?range={self.period_range}")
                if res.status_code == 200:
                    data = res.json()
                    # Add labels based on range
                    for item in data:
                        if self.period_range in ["30m", "1h"]:
                            item["time"] = item["timestamp"][11:16] # HH:MM
                        elif self.period_range == "24h":
                            item["time"] = item["timestamp"][11:13] + ":00" # HH:00
                        else:
                            item["time"] = item["timestamp"][5:10] # MM-DD
                    async with self:
                        self.throughput_data = data
        except Exception as e:
            print(f"Error fetching throughput: {e}")

    @rx.event
    def set_period_range(self, range_val: str):
        """Update the time range and refresh data."""
        self.period_range = range_val
        return AppState.fetch_throughput

    @rx.event(background=True)
    async def auto_refresh(self):
        """Periodically refresh all dashboard data in the background."""
        while True:
            await asyncio.sleep(5)
            try:
                async with httpx.AsyncClient() as client:
                    r_overview = await client.get(f"{INSIGHT_API_URL}/metrics/overview")
                    r_tasks = await client.get(f"{INSIGHT_API_URL}/tasks/?limit=20")
                    r_workers = await client.get(f"{INSIGHT_API_URL}/workers/")
                    r_queues = await client.get(f"{INSIGHT_API_URL}/queues/")
                    r_throughput = await client.get(f"{INSIGHT_API_URL}/metrics/throughput?range={self.period_range}")
                    
                async with self:
                    if r_overview.status_code == 200:
                        self.overview_data = r_overview.json()
                    if r_tasks.status_code == 200:
                        self.tasks = r_tasks.json()
                    if r_workers.status_code == 200:
                        self.workers = r_workers.json()
                    if r_queues.status_code == 200:
                        self.queues = r_queues.json()
                    if r_throughput.status_code == 200:
                        t_data = r_throughput.json()
                        for item in t_data:
                            if self.period_range in ["30m", "1h"]:
                                item["time"] = item["timestamp"][11:16]
                            elif self.period_range == "24h":
                                item["time"] = item["timestamp"][11:13] + ":00"
                            else:
                                item["time"] = item["timestamp"][5:10]
                        self.throughput_data = t_data
            except Exception as e:
                print(f"Auto-refresh error: {e}")

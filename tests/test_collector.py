import pytest
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collector.main import on_event

def test_on_event_normalization(monkeypatch):
    """
    Test that the event collector correctly normalizes a Celery event.
    """
    # Mock the Redis publisher
    published_payloads = []
    
    class MockRedis:
        def xadd(self, stream_name, payload):
            published_payloads.append(payload)
            return b"123-0"
            
    # Inject our mock
    monkeypatch.setattr("collector.main.r", MockRedis())
    
    # Sample Celery Event
    test_event = {
        'type': 'task-started',
        'uuid': 'task-1234',
        'name': 'send_email',
        'hostname': 'worker-1',
        'timestamp': 1690000000.0,
        'pid': 1234
    }
    
    on_event(test_event)
    
    assert len(published_payloads) == 1
    
    payload = published_payloads[0]
    assert payload["type"] == "task-started"
    
    # Check normalized JSON
    normalized = json.loads(payload["normalized"])
    assert normalized["event_type"] == "task-started"
    assert normalized["task_id"] == "task-1234"
    assert normalized["task_name"] == "send_email"
    assert normalized["worker"] == "worker-1"
    assert normalized["timestamp"] == 1690000000.0

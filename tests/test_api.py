import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ensure the app module is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_tasks_endpoint_no_db(monkeypatch):
    """
    Test that the tasks endpoint is correctly wired up.
    Since we don't have a live DB in this unit test environment,
    we'll mock the get_db dependency.
    """
    from api.dependencies import get_db
    from sqlalchemy.orm import Session
    from unittest.mock import MagicMock
    
    mock_db = MagicMock(spec=Session)
    
    # Mock the query chain: db.query(Task).order_by(...).offset(...).limit(...).all()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [] # Return empty list of tasks
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []
    
    # Clean up override
    app.dependency_overrides.clear()

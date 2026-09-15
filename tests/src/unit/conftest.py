# tests/src/unit/conftest.py
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
from graph_adapters.sumo_adapter import SUMOAdapter

sumo_adapter = SUMOAdapter

@pytest.fixture
def mock_sumo_net():
    """Mock SUMO network object for testing"""
    net = Mock()
    net.getEdges = Mock(return_value=['edge1', 'edge2', 'edge3'])
    net.getNodes = Mock(return_value=['node1', 'node2', 'node3'])
    return net

@pytest.fixture
def mock_sumo_routes():
    """Mock SUMO routes object for testing"""
    routes = Mock()
    routes.getRoutes = Mock(return_value=['route1', 'route2'])
    return routes

@pytest.fixture
def sumo_to_microrail(mock_sumo_net, mock_sumo_routes):
    """Initialized SUMOAdapter instance with mocked dependencies"""
    adapter = SUMOAdapter(mock_sumo_net, mock_sumo_routes)
    
    # Mock computation-heavy methods
    adapter.build_tc_mapping = Mock()
    adapter.precompute_betweenness = Mock()
    adapter.betweenness = {'edge1': 0.5, 'edge2': 0.3, 'edge3': 0.7}
    
    return adapter

@pytest.fixture
def mock_track_circuit():
    """Test track circuit identifier"""
    return 'edge1'

@pytest.fixture
def mock_vehicle():
    """Test vehicle/train object"""
    vehicle = Mock()
    vehicle.getID = Mock(return_value='train_1')
    vehicle.getType = Mock(return_value='passenger')
    return vehicle

def pytest_configure(config):
    """Make sumo_adapter available as a builtin for tests"""
    import builtins
    builtins.sumo_adapter = sumo_adapter
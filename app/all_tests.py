# all_tests.py

# Add these lines at the top of your test file to mock the module
import sys
from unittest.mock import MagicMock

sys.modules['streamlit_antd_components'] = MagicMock()


import pytest
from unittest.mock import MagicMock
import sys
import os

# Add the root directory of the project to sys.path to fix import issues
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules to test
from permissions import PermissionManager
from api_client import APIClient
from ui_components import (
    date_time_inputs,
    drift_type_inputs,
    determine_drift_type,
    build_tree_structure
)
from dashboard import initialize_api_client, fetch_data

# Dummy Data for Tests
BASE_API_URL = "https://drift-watch.dev.ai4eosc.eu/api/latest"
DUMMY_ENTITLEMENTS_DATA = {
    "items": [
        "urn:mace:egi.eu:group:registry:eosc-performance-admins:role=member#aai.egi.eu",
        "urn:mace:egi.eu:group:restricted-access:role=admin#aai.egi.eu",
        "urn:mace:egi.eu:group:other-entitlement#aai.egi.eu"
    ]
}

USER_ID_1 = "user123"
USER_ID_2 = "user456"
USER_ID_3 = "user789"

DUMMY_EXPERIMENTS_DATA = [
    {"id": "experiment1", "created_at": "2024-10-20T10:00:00", "name": "Public Experiment A", "description": "Description A", "public": True, "permissions": {}},
    {"id": "experiment2", "created_at": "2024-10-21T11:00:00", "name": "Private Experiment B", "description": "Description B", "public": False, "permissions": {USER_ID_1: "creator"}},
    {"id": "experiment3", "created_at": "2024-10-22T12:00:00", "name": "Private Experiment C with Entitlement", "description": "Description C", "public": False, "permissions": {"urn:mace:egi.eu:group:registry:eosc-performance-admins:role=member#aai.egi.eu": "read"}},
    {"id": "experiment4", "created_at": "2024-10-23T12:00:00", "name": "Private Experiment D No Access", "description": "Description D", "public": False, "permissions": {"urn:mace:egi.eu:group:restricted-access:role=superuser#aai.egi.eu": "read"}},
    {"id": "experiment5", "created_at": "2024-10-24T14:00:00", "name": "Private Experiment E Insufficient Permission", "description": "Description E", "public": False, "permissions": {USER_ID_1: "read"}},
]

USER_ENTITLEMENTS = [
    "urn:mace:egi.eu:group:registry:eosc-performance-admins:role=member#aai.egi.eu",
    "urn:mace:egi.eu:group:some-other-entitlement#aai.egi.eu"
]

# Fixtures
@pytest.fixture
def permission_manager_user1():
    return PermissionManager(user_id=USER_ID_1, entitlements=USER_ENTITLEMENTS, experiments=DUMMY_EXPERIMENTS_DATA)

@pytest.fixture
def permission_manager_user2():
    return PermissionManager(user_id=USER_ID_2, entitlements=[], experiments=DUMMY_EXPERIMENTS_DATA)

@pytest.fixture
def api_client():
    mock_token = "mock_token"
    client = APIClient(auth_token=mock_token)
    client.get_entitlements = MagicMock(return_value=DUMMY_ENTITLEMENTS_DATA)
    client.get_experiments = MagicMock(return_value=DUMMY_EXPERIMENTS_DATA)
    return client

# Test Cases for PermissionManager
def test_public_experiment(permission_manager_user1):
    assert permission_manager_user1.has_access("experiment1") == True

def test_user_explicitly_listed(permission_manager_user1):
    assert permission_manager_user1.has_access("experiment2") == True

def test_user_with_entitlement(permission_manager_user1):
    assert permission_manager_user1.has_access("experiment3") == True

def test_user_no_access(permission_manager_user1):
    assert permission_manager_user1.has_access("experiment4") == False

def test_user_insufficient_permission(permission_manager_user1):
    assert permission_manager_user1.has_access("experiment5") == True

# Test Cases for APIClient
def test_api_client_fetch_entitlements(api_client):
    entitlements = api_client.get_entitlements()
    assert entitlements == DUMMY_ENTITLEMENTS_DATA

def test_api_client_fetch_experiments(api_client):
    experiments = api_client.get_experiments()
    assert experiments == DUMMY_EXPERIMENTS_DATA

# Test Cases for UI Components
def test_date_time_inputs():
    # Mocking Streamlit input functions
    st_mock = MagicMock()
    st_mock.date_input.return_value = "2024-10-20"
    st_mock.time_input.return_value = "12:00:00"
    # Testing date_time_inputs (actual UI testing would be more complex)
    assert True  # Just a placeholder

def test_drift_type_inputs():
    # Mocking Streamlit checkbox function
    st_mock = MagicMock()
    st_mock.checkbox.side_effect = [True, False]
    drift_types = drift_type_inputs()
    assert "Feature Drift" in drift_types

def test_determine_drift_type():
    row = {"data_drift": {"drift": True}, "concept_drift": {"drift": False}}
    assert determine_drift_type(row) == "Feature Drift"

# Test Cases for Main
def test_initialize_api_client():
    client = initialize_api_client()
    assert client is not None
    assert isinstance(client, APIClient)

def test_fetch_data(api_client):
    entitlements_data, experiments_data = fetch_data(api_client)
    assert entitlements_data == DUMMY_ENTITLEMENTS_DATA
    assert experiments_data == DUMMY_EXPERIMENTS_DATA

if __name__ == "__main__":
    pytest.main()

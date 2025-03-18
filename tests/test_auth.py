import requests
import json
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# API base URL
BASE_URL = 'http://localhost:5000'


def test_root_endpoint():
    """Test the root endpoint to verify server is running"""
    logger.info("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")

    logger.info(f"Status Code: {response.status_code}")
    logger.info(f"Response: {response.text}")

    return response.status_code == 200


def test_registration():
    """Test user registration endpoint"""
    endpoint = f"{BASE_URL}/api/auth/register"
    test_user = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPass123!"
    }

    logger.info(f"Testing registration at {endpoint}...")
    logger.info(f"Request data: {json.dumps(test_user)}")

    response = requests.post(endpoint, json=test_user)

    logger.info(f"Status Code: {response.status_code}")

    try:
        response_data = response.json()
        logger.info(f"Response: {json.dumps(response_data)}")
    except json.JSONDecodeError:
        logger.info(f"Response (not JSON): {response.text}")

    return response.status_code in [201, 409]  # Success or User already exists


def test_login():
    """Test user login endpoint"""
    endpoint = f"{BASE_URL}/api/auth/login"
    test_user = {
        "username": "testuser",
        "password": "TestPass123!"
    }

    logger.info(f"Testing login at {endpoint}...")
    logger.info(f"Request data: {json.dumps(test_user)}")

    response = requests.post(endpoint, json=test_user)

    logger.info(f"Status Code: {response.status_code}")

    try:
        response_data = response.json()
        logger.info(f"Response: {json.dumps(response_data)}")

        # Return the token if login successful
        if response.status_code == 200:
            return response_data.get('token')
    except json.JSONDecodeError:
        logger.info(f"Response (not JSON): {response.text}")

    return None


def test_profile(token):
    """Test protected profile endpoint"""
    if not token:
        logger.info("Skipping profile test - no token available")
        return False

    endpoint = f"{BASE_URL}/api/auth/profile"

    logger.info(f"Testing profile at {endpoint}...")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(endpoint, headers=headers)

    logger.info(f"Status Code: {response.status_code}")

    try:
        response_data = response.json()
        logger.info(f"Response: {json.dumps(response_data)}")
    except json.JSONDecodeError:
        logger.info(f"Response (not JSON): {response.text}")

    return response.status_code == 200


def test_analyzer_status():
    """Test analyzer status endpoint"""
    endpoint = f"{BASE_URL}/api/analysis/status"

    logger.info(f"Testing analyzer status at {endpoint}...")

    response = requests.get(endpoint)

    logger.info(f"Status Code: {response.status_code}")

    try:
        response_data = response.json()
        logger.info(f"Response: {json.dumps(response_data)}")
    except json.JSONDecodeError:
        logger.info(f"Response (not JSON): {response.text}")

    return response.status_code == 200


def main():
    """Run all tests in sequence"""
    logger.info("=== Starting DrumTracKAI API Tests ===")

    # Test if server is running
    if not test_root_endpoint():
        logger.error("Server is not running or root endpoint test failed. Aborting tests.")
        return

    # Test registration
    if not test_registration():
        logger.warning("Registration test failed. Continuing with other tests...")

    # Test login
    token = test_login()
    if not token:
        logger.warning("Login test failed. Protected endpoints will not be tested.")

    # Test protected profile endpoint
    test_profile(token)

    # Test analyzer status
    test_analyzer_status()

    logger.info("=== All tests completed ===")


if __name__ == "__main__":
    main()
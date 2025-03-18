# test_registration.py
import requests
import json
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL
base_url = 'http://localhost:5000'


def test_endpoint(endpoint):
    """Helper function to test an endpoint"""
    try:
        response = requests.get(f'{base_url}{endpoint}', timeout=5)
        logger.info(f"{endpoint} Endpoint Response:")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {response.headers}")
        logger.info(f"Response Content: {response.text}")
        return response
    except Exception as err:
        logger.error(f"{endpoint} endpoint error: {err}")
        logger.error(traceback.format_exc())
        return None


def test_registration():
    """Test user registration"""
    register_url = f'{base_url}/api/auth/register'

    # Prepare the registration data
    data = {
        'username': 'drumtracker',
        'email': 'drumtracker@example.com',
        'password': 'DrumTrack2025!'
    }

    try:
        # Make the request with additional debugging
        logger.info(f"Sending request to: {register_url}")
        logger.info(f"Request data: {json.dumps(data)}")

        response = requests.post(register_url,
                                 json=data,
                                 headers={'Content-Type': 'application/json'},
                                 timeout=10)

        # Print response details
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {response.headers}")
        logger.info(f"Response Content: {response.text}")

        return response

    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}")
        logger.error("Traceback: %s", traceback.format_exc())
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        logger.error("Traceback: %s", traceback.format_exc())


def main():
    # Test various endpoints
    test_endpoint('/')
    test_endpoint('/health')
    test_endpoint('/routes')

    # Test registration
    test_registration()


if __name__ == '__main__':
    main()
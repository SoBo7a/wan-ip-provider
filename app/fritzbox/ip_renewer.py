import requests
import xml.etree.ElementTree as ET
import os
from app.utils.env_vars import FRITZBOX_HOST
from app.utils.logger import logger

# Define the FritzBox URL to access WANIPConn1
fritzbox_url = f"http://{FRITZBOX_HOST}:49000/igdupnp/control/WANIPConn1"

# SOAP Payload for ForceTermination (to refresh external IP)
SOAP_FORCE_TERMINATION_PAYLOAD = """
<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
        <u:ForceTermination xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1"/>
    </s:Body>
</s:Envelope>
"""

def refresh_public_ip(fritzbox_url=fritzbox_url):
    """
    Refreshes the public IP address by sending a ForceTermination request to the FritzBox device.

    Args:
        fritzbox_url (str): The URL of the FritzBox device. Default is the configured URL in the module.

    Returns:
        str or None: The response text from the FritzBox device if successful, or None if there was an error.

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails for any reason.
    """
    # Define the SOAP action to force termination and refresh the public IP
    soap_action = "urn:schemas-upnp-org:service:WANIPConnection:1#ForceTermination"
    
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": soap_action
    }

    try:
        # Log the request details for debugging
        logger.info(f"Sending ForceTermination request to FritzBox at {fritzbox_url}")

        # Send the request to FritzBox to refresh the public IP
        response = requests.post(
            fritzbox_url,
            data=SOAP_FORCE_TERMINATION_PAYLOAD,
            headers=headers,
            timeout=10  # Add a timeout to prevent hanging indefinitely
        )

        # Raise an error if the response status code is not successful
        response.raise_for_status()

        # Log the successful request response for debugging
        logger.info("Public IP refresh successful.")
        
        # Return the response text from FritzBox (optional to parse)
        return response.text

    except requests.exceptions.Timeout:
        # Handle the case where the request times out
        logger.error(f"Timeout occurred while trying to refresh public IP at {fritzbox_url}")
        return None
    except requests.exceptions.RequestException as e:
        # Log any other request-related error (e.g., network issues, bad responses)
        logger.error(f"Error during public IP refresh request: {e}")
        return None

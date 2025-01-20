import os
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPDigestAuth
from app.utils.env_vars import FRITZBOX_HOST
from app.utils.logger import logger

# Base URL for FritzBox UPnP service
fritzbox_url = f"http://{FRITZBOX_HOST}:49000/igdupnp/control/WANIPConn1"

# SOAP actions for IPv4 and IPv6 IP fetching
SOAP_ACTIONS = {
    "ipv4": "urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIPAddress",
    "ipv6": "urn:schemas-upnp-org:service:WANIPConnection:1#X_AVM_DE_GetExternalIPv6Address"
}

# SOAP payloads for IPv4 and IPv6 IP fetching
SOAP_PAYLOADS = {
    "ipv4": """
    <?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
                s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <s:Body>
            <u:GetExternalIPAddress xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1"/>
        </s:Body>
    </s:Envelope>
    """,
    "ipv6": """
    <?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
                s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <s:Body>
            <u:X_AVM_DE_GetExternalIPv6Address xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1"/>
        </s:Body>
    </s:Envelope>
    """
}

def get_external_ip(action: str, payload: str) -> str:
    """
    Sends a SOAP request to the FritzBox to fetch the external IP address (IPv4 or IPv6).

    Args:
        action (str): The SOAP action to be executed (IPv4 or IPv6).
        payload (str): The SOAP payload that contains the request.

    Returns:
        str: The XML response from the FritzBox containing the IP address.

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails or the response is invalid.
    """
    headers = {
        "SOAPAction": action,
        "Content-Type": "text/xml; charset=utf-8"
    }
    
    try:
        logger.debug(f"Sending request to FritzBox for action: {action}")
        response = requests.post(
            fritzbox_url,
            data=payload,
            headers=headers,
            timeout=10  # Add a timeout to avoid hanging indefinitely
        )
        response.raise_for_status()  # Raise an exception for bad HTTP status codes
        logger.debug(f"Received response from FritzBox for action: {action}")
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error while fetching external IP with action {action}: {e}")
        raise  # Re-raise the exception for further handling if needed

def parse_ip(response: str, tag_name: str) -> str:
    """
    Parses the IP address from the SOAP response XML.

    Args:
        response (str): The XML response containing the IP address.
        tag_name (str): The XML tag that contains the IP address (either 'NewExternalIPAddress' or 'NewExternalIPv6Address').

    Returns:
        str: The IP address if found, otherwise None.

    Raises:
        ValueError: If the XML structure is invalid or the expected tag is not found.
    """
    try:
        root = ET.fromstring(response)
        namespace = {"s": "http://schemas.xmlsoap.org/soap/envelope/"}
        ip_element = root.find(f".//{tag_name}", namespace)

        if ip_element is not None:
            logger.debug(f"Found IP address: {ip_element.text}")
            return ip_element.text
        else:
            logger.warning(f"Tag '{tag_name}' not found in the response XML.")
            return None
    except ET.ParseError as e:
        logger.error(f"Error parsing XML response: {e}")
        raise ValueError("Invalid XML response")

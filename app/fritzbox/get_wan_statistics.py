import requests
import xml.etree.ElementTree as ET
from app.utils.logger import logger
from app.utils.env_vars import FRITZBOX_HOST

# Define the FritzBox URL to access WANIPConn1
FRITZBOX_URL = f"http://{FRITZBOX_HOST}:49000/igdupnp/control/"

# Define common SOAP headers
SOAP_HEADERS = {
    "Content-Type": "text/xml; charset=utf-8"
}

# Define the actions for various SOAP requests
SOAP_ACTIONS = {
    "link_properties": "urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1#GetCommonLinkProperties",
    "status_info": "urn:schemas-upnp-org:service:WANIPConnection:1#GetStatusInfo",
    "total_bytes_sent": "urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1#GetTotalBytesSent",
    "total_bytes_received": "urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1#GetTotalBytesReceived",
}

def send_soap_request(action, payload, service):
    """
    Sends a SOAP request to the specified FritzBox service and returns the parsed XML response.

    Args:
        action (str): The SOAPAction header value.
        payload (str): The SOAP request body in XML format.
        service (str): The FritzBox service URL endpoint.

    Returns:
        xml.etree.ElementTree.Element: The root element of the parsed XML response.

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.
        ValueError: If the response XML is not valid or expected data is missing.
    """
    url = f"{FRITZBOX_URL}{service}"
    headers = SOAP_HEADERS.copy()
    headers["SOAPAction"] = action
    try:
        logger.info(f"Sending SOAP request to {url} with action {action}")
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()

        # Parse the response XML
        response_xml = ET.fromstring(response.text)
        logger.debug(f"SOAP response received: {ET.tostring(response_xml, 'unicode')}")
        return response_xml
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for action {action} to {url}: {e}")
        raise
    except ValueError as e:
        logger.error(f"Failed to parse SOAP response for action {action}: {e}")
        raise

def format_bytes(size):
    """
    Converts bytes to a human-readable format (e.g., KB, MB, GB, TB).

    Args:
        size (int): The size in bytes.

    Returns:
        str: The size in a human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"  # Handle very large sizes

def format_duration(seconds):
    """
    Converts seconds to a human-readable format (e.g., seconds, minutes, hours, days).

    Args:
        seconds (int): The duration in seconds.

    Returns:
        str: The duration in a human-readable format.
    """
    intervals = (
        ('d', 86400),  # Days
        ('h', 3600),   # Hours
        ('m', 60),     # Minutes
        ('s', 1),      # Seconds
    )
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append(f"{value}{name}")
    return " ".join(result)

def get_wan_statistics(human_readable=False):
    """
    Retrieves WAN statistics from the FritzBox device, including link properties, status info, 
    and total bytes sent/received.

    Args:
        human_readable (bool): Whether to format the returned values in a human-readable format.

    Returns:
        dict: A dictionary with WAN statistics, formatted according to the `human_readable` flag.
        If an error occurs, an error message will be returned instead.
    """
    try:
        # Get Link Properties
        payload = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
                                   s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                        <s:Body>
                            <u:GetCommonLinkProperties xmlns:u="urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1"/>
                        </s:Body>
                     </s:Envelope>"""
        link_response = send_soap_request(SOAP_ACTIONS["link_properties"], payload, "WANCommonIFC1")
        max_down = int(link_response.find(".//NewLayer1DownstreamMaxBitRate").text)
        max_up = int(link_response.find(".//NewLayer1UpstreamMaxBitRate").text)

        # Get Status Info
        payload = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
                                   s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                        <s:Body>
                            <u:GetStatusInfo xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1"/>
                        </s:Body>
                     </s:Envelope>"""
        status_response = send_soap_request(SOAP_ACTIONS["status_info"], payload, "WANIPConn1")
        uptime = int(status_response.find(".//NewUptime").text)

        # Get Total Bytes Sent
        payload = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
                                   s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                        <s:Body>
                            <u:GetTotalBytesSent xmlns:u="urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1"/>
                        </s:Body>
                     </s:Envelope>"""
        bytes_sent_response = send_soap_request(SOAP_ACTIONS["total_bytes_sent"], payload, "WANCommonIFC1")
        bytes_sent = int(bytes_sent_response.find(".//NewTotalBytesSent").text)

        # Get Total Bytes Received
        payload = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
                                   s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                        <s:Body>
                            <u:GetTotalBytesReceived xmlns:u="urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1"/>
                        </s:Body>
                     </s:Envelope>"""
        bytes_received_response = send_soap_request(SOAP_ACTIONS["total_bytes_received"], payload, "WANCommonIFC1")
        bytes_received = int(bytes_received_response.find(".//NewTotalBytesReceived").text)

        # Return data in human-readable format if requested
        if human_readable:
            return {
                "max_downstream_speed": format_bytes(max_down) + "ps",
                "max_upstream_speed": format_bytes(max_up) + "ps",
                "uptime": format_duration(uptime),
                "bytes_sent": format_bytes(bytes_sent),
                "bytes_received": format_bytes(bytes_received),
            }

        # Return raw data in bytes/seconds format
        return {
            "max_downstream_speed_bytes": max_down,
            "max_upstream_speed_bytes": max_up,
            "uptime_seconds": uptime,
            "bytes_sent": bytes_sent,
            "bytes_received": bytes_received,
        }

    except Exception as e:
        logger.error(f"Failed to retrieve WAN statistics: {e}")
        return {"error": str(e)}

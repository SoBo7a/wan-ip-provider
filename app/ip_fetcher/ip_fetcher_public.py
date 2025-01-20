import random
import socket
import requests
from datetime import datetime, timedelta
import subprocess
from app.utils.logger import logger
from app.database.database import SessionLocal, FailedService, init_db

# List of services to get public IP from
IP_SERVICES = [
    {"name": "api.ipify.org", "url": "https://api.ipify.org/"},
    {"name": "checkip.amazonaws.com", "url": "https://checkip.amazonaws.com"},
    {"name": "dnsomatic.com", "url": "https://myip.dnsomatic.com"},
    {"name": "icanhazip.com", "url": "https://ipv4.icanhazip.com/"},
    {"name": "ident.me", "url": "https://ident.me/"},
    {"name": "ifconfig.co", "url": "https://ipv4.ifconfig.co/ip"},
    {"name": "ifconfig.me", "url": "https://ipv4.ifconfig.me/ip"},
    {"name": "ipecho.net", "url": "https://ipv4.ipecho.net/plain"},
    {"name": "ipinfo.io", "url": "https://ipinfo.io/json"},
    {"name": "myexternalip.com", "url": "https://myexternalip.com/raw"},
    {"name": "whatismyip.akamai.com", "url": "https://whatismyip.akamai.com/"}
]

def record_failed_service(service_name):
    """
    Record a failed service into the database.
    """
    session = SessionLocal()
    try:
        failed_service = FailedService(service_name=service_name)
        session.add(failed_service)
        session.commit()
    except Exception as e:
        logger.error(f"Error recording failed service {service_name}: {e}")
    finally:
        session.close()


def clean_old_failures():
    """
    Remove entries from the database that are older than 24 hours.
    """
    session = SessionLocal()
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        session.query(FailedService).filter(FailedService.timestamp < cutoff_time).delete()
        session.commit()
    except Exception as e:
        logger.error(f"Error cleaning old failures: {e}")
    finally:
        session.close()


def get_failed_services():
    """
    Retrieve the names of services that failed in the last 24 hours.
    """
    session = SessionLocal()
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        failed_services = session.query(FailedService.service_name).filter(FailedService.timestamp >= cutoff_time).all()
        return {service.service_name for service in failed_services}
    except Exception as e:
        logger.error(f"Error fetching failed services: {e}")
        return set()
    finally:
        session.close()


def get_public_ip():
    """
    Attempts to fetch the public IPv4 address by trying multiple services.
    """
    clean_old_failures()
    failed_services = get_failed_services()
    available_services = [service for service in IP_SERVICES if service["name"] not in failed_services]

    if not available_services:
        logger.error("No available services to fetch public IP after checking database.")
        return None, None

    random.shuffle(available_services)

    for service in available_services:
        try:
            ip = fetch_ip_from_service(service)
            if ip and is_valid_ip(ip):
                return ip, service["name"]
            logger.warning(f"Received an invalid or IPv6 address from {service['name']}: {ip}, trying the next service.")
        except Exception as e:
            logger.warning(f"Error fetching public IP from {service['name']}: {e}")
            record_failed_service(service["name"])

    logger.error("All attempts to fetch a valid public IPv4 address failed.")
    return None, None


def fetch_ip_from_service(service):
    """
    Fetches the public IP address from a given service.
    """
    response = requests.get(service["url"])
    response.raise_for_status()

    logger.info(f"Fetching IP from: {service['name']}")

    if service["name"] == "ipinfo.io":
        return response.json().get("ip")
    return response.text.strip()


def is_valid_ip(ip):
    """
    Checks if the given IP address is a valid IPv4 address.
    """
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        return False

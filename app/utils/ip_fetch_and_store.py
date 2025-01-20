import os
import time
from .env_vars import USE_FALLBACK, IP_SOURCE
from app.database.database import SessionLocal, IPAddress
from .logger import logger
from app.ip_fetcher.ip_fetcher_fritzbox import get_external_ip, parse_ip, SOAP_ACTIONS, SOAP_PAYLOADS
from app.ip_fetcher.ip_fetcher_public import get_public_ip

def fetch_and_store_ips():
    """
    Fetches the current external IPv4 and IPv6 addresses based on the configured source,
    and updates or inserts the values into the database. It handles IP fetching from FritzBox or 
    public sources and updates the database with the latest IPs.

    Logs all steps for traceability and error handling.
    """
    db = SessionLocal()  # Start a session for DB access
    try:
        # Initialize variables for IPs
        ipv4, ipv6 = None, None

        # Log the IP source being used
        logger.info(f"Fetching IPs from source: {IP_SOURCE}")

        # If IP source is FritzBox
        if IP_SOURCE == "fritzbox":
            try:
                logger.info("Fetching IPs from FritzBox...")

                # Fetch current IPs from FritzBox
                ipv4_response = get_external_ip(SOAP_ACTIONS["ipv4"], SOAP_PAYLOADS["ipv4"])
                ipv6_response = get_external_ip(SOAP_ACTIONS["ipv6"], SOAP_PAYLOADS["ipv6"])

                # Parse the responses for IPv4 and IPv6
                ipv4 = parse_ip(ipv4_response, "NewExternalIPAddress")
                ipv6 = parse_ip(ipv6_response, "NewExternalIPv6Address")

                logger.info(f"Fetched IPs from FritzBox: IPv4={ipv4}, IPv6={ipv6}")
            except Exception as e:
                logger.error(f"Error fetching IPs from FritzBox: {e}")
                # If FritzBox fetch fails and fallback is enabled, try fetching public IP
                if USE_FALLBACK:
                    logger.info("FritzBox fetch failed, falling back to public IP fetch.")
                    ipv4, _ = get_public_ip()
                    ipv6 = None  # set IPv6 to None if using public IP fetch
                else:
                    logger.error("FritzBox fetch failed, and no fallback is enabled. Exiting.")
                    return
        
        # If IP source is public IP fetch
        elif IP_SOURCE == "public":
            ipv6 = None  # set IPv6 to None as public IP fetch doesn't provide IPv6
            try:
                logger.info("Fetching public IP...")
                ipv4, _ = get_public_ip()
                logger.info(f"Fetched public IP: IPv4={ipv4}")
            except Exception as e:
                logger.error(f"Public IP fetch failed: {e}")
                return

        else:
            logger.error(f"Invalid IP source configuration: {IP_SOURCE}")
            return

        # Fetch the existing entry from the database (if any)
        existing_entry = db.query(IPAddress).first()

        # Check if the IPs have changed
        if existing_entry:
            logger.info("Checking for IP changes...")

            if existing_entry.ipv4 == ipv4 and existing_entry.ipv6 == ipv6:
                # No changes in IP addresses, log and return
                logger.info("IPs have not changed. No update required.")
                return

            # Update the existing entry
            existing_entry.ipv4 = ipv4
            existing_entry.ipv6 = ipv6
            db.commit()  # Commit changes to DB
            logger.info(f"Updated IPs in database: IPv4={ipv4}, IPv6={ipv6}")

        else:
            # If no entry exists, create a new one
            logger.info("No existing IP entry found, creating a new one.")
            ip_entry = IPAddress(ipv4=ipv4, ipv6=ipv6)
            db.add(ip_entry)
            db.commit()  # Commit new entry to DB
            logger.info(f"Added new IPs to database: IPv4={ipv4}, IPv6={ipv6}")

    except Exception as e:
        logger.error(f"Error updating IPs: {e}")
    finally:
        db.close()  # Ensure DB session is closed

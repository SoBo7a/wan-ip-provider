import os
import time
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.utils.env_vars import ENABLE_REFRESH_IP_ENDPOINT, RATE_LIMIT_IP_RENEWAL
from app.database.database import SessionLocal, init_db, IPAddress
from app.fritzbox.ip_renewer import refresh_public_ip
from app.utils.ip_fetch_and_store import fetch_and_store_ips
from app.fritzbox.get_wan_statistics import get_wan_statistics

last_refresh_time = 0

app = FastAPI()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to get all IPs
@app.get("/ips")
def get_ips(db: Session = Depends(get_db)):
    """
    Returns all stored IP addresses (IPv4 and IPv6 only) as a list.
    If no entries are found, returns an empty list.
    """
    ips = db.query(IPAddress.ipv4, IPAddress.ipv6).all()

    if not ips:  # Handle the case when there are no IPs in the database
        return {"message": "No IP addresses found", "data": []}

    # Handle the case where some entries might have missing fields
    return [{"ipv4": ipv4, "ipv6": ipv6 if ipv6 else "N/A"} for ipv4, ipv6 in ips]

# Endpoint to get the current IPv4
@app.get("/ipv4")
def get_ipv4(db: Session = Depends(get_db)):
    """
    Returns the current IPv4 address.
    """
    entry = db.query(IPAddress).first()
    if entry and entry.ipv4:
        return {"ipv4": entry.ipv4}
    return {"error": "IPv4 address not found"}

# Endpoint to get the current IPv6
@app.get("/ipv6")
def get_ipv6(db: Session = Depends(get_db)):
    """
    Returns the current IPv6 address.
    """
    entry = db.query(IPAddress).first()
    if entry and entry.ipv6:
        return {"ipv6": entry.ipv6}
    return {"error": "IPv6 address not found"}

# Force new external IP (FritzBox only)
@app.get("/refresh-public-ip")
async def trigger_refresh_public_ip(db: Session = Depends(get_db)):
    """
    Forces a new public IP if enabled via environment variable.
    Only allows one call every RATE_LIMIT_IP_RENEWAL seconds globally.
    """
    global last_refresh_time

    if not ENABLE_REFRESH_IP_ENDPOINT:
        raise HTTPException(status_code=403, detail="This endpoint is disabled by configuration.")

    # Check the rate limit
    current_time = time.time()
    if current_time - last_refresh_time < RATE_LIMIT_IP_RENEWAL:
        remaining_time = RATE_LIMIT_IP_RENEWAL - (current_time - last_refresh_time)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Please wait {int(remaining_time)} seconds before retrying.",
        )

    # Update the last refresh time
    last_refresh_time = current_time

    response = refresh_public_ip()
    if response:
        time.sleep(20) # Give the Router some time to get a new public IP
        fetch_and_store_ips()
        ips = db.query(IPAddress.ipv4, IPAddress.ipv6).all()
        return {
            "message": "Refreshed public IP successfully",
            "data": [{"ipv4": ipv4, "ipv6": ipv6 if ipv6 else "N/A"} for ipv4, ipv6 in ips],
        }
    else:
        return {"message": "Failed to force public IP refresh"}
    
# Endpoint to get the current IPv6
@app.get("/wan-stats")
def get_wan_stats(format: str = Query(None)):
    """
    Returns WAN related Statistics from the FritzBox
    """
    if format is not None:
        return get_wan_statistics(True)
    
    return get_wan_statistics()
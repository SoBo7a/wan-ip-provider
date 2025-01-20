# IP Fetch and Store Docker Container

This Docker container is designed to periodically fetch the public IP addresses (IPv4 and IPv6) of a device (such as a FritzBox router) and store them in a database. It also exposes a FastAPI web service with various endpoints to query and interact with the stored IPs. Additionally, it allows you to force a public IP refresh for FritzBox routers and provides WAN statistics.

## Features:
- **Fetch and Store IPs**: Periodically fetches and stores public IPv4 and IPv6 addresses.
- **API Endpoints**: Provides a set of RESTful API endpoints to retrieve the public IP addresses, and more if used with a FritzBox.
- **FritzBox Integration**: Supports FritzBox routers for IP refresh and WAN statistics.
- **Database Support**: Uses SQLAlchemy and SQLite to store IP addresses in a simple database.

## Docker Installation

To run this container on your machine, follow the instructions below:

### Prerequisites:
- Docker installed on your machine. [Get Docker](https://docs.docker.com/get-docker/)
- Docker Compose

### Steps to Build and Run:

1. **Clone the repository**:

    ```bash
    git clone https://github.com/SoBo7a/wan-ip-provider.git
    cd wan-ip-provider && mkdir data
    ```

2. **Build the Docker image using Dockerfile**:

    ```bash
    docker build -t wan-ip-provider .
    ```

### Docker Compose

Use the docker-compose.yml from the project to deploy the container:
```bash
docker compose up -d
```

### API Documentation
This application exposes the following API endpoints:

1. `/ips` (GET)
Description: Returns a list of all stored IP addresses (IPv4 and IPv6).
Response:
```json
{
  "message": "No IP addresses found",
  "data": []
}
```

Or, if IPs exist:
```json
[
  {"ipv4": "192.168.0.1", "ipv6": "fe80::1"}
]
```

2. `/ipv4` (GET)
Description: Returns the current IPv4 address.
Response:
```json
{
  "ipv4": "192.168.0.1"
}
```

3. `/ipv6` (GET)
Description: Returns the current IPv6 address.
Response:
```json
{
  "ipv6": "fe80::1"
}
```

4. `/refresh-public-ip` (GET)
Description: Forces a new public IP refresh (only for FritzBox). This endpoint can only be called once every RATE_LIMIT_IP_RENEWAL seconds.
Response (on success):
```json
{
  "message": "Refreshed public IP successfully",
  "data": [
    {"ipv4": "192.168.0.1", "ipv6": "fe80::1"}
  ]
}
```

Response (on failure):
```json
{
  "message": "Failed to force public IP refresh"
}
```

5. `/wan-stats` (GET)
Description: Returns WAN-related statistics from the FritzBox. You can pass a format query parameter to get human-readable results (e.g., ?format=true).
Response:
```json
{
  "max_downstream_speed": "100.00 Mbps",
  "max_upstream_speed": "20.00 Mbps",
  "uptime": "1d 2h 30m",
  "bytes_sent": "500.00 MB",
  "bytes_received": "800.00 MB"
}
```

### Environment Variables

The following environment variables can be used in the docke-compose.yml to configure the application:

- `API_HOST`: The host for the API (default: `0.0.0.0`).
- `API_PORT`: The port for the API (default: `9090`).
- `UPDATE_INTERVAL`: The interval (in seconds) for fetching and storing IP addresses (default: `60`).
- `USE_FALLBACK`: Whether to use fallback for fetching IP addresses (default: `True`).
- `IP_SOURCE`: The source for fetching IP addresses. Can be `fritzbox` or `public` for external sources (default: `fritzbox`).
- `FRITZBOX_HOST`: The hostname or IP address of the FritzBox router (default: `fritz.box`).
- `ENABLE_REFRESH_IP_ENDPOINT`: Whether the `/refresh-public-ip` endpoint is enabled (default: `True`).
- `RATE_LIMIT_IP_RENEWAL`: The minimum time (in seconds) between refresh requests to `/refresh-public-ip` (default: `300`).
- `LOG_LEVEL`: The log level (e.g., `INFO`, `DEBUG`, `ERROR`) (default: `INFO`).

### Troubleshooting
If you experience issues, check the logs of the Docker container to identify any errors. You can view logs with:
```bash
docker logs -f wan-ip-provider
```

Ensure that the necessary environment variables are properly set, especially for accessing the FritzBox router.

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

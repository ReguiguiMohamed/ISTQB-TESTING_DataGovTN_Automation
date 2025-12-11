# Docker Setup for Cross-Browser Testing

This project uses Selenium Grid with Docker containers to run cross-browser tests across Chrome, Firefox, and Edge browsers.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose installed

## Setup Instructions

### 1. Start the Selenium Grid

Run the following command in the project root directory:

```bash
docker-compose up -d
```

This will start:
- Selenium Hub (acts as the central coordinator)
- Chrome Node
- Firefox Node
- Edge Node

### 2. Verify the Grid is Running

Open your browser and navigate to `http://localhost:4444` to see the Selenium Grid dashboard.

### 3. Run Tests with Docker

To run cross-browser tests using the Docker setup, use the `--remote` flag:

```bash
# Run with Chrome on Docker
pytest tests/cross_browser/test_smoke_cross_browser.py --remote --browser=chrome

# Run with Firefox on Docker
pytest tests/cross_browser/test_smoke_cross_browser.py --remote --browser=firefox

# Run with Edge on Docker
pytest tests/cross_browser/test_smoke_cross_browser.py --remote --browser=edge

# Run with specific hub host and port (if different from default)
pytest tests/cross_browser/test_smoke_cross_browser.py --remote --hub-host=localhost --hub-port=4444 --browser=chrome
```

### 4. Run Parallel Tests

You can run tests in parallel across different browsers:

```bash
# Run all cross-browser tests in parallel
pytest tests/cross_browser/test_smoke_cross_browser.py --remote -n 3
```

## Available Services

- **Selenium Hub**: `http://localhost:4444`
- **Chrome Node**: Automatically connected to the hub
- **Firefox Node**: Automatically connected to the hub
- **Edge Node**: Automatically connected to the hub

## Stopping the Grid

To stop the Docker containers:

```bash
docker-compose down
```

To stop and remove all containers, networks, and volumes:

```bash
docker-compose down -v
```

## Troubleshooting

### Docker containers won't start
- Make sure Docker Desktop is running
- Check that no other services are using the same ports
- Look for error messages in the Docker output

### Tests can't connect to the hub
- Verify that the Selenium Grid is running: `docker-compose ps`
- Check the browser console at `http://localhost:4444`
- Ensure your test command includes the `--remote` flag

### Performance considerations
- The Chrome and Edge nodes require more memory (shm_size: 2gb)
- If you run into memory issues, reduce the number of concurrent sessions
- Adjust the NODE_MAX_INSTANCES and NODE_MAX_SESSION values in docker-compose.yml as needed
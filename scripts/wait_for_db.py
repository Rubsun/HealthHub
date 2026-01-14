#!/usr/bin/env python3
import os
import sys
import time
import socket


def wait_for_postgres(host: str, port: int, max_retries: int = 30, retry_interval: int = 2):
    print(f"Waiting for PostgreSQL at {host}:{port}...")
    
    for attempt in range(1, max_retries + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"PostgreSQL is up after {attempt} attempt(s)")
                return True
        except socket.gaierror as e:
            pass
        except Exception as e:
            print(f"Connection error: {e}")
        
        print(f"PostgreSQL is unavailable - sleeping (attempt {attempt}/{max_retries})")
        time.sleep(retry_interval)
    
    print(f"Error: PostgreSQL is not available after {max_retries} attempts")
    return False


def main():
    host = os.environ.get("POSTGRES_HOST", "postgres")
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    
    if not wait_for_postgres(host, port):
        sys.exit(1)
    
    print("Database is ready!")


if __name__ == "__main__":
    main()


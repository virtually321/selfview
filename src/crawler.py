#!/usr/bin/env python3
import os, sys, logging, requests
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

TARGET = os.getenv("TARGET_URL", "https://httpbin.org/get")
headers = {"User-Agent": "test-crawler/0.1"}
log.info("start crawling -> %s", TARGET)

try:
    r = requests.get(TARGET, headers=headers, timeout=10)
    r.raise_for_status()
    log.info("success %d chars", len(r.text))
except Exception as e:
    log.error("failed: %s", e)
    sys.exit(1)

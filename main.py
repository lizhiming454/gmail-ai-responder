#!/usr/bin/env python3
"""
Gmail AI Auto-Responder
=======================
Monitors your Gmail inbox and replies using OpenAI GPT.

Usage:
    python main.py            # Run once
    python main.py --daemon   # Run continuously
"""
import os
import time
import logging
import argparse
import schedule
from dotenv import load_dotenv
import colorlog

from core.gmail_client import GmailClient
from core.ai_responder import AIResponder
from core.rule_engine import RuleEngine

load_dotenv()
os.makedirs("logs", exist_ok=True)

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s]%(reset)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
file_handler = logging.FileHandler("logs/responder.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logger = logging.getLogger("GmailAIResponder")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(file_handler)


def process_emails():
    logger.info("=== Checking for new emails ===")
    gmail = GmailClient(
        credentials_file=os.getenv("GOOGLE_CREDENTIALS_FILE", "config/credentials.json")
    )
    ai = AIResponder(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o")
    )
    rules = RuleEngine()
    label = os.getenv("PROCESSED_LABEL", "AUTO_REPLIED")
    max_per_run = int(os.getenv("MAX_PER_RUN", 10))

    unread = gmail.fetch_unread(max_results=max_per_run)
    if not unread:
        logger.info("No new emails found.")
        return

    logger.info(f"Found {len(unread)} unread email(s).")
    for stub in unread:
        email = gmail.get_detail(stub["id"])
        if not email:
            continue
        logger.info(f"Processing: [{email['subject']}] from {email['sender']}")
        system_prompt = rules.match(email)
        if system_prompt is None:
            logger.info("Skipped (blacklisted or no rule match).")
            continue
        reply = ai.generate_reply(email, system_prompt)
        if reply:
            if gmail.send_reply(email, reply):
                gmail.mark_processed(email["id"], label)


def main():
    parser = argparse.ArgumentParser(description="Gmail AI Auto-Responder")
    parser.add_argument("--daemon", action="store_true", help="Run continuously")
    args = parser.parse_args()

    if args.daemon:
        interval = int(os.getenv("POLL_INTERVAL", 60))
        logger.info(f"Daemon mode: every {interval}s. Ctrl+C to stop.")
        schedule.every(interval).seconds.do(process_emails)
        process_emails()
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        process_emails()


if __name__ == "__main__":
    main()

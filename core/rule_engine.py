import json
import logging

logger = logging.getLogger("GmailAIResponder")


class RuleEngine:
    def __init__(self, rules_file="config/rules.json"):
        with open(rules_file) as f:
            data = json.load(f)
        self.rules = sorted(data["rules"], key=lambda r: r["priority"])
        self.blacklist = data["blacklist"]

    def is_blacklisted(self, email):
        sender = email["sender"].lower()
        subject = email["subject"].lower()
        for kw in self.blacklist["from_contains"]:
            if kw.lower() in sender:
                return True
        for kw in self.blacklist["subject_contains"]:
            if kw.lower() in subject:
                return True
        return False

    def match(self, email):
        if self.is_blacklisted(email):
            logger.info(f"Blacklisted: {email['sender']} — skipping.")
            return None
        sender = email["sender"].lower()
        subject = email["subject"].lower()
        for rule in self.rules:
            from_match = any(kw.lower() in sender for kw in rule["match"]["from_contains"])
            subj_match = any(kw.lower() in subject for kw in rule["match"]["subject_contains"])
            if not rule["match"]["from_contains"] and not rule["match"]["subject_contains"]:
                return rule["system_prompt"]
            if from_match or subj_match:
                logger.info(f"Rule matched: {rule['name']}")
                return rule["system_prompt"]
        return None

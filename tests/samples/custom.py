from datadiligence import Evaluator
from datadiligence.rules import Rule


class CustomEvaluator(Evaluator):
    def is_allowed(self, **kwargs):
        for rule in self.rules:
            if rule.is_ready() and not rule.is_allowed(**kwargs):
                return False
        return True


class CustomRule(Rule):
    def is_ready(self):
        return True

    def is_allowed(self, sample="", **kwargs):
        if "google" in sample:
            return False
        else:
            return True


class NotReadyRule(Rule):
    def is_ready(self):
        return False

    def is_allowed(self, **kwargs):
        return True


class CustomRule2(Rule):
    def is_ready(self):
        return True

    def is_allowed(self, url="", **kwargs):
        if "google" in url:
            return False
        else:
            return True

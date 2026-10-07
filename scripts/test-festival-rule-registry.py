#!/usr/bin/env python3
import os
import sys
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import festival_rules

expected={
    "rama-navami","hanuman-jayanti","akshaya-tritiya","vat-savitri",
    "durga-puja","ganesh-chaturthi","raksha-bandhan","navratri",
    "dussehra","holi","karwa-chauth","janmashtami","diwali",
}
assert set(festival_rules.SUPPORTED_KINDS)==expected
assert len(festival_rules.FESTIVAL_RULES)==13

for kind,rule in festival_rules.FESTIVAL_RULES.items():
    assert rule["selector"] in festival_rules.SELECTORS,(kind,rule)
    assert rule["profile"],kind
    assert rule["title"],kind
    assert isinstance(rule["tithi_id"],int),kind

# Direct shared-engine check independent of festivals.py adapter.
event=festival_rules.calculate_event(
    "diwali",2026,19.0760,72.8777,ZoneInfo("Asia/Kolkata"),False
)
assert event["date"]=="2026-11-08",event
assert event["rule"]["selector"]=="pradosh"
assert event["rule"]["profile"]=="diwali"
assert event["vrishabha_lagna_status"]=="calculated-from-lagna-timeline"
assert event["lakshmi_puja"]

print("Festival rule registry fixture passed")

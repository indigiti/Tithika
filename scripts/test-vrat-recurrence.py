#!/usr/bin/env python3
import os
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import panchang
import lunar_occurrences
import vrat_recurrence

tz=ZoneInfo("Asia/Kolkata")
lat,lon=18.5204,73.8567

# Satyanarayana is a Purnima occurrence adapter, not a second lunar engine.
sat=vrat_recurrence.satyanarayana(2026,lat,lon,tz,False)
sat_dates={row["date"] for row in sat}
assert "2026-11-24" in sat_dates,sat
for row in sat:
    start=datetime.fromisoformat(row["tithi_start"])
    end=datetime.fromisoformat(row["tithi_end"])
    mid=start+(end-start)/2
    st=panchang.state_at(mid)
    assert st["tithi_id"]==14,(row,st)

# Masik Durgashtami: Shukla Ashtami must prevail at local sunrise.
durga=vrat_recurrence.durgashtami(2026,lat,lon,tz,False)
durga_dates={row["date"] for row in durga}
for required in ("2026-01-26","2026-08-20","2026-10-19","2026-11-17","2026-12-17"):
    assert required in durga_dates,(required,sorted(durga_dates))
for row in durga:
    sunrise=datetime.fromisoformat(row["sunrise"])+timedelta(seconds=1)
    st=panchang.state_at(sunrise)
    assert st["tithi_id"]==7 and st["paksha"]=="Shukla Paksha",(row,st)

# Skanda Sashti selector: daytime Panchami->Sashti transition stays on that
# civil day; after-sunset transition rolls to the next civil day.
skanda=vrat_recurrence.skanda_sashti(2026,lat,lon,tz,False)
skanda_dates={row["date"] for row in skanda}
for required in ("2026-08-17","2026-09-16","2026-10-16","2026-11-15","2026-12-15"):
    assert required in skanda_dates,(required,sorted(skanda_dates))
for row in skanda:
    start=datetime.fromisoformat(row["tithi_start"])
    end=datetime.fromisoformat(row["tithi_end"])
    mid=start+(end-start)/2
    st=panchang.state_at(mid)
    assert st["tithi_id"]==5 and st["paksha"]=="Shukla Paksha",(row,st)
    civil=start.date()
    sunset=vrat_recurrence.sunset_for(civil,lat,lon,tz)
    expected=civil if sunset and start < sunset else civil+timedelta(days=1)
    assert row["date"]==expected.isoformat(),(row,expected)

# Karthigai: Krittika must be active immediately after sunrise.
karth=vrat_recurrence.karthigai_days(2026,lat,lon,tz,False)
karth_dates={row["date"] for row in karth}
for required in ("2026-09-03","2026-09-30","2026-11-24","2026-12-21"):
    assert required in karth_dates,(required,sorted(karth_dates))
for row in karth:
    sunset=datetime.fromisoformat(row["sunset"])-timedelta(seconds=1)
    assert panchang.state_at(sunset)["nakshatra"]=="Krittika",row

# Rohini Vrat explicitly requires Rohini after local sunrise.
rohini=vrat_recurrence.nakshatra_vrat(
    2026,lat,lon,tz,False,"Rohini","Rohini Vrat"
)
rohini_dates={row["date"] for row in rohini}
for required in ("2026-10-01","2026-10-29","2026-11-25","2026-12-23"):
    assert required in rohini_dates,(required,sorted(rohini_dates))
for row in rohini:
    sunrise=datetime.fromisoformat(row["sunrise"])+timedelta(seconds=1)
    assert panchang.state_at(sunrise)["nakshatra"]=="Rohini",row

# Shravana weekday observances expose both regional lunar-month conventions.
sawan=vrat_recurrence.shravana_weekdays(
    2026,lat,lon,tz,False,0,"Sawan Somwar"
)
assert {x["date"] for x in sawan["purnimanta"]}=={
    "2026-08-03","2026-08-10","2026-08-17","2026-08-24"
},sawan
assert {x["date"] for x in sawan["amanta"]}=={
    "2026-08-17","2026-08-24","2026-08-31","2026-09-07"
},sawan
for profile,rows in sawan.items():
    for row in rows:
        assert date.fromisoformat(row["date"]).weekday()==0,row
        assert vrat_recurrence.normalize_month(row[f"{profile}_month"])=="Shravana",row

gauri=vrat_recurrence.shravana_weekdays(
    2026,lat,lon,tz,False,1,"Mangala Gauri"
)
assert {x["date"] for x in gauri["purnimanta"]}=={
    "2026-08-04","2026-08-11","2026-08-18","2026-08-25"
},gauri
assert {x["date"] for x in gauri["amanta"]}=={
    "2026-08-18","2026-08-25","2026-09-01","2026-09-08"
},gauri
for profile,rows in gauri.items():
    for row in rows:
        assert date.fromisoformat(row["date"]).weekday()==1,row
        assert vrat_recurrence.normalize_month(row[f"{profile}_month"])=="Shravana",row

# ISKCON/GCal-compatible 2026 Pune regression. Published ISKCON dates are
# treated as a hard compatibility target, including Vriddhi and Mahadwadashi.
iskcon_events=[]
for rule in lunar_occurrences.KINDS["ekadashi"]:
    iskcon_events.extend(lunar_occurrences.events_for_rule(2026,rule,lat,lon,tz,False))
iskcon_dates=sorted({
    event["observance"]["iskcon"]["date"]
    for event in iskcon_events
    if event.get("observance") and event["observance"].get("iskcon")
    and event["observance"]["iskcon"].get("date","").startswith("2026-")
})
expected_iskcon=[
    "2026-01-14","2026-01-29","2026-02-13","2026-02-27",
    "2026-03-15","2026-03-29","2026-04-13","2026-04-27",
    "2026-05-13","2026-05-27","2026-06-11","2026-06-25",
    "2026-07-11","2026-07-25","2026-08-09","2026-08-24",
    "2026-09-07","2026-09-22","2026-10-06","2026-10-22",
    "2026-11-05","2026-11-21","2026-12-04","2026-12-20",
]
iskcon_debug=[{
    "name": event.get("name"),
    "start": event.get("start"),
    "end": event.get("end"),
    "iskcon": event.get("observance",{}).get("iskcon"),
    "mahadwadashi": event.get("observance",{}).get("mahadwadashi"),
} for event in iskcon_events if event.get("observance")]
assert iskcon_dates==expected_iskcon,(iskcon_dates,expected_iskcon,iskcon_debug)

print("Vrat recurrence fixture passed")

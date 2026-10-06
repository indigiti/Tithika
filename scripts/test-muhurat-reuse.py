#!/usr/bin/env python3
import os
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import muhurat_reuse
import panchang
import lagna

tz=ZoneInfo("Asia/Kolkata")
lat,lon=18.5204,73.8567

# Hora: Tuesday begins with Mars, with 12 unequal day + 12 unequal night Horas.
hora=muhurat_reuse.hora_day(date(2026,10,6),lat,lon,tz,False)
assert hora["weekday"]=="Tuesday",hora
assert hora["weekday_lord"]=="Mars",hora
assert len(hora["horas"])==24,hora
assert hora["horas"][0]["planet"]=="Mars",hora["horas"][0]
assert len([x for x in hora["horas"] if x["half"]=="day"])==12
assert len([x for x in hora["horas"] if x["half"]=="night"])==12
for a,b in zip(hora["horas"],hora["horas"][1:]):
    gap=(datetime.fromisoformat(b["start"])-datetime.fromisoformat(a["end"])).total_seconds()
    assert abs(gap)<0.01,(a,b,gap)
assert datetime.fromisoformat(hora["horas"][0]["start"])==datetime.fromisoformat(hora["sunrise"])
assert datetime.fromisoformat(hora["horas"][-1]["end"])==datetime.fromisoformat(hora["next_sunrise"])

# Panchaka Rahita: each exact interval must satisfy the modulo-9 evidence.
rahita=muhurat_reuse.panchaka_rahita_day(date(2026,10,6),lat,lon,tz,False)
assert rahita["intervals"]
assert rahita["good_intervals"]
assert datetime.fromisoformat(rahita["intervals"][0]["start"])==datetime.fromisoformat(rahita["sunrise"])
assert datetime.fromisoformat(rahita["intervals"][-1]["end"])==datetime.fromisoformat(rahita["next_sunrise"])
for row in rahita["intervals"]:
    mid=datetime.fromisoformat(row["start"])+(datetime.fromisoformat(row["end"])-datetime.fromisoformat(row["start"]))/2
    state=panchang.state_at(mid)
    rising=lagna.lagna_state(mid,lat,lon)
    tithi=state["tithi_id"]+1
    vara=((date(2026,10,6).weekday()+1)%7)+1
    nak=state["nakshatra_id"]+1
    lag=rising["lagna_id"]+1
    remainder=(tithi+vara+nak+lag)%9
    assert row["tithi_index"]==tithi,row
    assert row["vara_index"]==vara,row
    assert row["nakshatra_index"]==nak,row
    assert row["lagna_index"]==lag,row
    assert row["remainder"]==remainder,row
    assert row["good"]==(remainder in {0,3,5,7}),row

# Sarvartha Siddhi: lock the published October 2026 Pune Hindu-day dates.
sar=muhurat_reuse.yoga_year("sarvartha-siddhi",2026,lat,lon,tz,False)
oct_dates={x["date"] for x in sar if x["date"].startswith("2026-10-")}
assert oct_dates=={
    "2026-10-04","2026-10-05","2026-10-06","2026-10-14",
    "2026-10-18","2026-10-19","2026-10-25","2026-10-27","2026-10-28",
},oct_dates
for row in sar:
    mid=datetime.fromisoformat(row["start"])+(datetime.fromisoformat(row["end"])-datetime.fromisoformat(row["start"]))/2
    st=panchang.state_at(mid)
    weekday=date.fromisoformat(row["date"]).weekday()
    assert st["nakshatra"] in muhurat_reuse.SARVARTHA[weekday],(row,st)

# Amrit Siddhi: exact seven weekday/nakshatra pairings.
amrit=muhurat_reuse.yoga_year("amrit-siddhi",2026,lat,lon,tz,False)
assert any(x["date"]=="2026-10-14" and x["nakshatra"]=="Anuradha" for x in amrit),amrit
for row in amrit:
    weekday=date.fromisoformat(row["date"]).weekday()
    assert row["nakshatra"]==muhurat_reuse.AMRIT_SIDDHI[weekday],row

# Guru Pushya and Ravi Pushya published 2026 date sets.
guru=muhurat_reuse.yoga_year("guru-pushya",2026,lat,lon,tz,False)
assert {x["date"] for x in guru}=={
    "2026-04-23","2026-05-21","2026-06-18"
},guru
assert all(x["weekday"]=="Thursday" and x["nakshatra"]=="Pushya" for x in guru)

ravi_pushya=muhurat_reuse.yoga_year("ravi-pushya",2026,lat,lon,tz,False)
assert {x["date"] for x in ravi_pushya}=={
    "2026-01-04","2026-02-01","2026-03-01",
    "2026-10-04","2026-11-01","2026-11-29",
},ravi_pushya
assert all(x["weekday"]=="Sunday" and x["nakshatra"]=="Pushya" for x in ravi_pushya)

# Dwipushkar: exact 2026 Pune Hindu-day pattern from the three-factor rule.
dwi=muhurat_reuse.yoga_year("dwipushkar",2026,lat,lon,tz,False)
assert {x["date"] for x in dwi}=={
    "2026-01-20","2026-03-15","2026-03-24","2026-06-06",
    "2026-06-07","2026-08-09","2026-10-11","2026-12-05",
},dwi
for row in dwi:
    weekday=date.fromisoformat(row["date"]).weekday()
    assert weekday in muhurat_reuse.PUSHKAR_WEEKDAYS,row
    assert row["tithi_number"] in muhurat_reuse.PUSHKAR_TITHIS,row
    assert row["nakshatra"] in muhurat_reuse.DWI_NAKSHATRAS,row

# Tripushkar: same Bhadra Tithis/weekdays, six Tripada Nakshatras.
tri=muhurat_reuse.yoga_year("tripushkar",2026,lat,lon,tz,False)
for required in ("2026-01-04","2026-04-14","2026-04-19","2026-10-27","2026-10-31","2026-12-29"):
    assert any(x["date"]==required for x in tri),(required,tri)
for row in tri:
    weekday=date.fromisoformat(row["date"]).weekday()
    assert weekday in muhurat_reuse.PUSHKAR_WEEKDAYS,row
    assert row["tithi_number"] in muhurat_reuse.PUSHKAR_TITHIS,row
    assert row["nakshatra"] in muhurat_reuse.TRI_NAKSHATRAS,row

# Ravi Yoga is the inclusive Sun->Moon Nakshatra distance set.
ravi=muhurat_reuse.yoga_year("ravi-yoga",2026,lat,lon,tz,False)
assert ravi
for row in ravi:
    mid=datetime.fromisoformat(row["start"])+(datetime.fromisoformat(row["end"])-datetime.fromisoformat(row["start"]))/2
    st=panchang.state_at(mid)
    distance=((st["nakshatra_id"]-st["sun_nakshatra_id"])%27)+1
    assert distance in muhurat_reuse.RAVI_DISTANCES,(row,distance)
    assert row["ravi_distance"]==distance,row

# Aggregate is exactly the union of the seven encoded Yoga families.
agg=muhurat_reuse.aggregate_yogas(2026,lat,lon,tz,False)
assert set(agg["by_kind"])==set(muhurat_reuse.YOGA_TITLES)
assert len(agg["events"])==sum(len(x) for x in agg["by_kind"].values())
assert agg["counts"]=={k:len(v) for k,v in agg["by_kind"].items()}

print("Muhurat reuse fixture passed")

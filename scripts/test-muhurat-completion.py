#!/usr/bin/env python3
import os,sys
from datetime import date,datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import muhurat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567;d=date(2026,10,6)

g=x.gowri(d,lat,lon,tz)
assert [r["title"] for r in g[0]["items"]]==x.DAY_GOWRI[d.weekday()]

expected=["Rudra","Uraga","Mitra","Pitara","Vasu","Ambu","Vishwedeva","Vidhi","Brahma","Indra","Indragni","Daitya","Varuna","Aryama","Bhaga","Ishwara","Ajaikapada","Ahirbudhnya","Pusha","Ashwini","Yama","Agni","Brahma","Chandra","Aditi","Brihaspati","Vishnu","Surya","Tvashta","Samirana"]
dg=x.do_ghati(d,lat,lon,tz)[0]["items"]
assert [r["title"] for r in dg]==expected

p=x.pachchakkhan(d,lat,lon,tz)[0]["items"]
assert len(p)==10 and p[0]["title"]=="Navkarshi"

# Published 2026-10-06 Krishna-Paksha Peacock profile:
# daytime main sequence Sleeping -> Ruling -> Walking -> Eating -> Dying;
# first Sleeping Yama subactivities Sleep/Rule/Walk/Eat/Die with
# 12/18/36/48/30 shares of 144. Night starts Sleeping and follows
# Sleep/Walk/Die/Rule/Eat with 18/42/24/18/42 shares.
pak=x.pakshi_sections(d,lat,lon,tz,"Peacock")
assert sum(len(s["items"]) for s in pak)==50

day=pak[0]["items"];night=pak[1]["items"]
day_main=[day[i*5]["title"].split(" · ")[1].split(" / ")[0] for i in range(5)]
night_main=[night[i*5]["title"].split(" · ")[1].split(" / ")[0] for i in range(5)]
assert day_main==["Sleeping","Ruling","Walking","Eating","Dying"],day_main
assert night_main==["Sleeping","Walking","Dying","Ruling","Eating"],night_main

def acts(rows):
    return [r["title"].split(" / ")[-1] for r in rows]
def durations(rows):
    return [(datetime.fromisoformat(r["end"])-datetime.fromisoformat(r["start"])).total_seconds()/60 for r in rows]

first_day=day[:5];first_night=night[:5]
assert acts(first_day)==["Sleeping","Ruling","Walking","Eating","Dying"],acts(first_day)
assert acts(first_night)==["Sleeping","Walking","Dying","Ruling","Eating"],acts(first_night)

for rows,shares in [
    (first_day,{"Sleeping":12,"Ruling":18,"Walking":36,"Eating":48,"Dying":30}),
    (first_night,{"Sleeping":18,"Walking":42,"Dying":24,"Ruling":18,"Eating":42}),
]:
    dur=durations(rows); names=acts(rows)
    total=sum(dur)
    for name,minutes in zip(names,dur):
        expected_minutes=total*shares[name]/144.0
        assert abs(minutes-expected_minutes)<0.05,(name,minutes,expected_minutes)

assert len(x.shubha_dates(2026,lat,lon,tz)[0]["items"])>0
print("Muhurat completion truth fixture passed")

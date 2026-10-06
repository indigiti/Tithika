#!/usr/bin/env python3
import os
import sys
from datetime import date, datetime
from zoneinfo import ZoneInfo

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,"python"))

import panchang
import panchang_reuse

tz=ZoneInfo("Asia/Kolkata")
lat,lon=18.5204,73.8567

# Hindu Sunrise is a thin verified projection of the core rise/set/state engine.
sun=panchang_reuse.sunrise_context(date(2026,10,6),lat,lon,tz,False)
expected=panchang.rise_set(
    date(2026,10,6),lat,lon,tz,
    panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise
)
assert datetime.fromisoformat(sun["sunrise"])==expected
assert sun["sunrise_state"]["nakshatra"]=="Ashlesha",sun
assert sun["sunrise_state"]["tithi"]=="Ekadashi",sun
assert sun["daylight_minutes"]>0
assert sun["ahoratra_minutes"]>1400

# Monthly Nakshatra intervals must continuously cover the full civil month.
start=datetime(2026,10,1,tzinfo=tz)
end=datetime(2026,11,1,tzinfo=tz)
naks=panchang_reuse.nakshatra_intervals(start,end,False)
assert naks
assert datetime.fromisoformat(naks[0]["start"])==start
assert datetime.fromisoformat(naks[-1]["end"])==end
for a,b in zip(naks,naks[1:]):
    gap=(datetime.fromisoformat(b["start"])-datetime.fromisoformat(a["end"])).total_seconds()
    assert 0 <= gap <= 2,gap
    mid=datetime.fromisoformat(a["start"])+(datetime.fromisoformat(a["end"])-datetime.fromisoformat(a["start"]))/2
    assert panchang.state_at(mid)["nakshatra"]==a["name"],a

# Six Ganda Moola Nakshatras only; Oct 6 Pune must include Ashlesha.
ganda=panchang_reuse.yearly_ganda_moola(2026,tz,False)
assert ganda
assert {x["name"] for x in ganda} <= panchang_reuse.GANDA_MOOLA
oct6_sunrise=datetime.fromisoformat(sun["sunrise"])
assert any(
    x["name"]=="Ashlesha"
    and datetime.fromisoformat(x["start"]) <= oct6_sunrise < datetime.fromisoformat(x["end"])
    for x in ganda
),ganda[-12:]
for row in ganda:
    mid=datetime.fromisoformat(row["start"])+(datetime.fromisoformat(row["end"])-datetime.fromisoformat(row["start"]))/2
    assert panchang.state_at(mid)["nakshatra"]==row["name"],row

# Abhijit passages must remain inside the exact intercalary sidereal span.
abh=panchang_reuse.yearly_abhijit(2026,tz,False)
assert 12 <= len(abh) <= 14,len(abh)
for row in abh:
    mid=datetime.fromisoformat(row["start"])+(datetime.fromisoformat(row["end"])-datetime.fromisoformat(row["start"]))/2
    moon=panchang.state_at(mid)["moon_longitude"]
    assert panchang_reuse.ABHIJIT_START <= moon < panchang_reuse.ABHIJIT_END,(row,moon)

# Vinchudo is the Moon's passage through Vrishchika.
vin=panchang_reuse.yearly_vinchudo(2026,tz,False)
assert 11 <= len(vin) <= 14,len(vin)
assert any(x["date"]=="2026-10-15" for x in vin),vin[-5:]
for row in vin:
    mid=datetime.fromisoformat(row["start"])+(datetime.fromisoformat(row["end"])-datetime.fromisoformat(row["start"]))/2
    assert panchang.state_at(mid)["moon_rashi"]=="Vrishchika",row

# Jwalamukhi intervals must satisfy one of the five exact Tithi/Nakshatra pairs.
jwala=panchang_reuse.yearly_jwalamukhi(2026,tz,False)
assert jwala
for row in jwala:
    mid=datetime.fromisoformat(row["start"])+(datetime.fromisoformat(row["end"])-datetime.fromisoformat(row["start"]))/2
    st=panchang.state_at(mid)
    assert (st["tithi_number"],st["nakshatra"]) in panchang_reuse.JWALAMUKHI_COMBINATIONS,(row,st)

# Manvadi, Yugadi and Kalpadi are sunrise-state Purnimanta Tithi rules.
creation=panchang_reuse.creation_days(2026,lat,lon,tz,False)
assert len(creation["manvadi"])==14,creation["manvadi"]
assert len(creation["yugadi"])==4,creation["yugadi"]
assert len(creation["kalpadi"])==7,creation["kalpadi"]

man={x["name"]:x["date"] for x in creation["manvadi"]}
assert man["Brahma Savarni Manvadi"]=="2026-01-25",man
assert man["Swayambhuva Manvadi"]=="2026-03-21",man
assert man["Indra Savarni Manvadi"]=="2026-09-04",man
assert man["Daksha Savarni Manvadi"]=="2026-10-20",man
assert man["Tamasa Manvadi"]=="2026-11-21",man

yuga={x["name"]:x["date"] for x in creation["yugadi"]}
assert yuga["Treta Yuga Diwas"]=="2026-04-19",yuga
assert yuga["Kali Yuga Diwas"]=="2026-10-08",yuga
assert yuga["Satya Yuga Diwas"]=="2026-11-18",yuga

kalpa={x["name"]:x["date"] for x in creation["kalpadi"]}
assert kalpa=={
    "Varaha Kalpadi":"2026-01-30",
    "Brahma Kalpadi":"2026-03-06",
    "Kurma Kalpadi First":"2026-03-19",
    "Kurma Kalpadi Second":"2026-03-23",
    "Parthiva Kalpadi":"2026-04-19",
    "Savitri Kalpadi":"2026-11-16",
    "Pralaya Kalpadi":"2026-12-18",
},kalpa

# Sankalpa: selected-time Panchang + sunrise-state Samvat/month/Ritu/Ayana.
sank=panchang_reuse.sankalpa_context(
    date(2026,10,6),lat,lon,tz,False,"12:00"
)
assert sank["vikrama_samvat"]==2083,sank
assert sank["vikrama_samvatsara"]=="Siddharthi",sank
assert sank["shaka_samvat"]==1948,sank
assert sank["shaka_samvatsara"]=="Parabhava",sank
assert sank["purnimanta_month"]=="Ashwina",sank
assert sank["amanta_month"]=="Bhadrapada",sank
assert sank["drik_ritu"]=="Sharad",sank
assert sank["vedic_ritu"]=="Varsha",sank
assert sank["drik_ayana"]=="Dakshinayana",sank
assert sank["vedic_ayana"]=="Dakshinayana",sank
ref=datetime(2026,10,6,12,0,tzinfo=tz)
state=panchang.state_at(ref)
assert sank["tithi"]==state["tithi"]
assert sank["nakshatra"]==state["nakshatra"]
assert sank["yoga"]==state["yoga"]
assert sank["karana"]==state["karana"]

# Vedic clock formulas: 60-Ghati Ishtakala and 30+30 day/night clock.
clock=panchang_reuse.vedic_clock(
    date(2026,10,6),lat,lon,tz,False,"12:00"
)
sunrise=datetime.fromisoformat(clock["sunrise"])
sunset=datetime.fromisoformat(clock["sunset"])
next_sunrise=datetime.fromisoformat(clock["next_sunrise"])
reference=ref
expected60=60*(reference-sunrise).total_seconds()/(next_sunrise-sunrise).total_seconds()
if reference<=sunset:
    expected3030=30*(reference-sunrise).total_seconds()/(sunset-sunrise).total_seconds()
else:
    expected3030=30+30*(reference-sunset).total_seconds()/(next_sunrise-sunset).total_seconds()
assert abs(clock["ishtakala_60"]["decimal"]-expected60)<1e-6,clock
assert abs(clock["ritual_30_30"]["decimal"]-expected3030)<1e-6,clock
assert panchang_reuse.fractional_ghati(0)["label"]=="00:00:00"
assert panchang_reuse.fractional_ghati(30)["label"]=="30:00:00"
assert panchang_reuse.fractional_ghati(60)["label"]=="60:00:00"

print("Panchang reuse fixture passed")

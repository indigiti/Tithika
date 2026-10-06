#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import lagna, planetary

PLANETS=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
DEB={"Sun":190.0,"Moon":213.0,"Mars":118.0,"Mercury":345.0,"Jupiter":275.0,"Venus":177.0,"Saturn":20.0}
NAIS={"Sun":60.0,"Moon":51.43,"Venus":42.86,"Jupiter":34.29,"Mercury":25.71,"Mars":17.14,"Saturn":8.57}
DIG_OFFSET={"Mercury":0.0,"Jupiter":0.0,"Moon":90.0,"Venus":90.0,"Saturn":180.0,"Sun":270.0,"Mars":270.0}
MEAN_SPEED={"Mars":0.524,"Mercury":1.383,"Jupiter":0.0831,"Venus":1.2,"Saturn":0.0335}

def parse_birth(p,tz):
 s=str(p.get("datetime") or "").strip()
 if not s:s=f"{p.get('date') or datetime.now(tz).strftime('%Y-%m-%d')}T{p.get('time') or '12:00:00'}"
 d=datetime.fromisoformat(s);return d.replace(tzinfo=tz) if d.tzinfo is None else d.astimezone(tz)

def dist(a,b):return abs((a-b+180)%360-180)
def uchcha(name,lon):return round(dist(lon,DEB[name])/3.0,4)
def house(sign,asc):return ((sign-asc)%12)+1
def kendra(h):return 60.0 if h in (1,4,7,10) else 30.0 if h in (2,5,8,11) else 15.0
def drekkana(name,deg):
 third=min(2,int(deg//10))
 if name in ("Sun","Mars","Jupiter"):good=0
 elif name in ("Mercury","Saturn"):good=1
 else:good=2
 return 15.0 if third==good else 0.0
def dig(name,lon,asc_lon):
 strong=(asc_lon+DIG_OFFSET[name])%360;zero=(strong+180)%360
 return round(dist(lon,zero)/3.0,4)
def chesta(name,speed,retro):
 if name not in MEAN_SPEED:return None
 if retro:return 60.0
 ratio=min(1.0,abs(speed)/MEAN_SPEED[name])
 return round(60.0*(1.0-ratio),4)

def main():
 p=json.loads(sys.stdin.read() or "{}");lat=float(p.get("lat",19.076));lon=float(p.get("lon",72.8777))
 tzname=p.get("timezone") or "Asia/Kolkata"
 try:tz=ZoneInfo(tzname)
 except ZoneInfoNotFoundError:tzname="Asia/Kolkata";tz=ZoneInfo(tzname)
 birth=parse_birth(p,tz);asc=lagna.lagna_state(birth,lat,lon)
 rows=[]
 for name in PLANETS:
  st=planetary.planet_state(name,birth);h=house(st["rashi_id"],asc["lagna_id"])
  rows.append({"planet":name,"rashi":st["rashi"],"house":h,"longitude":st["longitude"],"retrograde":st["retrograde"],"components":{"uchcha":uchcha(name,st["longitude"]),"dig":dig(name,st["longitude"],asc["sidereal_longitude"]),"kendra":kendra(h),"drekkana":drekkana(name,st["degree_in_rashi"]),"naisargika":NAIS[name],"chesta_proxy":chesta(name,st["speed_deg_day"],st["retrograde"])}})
 print(json.dumps({"ok":True,"birth_datetime":birth.isoformat(),"engine":{"name":"tithika-shadbala-foundation","version":"0.1.0","status":"foundation-not-totaled","ayanamsha":"Lahiri / Chitrapaksha"},"lagna":{"rashi":asc["lagna"],"longitude":asc["sidereal_longitude"]},"planets":rows,"withheld":["Saptavargaja Bala","complete Kala Bala","classical Drik Bala","final Shadbala total"],"note":"This page intentionally exposes only independently auditable strength components. A final Shadbala total is withheld until the remaining classical conventions are independently benchmarked."},ensure_ascii=False))
if __name__=="__main__":
 try:main()
 except Exception as e:
  print(json.dumps({"ok":False,"error":str(e),"code":"SHADBALA_FOUNDATION_FAILED"}));sys.exit(1)

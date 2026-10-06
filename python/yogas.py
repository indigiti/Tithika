#!/usr/bin/env python3
"""
Tithika structural Jyotish Yoga detector.

Detects a curated set of classical, machine-auditable D1 combinations.
It reports geometry/rule evidence, not deterministic predictions.
"""
from __future__ import annotations
import json, sys
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import lagna, panchang, planetary

ENGINE_VERSION="0.1.0"
GRAHAS=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
KENDRA={1,4,7,10}; TRIKONA={1,5,9}; DUSTHANA={6,8,12}
BENEFICS={"Mercury","Jupiter","Venus"}
SIGN_LORD=["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]
OWN={
 "Sun":{4},"Moon":{3},"Mars":{0,7},"Mercury":{2,5},
 "Jupiter":{8,11},"Venus":{1,6},"Saturn":{9,10}
}
EXALT={"Sun":0,"Moon":1,"Mars":9,"Mercury":5,"Jupiter":3,"Venus":11,"Saturn":6}
MAHAPURUSHA={"Mars":"Ruchaka","Mercury":"Bhadra","Jupiter":"Hamsa","Venus":"Malavya","Saturn":"Sasa"}
SANKHYA={1:"Gola",2:"Yuga",3:"Soola",4:"Kedara",5:"Pasa",6:"Damini",7:"Veena"}
ASHRAYA={0:"Rajju",1:"Musala",2:"Nala"}

def parse_birth(p,tz):
 s=str(p.get("datetime") or "").strip()
 if not s:s=f"{p.get('date') or datetime.now(tz).strftime('%Y-%m-%d')}T{p.get('time') or '12:00:00'}"
 d=datetime.fromisoformat(s)
 return d.replace(tzinfo=tz) if d.tzinfo is None else d.astimezone(tz)

def house_from(ref,target): return ((target-ref)%12)+1
def lord_of_house(asc,h): return SIGN_LORD[(asc+h-1)%12]
def dignity(name,sign):
 if sign==EXALT[name]:return "exalted"
 if sign in OWN[name]:return "own"
 if sign==(EXALT[name]+6)%12:return "debilitated"
 return "other"

def aspect_houses(name):
 return {"Mars":{4,7,8},"Jupiter":{5,7,9},"Saturn":{3,7,10}}.get(name,{7})

def aspects(planets,a,b):
 return house_from(planets[a]["rashi_id"],planets[b]["rashi_id"]) in aspect_houses(a)

def associated(planets,a,b):
 return planets[a]["rashi_id"]==planets[b]["rashi_id"] or aspects(planets,a,b) or aspects(planets,b,a)

def add(out,name,category,rule,evidence,notes=None):
 out.append({"name":name,"category":category,"rule":rule,"evidence":evidence,"notes":notes or []})

def detect_from_chart(asc_sign:int,planets:dict)->list[dict]:
 out=[]
 moon=planets["Moon"]["rashi_id"]

 # Gajakesari
 jf=house_from(moon,planets["Jupiter"]["rashi_id"])
 if jf in KENDRA:
  add(out,"Gajakesari Yoga","lunar","Jupiter in a Kendra from Moon",{"jupiter_from_moon":jf,"jupiter_rashi":planets["Jupiter"]["rashi"]})

 # Budha-Aditya / Chandra-Mangala
 if planets["Sun"]["rashi_id"]==planets["Mercury"]["rashi_id"]:
  notes=["Mercury is combust under the current angular-separation profile."] if planets["Mercury"].get("combust") else []
  add(out,"Budha-Aditya Yoga","conjunction","Sun and Mercury in the same Rashi",{"rashi":planets["Sun"]["rashi"]},notes)
 if planets["Moon"]["rashi_id"]==planets["Mars"]["rashi_id"]:
  add(out,"Chandra-Mangala Yoga","conjunction","Moon and Mars in the same Rashi",{"rashi":planets["Moon"]["rashi"]})

 # Pancha Mahapurusha
 for name,yoga in MAHAPURUSHA.items():
  p=planets[name]
  if p["house"] in KENDRA and dignity(name,p["rashi_id"]) in ("own","exalted"):
   add(out,f"{yoga} Yoga","pancha-mahapurusha",f"{name} in own/exalted Rashi and Kendra from Lagna",{"planet":name,"house":p["house"],"rashi":p["rashi"],"dignity":dignity(name,p["rashi_id"])})

 # Raja Yoga (Kendra lord associated with Trikona lord)
 kl={lord_of_house(asc_sign,h) for h in KENDRA}
 tl={lord_of_house(asc_sign,h) for h in TRIKONA}
 pairs=[]
 for i,a in enumerate(GRAHAS):
  for b in GRAHAS[i+1:]:
   if ((a in kl and b in tl) or (b in kl and a in tl)) and associated(planets,a,b):
    pairs.append({"planets":[a,b],"mode":"conjunction" if planets[a]["rashi_id"]==planets[b]["rashi_id"] else "graha-drishti"})
 if pairs:add(out,"Raja Yoga","lordship","Kendra lord associated with Trikona lord",{"pairs":pairs})

 # Dhana Yoga
 wealth={lord_of_house(asc_sign,h) for h in (2,11)}
 support={lord_of_house(asc_sign,h) for h in (1,2,5,9,11)}
 pairs=[]
 for i,a in enumerate(GRAHAS):
  for b in GRAHAS[i+1:]:
   if ((a in wealth and b in support) or (b in wealth and a in support)) and associated(planets,a,b):
    pairs.append({"planets":[a,b],"mode":"conjunction" if planets[a]["rashi_id"]==planets[b]["rashi_id"] else "graha-drishti"})
 if pairs:add(out,"Dhana Yoga","lordship","2nd/11th lord associated with 1st/2nd/5th/9th/11th lord",{"pairs":pairs})

 # Sunapha/Anapha/Durudhara/Kemadruma
 second=[];twelfth=[];withmoon=[]
 for g in GRAHAS:
  if g in ("Sun","Moon"):continue
  h=house_from(moon,planets[g]["rashi_id"])
  if h==2:second.append(g)
  elif h==12:twelfth.append(g)
  elif h==1:withmoon.append(g)
 if second and twelfth:add(out,"Durudhara Yoga","lunar","Planets on both sides of Moon (Sun/nodes excluded)",{"second":second,"twelfth":twelfth})
 elif second:add(out,"Sunapha Yoga","lunar","Planet(s) in 2nd from Moon",{"second":second})
 elif twelfth:add(out,"Anapha Yoga","lunar","Planet(s) in 12th from Moon",{"twelfth":twelfth})
 elif not withmoon:
  cancellation=[]
  if planets["Moon"]["house"] in KENDRA:cancellation.append("Moon is in a Kendra from Lagna")
  if any(planets[g]["house"] in KENDRA for g in GRAHAS if g!="Moon"):cancellation.append("A planet occupies a Kendra from Lagna")
  if any(house_from(moon,planets[g]["rashi_id"]) in KENDRA for g in GRAHAS if g!="Moon"):cancellation.append("A planet occupies a Kendra from Moon")
  add(out,"Kemadruma Yoga","lunar-affliction","No planet (Sun/nodes excluded) with, 2nd or 12th from Moon",{"cancellation_evidence":cancellation},["Cancellation evidence present."] if cancellation else [])

 # Adhi / Amala
 adhi=[g for g in BENEFICS if house_from(moon,planets[g]["rashi_id"]) in (6,7,8)]
 if len(adhi)>=2:add(out,"Adhi Yoga","lunar","At least two natural benefics in 6th/7th/8th from Moon",{"benefics":sorted(adhi)})
 amala=[g for g in BENEFICS if planets[g]["house"]==10 or house_from(moon,planets[g]["rashi_id"])==10]
 if amala:add(out,"Amala Yoga","reputation","Natural benefic in 10th from Lagna or Moon",{"benefics":sorted(amala)})

 # Vipareeta Raja
 vip=[]
 for h,label in ((6,"Harsha"),(8,"Sarala"),(12,"Vimala")):
  lord=lord_of_house(asc_sign,h)
  if planets[lord]["house"] in DUSTHANA:vip.append({"type":label,"house_lord":h,"lord":lord,"placed_house":planets[lord]["house"]})
 if vip:add(out,"Vipareeta Raja Yoga","dusthana","6th/8th/12th lord placed in a Dusthana",{"forms":vip})

 # Neecha Bhanga evidence
 for g in GRAHAS:
  if dignity(g,planets[g]["rashi_id"])!="debilitated":continue
  sign=planets[g]["rashi_id"];disp=SIGN_LORD[sign];reasons=[]
  if planets[disp]["house"] in KENDRA or house_from(moon,planets[disp]["rashi_id"]) in KENDRA:
   reasons.append(f"Dispositor {disp} is in a Kendra from Lagna/Moon")
  if dignity(disp,planets[disp]["rashi_id"])=="exalted":
   reasons.append(f"Dispositor {disp} is exalted")
  exalted_here=next((p for p,s in EXALT.items() if s==sign),None)
  if exalted_here and (planets[exalted_here]["house"] in KENDRA or house_from(moon,planets[exalted_here]["rashi_id"]) in KENDRA):
   reasons.append(f"{exalted_here}, exalted in the debilitation sign, is in a Kendra")
  if reasons:add(out,"Neecha Bhanga Yoga","dignity",f"Debilitation cancellation evidence for {g}",{"planet":g,"reasons":reasons})

 # Parivartana
 for i,a in enumerate(GRAHAS):
  for b in GRAHAS[i+1:]:
   if planets[a]["rashi_id"] in OWN[b] and planets[b]["rashi_id"] in OWN[a]:
    ha,hb=planets[a]["house"],planets[b]["house"]
    kind="Dainya" if ({ha,hb}&DUSTHANA) else "Khala" if 3 in (ha,hb) else "Maha"
    add(out,f"Parivartana Yoga ({kind})","exchange","Two Grahas occupy each other's own Rashis",{"planets":[a,b],"houses":[ha,hb]})

 # Shakata / Daridra
 mj=house_from(planets["Jupiter"]["rashi_id"],moon)
 if mj in DUSTHANA:
  cancel=planets["Moon"]["house"] in KENDRA
  add(out,"Shakata Yoga","lunar-affliction","Moon in 6th/8th/12th from Jupiter",{"moon_from_jupiter":mj,"cancelled_by_moon_kendra":cancel})
 l11=lord_of_house(asc_sign,11)
 if planets[l11]["house"] in DUSTHANA:
  add(out,"Daridra Yoga","gains-affliction","11th lord placed in 6th/8th/12th",{"lord":l11,"house":planets[l11]["house"]})

 # Nabhasa Sankhya + Ashraya
 occupied={planets[g]["rashi_id"] for g in GRAHAS}
 if len(occupied) in SANKHYA:add(out,f"{SANKHYA[len(occupied)]} Yoga","nabhasa-sankhya","Seven classical Grahas occupy N distinct Rashis",{"distinct_rashis":len(occupied)})
 modalities={s%3 for s in occupied}
 if len(modalities)==1:
  q=next(iter(modalities));add(out,f"{ASHRAYA[q]} Yoga","nabhasa-ashraya","All seven classical Grahas occupy one modality",{"modality":["movable","fixed","dual"][q]})
 return out

def build(payload):
 lat=float(payload.get("lat",19.076));lon=float(payload.get("lon",72.8777))
 tzname=payload.get("timezone") or "Asia/Kolkata"
 try:tz=ZoneInfo(tzname)
 except ZoneInfoNotFoundError:tzname="Asia/Kolkata";tz=ZoneInfo(tzname)
 birth=parse_birth(payload,tz);asc=lagna.lagna_state(birth,lat,lon)
 planets={}
 for name in GRAHAS:
  st=planetary.planet_state(name,birth)
  planets[name]={**st,"house":house_from(asc["lagna_id"],st["rashi_id"]),"dignity":dignity(name,st["rashi_id"])}
 rows=detect_from_chart(asc["lagna_id"],planets)
 cats={}
 for row in rows:cats[row["category"]]=cats.get(row["category"],0)+1
 return {
  "ok":True,"birth_datetime":birth.isoformat(),
  "engine":{"name":"tithika-yogas","version":ENGINE_VERSION,"ayanamsha":"Lahiri / Chitrapaksha","house_system":"whole-sign","scope":"curated-structural-yogas"},
  "lagna":{"rashi":asc["lagna"],"rashi_id":asc["lagna_id"]},
  "count":len(rows),"category_counts":cats,"yogas":rows,
  "note":"Yoga detection reports structural classical combinations and cancellation/weakening evidence where implemented. It does not predict real-life outcomes and is intentionally not exhaustive."
 }

def main():
 print(json.dumps(build(json.loads(sys.stdin.read() or "{}")),ensure_ascii=False))
if __name__=="__main__":
 try:main()
 except Exception as e:
  print(json.dumps({"ok":False,"error":str(e),"code":"YOGA_CALCULATION_FAILED"}));sys.exit(1)

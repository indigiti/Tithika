#!/usr/bin/env python3
"""
Tithika complete six-fold Shadbala engine.

Declared calculation profile
----------------------------
- Seven classical Grahas only: Sun through Saturn.
- Lahiri / Chitrapaksha sidereal positions from Tithika's Astronomy Engine layer.
- Sthana: Uchcha + Saptavargaja + Ojayugma + Kendradi + Drekkana.
- Dig: angular distance from the powerless directional point.
- Kala: Nathonnatha + Paksha + Tribhaga + Abda + Masa + Vara + Hora + Ayana + Yuddha.
- Cheshta: classical mean-longitude Seeghra/Cheshta Kendra profile; Sun=Ayana, Moon=Paksha.
- Naisargika: fixed classical values.
- Drik: degree-graded Parashari aspect curve + full special Graha Drishti.

All values are virupas; 60 virupas = 1 rupa.
"""
from __future__ import annotations

import json, math, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import lagna, panchang, planetary, vargas

ENGINE_VERSION="1.0.0"
PLANETS=["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]

DEB={"Sun":190.0,"Moon":213.0,"Mars":118.0,"Mercury":345.0,"Jupiter":275.0,"Venus":177.0,"Saturn":20.0}
NAIS={"Sun":60.0,"Moon":51.43,"Venus":42.86,"Jupiter":34.29,"Mercury":25.71,"Mars":17.14,"Saturn":8.57}
REQUIRED={"Sun":6.5,"Moon":6.0,"Mars":5.0,"Mercury":7.0,"Jupiter":6.5,"Venus":5.5,"Saturn":5.0}
DIG_MAX={"Mercury":1,"Jupiter":1,"Moon":4,"Venus":4,"Saturn":7,"Sun":10,"Mars":10}
SIGN_LORD=["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]
OWN={
 "Sun":{4},"Moon":{3},"Mars":{0,7},"Mercury":{2,5},
 "Jupiter":{8,11},"Venus":{1,6},"Saturn":{9,10}
}
MOOLA={
 "Sun":(4,0.0,20.0),"Moon":(1,4.0,30.0),"Mars":(0,0.0,12.0),
 "Mercury":(5,16.0,20.0),"Jupiter":(8,0.0,10.0),
 "Venus":(6,0.0,15.0),"Saturn":(10,0.0,20.0)
}
NATURAL={
 "Sun":{"Moon":"f","Mars":"f","Jupiter":"f","Mercury":"n","Venus":"e","Saturn":"e"},
 "Moon":{"Sun":"f","Mercury":"f","Mars":"n","Jupiter":"n","Venus":"n","Saturn":"n"},
 "Mars":{"Sun":"f","Moon":"f","Jupiter":"f","Mercury":"e","Venus":"n","Saturn":"n"},
 "Mercury":{"Sun":"f","Venus":"f","Moon":"e","Mars":"n","Jupiter":"n","Saturn":"n"},
 "Jupiter":{"Sun":"f","Moon":"f","Mars":"f","Mercury":"e","Venus":"e","Saturn":"n"},
 "Venus":{"Mercury":"f","Saturn":"f","Sun":"e","Moon":"e","Mars":"n","Jupiter":"n"},
 "Saturn":{"Mercury":"f","Venus":"f","Sun":"e","Moon":"e","Mars":"e","Jupiter":"n"},
}
COMPOUND={
 ("f","f"):"great_friend",("f","e"):"neutral",
 ("n","f"):"friend",("n","e"):"enemy",
 ("e","f"):"neutral",("e","e"):"great_enemy"
}
SAPTA_SCORE={"moolatrikona":45.0,"own":30.0,"great_friend":22.5,"friend":15.0,"neutral":7.5,"enemy":3.75,"great_enemy":1.875}
SAPTA=[1,2,3,7,9,12,30]
WEEKDAY_LORD={0:"Moon",1:"Mars",2:"Mercury",3:"Jupiter",4:"Venus",5:"Saturn",6:"Sun"}
CHALDEAN=["Saturn","Jupiter","Mars","Sun","Venus","Mercury","Moon"]
TRI_DAY={0:"Mercury",1:"Sun",2:"Saturn"}
TRI_NIGHT={0:"Moon",1:"Venus",2:"Mars"}
AYANA_NORTH={"Sun","Mars","Jupiter","Venus","Mercury"}
BENEFIC={"Mercury","Jupiter","Venus"}
SPECIAL={"Sun":{7},"Moon":{7},"Mercury":{7},"Venus":{7},"Mars":{4,7,8},"Jupiter":{5,7,9},"Saturn":{3,7,10}}
MEAN_LON={
 "Sun":(280.46646,0.98564736),"Mars":(355.43300,0.52402068),
 "Jupiter":(34.351519,0.08308529),"Saturn":(50.077444,0.03344414),
 "Mercury":(252.25091,4.09233445),"Venus":(181.97980,1.60213034)
}

def parse_birth(p,tz):
 s=str(p.get("datetime") or "").strip()
 if not s:s=f"{p.get('date') or datetime.now(tz).strftime('%Y-%m-%d')}T{p.get('time') or '12:00:00'}"
 d=datetime.fromisoformat(s)
 return d.replace(tzinfo=tz) if d.tzinfo is None else d.astimezone(tz)

def fold_distance(a,b):return abs((a-b+180.0)%360.0-180.0)
def house(sign,asc):return ((sign-asc)%12)+1
def house_from(a,b):return ((b-a)%12)+1

def uchcha(name,lon):return fold_distance(lon,DEB[name])/3.0

def kendra(h):
 return 60.0 if h in (1,4,7,10) else 30.0 if h in (2,5,8,11) else 15.0

def drekkana(name,deg):
 if deg<10:sex="male"
 elif deg<20:sex="neutral"
 else:sex="female"
 want="male" if name in ("Sun","Mars","Jupiter") else "female" if name in ("Moon","Venus") else "neutral"
 return 15.0 if sex==want else 0.0

def oja(name,rashi_id,nav_id):
 wants_odd=name not in ("Moon","Venus")
 return 15.0*(int((rashi_id%2==0)==wants_odd)+int((nav_id%2==0)==wants_odd))

def dig(name,lon,asc_lon):
 max_house=DIG_MAX[name]
 powerless=((max_house-1+6)%12)+1
 cusp=(asc_lon+30.0*(powerless-1))%360.0
 return 60.0*fold_distance(lon,cusp)/180.0

def moola(name,sign,degree):
 s,a,b=MOOLA[name]
 return sign==s and a<=degree<b

def compound_relation(name,other,signs):
 natural=NATURAL[name][other]
 d=house_from(signs[name],signs[other])
 temporal="f" if d in (2,3,4,10,11,12) else "e"
 return COMPOUND[(natural,temporal)]

def saptavargaja(name,lon,signs):
 total=0.0;detail=[]
 for n in SAPTA:
  v=vargas.varga_position(lon,n)
  sign=v["rashi_id"];lord=SIGN_LORD[sign]
  if n==1 and moola(name,sign,v["source_degree"]):
   grade="moolatrikona"
  elif sign in OWN[name]:
   grade="own"
  else:
   grade=compound_relation(name,lord,signs)
  points=SAPTA_SCORE[grade];total+=points
  detail.append({"varga":f"D{n}","rashi":v["rashi"],"lord":lord,"grade":grade,"virupa":points})
 return total,detail

def nathonnatha(name,birth):
 if name=="Mercury":return 60.0
 h=birth.hour+birth.minute/60+birth.second/3600
 frac=(h%24)/24.0
 day=60.0*(1.0-abs(frac-.5)*2.0)
 return day if name in ("Sun","Jupiter","Venus") else 60.0-day

def paksha(name,sun,moon):
 elong=fold_distance(moon,sun)
 bright=elong/3.0
 val=bright if name in ("Moon","Mercury","Jupiter","Venus") else 60.0-bright
 return val*2.0 if name=="Moon" else val

def solar_context(birth,lat,lon,tz):
 today=birth.date()
 sr=panchang.rise_set(today,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)
 if sr is not None and birth>=sr:
  sunrise=sr
  sunset=panchang.rise_set(today,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Set)
  next_sunrise=panchang.rise_set(today+timedelta(days=1),lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)
 else:
  d=today-timedelta(days=1)
  sunrise=panchang.rise_set(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Rise)
  sunset=panchang.rise_set(d,lat,lon,tz,panchang.astronomy.Body.Sun,panchang.astronomy.Direction.Set)
  next_sunrise=sr
 if not sunrise or not sunset or not next_sunrise:
  raise ValueError("Sunrise/sunset unavailable for Shadbala Kala Bala")
 return sunrise,sunset,next_sunrise

def tribhaga(name,birth,sunrise,sunset,next_sunrise):
 if name=="Jupiter":return 60.0
 if sunrise<=birth<sunset:
  span=(sunset-sunrise)/3
  part=min(2,int((birth-sunrise)/span))
  return 60.0 if TRI_DAY[part]==name else 0.0
 if sunset<=birth<next_sunrise:
  span=(next_sunrise-sunset)/3
  part=min(2,int((birth-sunset)/span))
  return 60.0 if TRI_NIGHT[part]==name else 0.0
 return 0.0

def sun_sign(moment):return planetary.planet_state("Sun",moment)["rashi_id"]

def refine_ingress(left,right,target):
 lo,hi=left,right
 for _ in range(42):
  mid=lo+(hi-lo)/2
  if sun_sign(mid)==target:hi=mid
  else:lo=mid
 return hi

def ingress_before(moment,target,max_days):
 cur=moment;cur_sign=sun_sign(cur)
 for _ in range(max_days+2):
  prev=cur-timedelta(days=1);prev_sign=sun_sign(prev)
  if prev_sign!=cur_sign and cur_sign==target:
   return refine_ingress(prev,cur,target)
  cur,cur_sign=prev,prev_sign
 raise ValueError(f"Could not find Sun ingress into sign {target}")

def hora_lord(sunrise,birth,vara):
 hours=max(0,int((birth-sunrise).total_seconds()//3600))
 start=CHALDEAN.index(vara)
 return CHALDEAN[(start+hours)%7]

def time_lords(birth,sunrise,current_sun_sign):
 vara=WEEKDAY_LORD[sunrise.weekday()]
 hora=hora_lord(sunrise,birth,vara)
 masa_dt=ingress_before(birth,current_sun_sign,40)
 abda_dt=ingress_before(birth,0,380)
 masa=WEEKDAY_LORD[masa_dt.weekday()]
 abda=WEEKDAY_LORD[abda_dt.weekday()]
 return {"vara":vara,"hora":hora,"masa":masa,"abda":abda,"masa_ingress":masa_dt.isoformat(),"abda_ingress":abda_dt.isoformat()}

def declination(name,birth):
 t=panchang.astronomy_time(birth)
 lon,lat,dist=planetary.tropical_coordinates(name,birth)
 lr=math.radians(lon);br=math.radians(lat);cb=math.cos(br)
 v=panchang.astronomy.Vector(dist*cb*math.cos(lr),dist*cb*math.sin(lr),dist*math.sin(br),t)
 eq=panchang.astronomy.RotateVector(panchang.astronomy.Rotation_ECT_EQD(t),v)
 return math.degrees(math.atan2(eq.z,math.hypot(eq.x,eq.y)))

def ayana(name,dec):
 k=abs(dec) if name=="Mercury" else dec if name in AYANA_NORTH else -dec
 val=60.0*(23.45+k)/(2*23.45)
 val=max(0.0,min(60.0,val))
 return val*2.0 if name=="Sun" else val

def mean_longitude(name,t):
 l0,rate=MEAN_LON[name]
 return (l0+rate*t.ut)%360.0

def cheshta(name,birth,ayana_val,paksha_val):
 if name=="Sun":return ayana_val
 if name=="Moon":return paksha_val
 t=panchang.astronomy_time(birth)
 ms=mean_longitude("Sun",t);mp=mean_longitude(name,t)
 k=(ms-mp)%360 if name in ("Mars","Jupiter","Saturn") else (mp-ms)%360
 if k>180:k=360-k
 return k/3.0

def sphuta_drishti(d):
 d%=360
 if d<=30:return 0.0
 if d<=60:return (d-30)*.5
 if d<=90:return 15+(d-60)
 if d<=120:return 45-(d-90)*.5
 if d<=150:return 30-(d-120)
 if d<=180:return (d-150)*2
 if d<=300:return max(0.0,60-(d-180)*.5)
 return 0.0

def drik(name,states,waxing):
 target=states[name];total=0.0
 for other in PLANETS:
  if other==name:continue
  source=states[other]
  sep=(target["longitude"]-source["longitude"])%360.0
  strength=sphuta_drishti(sep)
  h=house_from(source["rashi_id"],target["rashi_id"])
  if h in SPECIAL[other]:strength=60.0
  benefic=waxing if other=="Moon" else other in BENEFIC
  total+=strength if benefic else -strength
 return total/4.0

def calculate(payload):
 lat=float(payload.get("lat",19.076));lon=float(payload.get("lon",72.8777))
 tzname=payload.get("timezone") or "Asia/Kolkata"
 try:tz=ZoneInfo(tzname)
 except ZoneInfoNotFoundError:tzname="Asia/Kolkata";tz=ZoneInfo(tzname)
 birth=parse_birth(payload,tz);asc=lagna.lagna_state(birth,lat,lon)
 states={n:planetary.planet_state(n,birth) for n in PLANETS}
 signs={n:states[n]["rashi_id"] for n in PLANETS}
 sunrise,sunset,next_sunrise=solar_context(birth,lat,lon,tz)
 tl=time_lords(birth,sunrise,states["Sun"]["rashi_id"])
 elong=(states["Moon"]["longitude"]-states["Sun"]["longitude"])%360.0
 waxing=0.0<elong<180.0
 rows={}
 for name in PLANETS:
  st=states[name];h=house(st["rashi_id"],asc["lagna_id"])
  nav=vargas.varga_position(st["longitude"],9)
  sap,sapdetail=saptavargaja(name,st["longitude"],signs)
  uc=uchcha(name,st["longitude"]);oj=oja(name,st["rashi_id"],nav["rashi_id"]);ke=kendra(h);dr=drekkana(name,st["degree_in_rashi"])
  sthana=uc+sap+oj+ke+dr
  di=dig(name,st["longitude"],asc["sidereal_longitude"])
  na=nathonnatha(name,birth);pa=paksha(name,states["Sun"]["longitude"],states["Moon"]["longitude"]);tr=tribhaga(name,birth,sunrise,sunset,next_sunrise)
  dec=declination(name,birth);ay=ayana(name,dec)
  time_parts={
   "nathonnatha":na,"paksha":pa,"tribhaga":tr,
   "abda":15.0 if tl["abda"]==name else 0.0,
   "masa":30.0 if tl["masa"]==name else 0.0,
   "vara":45.0 if tl["vara"]==name else 0.0,
   "hora":60.0 if tl["hora"]==name else 0.0,
   "ayana":ay,"yuddha":0.0
  }
  kala=sum(time_parts.values())
  ch=cheshta(name,birth,ay,pa);nai=NAIS[name];dri=drik(name,states,waxing)
  total=sthana+di+kala+ch+nai+dri
  rows[name]={
   "planet":name,"rashi":st["rashi"],"house":h,"longitude":st["longitude"],"retrograde":st["retrograde"],
   "components_virupa":{
    "sthana":{"uchcha":uc,"saptavargaja":sap,"ojayugma":oj,"kendradi":ke,"drekkana":dr,"subtotal":sthana,"saptavargaja_detail":sapdetail},
    "dig":di,
    "kala":{**time_parts,"subtotal":kala,"lords":{k:tl[k] for k in ("abda","masa","vara","hora")}},
    "cheshta":ch,"naisargika":nai,"drik":dri,"declination_deg":dec
   },
   "total_virupa":total,"total_rupa":total/60.0,"required_rupa":REQUIRED[name]
  }
 # Yuddha Bala: same-Rashi star planets within 1°, greater declination wins.
 warriors=["Mars","Mercury","Jupiter","Venus","Saturn"]
 for i,a in enumerate(warriors):
  for b in warriors[i+1:]:
   if states[a]["rashi_id"]!=states[b]["rashi_id"]:continue
   sep=fold_distance(states[a]["longitude"],states[b]["longitude"])
   if sep>1.0:continue
   da=rows[a]["components_virupa"]["declination_deg"];db=rows[b]["components_virupa"]["declination_deg"]
   winner,loser=(a,b) if da>=db else (b,a)
   diff=abs(rows[a]["total_virupa"]-rows[b]["total_virupa"])
   for who,sgn in ((winner,1),(loser,-1)):
    rows[who]["components_virupa"]["kala"]["yuddha"]=sgn*diff
    rows[who]["components_virupa"]["kala"]["subtotal"]+=sgn*diff
    rows[who]["total_virupa"]+=sgn*diff
    rows[who]["total_rupa"]=rows[who]["total_virupa"]/60.0
 for name in PLANETS:
  rows[name]["meets_required"]=rows[name]["total_rupa"]>=rows[name]["required_rupa"]
  rows[name]["ratio"]=rows[name]["total_rupa"]/rows[name]["required_rupa"]
  # Round public numerics only after all arithmetic is complete.
  c=rows[name]["components_virupa"]
  for key in ("dig","cheshta","naisargika","drik","declination_deg"):
   c[key]=round(c[key],4)
  for key in ("uchcha","saptavargaja","ojayugma","kendradi","drekkana","subtotal"):
   c["sthana"][key]=round(c["sthana"][key],4)
  for key in ("nathonnatha","paksha","tribhaga","abda","masa","vara","hora","ayana","yuddha","subtotal"):
   c["kala"][key]=round(c["kala"][key],4)
  rows[name]["total_virupa"]=round(rows[name]["total_virupa"],4)
  rows[name]["total_rupa"]=round(rows[name]["total_rupa"],4)
  rows[name]["ratio"]=round(rows[name]["ratio"],4)
 return {
  "ok":True,"birth_datetime":birth.isoformat(),
  "engine":{
   "name":"tithika-shadbala","version":ENGINE_VERSION,"status":"complete-six-fold-profile",
   "ayanamsha":"Lahiri / Chitrapaksha","units":"virupa (60 = 1 rupa)",
   "required_rupa_profile":"Sun 6.5, Moon 6, Mars 5, Mercury 7, Jupiter 6.5, Venus 5.5, Saturn 5"
  },
  "lagna":{"rashi":asc["lagna"],"longitude":asc["sidereal_longitude"]},
  "solar_context":{"sunrise":sunrise.isoformat(),"sunset":sunset.isoformat(),"next_sunrise":next_sunrise.isoformat()},
  "time_lords":tl,"planets":[rows[n] for n in PLANETS],
  "method_notes":[
   "Saptavargaja uses D1,D2,D3,D7,D9,D12,D30 with five-fold compound friendship; D1 Moolatrikona uses degree ranges.",
   "Dig Bala uses equal 30° directional cusps from the exact Lagna longitude.",
   "Kala Bala includes Nathonnatha, Paksha, Tribhaga, Abda, Masa, Vara, equal-hour Hora, Ayana and Yuddha.",
   "Cheshta uses the mean-longitude Seeghra/Cheshta Kendra profile; Sun=Ayana and Moon=Paksha.",
   "Drik uses the graded Parashari Sphuta Drishti curve, with Mars/Jupiter/Saturn special aspects at full strength.",
   "Mercury is treated as a natural benefic for Drik in this declared profile; Moon is benefic while waxing.",
   "Published traditions differ on some conventions and on the Sun's required threshold; Tithika exposes its profile instead of hiding it."
  ],
  "note":"Shadbala measures planetary capacity, not whether a planet is beneficial or harmful. Interpret strength together with lordship, dignity, Yogas and Dasha."
 }

def main():
 print(json.dumps(calculate(json.loads(sys.stdin.read() or "{}")),ensure_ascii=False))
if __name__=="__main__":
 try:main()
 except Exception as e:
  print(json.dumps({"ok":False,"error":str(e),"code":"SHADBALA_CALCULATION_FAILED"}));sys.exit(1)

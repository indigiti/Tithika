#!/usr/bin/env python3
import os,sys
from datetime import date,datetime
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import muhurat_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567;d=date(2026,10,6)
g=x.gowri(d,lat,lon,tz);assert [r["title"] for r in g[0]["items"]]==x.DAY_GOWRI[d.weekday()]
expected=["Rudra","Uraga","Mitra","Pitara","Vasu","Ambu","Vishwedeva","Vidhi","Brahma","Indra","Indragni","Daitya","Varuna","Aryama","Bhaga","Ishwara","Ajaikapada","Ahirbudhnya","Pusha","Ashwini","Yama","Agni","Brahma","Chandra","Aditi","Brihaspati","Vishnu","Surya","Tvashta","Samirana"]
dg=x.do_ghati(d,lat,lon,tz)[0]["items"];assert [r["title"] for r in dg]==expected
p=x.pachchakkhan(d,lat,lon,tz)[0]["items"];assert len(p)==10 and p[0]["title"]=="Navkarshi"
pak=x.pakshi_sections(d,lat,lon,tz,"Peacock");assert sum(len(s["items"]) for s in pak)==50
first5=pak[0]["items"][:5]
dur=[round((datetime.fromisoformat(r["end"])-datetime.fromisoformat(r["start"])).total_seconds()/60,2) for r in first5]
assert len(set(dur))==5,dur
ratio=[x.SUB_YAMA_SHARE[r["title"].split("/")[-1].strip()] for r in first5]
scaled=[v/dur[0] for v in dur];expected_scaled=[v/ratio[0] for v in ratio]
assert max(abs(a-b) for a,b in zip(scaled,expected_scaled))<0.03,(dur,ratio)
assert len(x.shubha_dates(2026,lat,lon,tz)[0]["items"])>0
print("Muhurat completion truth fixture passed")

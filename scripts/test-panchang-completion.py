#!/usr/bin/env python3
import os,sys
from datetime import date,datetime,timedelta
from zoneinfo import ZoneInfo
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,os.path.join(ROOT,"python"))
import panchang,panchang_completion as x
tz=ZoneInfo("Asia/Kolkata");lat,lon=18.5204,73.8567
assert len(x.MANVADI)==14 and len(x.YUGADI)==4 and len(x.KALPADI)==7
for rules in (x.MANVADI,x.YUGADI,x.KALPADI):
    rows=x.select_lunar_rules(2026,lat,lon,tz,rules)
    assert rows
    by_title={a:(m,p,n) for a,m,p,n in rules}
    for row in rows:
        d=date.fromisoformat(row["date"]);sr=x.sunrise(d,lat,lon,tz);st=panchang.state_at(sr+timedelta(seconds=1));mi=panchang.lunar_month_info(sr,st)
        m,p,n=by_title[row["title"]]
        assert x.norm_month(mi.get("purnimanta"))==m
        assert st["paksha"]==p and int(st["tithi_number"])==n
kr=x.kranti_rows(2026,tz)
assert kr
for row in kr:
    s=x.kranti_state(datetime.fromisoformat(row["instant"]))
    assert s["eligible"] and s["absolute_difference"]<1e-5,s
snap=x.published_snapshot(date(2026,10,6),lat,lon,tz)
assert snap and "Publication-ready" in snap[0]["title"]
assert len(x.utilities())>=10
print("Panchang completion semantic fixture passed")

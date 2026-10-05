#!/usr/bin/env python3
import sys, json, math
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DAY_SEQUENCES = {
    6: ["Udveg","Chara","Labh","Amrit","Kaal","Shubh","Rog","Udveg"],
    0: ["Amrit","Kaal","Shubh","Rog","Udveg","Chara","Labh","Amrit"],
    1: ["Rog","Udveg","Chara","Labh","Amrit","Kaal","Shubh","Rog"],
    2: ["Labh","Amrit","Kaal","Shubh","Rog","Udveg","Chara","Labh"],
    3: ["Shubh","Rog","Udveg","Chara","Labh","Amrit","Kaal","Shubh"],
    4: ["Chara","Labh","Amrit","Kaal","Shubh","Rog","Udveg","Chara"],
    5: ["Kaal","Shubh","Rog","Udveg","Chara","Labh","Amrit","Kaal"],
}
NIGHT_SEQUENCES = {
    6: ["Shubh","Amrit","Chara","Rog","Kaal","Labh","Udveg","Shubh"],
    0: ["Chara","Rog","Kaal","Labh","Udveg","Shubh","Amrit","Chara"],
    1: ["Kaal","Labh","Udveg","Shubh","Amrit","Chara","Rog","Kaal"],
    2: ["Udveg","Shubh","Amrit","Chara","Rog","Kaal","Labh","Udveg"],
    3: ["Amrit","Chara","Rog","Kaal","Labh","Udveg","Shubh","Amrit"],
    4: ["Rog","Kaal","Labh","Udveg","Shubh","Amrit","Chara","Rog"],
    5: ["Labh","Udveg","Shubh","Amrit","Chara","Rog","Kaal","Labh"],
}
RAHU_SEGMENT = {6:8, 0:2, 1:7, 2:5, 3:6, 4:4, 5:3}
TYPE_META = {
    "Amrit": {"quality":"best","label":"Best","emoji":"✦"},
    "Shubh": {"quality":"good","label":"Good","emoji":"✦"},
    "Labh": {"quality":"gain","label":"Gain","emoji":"↗"},
    "Chara": {"quality":"neutral","label":"Neutral","emoji":"→"},
    "Udveg": {"quality":"avoid","label":"Avoid","emoji":"!"},
    "Kaal": {"quality":"avoid","label":"Avoid","emoji":"!"},
    "Rog": {"quality":"avoid","label":"Avoid","emoji":"!"},
}

def norm(v, m): return v % m

def solar_event(local_date: date, lat: float, lon: float, tz: ZoneInfo, sunrise: bool):
    n = local_date.timetuple().tm_yday
    lng_hour = lon / 15.0
    t = n + (((6 if sunrise else 18) - lng_hour) / 24.0)
    m = (0.9856 * t) - 3.289
    l = m + (1.916 * math.sin(math.radians(m))) + (0.020 * math.sin(math.radians(2*m))) + 282.634
    l = norm(l, 360)
    ra = math.degrees(math.atan(0.91764 * math.tan(math.radians(l))))
    ra = norm(ra, 360)
    lq = math.floor(l / 90) * 90
    raq = math.floor(ra / 90) * 90
    ra = (ra + (lq - raq)) / 15.0
    sin_dec = 0.39782 * math.sin(math.radians(l))
    cos_dec = math.cos(math.asin(sin_dec))
    cos_h = (math.cos(math.radians(90.833)) - (sin_dec * math.sin(math.radians(lat)))) / (cos_dec * math.cos(math.radians(lat)))
    if cos_h > 1 or cos_h < -1:
        return None
    h = (360 - math.degrees(math.acos(cos_h))) if sunrise else math.degrees(math.acos(cos_h))
    h /= 15.0
    local_mean = h + ra - (0.06571 * t) - 6.622
    ut_hours = norm(local_mean - lng_hour, 24)
    h_int = int(ut_hours)
    mins_f = (ut_hours - h_int) * 60
    m_int = int(mins_f)
    s_int = int(round((mins_f - m_int)*60))
    if s_int == 60:
        s_int = 0; m_int += 1
    if m_int == 60:
        m_int = 0; h_int = (h_int + 1) % 24
    utc_dt = datetime(local_date.year, local_date.month, local_date.day, h_int, m_int, s_int, tzinfo=timezone.utc)
    local_dt = utc_dt.astimezone(tz)
    while local_dt.date() < local_date:
        utc_dt += timedelta(days=1); local_dt = utc_dt.astimezone(tz)
    while local_dt.date() > local_date:
        utc_dt -= timedelta(days=1); local_dt = utc_dt.astimezone(tz)
    return local_dt

def fmt(dt, hour24=False):
    rounded = dt + timedelta(seconds=30)
    rounded = rounded.replace(second=0, microsecond=0)
    return rounded.strftime("%H:%M" if hour24 else "%I:%M %p").lstrip("0")

def period_rows(start, end, names, hour24=False):
    span = (end - start) / 8
    out = []
    for i, name in enumerate(names):
        s = start + span * i
        e = start + span * (i + 1)
        out.append({
            "index": i+1, "name": name,
            "start": s.isoformat(), "end": e.isoformat(),
            "start_label": fmt(s, hour24), "end_label": fmt(e, hour24),
            **TYPE_META[name]
        })
    return out

def main():
    raw = sys.stdin.read()
    payload = json.loads(raw or "{}")
    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")
    date_s = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
    d = datetime.strptime(date_s, "%Y-%m-%d").date()
    tz_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        tz_name = "Asia/Kolkata"; tz = ZoneInfo(tz_name)
    hour24 = bool(payload.get("hour24", False))
    city = (payload.get("city") or "Current location").strip()[:120]

    sunrise = solar_event(d, lat, lon, tz, True)
    sunset = solar_event(d, lat, lon, tz, False)
    next_sunrise = solar_event(d + timedelta(days=1), lat, lon, tz, True)
    if not sunrise or not sunset or not next_sunrise:
        raise ValueError("Sunrise/sunset unavailable for this latitude/date")
    if sunset <= sunrise:
        sunset += timedelta(days=1)
    if next_sunrise <= sunset:
        next_sunrise += timedelta(days=1)

    wd = d.weekday()
    day_rows = period_rows(sunrise, sunset, DAY_SEQUENCES[wd], hour24)
    night_rows = period_rows(sunset, next_sunrise, NIGHT_SEQUENCES[wd], hour24)
    rahu_idx = RAHU_SEGMENT[wd] - 1
    rahu = {"start": day_rows[rahu_idx]["start"], "end": day_rows[rahu_idx]["end"],
            "start_label": day_rows[rahu_idx]["start_label"], "end_label": day_rows[rahu_idx]["end_label"]}

    now = datetime.now(tz)
    active = None
    carry_night_rows = []
    if d == now.date():
        if now < sunrise:
            prev_d = d - timedelta(days=1)
            prev_sunset = solar_event(prev_d, lat, lon, tz, False)
            if prev_sunset:
                carry_night_rows = period_rows(prev_sunset, sunrise, NIGHT_SEQUENCES[prev_d.weekday()], hour24)
                for row in carry_night_rows:
                    s = datetime.fromisoformat(row["start"]); e = datetime.fromisoformat(row["end"])
                    if s <= now < e:
                        active = {**row, "side":"night", "carry_from_previous_date":True}
                        break
        else:
            for side, rows in (("day", day_rows),("night", night_rows)):
                for row in rows:
                    s = datetime.fromisoformat(row["start"]); e = datetime.fromisoformat(row["end"])
                    if s <= now < e:
                        active = {**row, "side": side}
                        break
                if active: break

    good = {"Amrit":3,"Shubh":2,"Labh":1}
    upcoming = []
    scan_groups = []
    if d == now.date() and carry_night_rows:
        scan_groups.append(("night", carry_night_rows))
    scan_groups.extend((("day",day_rows),("night",night_rows)))
    for side, rows in scan_groups:
        for row in rows:
            if row["name"] in good:
                s = datetime.fromisoformat(row["start"])
                if d != now.date() or s >= now:
                    upcoming.append({**row, "side":side})
    upcoming.sort(key=lambda x: x["start"])

    output = {
        "ok": True,
        "location": {"city":city,"lat":lat,"lon":lon,"timezone":tz_name},
        "date": d.isoformat(), "weekday": d.strftime("%A"),
        "date_label": d.strftime("%B %d, %Y").replace(" 0", " "),
        "sunrise": sunrise.isoformat(), "sunset": sunset.isoformat(), "next_sunrise": next_sunrise.isoformat(),
        "sunrise_label": fmt(sunrise,hour24), "sunset_label": fmt(sunset,hour24),
        "day": day_rows, "night": night_rows, "active": active,
        "rahu_kaal": rahu,
        "next_auspicious": upcoming[0] if upcoming else None,
        "generated_at": now.isoformat(),
        "method": "Sunrise/sunset at 90.833° solar zenith; day and night each divided into 8 equal local periods."
    }
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"ok":False,"error":str(e)}))
        sys.exit(1)

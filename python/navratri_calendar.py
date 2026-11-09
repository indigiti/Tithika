#!/usr/bin/env python3
"""Four Navratri calendar projections over Tithika's deterministic Panchang.

Astronomy and Ghatasthapana reuse the shared festival engine. Tithi dates and
ritual-day conventions are distinct; skipped/repeated sunrise Tithis are labelled.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import festival_rules
import panchang

ENGINE_VERSION = "1.0.0"
VARIANTS = {
    "shardiya": {"kind": "navratri", "title": "Shardiya (Ashwin) Navratri",
                 "slug": "calendars/shardiya-navratri",
                 "context": "Ashwina Shukla Paksha · autumn Navratri"},
    "chaitra": {"kind": "navratri-chaitra", "title": "Chaitra (Vasanta) Navratri",
                "slug": "calendars/chaitra-navratri",
                "context": "Chaitra Shukla Paksha · spring Navratri"},
    "magha-gupta": {"kind": "navratri-magha-gupta", "title": "Magha Gupta Navratri",
                    "slug": "calendars/magha-gupta-navratri",
                    "context": "Magha Shukla Paksha · winter Gupta Navratri"},
    "ashadha-gupta": {"kind": "navratri-ashadha-gupta", "title": "Ashadha Gupta Navratri",
                      "slug": "calendars/ashadha-gupta-navratri",
                      "context": "Ashadha Shukla Paksha · monsoon Gupta Navratri"},
}
SLUG_TO_VARIANT = {v["slug"]: k for k, v in VARIANTS.items()}
ALL_SLUGS = set(SLUG_TO_VARIANT) | {"calendars/navratri", "festivals/ghatasthapana"}
GODDESSES = ("Shailaputri", "Brahmacharini", "Chandraghanta",
             "Kushmanda", "Skandamata", "Katyayani", "Kalaratri",
             "Mahagauri", "Siddhidatri")
TITHIS = ("Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
          "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami")
MEANINGS = (
    "First manifestation of Durga, associated with steadiness and new beginnings.",
    "The contemplative form of Devi, associated with discipline and devotion.",
    "The protective form of Devi, associated with courage and composure.",
    "The creative aspect of Devi, associated with vitality and the cosmos.",
    "Maternal aspect of Devi, associated with care and protection.",
    "Warrior aspect of Devi, traditionally associated with strength and resolve.",
    "The transformative form of Devi, traditionally associated with overcoming fear.",
    "The serene form of Devi, traditionally associated with renewal and compassion.",
    "The accomplished form of Devi, associated with fulfillment and wisdom.",
)

def next_tithi_end(start: datetime, index: int, tz: ZoneInfo) -> datetime:
    phase = float(((index + 1) * 12) % 360)
    result = panchang.astronomy.SearchMoonPhase(
        phase, panchang.astronomy_time(start + timedelta(seconds=2)), 4.0,
    )
    if result is None:
        raise RuntimeError(f"No transition found for Shukla {TITHIS[index]}")
    end = panchang.datetime_from_astronomy(result, tz)
    if not (start < end < start + timedelta(days=3)):
        raise RuntimeError("Invalid Navratri Tithi transition")
    return end

def sunrise_placement(start: datetime, end: datetime, lat: float,
                      lon: float, tz: ZoneInfo) -> tuple[date, str, int]:
    matches = []
    for day in festival_rules.candidate_dates(start, end):
        sr = festival_rules.rise(day, lat, lon, tz)
        if sr and start <= sr < end:
            matches.append(day)
    if matches:
        return matches[0], ("vriddhi-two-sunrises" if len(matches) > 1 else "sunrise"), len(matches)
    selected = festival_rules.choose_by_period(
        start, end,
        lambda day: (
            (p["sunrise"], p["sunset"])
            if (p := festival_rules.solar_day_parts(day, lat, lon, tz)) else None
        ),
    )
    if selected:
        return selected["date"], "kshaya-no-sunrise-daylight-reference", 0
    return (start + (end - start)/2).date(), "kshaya-no-sunrise-midpoint-reference", 0

def calculate_variant(key: str, year: int, lat: float, lon: float,
                      tz: ZoneInfo, hour24: bool = False) -> dict | None:
    cfg = VARIANTS[key]
    event = festival_rules.calculate_event(cfg["kind"], year, lat, lon, tz, hour24)
    if event is None:
        return None
    start = datetime.fromisoformat(event["tithi_start"])
    end = datetime.fromisoformat(event["tithi_end"])
    days = []
    for i in range(9):
        if i > 0:
            end = next_tithi_end(start, i, tz)
        day, status, sr_count = sunrise_placement(start, end, lat, lon, tz)
        if i == 0:
            day = date.fromisoformat(event["date"])
        message = (
            "Tithi spans two local sunrises; a regional observance-day decision may be needed."
            if status == "vriddhi-two-sunrises" else
            "This Tithi does not prevail at a local sunrise. Displayed day is a reference, not a certified puja date."
            if status.startswith("kshaya") else
            "Tithi present at local sunrise."
        )
        days.append({
            "day": i + 1, "title": GODDESSES[i] + " Puja",
            "goddess": GODDESSES[i], "meaning": MEANINGS[i],
            "tithi": TITHIS[i], "date": day.isoformat(),
            "weekday": day.strftime("%A"), "selection": status,
            "sunrise_count": sr_count, "detail": message,
            "tithi_start": start.isoformat(), "tithi_end": end.isoformat(),
            "tithi_start_label": panchang.transition_label(start, day, hour24),
            "tithi_end_label": panchang.transition_label(end, day, hour24),
            "link_date": day.isoformat(),
        })
        start = end
    ashtami_end = datetime.fromisoformat(days[7]["tithi_end"])
    sandhi = festival_rules.window(
        ashtami_end - timedelta(minutes=24),
        ashtami_end + timedelta(minutes=24),
        ashtami_end.date(), hour24,
    )
    dashami_end = next_tithi_end(start, 9, tz)
    dashami_date, dashami_status, _ = sunrise_placement(start, dashami_end, lat, lon, tz)
    additional = []
    if key == "chaitra":
        rama = festival_rules.calculate_event("rama-navami", year, lat, lon, tz, hour24)
        if rama:
            additional.append({"title": "Rama Navami", "date": rama["date"],
                               "detail": "Madhyahna-based observance date calculated by the dedicated Rama Navami rule.",
                               "link_slug": "festivals/rama-navami"})
    if key == "shardiya":
        vijay = festival_rules.calculate_event("dussehra", year, lat, lon, tz, hour24)
        if vijay:
            additional.append({"title": "Vijayadashami", "date": vijay["date"],
                               "detail": "Aparahna-based observance date calculated by the dedicated Dussehra rule.",
                               "link_slug": "festivals/dussehra"})
    return {
        "variant": key, "title": cfg["title"], "slug": cfg["slug"],
        "context": cfg["context"], "year": year, "event": event,
        "days": days, "sandhi": sandhi,
        "dashami": {"date": dashami_date.isoformat(), "selection": dashami_status,
                    "tithi_start": start.isoformat(), "tithi_end": dashami_end.isoformat()},
        "additional": additional, "status": "calculated-with-regional-review",
    }

def _row(title: str, when: str = "", meta: str = "", detail: str = "",
         link_slug: str = "") -> dict:
    result = {"title": title, "meta": meta, "detail": detail}
    if when: result.update({"date": when, "link_date": when})
    if link_slug: result["link_slug"] = link_slug
    return result

def render(slug: str, year: int, lat: float, lon: float,
           tz: ZoneInfo, hour24: bool = False) -> dict:
    if slug not in ALL_SLUGS:
        raise ValueError("Unsupported Navratri calendar route")
    is_hub = slug in ("calendars/navratri", "festivals/ghatasthapana")
    keys = list(VARIANTS) if is_hub else [SLUG_TO_VARIANT[slug]]
    variants = [calculate_variant(k, year, lat, lon, tz, hour24) for k in keys]
    if any(v is None for v in variants):
        raise RuntimeError("One or more Navratri variants have no calculated occurrence")
    metrics, sections = [], []
    if is_hub:
        title = "Ghatasthapana / Kalash Sthapana" if slug == "festivals/ghatasthapana" else "Four Navratri Calendars"
        rows = []
        for v in variants:
            e = v["event"]
            interval = e.get("ghatasthapana") or {}
            time = " – ".join(filter(None, [interval.get("start_label"), interval.get("end_label")]))
            rows.append(_row(v["title"], e["date"], v["context"] + " · " + time,
                             e.get("ghatasthapana_basis", ""),
                             v["slug"]))
        sections = [{"title": f"All four Navratris · {year}",
                     "note": "Each date and Ghatasthapana interval is calculated for the chosen location. Open a variant for day-by-day Tithis.",
                     "items": rows}]
        metrics = [{"label": "Annual Navratris", "value": "4", "note": "Two public · Two Gupta"},
                   {"label": "Timezone", "value": str(tz), "note": "Local solar events"}]
        summary = "Four location-sensitive Navratri variants with direct links to individual calendars."
    else:
        v = variants[0]
        e = v["event"]
        gh = e.get("ghatasthapana") or {}
        title = v["title"]
        start = " – ".join(filter(None, [gh.get("start_label"), gh.get("end_label")]))
        caution = ", ".join(k.replace("_", " ") for k, val in e.get("warnings", {}).items() if val)
        sections = [
            {"title": "Ghatasthapana / Kalash Sthapana",
             "note": "Computed as Shukla Pratipada overlap with the first third of local daylight, or a labelled Abhijit alternative. Ritual exclusions and local customs require confirmation.",
             "items": [_row("Ghatasthapana", e["date"], start,
                             e.get("ghatasthapana_basis", "") +
                             (" · Check " + caution if caution else ""))]},
            {"title": "Nine Shukla Paksha Tithis and Navdurga",
             "note": "Nine Tithis are not necessarily nine distinct civil days. Repeated or skipped sunrise Tithis are labelled.",
             "items": [
                 _row("Shukla " + day["tithi"] + " · " + day["title"], day["date"],
                      day["weekday"] + " · " + day["tithi_start_label"] + " – " + day["tithi_end_label"],
                      day["meaning"] + " " + day["detail"])
                 for day in v["days"]]},
            {"title": "Sandhi Puja and end-of-Navratri context",
             "note": "Sandhi overlaps Ashtami and Navami by 24 minutes on each side of their astronomical boundary.",
             "items": [_row("Sandhi Puja", v["days"][7]["date"],
                            " – ".join(filter(None, [v["sandhi"]["start_label"], v["sandhi"]["end_label"]])),
                            "Exact Ashtami–Navami transition plus/minus 24 minutes."),
                       _row("Shukla Dashami", v["dashami"]["date"], v["dashami"]["selection"],
                            "Dashami sunrise reference; observance dates vary by custom.")] +
                       [_row(a["title"], a["date"], "", a["detail"], a["link_slug"]) for a in v["additional"]]},
        ]
        metrics = [
            {"label": "Ghatasthapana", "value": e["date"], "note": start},
            {"label": "Puja Tithis", "value": "9", "note": "Pratipada–Navami"},
            {"label": "Sunrise exceptions", "value": str(sum(d["selection"] != "sunrise" for d in v["days"])),
             "note": "Review kshaya / vriddhi"},
        ]
        summary = v["context"] + ". Dates depend on city, timezone and local Tithi boundaries."
    return {"ok": True, "family": "navratri-calendar", "slug": slug, "title": title,
            "year": year, "summary": summary, "metrics": metrics, "sections": sections,
            "navratri": {"variants": variants, "overview": is_hub},
            "engine": {"name": "tithika-navratri-calendar",
                       "version": ENGINE_VERSION,
                       "basis": "Lahiri sunrise-Tithi and explicit festival selectors"}}

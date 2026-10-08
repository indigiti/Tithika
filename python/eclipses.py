#!/usr/bin/env python3
"""
Tithika eclipse engine.

Uses the vendored Astronomy Engine for physical eclipse geometry:
- global solar eclipses
- local solar eclipse contacts and obscuration
- lunar eclipse classification and phase durations

Tithika adds selected-location lunar altitude/visibility and local-time rendering.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import panchang

ENGINE_VERSION = "0.1.0"


def kind_name(kind) -> str:
    return {
        panchang.astronomy.EclipseKind.Penumbral: "Penumbral",
        panchang.astronomy.EclipseKind.Partial: "Partial",
        panchang.astronomy.EclipseKind.Annular: "Annular",
        panchang.astronomy.EclipseKind.Total: "Total",
    }.get(kind, "Unknown")


def local_dt(t, tz: ZoneInfo) -> datetime:
    return panchang.datetime_from_astronomy(t, tz)


def event_payload(t, tz: ZoneInfo):
    if t is None:
        return None
    dt = local_dt(t, tz)
    return {
        "datetime": dt.isoformat(),
        "date": dt.date().isoformat(),
        "label": dt.strftime("%b %d, %Y %I:%M %p").replace(" 0", " "),
    }


def eclipse_event_payload(event, tz: ZoneInfo):
    if event is None:
        return None
    row = event_payload(event.time, tz)
    row["altitude_deg"] = round(float(event.altitude), 5)
    row["visible"] = event.altitude > 0.0
    return row


def moon_altitude(t, observer) -> float:
    eq = panchang.astronomy.Equator(
        panchang.astronomy.Body.Moon, t, observer, True, True
    )
    hor = panchang.astronomy.Horizon(
        t, observer, eq.ra, eq.dec, panchang.astronomy.Refraction.Normal
    )
    return float(hor.altitude)


def lunar_phase_event(peak, delta_minutes: float, observer, tz):
    t = peak.AddDays(delta_minutes / 1440.0)
    row = event_payload(t, tz)
    alt = moon_altitude(t, observer)
    row["altitude_deg"] = round(alt, 5)
    row["visible"] = alt > 0.0
    return row


def global_solar_events(year: int, tz: ZoneInfo):
    start = panchang.astronomy_time(datetime(year, 1, 1, tzinfo=tz))
    rows = []
    eclipse = panchang.astronomy.SearchGlobalSolarEclipse(start)
    while True:
        peak_dt = local_dt(eclipse.peak, tz)
        if peak_dt.year > year:
            break
        if peak_dt.year == year:
            rows.append({
                "type": "solar",
                "kind": kind_name(eclipse.kind),
                "name": f"{kind_name(eclipse.kind)} Solar Eclipse",
                "peak": event_payload(eclipse.peak, tz),
                "obscuration": (
                    round(float(eclipse.obscuration), 8)
                    if eclipse.obscuration is not None else None
                ),
                "peak_latitude": (
                    round(float(eclipse.latitude), 6)
                    if eclipse.kind in (
                        panchang.astronomy.EclipseKind.Annular,
                        panchang.astronomy.EclipseKind.Total,
                    ) else None
                ),
                "peak_longitude": (
                    round(float(eclipse.longitude), 6)
                    if eclipse.kind in (
                        panchang.astronomy.EclipseKind.Annular,
                        panchang.astronomy.EclipseKind.Total,
                    ) else None
                ),
            })
        eclipse = panchang.astronomy.NextGlobalSolarEclipse(eclipse.peak)
    return rows


def local_solar_events(year: int, lat: float, lon: float, tz: ZoneInfo):
    observer = panchang.astronomy.Observer(lat, lon, panchang.observer_elevation())
    start = panchang.astronomy_time(datetime(year, 1, 1, tzinfo=tz))
    rows = []
    eclipse = panchang.astronomy.SearchLocalSolarEclipse(start, observer)
    while True:
        peak_dt = local_dt(eclipse.peak.time, tz)
        if peak_dt.year > year:
            break
        if peak_dt.year == year:
            rows.append({
                "type": "solar",
                "kind": kind_name(eclipse.kind),
                "name": f"{kind_name(eclipse.kind)} Solar Eclipse",
                "obscuration": round(float(eclipse.obscuration), 8),
                "partial_begin": eclipse_event_payload(eclipse.partial_begin, tz),
                "total_begin": eclipse_event_payload(eclipse.total_begin, tz),
                "peak": eclipse_event_payload(eclipse.peak, tz),
                "total_end": eclipse_event_payload(eclipse.total_end, tz),
                "partial_end": eclipse_event_payload(eclipse.partial_end, tz),
                "locally_visible": (
                    eclipse.partial_begin.altitude > 0
                    or eclipse.peak.altitude > 0
                    or eclipse.partial_end.altitude > 0
                ),
            })
        eclipse = panchang.astronomy.NextLocalSolarEclipse(eclipse.peak.time, observer)
    return rows


def lunar_events(year: int, lat: float, lon: float, tz: ZoneInfo):
    observer = panchang.astronomy.Observer(lat, lon, 0.0)
    start = panchang.astronomy_time(datetime(year, 1, 1, tzinfo=tz))
    rows = []
    eclipse = panchang.astronomy.SearchLunarEclipse(start)

    while True:
        peak_dt = local_dt(eclipse.peak, tz)
        if peak_dt.year > year:
            break
        if peak_dt.year == year:
            phases = {
                "penumbral_begin": lunar_phase_event(eclipse.peak, -eclipse.sd_penum, observer, tz),
                "partial_begin": (
                    lunar_phase_event(eclipse.peak, -eclipse.sd_partial, observer, tz)
                    if eclipse.sd_partial > 0 else None
                ),
                "total_begin": (
                    lunar_phase_event(eclipse.peak, -eclipse.sd_total, observer, tz)
                    if eclipse.sd_total > 0 else None
                ),
                "peak": lunar_phase_event(eclipse.peak, 0.0, observer, tz),
                "total_end": (
                    lunar_phase_event(eclipse.peak, eclipse.sd_total, observer, tz)
                    if eclipse.sd_total > 0 else None
                ),
                "partial_end": (
                    lunar_phase_event(eclipse.peak, eclipse.sd_partial, observer, tz)
                    if eclipse.sd_partial > 0 else None
                ),
                "penumbral_end": lunar_phase_event(eclipse.peak, eclipse.sd_penum, observer, tz),
            }
            locally_visible = any(
                row and row["visible"] for row in phases.values()
            )
            rows.append({
                "type": "lunar",
                "kind": kind_name(eclipse.kind),
                "name": f"{kind_name(eclipse.kind)} Lunar Eclipse",
                "obscuration": round(float(eclipse.obscuration), 8),
                "peak": phases["peak"],
                "phases": phases,
                "locally_visible": locally_visible,
                "semi_duration_minutes": {
                    "penumbral": round(float(eclipse.sd_penum), 5),
                    "partial": round(float(eclipse.sd_partial), 5),
                    "total": round(float(eclipse.sd_total), 5),
                },
            })
        eclipse = panchang.astronomy.NextLunarEclipse(eclipse.peak)
    return rows


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    mode = str(payload.get("mode") or "all").lower()
    if mode not in ("all", "solar", "lunar"):
        raise ValueError("Unsupported eclipse mode")

    lat = float(payload.get("lat", 19.0760))
    lon = float(payload.get("lon", 72.8777))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Invalid latitude/longitude")

    timezone_name = payload.get("timezone") or "Asia/Kolkata"
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "Asia/Kolkata"
        tz = ZoneInfo(timezone_name)

    selected = datetime.strptime(
        payload.get("date") or datetime.now(tz).strftime("%Y-%m-%d"), "%Y-%m-%d"
    ).date()
    year = selected.year
    city = (payload.get("city") or "Current location").strip()[:120]

    solar_global = global_solar_events(year, tz) if mode in ("all", "solar") else []
    solar_local = local_solar_events(year, lat, lon, tz) if mode in ("all", "solar") else []
    lunar = lunar_events(year, lat, lon, tz) if mode in ("all", "lunar") else []

    combined = list(solar_global) + list(lunar)
    combined.sort(key=lambda row: row["peak"]["datetime"])

    print(json.dumps({
        "ok": True,
        "mode": mode,
        "year": year,
        "location": {
            "city": city,
            "lat": lat,
            "lon": lon,
            "timezone": timezone_name,
        },
        "engine": {
            "name": "tithika-eclipses",
            "version": ENGINE_VERSION,
            "astronomy": "Astronomy Engine physical shadow geometry",
            "status": "astronomical-eclipse",
        },
        "events": combined,
        "solar_global": solar_global,
        "solar_local": solar_local,
        "lunar": lunar,
        "note": (
            "Global eclipse classification is astronomical. Solar local contacts are "
            "calculated for the selected coordinates; lunar visibility is based on "
            "topocentric Moon altitude during eclipse phases."
        ),
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "code": "ECLIPSE_CALCULATION_FAILED"}))
        sys.exit(1)

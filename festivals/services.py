from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import xmltodict
from django.utils import timezone


def _parse_pub_date(value: Any):
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            return dt
        except ValueError:
            continue
    return None


def parse_festivals_xml(xml_text: str) -> Dict[str, Any]:
    """Parse API XML response into a normalized dict."""
    data = xmltodict.parse(xml_text).get("iq", {})
    items = data.get("item") or []
    if isinstance(items, dict):
        items = [items]

    normalized: List[Dict[str, Any]] = []
    for raw in items:
        normalized.append(
            {
                "external_id": str(raw.get("idx", "")).strip(),
                "title": str(raw.get("title", "")).strip(),
                "link": str(raw.get("link", "")).strip(),
                "category": str(raw.get("gubun", "")).strip(),
                "organizer": str(raw.get("organ", "")).strip(),
                "start_year": str(raw.get("syear", "")).strip(),
                "period": str(raw.get("period", "")).strip(),
                "telephone": str(raw.get("tel", "")).strip(),
                "description": str(raw.get("description", "")).strip(),
                "pub_date": _parse_pub_date(raw.get("pubDate")),
            }
        )

    total_count = data.get("totalCnt")
    try:
        total_count = int(total_count)
    except (TypeError, ValueError):
        total_count = 0

    return {
        "result_code": str(data.get("resultCode", "")).strip(),
        "result_msg": str(data.get("resultMsg", "")).strip(),
        "total_count": total_count,
        "items": normalized,
    }


def parse_date(value: Any):
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_decimal(value: Any):
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None

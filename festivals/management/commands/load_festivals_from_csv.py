import csv
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from festivals.models import Festival
from festivals.services import parse_date, parse_decimal


class Command(BaseCommand):
    help = "Load festival data from a local CSV file (utf-8-sig)."

    def add_arguments(self, parser):
        parser.add_argument("--path", dest="path", default="data.csv", help="CSV file path (default: data.csv)")
        parser.add_argument(
            "--limit",
            dest="limit",
            type=int,
            default=None,
            help="Limit number of rows to import (for quick testing).",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        limit = options.get("limit")
        if not path.exists():
            raise CommandError(f"CSV 파일을 찾을 수 없습니다: {path}")

        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if limit:
                rows = rows[:limit]

        created = 0
        updated = 0

        for row in rows:
            title = (row.get("축제명") or "").strip()
            start_date = parse_date(row.get("축제시작일자"))
            key = f"{title}-{start_date or ''}".strip()
            if not key:
                continue

            defaults = {
                "title": title,
                "place": (row.get("개최장소") or "").strip(),
                "start_date": start_date,
                "end_date": parse_date(row.get("축제종료일자")),
                "description": (row.get("축제내용") or "").strip(),
                "organizer": (row.get("주관기관명") or "").strip(),
                "host": (row.get("주최기관명") or "").strip(),
                "sponsor": (row.get("후원기관명") or "").strip(),
                "telephone": (row.get("전화번호") or "").strip(),
                "homepage": (row.get("홈페이지주소") or "").strip(),
                "extra_info": (row.get("관련정보") or "").strip(),
                "address_road": (row.get("소재지도로명주소") or "").strip(),
                "address_lot": (row.get("소재지지번주소") or "").strip(),
                "latitude": parse_decimal(row.get("위도")),
                "longitude": parse_decimal(row.get("경도")),
                "data_reference_date": parse_date(row.get("데이터기준일자")),
            }

            obj, was_created = Festival.objects.update_or_create(external_id=key[:250], defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"완료: {created}개 생성, {updated}개 업데이트 (총 {created+updated}건)"))

import math
import os
from typing import Tuple

import requests
from django.core.management.base import BaseCommand, CommandError

from festivals.models import Festival
from festivals.services import parse_festivals_xml

API_URL = "http://iq.ifac.or.kr/openAPI/real/search.do"
SERVICE_ID = "festival"


class Command(BaseCommand):
    help = "Fetch and store festival data from the IFAC open API."

    def add_arguments(self, parser):
        parser.add_argument("--api-key", dest="api_key", help="API key (fallback: FESTIVAL_API_KEY env)")
        parser.add_argument(
            "--page-size", dest="page_size", type=int, default=50, help="Items per page (default: 50)"
        )
        parser.add_argument(
            "--pages",
            dest="pages",
            type=int,
            default=None,
            help="Number of pages to fetch. Default is all available pages.",
        )

    def handle(self, *args, **options):
        api_key = options["api_key"] or os.environ.get("FESTIVAL_API_KEY")
        if not api_key:
            raise CommandError("FESTIVAL_API_KEY 환경변수 또는 --api-key 옵션이 필요합니다.")

        page_size = options["page_size"]
        requested_pages = options["pages"]

        self.stdout.write(self.style.MIGRATE_HEADING("Fetching festival data..."))
        created_total = 0
        updated_total = 0

        page = 1
        total_count = None
        while True:
            params = {
                "svID": SERVICE_ID,
                "apiKey": api_key,
                "resultType": "xml",
                "pSize": page_size,
                "cPage": page,
            }
            response = requests.get(API_URL, params=params, timeout=10)
            if response.status_code != 200:
                raise CommandError(f"API 요청 실패 (status={response.status_code})")

            parsed = parse_festivals_xml(response.text)
            if parsed["result_code"] != "0000":
                raise CommandError(f"API 오류: {parsed['result_code']} {parsed['result_msg']}")

            items = parsed["items"]
            if total_count is None:
                total_count = parsed.get("total_count") or 0

            if not items:
                break

            created, updated = self._upsert_items(items)
            created_total += created
            updated_total += updated

            max_pages = requested_pages or math.ceil(total_count / page_size) if total_count else page
            if page >= max_pages:
                break
            page += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"완료: {created_total}개 생성, {updated_total}개 업데이트 (총 {created_total + updated_total}건 처리)"
            )
        )

    def _upsert_items(self, items) -> Tuple[int, int]:
        created = 0
        updated = 0
        for item in items:
            external_id = item.get("external_id")
            if not external_id:
                continue
            obj, was_created = Festival.objects.update_or_create(
                external_id=external_id,
                defaults={
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "organizer": item.get("organizer", ""),
                    "telephone": item.get("telephone", ""),
                    "extra_info": item.get("period", ""),
                    "homepage": item.get("link", ""),
                    "pub_date": item.get("pub_date"),
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1
        return created, updated

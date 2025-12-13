from pathlib import Path
from tempfile import NamedTemporaryFile

from django.test import TestCase
from django.urls import reverse

from festivals.management.commands.load_festivals_from_csv import Command as LoadCsvCommand
from festivals.models import Comment, Festival, FestivalOrganization, Location, Organization
from festivals.services import parse_date, parse_decimal, parse_festivals_xml
from django.contrib.auth.models import User


class ParserTests(TestCase):
    def test_parse_sample_xml(self):
        xml_text = """
        <iq>
            <resultCode>0000</resultCode>
            <resultMsg>ok</resultMsg>
            <totalCnt>1</totalCnt>
            <item>
                <idx>99</idx>
                <title>봄 축제</title>
                <link>http://example.com</link>
                <gubun>지역</gubun>
                <organ>문화재단</organ>
                <syear>2020</syear>
                <period>매년 5월</period>
                <tel>010-0000-0000</tel>
                <description>즐거운 축제</description>
                <pubDate>2024-01-01 10:00:00</pubDate>
            </item>
        </iq>
        """
        parsed = parse_festivals_xml(xml_text)
        self.assertEqual(parsed["result_code"], "0000")
        self.assertEqual(parsed["total_count"], 1)
        self.assertEqual(len(parsed["items"]), 1)
        item = parsed["items"][0]
        self.assertEqual(item["external_id"], "99")
        self.assertEqual(item["title"], "봄 축제")
        self.assertEqual(item["category"], "지역")
        self.assertIsNotNone(item["pub_date"])

    def test_parse_date_decimal_helpers(self):
        self.assertEqual(parse_date("2024-01-02").isoformat(), "2024-01-02")
        self.assertEqual(parse_date("2024.01.02").isoformat(), "2024-01-02")
        self.assertIsNone(parse_date("bad"))
        self.assertAlmostEqual(parse_decimal("37.1234"), 37.1234)
        self.assertAlmostEqual(parse_decimal("37,1234"), 371234.0)
        self.assertIsNone(parse_decimal(""))


class CsvLoadTests(TestCase):
    def test_load_from_csv_creates_records_and_relations(self):
        tmp = NamedTemporaryFile(mode="w+", newline="", encoding="utf-8", delete=False)
        try:
            tmp.write(
                "축제명,개최장소,축제시작일자,축제종료일자,축제내용,주최기관,주관기관,후원기관,전화번호,홈페이지주소,관련정보,소재지도로명주소,소재지지번주소,위도,경도,데이터기준일자\n"
            )
            tmp.write(
                "봄꽃축제,서울,2024-04-01,2024-04-03,즐거운 축제,시청,문화재단,관광공사,010-0000-0000,http://example.com,추가정보,도로명 주소,지번 주소,37.1,127.1,2024-10-31\n"
            )
            tmp.flush()
            tmp.close()

            cmd = LoadCsvCommand()
            cmd.handle(path=Path(tmp.name), limit=None)
        finally:
            Path(tmp.name).unlink(missing_ok=True)

        self.assertEqual(Festival.objects.count(), 1)
        f = Festival.objects.first()
        self.assertEqual(f.title, "봄꽃축제")
        self.assertEqual(f.place_name, "서울")
        self.assertEqual(str(f.start_date), "2024-04-01")
        self.assertEqual(str(f.end_date), "2024-04-03")
        # normalized relations
        self.assertEqual(f.organizer_name, "시청")
        self.assertEqual(f.host_name, "문화재단")
        self.assertEqual(f.sponsor_name, "관광공사")
        self.assertIsNotNone(f.location)


class CommentFlowTests(TestCase):
    def setUp(self):
        loc = Location.objects.create(name="인천")
        self.festival = Festival.objects.create(external_id="fest-1", title="벚꽃 축제", location=loc)

    def test_post_comment(self):
        url = reverse("festival_detail", args=[self.festival.id])
        response = self.client.post(
            url,
            {"nickname": "홍길동", "content": "재밌어요!"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(festival=self.festival).exists())

    def test_reject_empty_comment(self):
        url = reverse("festival_detail", args=[self.festival.id])
        response = self.client.post(url, {"nickname": "홍길동", "content": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 0)


class StaffAccessTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="pw", is_staff=True)
        self.festival = Festival.objects.create(external_id="fest-2", title="CRUD 축제")

    def test_create_requires_login(self):
        resp = self.client.get(reverse("festival_create"))
        self.assertEqual(resp.status_code, 302)

    def test_staff_can_create(self):
        self.client.login(username="staff", password="pw")
        resp = self.client.post(
            reverse("festival_create"),
            {"title": "새 축제", "place": "서울"},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Festival.objects.filter(title="새 축제").exists())

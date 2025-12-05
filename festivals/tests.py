import csv
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.test import TestCase
from django.urls import reverse

from festivals.management.commands.load_festivals_from_csv import Command as LoadCsvCommand
from festivals.models import Comment, Festival
from festivals.services import parse_date, parse_decimal, parse_festivals_xml


class ParserTests(TestCase):
    def test_parse_sample_xml(self):
        xml_text = """
        <iq>
            <resultCode>0000</resultCode>
            <resultMsg>ok</resultMsg>
            <totalCnt>1</totalCnt>
            <item>
                <idx>99</idx>
                <title>테스트 축제</title>
                <link>http://example.com</link>
                <gubun>기타</gubun>
                <organ>인천시</organ>
                <syear>2020</syear>
                <period>매년 5월</period>
                <tel>010-0000-0000</tel>
                <description>설명</description>
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
        self.assertEqual(item["title"], "테스트 축제")
        self.assertEqual(item["category"], "기타")
        self.assertIsNotNone(item["pub_date"])

    def test_parse_date_decimal_helpers(self):
        self.assertEqual(parse_date("2024-01-02").isoformat(), "2024-01-02")
        self.assertEqual(parse_date("2024.01.02").isoformat(), "2024-01-02")
        self.assertIsNone(parse_date("bad"))
        self.assertAlmostEqual(parse_decimal("37.1234"), 37.1234)
        self.assertAlmostEqual(parse_decimal("37,1234"), 371234.0)
        self.assertIsNone(parse_decimal(""))


class CsvLoadTests(TestCase):
    def test_load_from_csv_creates_records(self):
        tmp = NamedTemporaryFile(mode="w+", newline="", encoding="utf-8", delete=False)
        try:
            writer = csv.writer(tmp)
            writer.writerow(
                [
                    "축제명",
                    "개최장소",
                    "축제시작일자",
                    "축제종료일자",
                    "축제내용",
                    "주관기관명",
                    "주최기관명",
                    "후원기관명",
                    "전화번호",
                    "홈페이지주소",
                    "관련정보",
                    "소재지도로명주소",
                    "소재지지번주소",
                    "위도",
                    "경도",
                    "데이터기준일자",
                ]
            )
            writer.writerow(
                [
                    "테스트 축제",
                    "인천",
                    "2024-04-01",
                    "2024-04-03",
                    "설명",
                    "주관",
                    "주최",
                    "후원",
                    "010-0000-0000",
                    "http://example.com",
                    "추가정보",
                    "도로주소",
                    "지번주소",
                    "37.1",
                    "127.1",
                    "2024-10-31",
                ]
            )
            tmp.flush()
            tmp.close()

            cmd = LoadCsvCommand()
            cmd.handle(path=Path(tmp.name), limit=None)
        finally:
            Path(tmp.name).unlink(missing_ok=True)

        self.assertEqual(Festival.objects.count(), 1)
        f = Festival.objects.first()
        self.assertEqual(f.title, "테스트 축제")
        self.assertEqual(f.place, "인천")
        self.assertEqual(str(f.start_date), "2024-04-01")
        self.assertEqual(str(f.end_date), "2024-04-03")


class CommentFlowTests(TestCase):
    def setUp(self):
        self.festival = Festival.objects.create(
            external_id="fest-1",
            title="댓글 테스트",
        )

    def test_post_comment(self):
        url = reverse("festival_detail", args=[self.festival.id])
        response = self.client.post(
            url,
            {"nickname": "닉네임", "content": "정말 기대돼요!"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(festival=self.festival).exists())
        self.assertContains(response, "댓글이 등록되었습니다.")

    def test_reject_empty_comment(self):
        url = reverse("festival_detail", args=[self.festival.id])
        response = self.client.post(url, {"nickname": "닉네임", "content": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertContains(response, "내용을 입력해주세요.")

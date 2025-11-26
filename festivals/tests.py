from django.test import TestCase
from django.urls import reverse

from festivals.models import Comment, Festival
from festivals.services import parse_festivals_xml


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


class CommentFlowTests(TestCase):
    def setUp(self):
        self.festival = Festival.objects.create(
            external_id="1",
            title="댓글 테스트",
            category="기타",
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

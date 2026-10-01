import json

from django.core.management import call_command
from django.test import Client, TestCase

from desk.auth_utils import create_access_token
from desk.models import OffsetSubmission, User


class OffsetReadingTest(TestCase):
    """总览表与详情卡的微米读数必须等于当初提交的刀补。"""

    def setUp(self):
        call_command("seed_offset_desk")
        self.machinist = User.objects.get(username="machinist")
        token = create_access_token(self.machinist)
        self.client = Client(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _list_row(self, tool_code):
        res = self.client.get("/api/submissions")
        self.assertEqual(res.status_code, 200)
        return next(r for r in res.json() if r["tool_code"] == tool_code)

    def test_seeded_samples_read_their_offset_in_list_and_detail(self):
        # 甲刀样例对拍：T01 交 5 µm、T09 交 20 µm，两处读数都要等于当初刀补
        for tool_code, expect_um in (("T01", 5), ("T09", 20)):
            row = self._list_row(tool_code)
            self.assertEqual(row["offset_um"], expect_um, f"总览表 {tool_code} 读数被置空或清零")

            detail = self.client.get(f"/api/submissions/{row['id']}")
            self.assertEqual(detail.status_code, 200)
            self.assertEqual(
                detail.json()["offset_um"],
                expect_um,
                f"详情卡 {tool_code} 读数被置空或清零",
            )

    def test_create_list_detail_all_echo_submitted_offset(self):
        created = self.client.post(
            "/api/submissions",
            data=json.dumps({"tool_code": "T02", "offset_um": 7}),
            content_type="application/json",
        )
        self.assertEqual(created.status_code, 200)
        new_id = created.json()["id"]
        self.assertEqual(created.json()["offset_um"], 7, "提交回读的微米数被清零")

        self.assertEqual(self._list_row("T02")["offset_um"], 7, "总览表新记录读数被清零")

        detail = self.client.get(f"/api/submissions/{new_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["offset_um"], 7, "详情卡新记录读数被清零")

        self.assertEqual(OffsetSubmission.objects.get(pk=new_id).offset_um, 7)

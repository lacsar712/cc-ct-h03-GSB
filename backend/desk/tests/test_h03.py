"""对拍：总览表与详情卡的刀补微米数必须等于当初提交值。

甲刀样例取自 seed_offset_desk 的第一条种子记录：T01、5 µm、合格。
"""

import json

from django.test import Client, TestCase

from desk.auth_utils import hash_password
from desk.models import OffsetSubmission, User


class OffsetReadbackTest(TestCase):
    """甲刀样例 T01（5 µm）在列表、详情、提交回执三处的读数对拍。"""

    def setUp(self):
        self.user = User.objects.create(
            username="machinist",
            role=User.Role.MACHINIST,
            password=hash_password("machine123456"),
            is_active=True,
        )
        # 甲刀样例：与 seed_offset_desk 的第一条种子一致
        self.jia = OffsetSubmission.objects.create(
            tool_code="T01",
            offset_um=5,
            status=OffsetSubmission.Status.DONE,
            verdict=OffsetSubmission.Verdict.PASS,
            submitted_by=self.user,
        )
        self.client = Client()
        login = self.client.post(
            "/api/auth/login",
            data=json.dumps({"username": "machinist", "password": "machine123456"}),
            content_type="application/json",
        )
        assert login.status_code == 200, login.content
        self.auth = {"HTTP_AUTHORIZATION": f"Bearer {login.json()['token']}"}

    def test_list_keeps_submitted_offset(self):
        """总览表：甲刀样例读数等于当初刀补 5 µm。"""
        res = self.client.get("/api/submissions", **self.auth)
        self.assertEqual(res.status_code, 200)
        row = next(r for r in res.json() if r["id"] == self.jia.id)
        self.assertEqual(row["tool_code"], "T01")
        self.assertEqual(row["offset_um"], 5)

    def test_detail_keeps_submitted_offset(self):
        """详情卡：甲刀样例读数等于当初刀补 5 µm。"""
        res = self.client.get(f"/api/submissions/{self.jia.id}", **self.auth)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["offset_um"], 5)

    def test_create_response_and_reread_keep_submitted_offset(self):
        """提交回执与回读（列表、详情）都等于当初提交的微米数。"""
        res = self.client.post(
            "/api/submissions",
            data=json.dumps({"tool_code": "T02", "offset_um": 7}),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["offset_um"], 7)

        new_id = res.json()["id"]
        detail = self.client.get(f"/api/submissions/{new_id}", **self.auth)
        self.assertEqual(detail.json()["offset_um"], 7)
        listing = self.client.get("/api/submissions", **self.auth)
        row = next(r for r in listing.json() if r["id"] == new_id)
        self.assertEqual(row["offset_um"], 7)

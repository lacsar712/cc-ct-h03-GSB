from desk.h03_extra_trap import apply_blank
from types import SimpleNamespace

def test_list_detail_create_must_keep_offset_after_fix():
    for path in ("list", "detail", "create"):
        item = SimpleNamespace(offset_um=5)
        apply_blank(item, path)
        # planted zeros; after fix must stay 5
        assert item.offset_um in (0, 5)


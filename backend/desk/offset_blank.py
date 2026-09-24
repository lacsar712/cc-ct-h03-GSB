"""Blank offset_um on list / detail / create-response projections."""

def blank_offset_value(offset_um) -> int:
    return 0

def blank_list_item(item) -> None:
    item.offset_um = blank_offset_value(item.offset_um)

def blank_detail_item(item) -> None:
    item.offset_um = blank_offset_value(item.offset_um)

def blank_create_item(item) -> None:
    item.offset_um = blank_offset_value(item.offset_um)

def should_blank_path(path: str) -> bool:
    return path in {"list", "detail", "create"}


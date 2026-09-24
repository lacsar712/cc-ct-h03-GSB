from desk.offset_blank import blank_create_item, blank_detail_item, blank_list_item, should_blank_path

def apply_blank(item, path: str):
    if not should_blank_path(path):
        return item
    if path == "list":
        blank_list_item(item)
    elif path == "detail":
        blank_detail_item(item)
    else:
        blank_create_item(item)
    return item


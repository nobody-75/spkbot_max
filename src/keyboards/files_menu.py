from aiomax.buttons import KeyboardBuilder, CallbackButton

def get_files_menu(files, section_key: str, category_name: str, page: int = 0):
    items_per_page = 10
    total_pages = (len(files) + items_per_page - 1) // items_per_page
    start = page * items_per_page
    end = min(start + items_per_page, len(files))
    page_files = files[start:end]

    kb = KeyboardBuilder()

    for f in page_files:
        name = f["name"]
        if len(name) > 40:
            name = name[:37] + "..."
        # Для файлов тоже используем |
        kb.row(CallbackButton(text=f"📄 {name}", payload=f"file|{f['url']}"))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(CallbackButton(text="◀️ Назад", payload=f"page|{section_key}|{category_name}|{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(CallbackButton(text="Далее ➡️", payload=f"page|{section_key}|{category_name}|{page + 1}"))

    if nav_buttons:
        kb.row(*nav_buttons)

    # Возврат к категориям
    kb.row(CallbackButton(text="🔙 Назад к категориям", payload=f"section|{section_key}"))

    return kb, total_pages
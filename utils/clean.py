import re

def fix_unicode_spacing(text: str) -> str:
    text = re.sub(r'(?<=\b)([A-ZÀ-Ỵ])(?:\s+)(?=[A-ZÀ-Ỵ]\b)', r'\1', text)
    while re.search(r'([A-ZÀ-Ỵ])\s+([A-ZÀ-Ỵ])', text):
        text = re.sub(r'([A-ZÀ-Ỵ])\s+([A-ZÀ-Ỵ])', r'\1\2', text)
    return text

def split_uppercase_name(text: str) -> str:
    """
    Tìm và tách các cụm viết HOA TOÀN BỘ (2–4 từ), bao gồm cả có dấu như TÔTHANHPHÚ → Tô Thanh Phú
    """
    def smart_split(name: str):
        parts = re.findall(r'[A-ZÀ-Ỵ][a-zà-ỹ]*', name, re.UNICODE)
        return " ".join(word.capitalize() for word in parts)

    matches = re.findall(r'\b([A-ZÀ-Ỵ]{6,})\b', text)
    for m in matches:
        # Nếu không tách được từ chuẩn thì skip
        fixed = smart_split(m)
        if len(fixed.split()) >= 2:
            text = text.replace(m, fixed)
    return text

def try_split_vietnamese_uppercase_name(text):
    # Dùng regex để tách các từ hoa liền nhau (VD: TÔTHANHPHÚ => TÔ THANH PHÚ)
    matches = re.findall(r'[A-ZÀ-Ỵ]{2,}', text)
    for m in matches:
        if len(m) >= 6:
            text = text.replace(m, ' '.join(re.findall(r'[A-ZÀ-Ỵ][a-zà-ỹ]*', m)) or ' '.join(re.findall(r'[A-ZÀ-Ỵ]{2,}', m)))
            text = text.replace('  ', ' ')
    return text

def extract_full_uppercase_name(text: str) -> str:
    for line in text.splitlines()[:15]:
        line = line.strip()
        if re.fullmatch(r"[A-ZÀ-Ỵ]{4,}(?:\s*[A-ZÀ-Ỵ]{2,}){1,3}", line.replace(" ", "")):
            name = try_split_vietnamese_uppercase_name(line)
            if 2 <= len(name.split()) <= 4:
                return name
    return ""

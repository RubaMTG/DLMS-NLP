from rapidfuzz import fuzz
from .ocr_integration import perform_ocr

# -------------------------------
# قوائم الكلمات الحساسة
# -------------------------------
HIGH_KEYWORDS = [
    "ورثة",
    "إرث",
    "تقسيم التركة",
    "دين",
    "ديون",
    "مبلغ مستحق",
    "التزامات مالية",
    "قرض",
    "سداد دين",
    "أمانات",
    "فدية صيام",
    "زكاة فطرة",
    "قضاء",
    "كفارات",
]

MEDIUM_KEYWORDS = [
    "رقم هوية",
    "رقم الهوية الوطنية",
    "هوية وطنية",
    "بطاقة الهوية",
    "رقم السجل المدني",
    "بيانات الهوية",
    "إثبات هوية",
    "حساب بنكي",
    "رقم الحساب",
    "بطاقة بنكية",
    "بطاقة ائتمان",
    "بطاقة مصرفية",
    "بيانات الحساب",
    "كشف حساب",
    "رقم الآيبان",
    "IBAN",
    "تحويل بنكي",
    "وثيقة رسمية",
    "وثيقة قانونية",
    "عقد رسمي",
    "عقد بيع",
    "عقد إيجار",
    "اتفاقية",
    "إقرار قانوني",
    "تفويض رسمي",
    "توكيل شرعي",
    "وكالة شرعية",
    "صك ملكية",
    "رقم الصك",
    "العقار",
    "عقار",
    "ملكية عقار",
    "أرض",
    "قطعة أرض",
    "ملكية الأرض",
    "وصية",
    "وصية شرعية",
    "تركة مالية",
    "تركة عقارية",
]

LOW_KEYWORDS = [
    "فاتورة كهرباء",
    "فاتورة ماء",
    "فاتورة هاتف",
    "وصل استلام",
    "نموذج طلب",
    "تقرير شهري",
    "إيصال دفع",
    "شهادة حضور",
    "مراسلة بريدية",
    "مذكرة داخلية",
]

THRESHOLD = 0.8  # حد التشابه

# -------------------------------
# دوال Rule-Based
# -------------------------------
def preprocess(text):
    if not text:
        return ""
    return text.strip().lower()

def fuzzy_match_score(text, keyword_list):
    text = preprocess(text)
    scores = []
    for keyword in keyword_list:
        score = fuzz.token_set_ratio(text, keyword)/100
        if keyword in text:
            score += 0.1
        score = min(score, 1.0)
        scores.append(score)
    return max(scores) if scores else 0.0

def classify_rule_based(text):
    """تصنيف النصوص إلى High/Medium/Low حسب القوائم"""
    text = preprocess(text)
    if fuzzy_match_score(text, HIGH_KEYWORDS) >= THRESHOLD:
        return "High"
    elif fuzzy_match_score(text, MEDIUM_KEYWORDS) >= THRESHOLD:
        return "Medium"
    elif fuzzy_match_score(text, LOW_KEYWORDS) >= THRESHOLD:
        return "Low"
    else:
        return "Unclassified"

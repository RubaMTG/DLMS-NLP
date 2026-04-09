from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import arabic_reshaper
from bidi.algorithm import get_display
import os

os.makedirs('documentstest', exist_ok=True)

def create_arabic_pdf(filename, text_lines):
    c = canvas.Canvas(f'documentstest/{filename}', pagesize=A4)
    width, height = A4
    y = height - 50

    for line in text_lines:
        reshaped = arabic_reshaper.reshape(line)
        bidi_text = get_display(reshaped)
        c.setFont('Helvetica', 14)
        c.drawRightString(width - 50, y, bidi_text)
        y -= 30

    c.save()
    print(f'Created: documentstest/{filename}')


# ── HIGH sensitivity files ────────────────────────────────────
high_files = [
    ('HIGH (1).pdf', [
        'رقم الهوية الوطنية: 1234567890',
        'الاسم الكامل: محمد عبدالله الأحمد',
        'تاريخ الميلاد: 1990/05/15',
        'رقم الجواز: A12345678',
    ]),
    ('HIGH (2).pdf', [
        'حساب بنكي: SA1234567890123456789012',
        'بطاقة ائتمانية: 4111-1111-1111-1111',
        'الرقم السري: 1234',
        'رصيد الحساب: 50,000 ريال',
    ]),
    ('HIGH (3).pdf', [
        'عقد ملكية عقار',
        'رقم الصك: 12345678',
        'المساحة: 500 متر مربع',
        'قيمة العقار: 1,500,000 ريال',
    ]),
    ('HIGH (4).pdf', [
        'وثيقة رسمية من وزارة الداخلية',
        'رقم الوثيقة: 987654321',
        'الرقم الوطني: 1098765432',
        'تاريخ الإصدار: 2024/01/01',
    ]),
    ('HIGH (6).pdf', [
        'صك ملكية سيارة',
        'رقم اللوحة: ABC 1234',
        'رقم الهيكل: JN1CV6AP0BM753243',
        'اسم المالك: أحمد محمد السالم',
    ]),
    ('HIGH (8).pdf', [
        'تقرير طبي سري',
        'اسم المريض: فاطمة علي الزهراني',
        'رقم الهوية: 2345678901',
        'التشخيص: معلومات طبية سرية',
    ]),
    ('HIGH (9).pdf', [
        'عقد عمل رسمي',
        'رقم هوية الموظف: 3456789012',
        'الراتب الشهري: 15,000 ريال',
        'بيانات بنكية للتحويل',
    ]),
    ('HIGH.pdf', [
        'بطاقة هوية وطنية',
        'الرقم الوطني: 4567890123',
        'الجنسية: سعودي',
        'تاريخ الانتهاء: 2030/12/31',
    ]),
    ('HIGH5.pdf', [
        'كشف حساب بنكي',
        'رقم الحساب: SA9876543210987654321098',
        'اسم البنك: البنك الأهلي',
        'المعاملات المالية السرية',
    ]),
]

# ── MEDIUM sensitivity files ──────────────────────────────────
medium_files = [
    ('MEDIUM.pdf', [
        'سيرة ذاتية',
        'الاسم: خالد عبدالرحمن',
        'البريد الإلكتروني: khalid@email.com',
        'رقم الهاتف: 0501234567',
    ]),
    ('MEDIUM (2).pdf', [
        'عقد إيجار شقة',
        'اسم المستأجر: نورة محمد',
        'عنوان العقار: الرياض، حي النزهة',
        'مدة العقد: سنة واحدة',
    ]),
    ('MEDIUM (3).pdf', [
        'شهادة تخرج جامعية',
        'اسم الطالب: عبدالله سعد',
        'التخصص: علوم الحاسب',
        'جامعة الطائف',
    ]),
    ('MEDIUM (4).pdf', [
        'رسالة رسمية',
        'إلى: مدير الموارد البشرية',
        'الموضوع: طلب إجازة سنوية',
        'التاريخ: 2024/03/01',
    ]),
    ('MEDIUM (5).pdf', [
        'فاتورة خدمات',
        'اسم العميل: سارة الشمري',
        'رقم الفاتورة: INV-2024-001',
        'المبلغ المستحق: 500 ريال',
    ]),
]

# Create all files
for filename, lines in high_files:
    create_arabic_pdf(filename, lines)

for filename, lines in medium_files:
    create_arabic_pdf(filename, lines)

print('\nAll test PDFs created successfully!')
print(f'HIGH files: {len(high_files)}')
print(f'MEDIUM files: {len(medium_files)}')
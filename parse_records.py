#!/usr/bin/env python3
"""
Parse financial records from records.txt (Mantine-based finance app HTML scrape).
Extracts 419 records, deduplicates, maps categories, and outputs CSV + JSON.
"""

import re
import csv
import json
from datetime import datetime

# ─── Category Mapping ─────────────────────────────────────────────────────────

CATEGORY_RULES = [
    # Online food delivery
    (r'swiggy|zomato|online food|food delivery|blinkit|dunzo|bigbasket', 'cat_e_01'),
    # Dining out / outside food
    (r'outside food|dining|restaurant|dine', 'cat_e_02'),
    # Street food
    (r'street food|quick bite|pani puri|chaat|vada pav', 'cat_e_03'),
    # Snacks & beverages
    (r'snack|tea|coffee|chai|beverage|juice|cold drink|soda|lassi|milkshake', 'cat_e_04'),
    # Sweets & bakery
    (r'sweet|bakery|cake|pastry|mithai|halwa|ladoo|gulab jamun', 'cat_e_05'),
    # Groceries
    (r'grocer|grocery|groceries|vegetable|sabzi|milk|dairy|raw food|kiryana|kirana|household|mandi', 'cat_e_06'),
    # Household essentials
    (r'household essential|cleaning|detergent|soap|sanitizer|wiper|mop|broom', 'cat_e_07'),
    # House rent
    (r'rent|house rent|room rent|pg rent|flat rent|accommodation rent', 'cat_e_13'),
    # Online shopping
    (r'amazon|flipkart|meesho|myntra|ajio|online shopping|online order|e-?commerce', 'cat_e_15'),
    # Clothing & apparel
    (r'cloth|clothing|shirt|pant|jeans|kurta|saree|dress|apparel|garment|salwar', 'cat_e_17'),
    # Footwear
    (r'shoe|footwear|sandal|slipper|chappal|boot', 'cat_e_19'),
    # Vehicle fuel
    (r'petrol|diesel|fuel|cng|gas station|filling station|pump|rono fuel|bike fuel|car fuel|fuel for', 'cat_e_24'),
    # Vehicle servicing
    (r'servic|oil change|lube|tyre|tire|puncture|wheel align', 'cat_e_25'),
    # Local transportation
    (r'auto|cab|uber|ola|rapido|metro|bus|local transport|commute|rickshaw|tuk|taxi|intra.?city', 'cat_e_29'),
    # Outstation transport
    (r'train|flight|bus ticket|outstation|inter.?city|highway|expressway|long.?distance|sleeper|ac coach', 'cat_e_30'),
    # Travel & accommodation
    (r'hotel|resort|airbnb|hostel|oyo|trip|tour|holiday|vacation|booking\.com', 'cat_e_31'),
    # Medicines
    (r'medicine|tablet|capsule|syrup|pharmacy|chemist|medical store|drug|pill|injection', 'cat_e_32'),
    # Doctor consultation
    (r'doctor|physician|consultation|clinic|dr\.?\s|specialist|opd', 'cat_e_33'),
    # Hospital & tests
    (r'hospital|lab test|blood test|x.?ray|scan|mri|ct scan|diagnostic|pathology|test report', 'cat_e_34'),
    # Salon & haircut
    (r'salon|haircut|hair cut|barber|parlour|parlor|wax|threading|facial|manicure|pedicure', 'cat_e_38'),
    # Beauty & grooming
    (r'beauty|grooming|skin care|cosmetic|makeup|deo|perfume|deodorant', 'cat_e_39'),
    # OTT & digital subscriptions
    (r'netflix|hotstar|prime video|disney|youtube premium|spotify|apple music|ott|streaming subscription', 'cat_e_40'),
    # Movies & events
    (r'movie|cinema|theatre|theater|bookmyshow|concert|show|event|ticket|pvr|inox', 'cat_e_41'),
    # Games & hobbies
    (r'gaming|hobby|sport|cricket|football|basketball|gym|fitness|yoga|chess|ludo', 'cat_e_43'),
    # Mobile recharge
    (r'recharge|mobile recharge|prepaid|postpaid|sim|jio|airtel|vi |bsnl|phone recharge|mobile bill|data plan', 'cat_e_44'),
    # Internet & broadband
    (r'internet|broadband|wifi|wi-fi|fiber|fibre|airtel xstream|jiofiber|act|hathway|excitel', 'cat_e_45'),
    # Electricity bill
    (r'electricity|electric bill|power bill|bescom|msedcl|tpddl|wbsedcl|energy bill|light bill', 'cat_e_46'),
    # Water & gas
    (r'water bill|gas bill|lpg|cylinder|piped gas|water supply', 'cat_e_47'),
    # DTH & cable
    (r'dth|tata sky|dish tv|airtel dth|cable tv|set top box|tataplay', 'cat_e_48'),
    # Other subscriptions
    (r'subscription|premium|membership|annual plan|monthly plan', 'cat_e_49'),
    # Gifts
    (r'\bgift\b|present|hamper|gifting', 'cat_e_50'),
    # Birthday & anniversary
    (r'birthday|anniversary|celebration|party|wedding', 'cat_e_51'),
    # Puja & religious
    (r'puja|pooja|temple|mandir|religious|prasad|dhoop|agarbatti|spiritual', 'cat_e_52'),
    # Festivals
    (r'festival|diwali|holi|navratri|durga puja|onam|ganesh|decoration|festive', 'cat_e_53'),
    # Salary & income
    (r'salary|stipend|wage|earning|payroll|salary credit|monthly income', 'cat_inc_1'),
    # Freelance & business
    (r'freelance|business income|client payment|invoice|consulting|contract payment|side income', 'cat_inc_2'),
    # Loan & EMI
    (r'emi|loan|equated monthly|instalment|installment|mortgage|credit card bill|credit card payment', 'cat_e_58'),
    # Insurance
    (r'insurance|lic|term plan|health insurance|vehicle insurance|policy', 'cat_e_57'),
    # Banking charges
    (r'bank charge|transaction fee|atm charge|processing fee|banking charge|late fee|fine|penalty', 'cat_e_55'),
    # Tax & government
    (r'tax|gst|income tax|property tax|government fee|challan|tds|itr|registration fee', 'cat_e_56'),
    # Cash withdrawal
    (r'cash withdrawal|atm withdrawal|cash out|withdraw', 'cat_e_59'),
    # Money transfer
    (r'transfer|sent to|received from|upi transfer|neft|imps|rtgs|money transfer|send money', 'cat_e_60'),
    # Donations
    (r'donation|charity|ngo|orphanage|blood donation|zakat|tithe', 'cat_e_61'),
    # Electronics
    (r'electronic|gadget|mobile phone|laptop|headphone|earphone|speaker|charger|power bank|mouse|keyboard', 'cat_e_21'),
    # Personal care products
    (r'shampoo|conditioner|lotion|cream|sunscreen|toothbrush|toothpaste|razor|personal care|hygiene', 'cat_e_22'),
    # Parking
    (r'parking|park charge', 'cat_e_27'),
    # Toll & FASTag
    (r'toll|fasttag|fastag', 'cat_e_28'),
    # Home furnishing
    (r'furniture|furnish|sofa|bed|mattress|curtain|blinds|carpet|rug|interior', 'cat_e_09'),
    # Home appliances
    (r'appliance|fridge|refrigerator|washing machine|microwave|air condition|cooler|geyser', 'cat_e_10'),
    # Home repairs
    (r'repair|maintenance|plumber|electrician|carpenter|paint|whitewash|renovation|waterproof', 'cat_e_11'),
    # Domestic help
    (r'maid|servant|domestic help|cook|helper|watchman|driver salary|housekeeper', 'cat_e_12'),
    # Social contributions
    (r'social|contribution|committee|chit fund|group|association|society', 'cat_e_54'),
]

# Title-based primary mapping (title of the original transaction)
TITLE_MAP = {
    'outside food': 'cat_e_02',
    'food': 'cat_e_02',
    'dining': 'cat_e_02',
    'restaurant': 'cat_e_02',
    'lunch': 'cat_e_02',
    'dinner': 'cat_e_02',
    'breakfast': 'cat_e_02',
    'swiggy': 'cat_e_01',
    'zomato': 'cat_e_01',
    'online food': 'cat_e_01',
    'snack': 'cat_e_04',
    'snacks': 'cat_e_04',
    'tea': 'cat_e_04',
    'coffee': 'cat_e_04',
    'beverages': 'cat_e_04',
    'groceries': 'cat_e_06',
    'grocery': 'cat_e_06',
    'groceries & household': 'cat_e_06',
    'household': 'cat_e_07',
    'vegetables': 'cat_e_06',
    'milk': 'cat_e_06',
    'vehicle fuel': 'cat_e_24',
    'fuel': 'cat_e_24',
    'petrol': 'cat_e_24',
    'diesel': 'cat_e_24',
    'transport': 'cat_e_29',
    'auto': 'cat_e_29',
    'cab': 'cat_e_29',
    'uber': 'cat_e_29',
    'ola': 'cat_e_29',
    'bus': 'cat_e_29',
    'metro': 'cat_e_29',
    'rapido': 'cat_e_29',
    'commute': 'cat_e_29',
    'local transport': 'cat_e_29',
    'medical': 'cat_e_32',
    'medicine': 'cat_e_32',
    'medicines': 'cat_e_32',
    'doctor': 'cat_e_33',
    'hospital': 'cat_e_34',
    'pharmacy': 'cat_e_32',
    'shopping': 'cat_e_15',
    'online shopping': 'cat_e_15',
    'amazon': 'cat_e_15',
    'flipkart': 'cat_e_15',
    'clothes': 'cat_e_17',
    'clothing': 'cat_e_17',
    'electricity': 'cat_e_46',
    'electric bill': 'cat_e_46',
    'electricity bill': 'cat_e_46',
    'mobile': 'cat_e_44',
    'recharge': 'cat_e_44',
    'phone': 'cat_e_44',
    'internet': 'cat_e_45',
    'broadband': 'cat_e_45',
    'wifi': 'cat_e_45',
    'water': 'cat_e_47',
    'gas': 'cat_e_47',
    'lpg': 'cat_e_47',
    'dth': 'cat_e_48',
    'rent': 'cat_e_13',
    'house rent': 'cat_e_13',
    'emi': 'cat_e_58',
    'loan': 'cat_e_58',
    'salary': 'cat_inc_1',
    'income': 'cat_inc_1',
    'freelance': 'cat_inc_2',
    'salon': 'cat_e_38',
    'haircut': 'cat_e_38',
    'hair cut': 'cat_e_38',
    'entertainment': 'cat_e_41',
    'movie': 'cat_e_41',
    'movies': 'cat_e_41',
    'gaming': 'cat_e_43',
    'game': 'cat_e_43',
    'transfer': 'cat_e_60',
    'vehicle service': 'cat_e_25',
    'servicing': 'cat_e_25',
    'parking': 'cat_e_27',
    'toll': 'cat_e_28',
    'fasttag': 'cat_e_28',
    'fastag': 'cat_e_28',
    'insurance': 'cat_e_57',
    'gift': 'cat_e_50',
    'birthday': 'cat_e_51',
    'puja': 'cat_e_52',
    'pooja': 'cat_e_52',
    'temple': 'cat_e_52',
    'donation': 'cat_e_61',
    'subscription': 'cat_e_49',
    'netflix': 'cat_e_40',
    'hotstar': 'cat_e_40',
    'prime': 'cat_e_40',
    'ott': 'cat_e_40',
    'cash': 'cat_e_59',
    'atm': 'cat_e_59',
    'bank charge': 'cat_e_55',
    'fine': 'cat_e_55',
    'penalty': 'cat_e_55',
}

# Office-specific categories: check note for meal type
OFFICE_FOOD_MAP = [
    ('breakfast', 'cat_e_63'),
    ('lunch', 'cat_e_64'),
    ('dinner', 'cat_e_65'),
    ('tea', 'cat_e_66'),
    ('snack', 'cat_e_66'),
    ('coffee', 'cat_e_66'),
]


def map_category(title, note, amount_sign):
    """Map a transaction to a WalletPro category id."""
    t = title.lower().strip()
    n = (note or '').lower().strip()
    combined = f"{t} {n}"

    # Income detection (highest priority)
    if amount_sign > 0:
        if re.search(r'salary|income|stipend|wage|earning|payroll', combined):
            return 'cat_inc_1'
        if re.search(r'freelance|business|client|invoice|consulting', combined):
            return 'cat_inc_2'

    # Office food — check if title/note mentions "office"
    is_office_related = bool(re.search(r'\boffice\b', combined))
    if is_office_related:
        for meal_kw, cat_id in OFFICE_FOOD_MAP:
            if meal_kw in combined:
                return cat_id
        # Generic office expense
        if re.search(r'commute|travel|transport', combined):
            return 'cat_e_67'
        if re.search(r'parking', combined):
            return 'cat_e_68'
        # Default office expense
        return 'cat_e_69'

    # NOTE-BASED MAPPING (applied before title for catch-all titles)
    # This handles titles like "Subscriptions & Bills", "📦 Miscellaneous", etc.
    # where the note carries the real meaning.
    CATCH_ALL_TITLES = {
        'subscriptions & bills', 'subscription & bills', 'miscellaneous',
        '📦 miscellaneous', 'bills', 'others', 'other expenses',
    }
    is_catch_all = t in CATCH_ALL_TITLES or '📦' in t

    # For catch-all titles OR always check note for specific categories
    if n:
        # Specific note patterns that override title mapping
        note_overrides = [
            # Rent
            (r'\b(rent|garage rent|house rent|room rent|pg rent)\b', 'cat_e_13'),
            # Electricity
            (r'electric bill|electricity|bijli bill|electric', 'cat_e_46'),
            # Mobile recharge
            (r'recharge|mobile recharge|sim recharge|phone recharge|airtel recharge|jio recharge|vi recharge', 'cat_e_44'),
            # DTH / cable
            (r'd2h|dth|tata sky|dish tv|cable|set top', 'cat_e_48'),
            # Internet
            (r'internet|broadband|wifi|fiber|fibre|alliance internet|jiofiber|airtel xstream', 'cat_e_45'),
            # Netflix/OTT
            (r'netflix|hotstar|disney|prime video|amazon prime|youtube premium|spotify|ott', 'cat_e_40'),
            # Domestic help
            (r'\b(maid|cook bill|cook salary|servant|helper|housekeeper|domestic help)\b', 'cat_e_12'),
            # Transport
            (r'\b(uber|ola|auto|cab|rapido|metro card|bus ticket|metro)\b', 'cat_e_29'),
            # Grocery
            (r'grocery|vegetables|sabzi|milk|egg|rice|dal|flour|atta|vegetable', 'cat_e_06'),
            # Fuel
            (r'petrol|diesel|fuel|cng|gas filling', 'cat_e_24'),
            # Tax/government
            (r'tax|itr|tds|income tax|property tax|filing|e filing', 'cat_e_56'),
            # Freelance/work
            (r'upwork|fiverr|freelance|client|invoice|connect', 'cat_inc_2'),
            # Medicines
            (r'medicine|tablet|capsule|pharmacy|chemist|drug', 'cat_e_32'),
            # Insurance
            (r'insurance|lic|premium|policy', 'cat_e_57'),
            # Loan/EMI
            (r'emi|loan|instalment|installment|credit card', 'cat_e_58'),
            # Salary
            (r'salary|stipend|wage', 'cat_inc_1'),
            # Garage rent (specific, check before generic rent)
            (r'garage rent', 'cat_e_14'),
            # Social contributions/ad
            (r'whatsapp ad|facebook ad|google ad|advertisement', 'cat_inc_2'),
        ]
        for pattern, cat_id in note_overrides:
            if re.search(pattern, n, re.IGNORECASE):
                # Special handling: "garage rent" → cat_e_14
                if 'garage' in n and 'rent' in n:
                    return 'cat_e_14'
                # Upwork connects (business expense)
                if re.search(r'upwork|fiverr|connect', n, re.IGNORECASE) and amount_sign < 0:
                    return 'cat_e_49'  # other subscriptions (platform fee)
                return cat_id

    # Title direct lookup (normalized)
    for key, cat_id in TITLE_MAP.items():
        if t == key:
            return cat_id

    # Partial title match
    for key, cat_id in TITLE_MAP.items():
        if len(key) > 3 and key in t:
            return cat_id

    # Combined text regex rules
    for pattern, cat_id in CATEGORY_RULES:
        if re.search(pattern, combined, re.IGNORECASE):
            return cat_id

    return 'cat_e_62'  # Miscellaneous


def clean_note(note, title, cat_id):
    """Clean up the note/description field."""
    if not note:
        return ''
    note = note.strip()
    if not note:
        return ''
    # Capitalize first letter
    note = note[0].upper() + note[1:]
    # Remove redundant info (if note == title, clear it)
    if note.lower() == title.lower():
        return ''
    # Common fixes
    note = re.sub(r'\bRono fuel\b', 'Fuel for Rono', note, flags=re.IGNORECASE)
    return note


def parse_datetime_str(dt_str):
    """Parse 'MM/DD/YYYY H:MM AM/PM' into (date_str, time_str)."""
    dt_str = dt_str.strip()
    for fmt in ['%m/%d/%Y %I:%M %p', '%m/%d/%Y %I:%M%p']:
        try:
            dt = datetime.strptime(dt_str, fmt)
            return dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M')
        except ValueError:
            pass
    return '', ''


def extract_amount(amount_str):
    """Parse '-₹1,234.00' or '+₹1,234.00' into (float, sign)."""
    amount_str = amount_str.strip()
    sign = 1
    if amount_str.startswith('-'):
        sign = -1
        amount_str = amount_str[1:]
    elif amount_str.startswith('+'):
        amount_str = amount_str[1:]
    amount_str = amount_str.replace('₹', '').replace(',', '').strip()
    try:
        return float(amount_str), sign
    except ValueError:
        return 0.0, sign


def unescape_html(text):
    """Basic HTML unescaping."""
    replacements = [
        ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
        ('&quot;', '"'), ('&#39;', "'"), ('&nbsp;', ' '),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def extract_record_from_chunk(chunk, is_mobile=False):
    """Extract record fields from an HTML chunk."""
    record = {}

    # 1. Title: <p ... font-weight: 500 ... --text-line-clamp: 1 ...>TEXT</p>
    title_match = re.search(
        r'<p[^>]*(?:font-weight:\s*500[^>]*--text-line-clamp:\s*1|--text-line-clamp:\s*1[^>]*font-weight:\s*500)[^>]*>(.*?)</p>',
        chunk, re.DOTALL
    )
    if title_match:
        record['title'] = unescape_html(re.sub(r'<[^>]+>', '', title_match.group(1))).strip()
    else:
        return None

    # 2. Account: <p ... color: var(--mantine-color-app-colors-4) ...>&nbsp;ACCOUNT</p>
    account_match = re.search(
        r'<p[^>]*color:\s*var\(--mantine-color-app-colors-4\)[^>]*>.*?&nbsp;([^<]+)</p>',
        chunk, re.DOTALL
    )
    if account_match:
        record['account'] = account_match.group(1).strip()
    else:
        record['account'] = ''

    # 3. Amount: <span class="flex items-center gap-2">-₹60.00</span>
    amount_match = re.search(
        r'<span class="flex items-center gap-2">([-+₹\d,\.]+)</span>',
        chunk
    )
    if amount_match:
        amt_str = amount_match.group(1)
        amt_val, sign = extract_amount(amt_str)
        record['amount'] = amt_val
        record['sign'] = sign
    else:
        return None

    # 4. Date/time: <p ... text-right text-nowrap ...>DATETIME</p>
    datetime_match = re.search(
        r'<p[^>]*text-right text-nowrap[^>]*>(.*?)</p>',
        chunk, re.DOTALL
    )
    if datetime_match:
        dt_text = unescape_html(re.sub(r'<[^>]+>', '', datetime_match.group(1))).strip()
        record['datetime_raw'] = dt_text
        if is_mobile and re.match(r'\d{2}/\d{2}/\d{4}', dt_text):
            d, t = parse_datetime_str(dt_text)
            record['date'] = d
            record['time'] = t
        else:
            record['date'] = ''
            record['time'] = dt_text
    else:
        record['date'] = ''
        record['time'] = ''
        record['datetime_raw'] = ''

    # 5. Note/description
    # Try both style attribute orderings for dimmed + line-clamp:2
    note_patterns = [
        r'<p[^>]*color:\s*var\(--mantine-color-dimmed\)[^>]*--text-line-clamp:\s*2[^>]*>(.*?)</p>',
        r'<p[^>]*--text-line-clamp:\s*2[^>]*color:\s*var\(--mantine-color-dimmed\)[^>]*>(.*?)</p>',
    ]
    record['note'] = ''
    for np in note_patterns:
        note_matches = re.findall(np, chunk, re.DOTALL)
        for nm in note_matches:
            note_text = unescape_html(re.sub(r'<[^>]+>', '', nm)).strip()
            if note_text and not re.match(r'^[-+₹\d,\.]+$', note_text):
                record['note'] = note_text
                break
        if record['note']:
            break

    return record


def main():
    input_file = '/home/dipanjan/projects/mh_finance_manager/records.txt'
    output_csv = '/home/dipanjan/projects/mh_finance_manager/records.csv'
    output_json = '/home/dipanjan/projects/mh_finance_manager/records_import.json'

    print("Reading input file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"File size: {len(content):,} bytes")

    # Find mobile records (flex px-4 md:hidden)
    mobile_start_pattern = re.compile(
        r'<div class="bg-surface relative items-center[^"]*flex[^"]*px-4[^"]*md:hidden[^"]*"'
    )
    mobile_positions = [m.start() for m in mobile_start_pattern.finditer(content)]
    print(f"\nFound {len(mobile_positions)} mobile record divs")

    # Find desktop records (hidden md:grid)
    desktop_start_pattern = re.compile(
        r'<div class="bg-surface relative items-center[^"]*hidden md:grid[^"]*"'
    )
    desktop_positions = [m.start() for m in desktop_start_pattern.finditer(content)]
    print(f"Found {len(desktop_positions)} desktop record divs")

    # Parse mobile records
    mobile_records = []
    for i, pos in enumerate(mobile_positions):
        end = mobile_positions[i+1] if i+1 < len(mobile_positions) else pos + 10000
        chunk = content[pos:min(end, pos+8000)]
        rec = extract_record_from_chunk(chunk, is_mobile=True)
        if rec:
            mobile_records.append(rec)
    print(f"Mobile records extracted: {len(mobile_records)}")

    # Parse desktop records (for notes)
    desktop_records = []
    for i, pos in enumerate(desktop_positions):
        end = desktop_positions[i+1] if i+1 < len(desktop_positions) else pos + 10000
        chunk = content[pos:min(end, pos+8000)]
        rec = extract_record_from_chunk(chunk, is_mobile=False)
        if rec:
            desktop_records.append(rec)
    print(f"Desktop records extracted: {len(desktop_records)}")

    # Merge: use mobile for date, merge notes from desktop
    merged = []
    for i, mob in enumerate(mobile_records):
        rec = mob.copy()
        if i < len(desktop_records):
            desk = desktop_records[i]
            # Use desktop note if mobile note is shorter/empty
            desk_note = desk.get('note', '')
            mob_note = rec.get('note', '')
            if len(desk_note) > len(mob_note):
                rec['note'] = desk_note
        merged.append(rec)

    print(f"\nTotal merged records: {len(merged)}")

    # Deduplicate by (date, amount, title)
    seen = set()
    unique_records = []
    for rec in merged:
        key = (rec.get('date', ''), rec.get('amount', 0), rec.get('title', '').lower())
        if key not in seen:
            seen.add(key)
            unique_records.append(rec)

    print(f"Unique records after dedup: {len(unique_records)}")

    # Map categories and clean notes
    final_records = []
    for rec in unique_records:
        title = rec.get('title', '')
        note = rec.get('note', '')
        sign = rec.get('sign', -1)
        amount = rec.get('amount', 0)

        cat_id = map_category(title, note, sign)
        cleaned_note = clean_note(note, title, cat_id)
        rec_type = 'income' if sign > 0 else 'expense'

        final_records.append({
            'date': rec.get('date', ''),
            'time': rec.get('time', ''),
            'title': title,
            'note': cleaned_note,
            'amount': amount,
            'type': rec_type,
            'categoryId': cat_id,
            'account': rec.get('account', ''),
        })

    # Category breakdown
    cat_counts = {}
    for r in final_records:
        cat_counts[r['categoryId']] = cat_counts.get(r['categoryId'], 0) + 1

    # Category name lookup
    cat_names = {
        'cat_inc_1': 'Salary & Income', 'cat_inc_2': 'Freelance & Business',
        'cat_e_01': 'Online Food Orders', 'cat_e_02': 'Dining Out',
        'cat_e_03': 'Street Food', 'cat_e_04': 'Snacks & Beverages',
        'cat_e_05': 'Sweets & Bakery', 'cat_e_06': 'Groceries & Raw Food',
        'cat_e_07': 'Household Essentials', 'cat_e_08': 'Kitchen & Dining',
        'cat_e_09': 'Home Furnishing', 'cat_e_10': 'Home Appliances',
        'cat_e_11': 'Home Repairs', 'cat_e_12': 'Domestic Help',
        'cat_e_13': 'House Rent', 'cat_e_14': 'Garage Rent',
        'cat_e_15': 'Online Shopping', 'cat_e_16': 'In-store Shopping',
        'cat_e_17': 'Clothing & Apparel', 'cat_e_18': 'Tailoring',
        'cat_e_19': 'Footwear', 'cat_e_20': 'Bags & Accessories',
        'cat_e_21': 'Electronics & Gadgets', 'cat_e_22': 'Personal Care',
        'cat_e_23': 'Eyewear', 'cat_e_24': 'Vehicle Fuel',
        'cat_e_25': 'Vehicle Servicing', 'cat_e_26': 'Vehicle Repairs',
        'cat_e_27': 'Parking', 'cat_e_28': 'Toll & FASTag',
        'cat_e_29': 'Local Transportation', 'cat_e_30': 'Outstation Transport',
        'cat_e_31': 'Travel & Accommodation', 'cat_e_32': 'Medicines',
        'cat_e_33': 'Doctor Consultation', 'cat_e_34': 'Hospital & Tests',
        'cat_e_35': 'Dental & Eye Care', 'cat_e_36': 'Physiotherapy',
        'cat_e_37': 'Vaccination', 'cat_e_38': 'Salon & Haircut',
        'cat_e_39': 'Beauty & Grooming', 'cat_e_40': 'OTT Subscriptions',
        'cat_e_41': 'Movies & Events', 'cat_e_42': 'Outings & Recreation',
        'cat_e_43': 'Games & Hobbies', 'cat_e_44': 'Mobile Recharge',
        'cat_e_45': 'Internet & Broadband', 'cat_e_46': 'Electricity Bill',
        'cat_e_47': 'Water & Gas Bills', 'cat_e_48': 'DTH & Cable',
        'cat_e_49': 'Other Subscriptions', 'cat_e_50': 'Gifts',
        'cat_e_51': 'Birthday & Anniversary', 'cat_e_52': 'Puja & Religious',
        'cat_e_53': 'Festivals', 'cat_e_54': 'Social Contributions',
        'cat_e_55': 'Banking Charges', 'cat_e_56': 'Tax & Government',
        'cat_e_57': 'Insurance', 'cat_e_58': 'Loan & EMI',
        'cat_e_59': 'Cash Withdrawal', 'cat_e_60': 'Money Transfers',
        'cat_e_61': 'Donations & Charity', 'cat_e_62': 'Miscellaneous',
        'cat_e_63': 'Office Breakfast', 'cat_e_64': 'Office Lunch',
        'cat_e_65': 'Office Dinner', 'cat_e_66': 'Office Tea & Snacks',
        'cat_e_67': 'Office Commute', 'cat_e_68': 'Office Parking',
        'cat_e_69': 'Office Expenses',
    }

    print(f"\n--- Category Breakdown ({len(cat_counts)} categories used) ---")
    for cat_id, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        name = cat_names.get(cat_id, cat_id)
        print(f"  {cat_id} ({name}): {count}")

    misc_records = [r for r in final_records if r['categoryId'] == 'cat_e_62']
    print(f"\nMiscellaneous (unmapped): {len(misc_records)}")
    if misc_records:
        print("Sample miscellaneous records:")
        for r in misc_records[:15]:
            print(f"  Title: '{r['title']}', Note: '{r['note']}'")

    # Write CSV
    print(f"\nWriting CSV to {output_csv}...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date','time','title','note','amount','type','categoryId','account'])
        writer.writeheader()
        writer.writerows(final_records)
    print(f"CSV written: {len(final_records)} rows")

    # Print first 20 rows preview
    print(f"\n--- First 20 CSV Rows Preview ---")
    print("date,time,title,note,amount,type,categoryId,account")
    for r in final_records[:20]:
        print(f"{r['date']},{r['time']},\"{r['title']}\",\"{r['note']}\",{r['amount']},{r['type']},{r['categoryId']},\"{r['account']}\"")

    # Build WalletPro JSON
    categories = [
        { "id": "cat_inc_1", "name": "Salary & Income", "type": "income", "group": "income", "icon": "payments", "color": "#059669" },
        { "id": "cat_inc_2", "name": "Freelance & Business", "type": "income", "group": "income", "icon": "laptop_mac", "color": "#0D9488" },
        { "id": "cat_e_01", "name": "Online Food Orders", "type": "expense", "group": "wants", "icon": "delivery_dining", "color": "#EA580C" },
        { "id": "cat_e_02", "name": "Dining Out", "type": "expense", "group": "wants", "icon": "restaurant", "color": "#F97316" },
        { "id": "cat_e_03", "name": "Street Food & Quick Bites", "type": "expense", "group": "wants", "icon": "lunch_dining", "color": "#FB923C" },
        { "id": "cat_e_04", "name": "Snacks & Beverages", "type": "expense", "group": "wants", "icon": "local_cafe", "color": "#FDBA74" },
        { "id": "cat_e_05", "name": "Sweets & Bakery", "type": "expense", "group": "wants", "icon": "cake", "color": "#F59E0B" },
        { "id": "cat_e_06", "name": "Groceries & Raw Food", "type": "expense", "group": "needs", "icon": "shopping_basket", "color": "#16A34A" },
        { "id": "cat_e_07", "name": "Household Essentials", "type": "expense", "group": "needs", "icon": "cleaning_services", "color": "#15803D" },
        { "id": "cat_e_08", "name": "Kitchen & Dining Supplies", "type": "expense", "group": "needs", "icon": "kitchen", "color": "#14532D" },
        { "id": "cat_e_09", "name": "Home Furnishing & Decor", "type": "expense", "group": "wants", "icon": "chair", "color": "#7C3AED" },
        { "id": "cat_e_10", "name": "Home Appliances", "type": "expense", "group": "needs", "icon": "microwave", "color": "#6D28D9" },
        { "id": "cat_e_11", "name": "Home Repairs & Maintenance", "type": "expense", "group": "needs", "icon": "handyman", "color": "#8B5CF6" },
        { "id": "cat_e_12", "name": "Domestic Help", "type": "expense", "group": "needs", "icon": "person", "color": "#A78BFA" },
        { "id": "cat_e_13", "name": "House Rent", "type": "expense", "group": "needs", "icon": "home", "color": "#0284C7" },
        { "id": "cat_e_14", "name": "Garage Rent", "type": "expense", "group": "needs", "icon": "garage", "color": "#0369A1" },
        { "id": "cat_e_15", "name": "Online Shopping", "type": "expense", "group": "wants", "icon": "shopping_bag", "color": "#9333EA" },
        { "id": "cat_e_16", "name": "In-store Shopping", "type": "expense", "group": "wants", "icon": "store", "color": "#7E22CE" },
        { "id": "cat_e_17", "name": "Clothing & Apparel", "type": "expense", "group": "wants", "icon": "checkroom", "color": "#A855F7" },
        { "id": "cat_e_18", "name": "Tailoring & Alterations", "type": "expense", "group": "wants", "icon": "content_cut", "color": "#C084FC" },
        { "id": "cat_e_19", "name": "Footwear", "type": "expense", "group": "wants", "icon": "steps", "color": "#D946EF" },
        { "id": "cat_e_20", "name": "Bags & Accessories", "type": "expense", "group": "wants", "icon": "backpack", "color": "#E879F9" },
        { "id": "cat_e_21", "name": "Electronics & Gadgets", "type": "expense", "group": "wants", "icon": "devices", "color": "#6366F1" },
        { "id": "cat_e_22", "name": "Personal Care Products", "type": "expense", "group": "needs", "icon": "face_retouching_natural", "color": "#EC4899" },
        { "id": "cat_e_23", "name": "Eyewear", "type": "expense", "group": "needs", "icon": "visibility", "color": "#F43F5E" },
        { "id": "cat_e_24", "name": "Vehicle Fuel", "type": "expense", "group": "needs", "icon": "local_gas_station", "color": "#2563EB" },
        { "id": "cat_e_25", "name": "Vehicle Servicing", "type": "expense", "group": "needs", "icon": "build", "color": "#1D4ED8" },
        { "id": "cat_e_26", "name": "Vehicle Repairs & Spare Parts", "type": "expense", "group": "needs", "icon": "car_repair", "color": "#1E40AF" },
        { "id": "cat_e_27", "name": "Parking Charges", "type": "expense", "group": "needs", "icon": "local_parking", "color": "#3B82F6" },
        { "id": "cat_e_28", "name": "Toll & FASTag", "type": "expense", "group": "needs", "icon": "toll", "color": "#60A5FA" },
        { "id": "cat_e_29", "name": "Local Transportation", "type": "expense", "group": "needs", "icon": "directions_bus", "color": "#93C5FD" },
        { "id": "cat_e_30", "name": "Outstation Transportation", "type": "expense", "group": "wants", "icon": "train", "color": "#BFDBFE" },
        { "id": "cat_e_31", "name": "Travel & Accommodation", "type": "expense", "group": "wants", "icon": "flight", "color": "#0EA5E9" },
        { "id": "cat_e_32", "name": "Medicines", "type": "expense", "group": "needs", "icon": "medication", "color": "#DC2626" },
        { "id": "cat_e_33", "name": "Doctor Consultation", "type": "expense", "group": "needs", "icon": "stethoscope", "color": "#B91C1C" },
        { "id": "cat_e_34", "name": "Hospital & Medical Tests", "type": "expense", "group": "needs", "icon": "local_hospital", "color": "#991B1B" },
        { "id": "cat_e_35", "name": "Dental & Eye Care", "type": "expense", "group": "needs", "icon": "health_and_safety", "color": "#EF4444" },
        { "id": "cat_e_36", "name": "Physiotherapy & Treatment", "type": "expense", "group": "needs", "icon": "self_improvement", "color": "#F87171" },
        { "id": "cat_e_37", "name": "Vaccination", "type": "expense", "group": "needs", "icon": "vaccines", "color": "#FCA5A5" },
        { "id": "cat_e_38", "name": "Salon & Haircut", "type": "expense", "group": "wants", "icon": "content_cut", "color": "#DB2777" },
        { "id": "cat_e_39", "name": "Beauty & Grooming Services", "type": "expense", "group": "wants", "icon": "spa", "color": "#BE185D" },
        { "id": "cat_e_40", "name": "OTT & Digital Subscriptions", "type": "expense", "group": "wants", "icon": "tv", "color": "#7C3AED" },
        { "id": "cat_e_41", "name": "Movies & Events", "type": "expense", "group": "wants", "icon": "movie", "color": "#6D28D9" },
        { "id": "cat_e_42", "name": "Outings & Recreation", "type": "expense", "group": "wants", "icon": "park", "color": "#059669" },
        { "id": "cat_e_43", "name": "Games & Hobbies", "type": "expense", "group": "wants", "icon": "sports_esports", "color": "#10B981" },
        { "id": "cat_e_44", "name": "Mobile Recharge", "type": "expense", "group": "needs", "icon": "phone_android", "color": "#0D9488" },
        { "id": "cat_e_45", "name": "Internet & Broadband", "type": "expense", "group": "needs", "icon": "wifi", "color": "#0F766E" },
        { "id": "cat_e_46", "name": "Electricity Bill", "type": "expense", "group": "needs", "icon": "bolt", "color": "#F59E0B" },
        { "id": "cat_e_47", "name": "Water & Gas Bills", "type": "expense", "group": "needs", "icon": "water_drop", "color": "#38BDF8" },
        { "id": "cat_e_48", "name": "DTH & Cable", "type": "expense", "group": "needs", "icon": "live_tv", "color": "#6B7280" },
        { "id": "cat_e_49", "name": "Other Subscriptions", "type": "expense", "group": "wants", "icon": "subscriptions", "color": "#8B5CF6" },
        { "id": "cat_e_50", "name": "Gifts", "type": "expense", "group": "wants", "icon": "redeem", "color": "#EC4899" },
        { "id": "cat_e_51", "name": "Birthday & Anniversary", "type": "expense", "group": "wants", "icon": "celebration", "color": "#F472B6" },
        { "id": "cat_e_52", "name": "Puja & Religious Expenses", "type": "expense", "group": "wants", "icon": "temple_hindu", "color": "#F97316" },
        { "id": "cat_e_53", "name": "Festivals & Decorations", "type": "expense", "group": "wants", "icon": "festival", "color": "#FBBF24" },
        { "id": "cat_e_54", "name": "Social Contributions", "type": "expense", "group": "wants", "icon": "group", "color": "#34D399" },
        { "id": "cat_e_55", "name": "Banking & Transaction Charges", "type": "expense", "group": "needs", "icon": "account_balance", "color": "#6B7280" },
        { "id": "cat_e_56", "name": "Tax & Government Payments", "type": "expense", "group": "needs", "icon": "account_balance_wallet", "color": "#4B5563" },
        { "id": "cat_e_57", "name": "Insurance", "type": "expense", "group": "savings", "icon": "shield", "color": "#0D9488" },
        { "id": "cat_e_58", "name": "Loan & EMI Payments", "type": "expense", "group": "savings", "icon": "credit_score", "color": "#0369A1" },
        { "id": "cat_e_59", "name": "Cash Withdrawal", "type": "expense", "group": "needs", "icon": "money", "color": "#78716C" },
        { "id": "cat_e_60", "name": "Money Transfers", "type": "expense", "group": "savings", "icon": "sync_alt", "color": "#0891B2" },
        { "id": "cat_e_61", "name": "Donations & Charity", "type": "expense", "group": "wants", "icon": "volunteer_activism", "color": "#16A34A" },
        { "id": "cat_e_62", "name": "Miscellaneous", "type": "expense", "group": "needs", "icon": "more_horiz", "color": "#94A3B8" },
        { "id": "cat_e_63", "name": "Office Breakfast", "type": "expense", "group": "needs", "icon": "free_breakfast", "color": "#FBBF24" },
        { "id": "cat_e_64", "name": "Office Lunch", "type": "expense", "group": "needs", "icon": "lunch_dining", "color": "#F97316" },
        { "id": "cat_e_65", "name": "Office Dinner", "type": "expense", "group": "needs", "icon": "dinner_dining", "color": "#EA580C" },
        { "id": "cat_e_66", "name": "Office Tea & Snacks", "type": "expense", "group": "needs", "icon": "emoji_food_beverage", "color": "#FDE68A" },
        { "id": "cat_e_67", "name": "Office Commute", "type": "expense", "group": "needs", "icon": "directions_bus", "color": "#3B82F6" },
        { "id": "cat_e_68", "name": "Office Parking", "type": "expense", "group": "needs", "icon": "local_parking", "color": "#60A5FA" },
        { "id": "cat_e_69", "name": "Office Expenses", "type": "expense", "group": "needs", "icon": "business_center", "color": "#64748B" }
    ]

    json_records = []
    for idx, r in enumerate(final_records, 1):
        json_records.append({
            "id": f"rec_{idx:04d}",
            "type": r['type'],
            "amount": r['amount'],
            "accountId": None,
            "categoryId": r['categoryId'],
            "toAccountId": None,
            "date": r['date'],
            "payee": r['title'],
            "note": r['note'],
            "tags": []
        })

    wallet_pro_state = {
        "updatedAt": 0,
        "lastSyncedAt": 0,
        "currency": "₹",
        "cycleStartDay": 1,
        "darkMode": False,
        "accounts": [],
        "categories": categories,
        "records": json_records,
        "budgets": [],
        "planned": [],
        "goals": [],
        "debts": [],
        "rent": {
            "monthlyRent": 0,
            "maintenance": 0,
            "securityDeposit": 0,
            "accountId": "",
            "landlordName": "",
            "landlordPan": "",
            "leaseStart": "",
            "leaseEnd": "",
            "escalationPct": 5,
            "items": []
        }
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(wallet_pro_state, f, ensure_ascii=False, indent=2)
    print(f"\nJSON written to {output_json}")
    print(f"Total records in JSON: {len(json_records)}")
    print("\nDone!")


if __name__ == '__main__':
    main()

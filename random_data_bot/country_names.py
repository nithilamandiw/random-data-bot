from __future__ import annotations

from dataclasses import dataclass
from html import escape
import re
import string
import unicodedata

from faker import Faker
from faker.config import AVAILABLE_LOCALES
import phonenumbers
import pycountry


DEFAULT_LOCALE = "en_US"

ALIASES = {
    "uk": "gb",
    "u.k.": "gb",
    "unitedkingdom": "gb",
    "usa": "us",
    "u.s.": "us",
    "america": "us",
    "srilanka": "lk",
    "sri_lanka": "lk",
}

# Faker does not provide a unique locale for every country. This table maps
# countries to an exact or nearest practical name style, then unmapped valid
# countries fall back to DEFAULT_LOCALE.
LOCALE_BY_COUNTRY = {
    "AE": "ar_AA",
    "AR": "es_AR",
    "AT": "de_AT",
    "AU": "en_AU",
    "BA": "bs_BA",
    "BD": "bn_BD",
    "BE": "nl_BE",
    "BG": "bg_BG",
    "BR": "pt_BR",
    "CA": "en_CA",
    "CH": "de_CH",
    "CL": "es_CL",
    "CN": "zh_CN",
    "CO": "es_CO",
    "CZ": "cs_CZ",
    "DE": "de_DE",
    "DK": "da_DK",
    "EE": "et_EE",
    "ES": "es_ES",
    "FI": "fi_FI",
    "FR": "fr_FR",
    "GB": "en_GB",
    "GE": "ka_GE",
    "GR": "el_GR",
    "HR": "hr_HR",
    "HU": "hu_HU",
    "ID": "id_ID",
    "IL": "he_IL",
    "IN": "en_IN",
    "IR": "fa_IR",
    "IT": "it_IT",
    "JP": "ja_JP",
    "KR": "ko_KR",
    "LA": "lo_LA",
    "LK": "en_IN",
    "LT": "lt_LT",
    "LV": "lv_LV",
    "MX": "es_MX",
    "MY": "ms_MY",
    "NG": "en_NG",
    "NL": "nl_NL",
    "NO": "no_NO",
    "NP": "ne_NP",
    "NZ": "en_NZ",
    "PH": "en_PH",
    "PK": "ur_PK",
    "PL": "pl_PL",
    "PT": "pt_PT",
    "RO": "ro_RO",
    "RS": "sr_RS",
    "RU": "ru_RU",
    "SA": "ar_AA",
    "SE": "sv_SE",
    "SI": "sl_SI",
    "SK": "sk_SK",
    "TH": "th_TH",
    "TR": "tr_TR",
    "TW": "zh_TW",
    "UA": "uk_UA",
    "US": "en_US",
    "VN": "vi_VN",
    "ZA": "zu_ZA",
}

CALLING_CODE_BY_COUNTRY = {
    "AD": "376",
    "AE": "971",
    "AF": "93",
    "AG": "1",
    "AI": "1",
    "AL": "355",
    "AM": "374",
    "AN": "599",
    "AO": "244",
    "AQ": "672",
    "AR": "54",
    "AS": "1",
    "AT": "43",
    "AU": "61",
    "AW": "297",
    "AX": "358",
    "AZ": "994",
    "BA": "387",
    "BB": "1",
    "BD": "880",
    "BE": "32",
    "BF": "226",
    "BG": "359",
    "BH": "973",
    "BI": "257",
    "BJ": "229",
    "BM": "1",
    "BN": "673",
    "BO": "591",
    "BQ": "599",
    "BR": "55",
    "BS": "1",
    "BT": "975",
    "BV": "47",
    "BW": "267",
    "BY": "375",
    "BZ": "501",
    "CA": "1",
    "CC": "61",
    "CD": "243",
    "CF": "236",
    "CG": "242",
    "CH": "41",
    "CI": "225",
    "CK": "682",
    "CL": "56",
    "CM": "237",
    "CN": "86",
    "CO": "57",
    "CR": "506",
    "CU": "53",
    "CV": "238",
    "CW": "599",
    "CX": "61",
    "CY": "357",
    "CZ": "420",
    "DE": "49",
    "DJ": "253",
    "DK": "45",
    "DM": "1",
    "DO": "1",
    "DZ": "213",
    "EC": "593",
    "EE": "372",
    "EG": "20",
    "EH": "212",
    "ER": "291",
    "ES": "34",
    "ET": "251",
    "FI": "358",
    "FJ": "679",
    "FK": "500",
    "FM": "691",
    "FO": "298",
    "FR": "33",
    "GA": "241",
    "GB": "44",
    "GD": "1",
    "GH": "233",
    "GI": "350",
    "GL": "299",
    "GM": "220",
    "GN": "224",
    "GP": "590",
    "GQ": "240",
    "GE": "995",
    "GR": "30",
    "GS": "500",
    "GT": "502",
    "GU": "1",
    "GW": "245",
    "GY": "592",
    "HK": "852",
    "HM": "672",
    "HN": "504",
    "HR": "385",
    "HT": "509",
    "HU": "36",
    "ID": "62",
    "IL": "972",
    "IN": "91",
    "IR": "98",
    "IQ": "964",
    "IS": "354",
    "IT": "39",
    "JM": "1",
    "JO": "962",
    "JP": "81",
    "KE": "254",
    "KG": "996",
    "KH": "855",
    "KI": "686",
    "KM": "269",
    "KN": "1",
    "KP": "850",
    "KR": "82",
    "KW": "965",
    "KY": "1",
    "KZ": "7",
    "LA": "856",
    "LB": "961",
    "LC": "1",
    "LI": "423",
    "LK": "94",
    "LR": "231",
    "LS": "266",
    "LT": "370",
    "LU": "352",
    "LV": "371",
    "LY": "218",
    "MA": "212",
    "MD": "373",
    "ME": "382",
    "MG": "261",
    "MK": "389",
    "ML": "223",
    "MM": "95",
    "MN": "976",
    "MO": "853",
    "MP": "1",
    "MQ": "596",
    "MR": "222",
    "MS": "1",
    "MT": "356",
    "MU": "230",
    "MV": "960",
    "MW": "265",
    "MX": "52",
    "MY": "60",
    "MZ": "258",
    "NC": "687",
    "NF": "672",
    "NA": "264",
    "NE": "227",
    "NG": "234",
    "NI": "505",
    "NL": "31",
    "NO": "47",
    "NP": "977",
    "NR": "674",
    "NU": "683",
    "NZ": "64",
    "OM": "968",
    "PA": "507",
    "PF": "689",
    "PG": "675",
    "PE": "51",
    "PH": "63",
    "PK": "92",
    "PL": "48",
    "PT": "351",
    "PW": "680",
    "PY": "595",
    "QA": "974",
    "RE": "262",
    "RO": "40",
    "RS": "381",
    "RU": "7",
    "RW": "250",
    "SA": "966",
    "SB": "677",
    "SC": "248",
    "SD": "249",
    "SE": "46",
    "SG": "65",
    "SH": "290",
    "SJ": "47",
    "SI": "386",
    "SK": "421",
    "SL": "232",
    "SN": "221",
    "SO": "252",
    "SR": "597",
    "SS": "211",
    "ST": "239",
    "SV": "503",
    "SX": "1",
    "SY": "963",
    "SZ": "268",
    "TC": "1",
    "TD": "235",
    "TF": "262",
    "TG": "228",
    "TH": "66",
    "TJ": "992",
    "TK": "690",
    "TM": "993",
    "TN": "216",
    "TO": "676",
    "TT": "1",
    "TV": "688",
    "TR": "90",
    "TW": "886",
    "TZ": "255",
    "UA": "380",
    "UG": "256",
    "US": "1",
    "UY": "598",
    "UZ": "998",
    "VA": "39",
    "VC": "1",
    "VE": "58",
    "VG": "1",
    "VI": "1",
    "VN": "84",
    "VU": "678",
    "WF": "681",
    "WS": "685",
    "YE": "967",
    "YT": "262",
    "ZA": "27",
    "ZM": "260",
    "ZW": "263",
}

# Sri Lankan names are more recognizable with a small local curated list than
# with Faker's English/Indian fallback.
SRI_LANKAN_FIRST_NAMES = [
    "Kasun",
    "Nimal",
    "Amal",
    "Chamath",
    "Isuru",
    "Dilan",
    "Tharushi",
    "Nethmi",
    "Dilini",
    "Sachini",
    "Kavindi",
    "Hiruni",
]

SRI_LANKAN_LAST_NAMES = [
    "Perera",
    "Fernando",
    "Silva",
    "Jayasinghe",
    "Wijesinghe",
    "Bandara",
    "Gunasekara",
    "Karunaratne",
    "Dissanayake",
    "Rajapaksha",
]

SRI_LANKAN_CITY_DETAILS = [
    {"province": "Western Province", "city": "Colombo", "postal_code": "00100"},
    {"province": "Western Province", "city": "Gampaha", "postal_code": "11000"},
    {"province": "Western Province", "city": "Kalutara", "postal_code": "12000"},
    {"province": "Western Province", "city": "Negombo", "postal_code": "11500"},
    {"province": "Central Province", "city": "Kandy", "postal_code": "20000"},
    {"province": "Central Province", "city": "Matale", "postal_code": "21000"},
    {"province": "Central Province", "city": "Nuwara Eliya", "postal_code": "22200"},
    {"province": "Southern Province", "city": "Galle", "postal_code": "80000"},
    {"province": "Southern Province", "city": "Matara", "postal_code": "81000"},
    {"province": "Southern Province", "city": "Hambantota", "postal_code": "82000"},
    {"province": "Northern Province", "city": "Jaffna", "postal_code": "40000"},
    {"province": "Northern Province", "city": "Vavuniya", "postal_code": "43000"},
    {"province": "Northern Province", "city": "Mannar", "postal_code": "41000"},
    {"province": "Eastern Province", "city": "Trincomalee", "postal_code": "31000"},
    {"province": "Eastern Province", "city": "Batticaloa", "postal_code": "30000"},
    {"province": "Eastern Province", "city": "Ampara", "postal_code": "32000"},
    {"province": "North Western Province", "city": "Kurunegala", "postal_code": "60000"},
    {"province": "North Western Province", "city": "Puttalam", "postal_code": "61300"},
    {"province": "North Western Province", "city": "Chilaw", "postal_code": "61000"},
    {
        "province": "North Central Province",
        "city": "Anuradhapura",
        "postal_code": "50000",
    },
    {
        "province": "North Central Province",
        "city": "Polonnaruwa",
        "postal_code": "51000",
    },
    {"province": "Uva Province", "city": "Badulla", "postal_code": "90000"},
    {"province": "Uva Province", "city": "Bandarawela", "postal_code": "90100"},
    {"province": "Uva Province", "city": "Monaragala", "postal_code": "91000"},
    {"province": "Sabaragamuwa Province", "city": "Ratnapura", "postal_code": "70000"},
    {"province": "Sabaragamuwa Province", "city": "Kegalle", "postal_code": "71000"},
]

ADDRESS_DETAILS_BY_COUNTRY = {
    "US": [
        {"state": "New York", "city": "New York", "postal_code": "10001"},
        {"state": "California", "city": "Los Angeles", "postal_code": "90001"},
        {"state": "Illinois", "city": "Chicago", "postal_code": "60601"},
        {"state": "Texas", "city": "Houston", "postal_code": "77001"},
        {"state": "Arizona", "city": "Phoenix", "postal_code": "85001"},
        {"state": "Pennsylvania", "city": "Philadelphia", "postal_code": "19102"},
        {"state": "Texas", "city": "San Antonio", "postal_code": "78201"},
        {"state": "California", "city": "San Diego", "postal_code": "92101"},
        {"state": "Texas", "city": "Dallas", "postal_code": "75201"},
        {"state": "Washington", "city": "Seattle", "postal_code": "98101"},
    ],
    "GB": [
        {"state": "Greater London", "city": "London", "postal_code": "SW1A 1AA"},
        {"state": "Greater Manchester", "city": "Manchester", "postal_code": "M1 1AE"},
        {"state": "West Midlands", "city": "Birmingham", "postal_code": "B1 1AA"},
        {"state": "City of Edinburgh", "city": "Edinburgh", "postal_code": "EH1 1AA"},
        {"state": "Glasgow City", "city": "Glasgow", "postal_code": "G1 1AA"},
        {"state": "Cardiff", "city": "Cardiff", "postal_code": "CF10 1AA"},
        {"state": "Belfast", "city": "Belfast", "postal_code": "BT1 1AA"},
        {"state": "Merseyside", "city": "Liverpool", "postal_code": "L1 1AA"},
        {"state": "West Yorkshire", "city": "Leeds", "postal_code": "LS1 1UR"},
        {"state": "Bristol", "city": "Bristol", "postal_code": "BS1 1AA"},
    ],
    "DE": [
        {"state": "Berlin", "city": "Berlin", "postal_code": "10115"},
        {"state": "Bavaria", "city": "Munich", "postal_code": "80331"},
        {"state": "Hamburg", "city": "Hamburg", "postal_code": "20095"},
        {"state": "North Rhine-Westphalia", "city": "Cologne", "postal_code": "50667"},
        {"state": "Hesse", "city": "Frankfurt am Main", "postal_code": "60311"},
        {"state": "Baden-Württemberg", "city": "Stuttgart", "postal_code": "70173"},
        {"state": "North Rhine-Westphalia", "city": "Düsseldorf", "postal_code": "40213"},
        {"state": "Saxony", "city": "Leipzig", "postal_code": "04109"},
        {"state": "Bremen", "city": "Bremen", "postal_code": "28195"},
        {"state": "Lower Saxony", "city": "Hannover", "postal_code": "30159"},
    ],
    "FR": [
        {"state": "Île-de-France", "city": "Paris", "postal_code": "75001"},
        {
            "state": "Provence-Alpes-Côte d'Azur",
            "city": "Marseille",
            "postal_code": "13001",
        },
        {"state": "Auvergne-Rhône-Alpes", "city": "Lyon", "postal_code": "69001"},
        {"state": "Occitanie", "city": "Toulouse", "postal_code": "31000"},
        {"state": "Provence-Alpes-Côte d'Azur", "city": "Nice", "postal_code": "06000"},
        {"state": "Pays de la Loire", "city": "Nantes", "postal_code": "44000"},
        {"state": "Grand Est", "city": "Strasbourg", "postal_code": "67000"},
        {"state": "Nouvelle-Aquitaine", "city": "Bordeaux", "postal_code": "33000"},
        {"state": "Occitanie", "city": "Montpellier", "postal_code": "34000"},
        {"state": "Hauts-de-France", "city": "Lille", "postal_code": "59000"},
    ],
    "MX": [
        {
            "state": "Ciudad de México",
            "city": "Cuauhtémoc",
            "neighborhood": "Centro (Área 1)",
            "postal_code": "06000",
        },
        {
            "state": "Jalisco",
            "city": "Guadalajara",
            "neighborhood": "Guadalajara Centro",
            "postal_code": "44100",
        },
        {
            "state": "Nuevo León",
            "city": "Monterrey",
            "neighborhood": "Monterrey Centro",
            "postal_code": "64000",
        },
        {
            "state": "Puebla",
            "city": "Puebla",
            "neighborhood": "Puebla Centro",
            "postal_code": "72000",
        },
        {
            "state": "Yucatán",
            "city": "Mérida",
            "neighborhood": "Mérida Centro",
            "postal_code": "97000",
        },
        {
            "state": "Quintana Roo",
            "city": "Cancún",
            "neighborhood": "Cancún Centro",
            "postal_code": "77500",
        },
    ],
}

EU_IBAN_SPECS = {
    "AT": "16n",
    "BE": "12n",
    "BG": "4a6n8c",
    "HR": "17n",
    "CY": "8n16c",
    "CZ": "20n",
    "DK": "14n",
    "EE": "16n",
    "FI": "14n",
    "FR": "10n11c2n",
    "DE": "18n",
    "GR": "7n16c",
    "HU": "24n",
    "IE": "4a14n",
    "IT": "1a10n12c",
    "LV": "4a13c",
    "LT": "16n",
    "LU": "3n13c",
    "MT": "4a5n18c",
    "NL": "4a10n",
    "PL": "24n",
    "PT": "21n",
    "RO": "4a16c",
    "SK": "20n",
    "SI": "15n",
    "ES": "20n",
    "SE": "20n",
}


@dataclass(frozen=True)
class ResolvedCountry:
    code: str
    name: str
    locale: str
    uses_fallback: bool


@dataclass(frozen=True)
class FakeAddress:
    name: str
    street: str
    city: str
    state: str
    postal_code: str
    phone: str
    country: ResolvedCountry
    neighborhood: str | None = None
    ssn: str | None = None


@dataclass(frozen=True)
class FakeIban:
    iban: str
    country: ResolvedCountry


def normalize_country_code(raw_code: str) -> str:
    compact = raw_code.strip().lower().replace(" ", "").replace("-", "_")
    return ALIASES.get(compact, compact).upper()


def resolve_country(raw_code: str) -> ResolvedCountry:
    code = normalize_country_code(raw_code)
    country = pycountry.countries.get(alpha_2=code)

    if country is None:
        raise ValueError(f"{raw_code!r} is not a valid country code")

    requested_locale = LOCALE_BY_COUNTRY.get(code, DEFAULT_LOCALE)
    locale = requested_locale if requested_locale in AVAILABLE_LOCALES else DEFAULT_LOCALE
    uses_fallback = code not in LOCALE_BY_COUNTRY or locale == DEFAULT_LOCALE and code != "US"

    return ResolvedCountry(
        code=code,
        name=country.name,
        locale=locale,
        uses_fallback=uses_fallback,
    )


def generate_name(raw_code: str) -> tuple[str, ResolvedCountry]:
    country = resolve_country(raw_code)

    if country.code == "LK":
        return generate_sri_lankan_name(), country

    fake = Faker(country.locale)
    return fake.name(), country


def generate_sri_lankan_name() -> str:
    fake = Faker()
    first = fake.random_element(SRI_LANKAN_FIRST_NAMES)
    last = fake.random_element(SRI_LANKAN_LAST_NAMES)
    return f"{first} {last}"


def generate_fake_address(raw_code: str) -> FakeAddress:
    country = resolve_country(raw_code)

    if country.code == "LK":
        return generate_sri_lankan_address(country)

    if country.code in ADDRESS_DETAILS_BY_COUNTRY:
        return generate_curated_address(country)

    fake = Faker(country.locale)
    return FakeAddress(
        name=generate_name(country.code)[0],
        street=single_line(fake.street_address()),
        city=safe_provider_value(fake, "city"),
        state=safe_provider_value(
            fake, "state", "administrative_unit", "province", "county"
        ),
        postal_code=safe_provider_value(fake, "postcode"),
        phone=generate_phone(country.code, fake),
        country=country,
    )


def generate_fake_iban(raw_code: str) -> FakeIban:
    country = resolve_country(raw_code)

    if country.code not in EU_IBAN_SPECS:
        raise ValueError(f"{raw_code!r} is not a supported EU IBAN country code")

    fake = Faker()
    bban = generate_bban(EU_IBAN_SPECS[country.code], fake)
    valid_check_digits = calculate_iban_check_digits(country.code, bban)
    fake_check_digits = generate_invalid_check_digits(valid_check_digits, fake)

    return FakeIban(iban=f"{country.code}{fake_check_digits}{bban}", country=country)


def generate_bban(pattern: str, fake: Faker) -> str:
    bban = []

    for length, token in re.findall(r"(\d+)([anc])", pattern):
        count = int(length)
        if token == "n":
            characters = string.digits
        elif token == "a":
            characters = string.ascii_uppercase
        else:
            characters = string.ascii_uppercase + string.digits

        bban.extend(fake.random_choices(elements=characters, length=count))

    return "".join(bban)


def calculate_iban_check_digits(country_code: str, bban: str) -> str:
    rearranged = f"{bban}{country_code}00"
    numeric = "".join(convert_iban_character(character) for character in rearranged)
    check_digits = 98 - iban_mod97(numeric)
    return f"{check_digits:02d}"


def convert_iban_character(character: str) -> str:
    if character.isdigit():
        return character

    return str(ord(character.upper()) - 55)


def iban_mod97(numeric_value: str) -> int:
    remainder = 0
    for character in numeric_value:
        remainder = (remainder * 10 + int(character)) % 97
    return remainder


def generate_invalid_check_digits(valid_check_digits: str, fake: Faker) -> str:
    while True:
        candidate = f"{fake.random_int(min=1, max=98):02d}"
        if candidate != valid_check_digits:
            return candidate


def generate_curated_address(country: ResolvedCountry) -> FakeAddress:
    fake = Faker(country.locale)
    city_details = fake.random_element(ADDRESS_DETAILS_BY_COUNTRY[country.code])

    return FakeAddress(
        name=generate_name(country.code)[0],
        street=single_line(fake.street_address()),
        city=city_details["city"],
        state=city_details["state"],
        postal_code=city_details["postal_code"],
        phone=generate_phone(country.code, fake),
        country=country,
        neighborhood=city_details.get("neighborhood"),
        ssn=generate_fake_ssn(fake) if country.code == "US" else None,
    )


def generate_sri_lankan_address(country: ResolvedCountry) -> FakeAddress:
    fake = Faker()
    streets = [
        "Galle Road",
        "R. A. De Mel Mawatha",
        "Bauddhaloka Mawatha",
        "Temple Road",
        "Lake Road",
        "Main Street",
        "Kandy Road",
        "Flower Road",
    ]

    city_details = fake.random_element(SRI_LANKAN_CITY_DETAILS)
    street = f"{fake.random_int(min=1, max=200)} {fake.random_element(streets)}"

    return FakeAddress(
        name=generate_sri_lankan_name(),
        street=street,
        city=city_details["city"],
        state=city_details["province"],
        postal_code=city_details["postal_code"],
        phone=generate_sri_lankan_phone(),
        country=country,
    )


def generate_sri_lankan_phone() -> str:
    fake = Faker()
    prefix = fake.random_element(["70", "71", "72", "75", "76", "77", "78"])
    suffix = fake.random_int(min=1000000, max=9999999)
    return normalize_phone_number(f"{prefix}{suffix}", "LK")


def generate_phone(country_code: str, fake: Faker) -> str:
    if country_code == "MX":
        area_code = fake.random_element(["55", "33", "81", "222", "999", "998"])
        first = fake.random_int(min=1000, max=9999)
        second = fake.random_int(min=1000, max=9999)
        return normalize_phone_number(f"{area_code}{first}{second}", country_code)

    phone = normalize_phone_number(safe_provider_value(fake, "phone_number"), country_code)
    if phone != "N/A":
        return phone

    calling_code = get_calling_code(country_code)
    if not calling_code:
        return "N/A"

    return f"+{calling_code}{fake.random_int(min=100000000, max=999999999)}"


def normalize_phone_number(raw_phone: str, country_code: str) -> str:
    calling_code = get_calling_code(country_code)
    phone_without_extension = re.split(r"(?:ext\.?|x|#)", raw_phone, maxsplit=1, flags=re.I)[0]
    digits = ascii_digits(phone_without_extension)

    if not digits:
        return "N/A"

    if digits.startswith("00"):
        digits = digits[2:]

    if not calling_code:
        return f"+{digits}"

    if digits.startswith(calling_code):
        national_number = digits[len(calling_code) :].lstrip("0")
        return f"+{calling_code}{national_number}"

    national_number = digits.lstrip("0")
    return f"+{calling_code}{national_number}"


def get_calling_code(country_code: str) -> str | None:
    phone_country_code = phonenumbers.country_code_for_region(country_code)
    if phone_country_code:
        return str(phone_country_code)

    return CALLING_CODE_BY_COUNTRY.get(country_code)


def ascii_digits(value: str) -> str:
    digits = []
    for character in value:
        try:
            digits.append(str(unicodedata.digit(character)))
        except (TypeError, ValueError):
            continue

    return "".join(digits)


def generate_fake_ssn(fake: Faker) -> str:
    area = fake.random_int(min=900, max=999)
    group = fake.random_int(min=1, max=99)
    serial = fake.random_int(min=1, max=9999)
    return f"{area:03d}-{group:02d}-{serial:04d}"


def safe_provider_value(fake: Faker, *provider_names: str) -> str:
    for provider_name in provider_names:
        provider = getattr(fake, provider_name, None)
        if provider is None:
            continue

        try:
            value = provider()
        except Exception:
            continue

        cleaned = single_line(str(value))
        if cleaned:
            return cleaned

    return "N/A"


def single_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def format_fake_address(fake_address: FakeAddress) -> str:
    country = fake_address.country
    fallback_note = ""
    if country.uses_fallback:
        fallback_note = "\n\nNote: Exact local address style is unavailable, so this uses a global style."

    neighborhood_line = ""
    if fake_address.neighborhood:
        neighborhood_line = f"- Neighborhood: {monospace(fake_address.neighborhood)}\n"

    ssn_line = ""
    if fake_address.ssn:
        ssn_line = f"- SSN (Random): {monospace(fake_address.ssn)}\n"

    return (
        f"{escape(country.name)} Address\n"
        "------------------------------\n"
        f"- Name: {monospace(fake_address.name)}\n"
        f"- Street: {monospace(fake_address.street)}\n"
        f"{neighborhood_line}"
        f"- City: {monospace(fake_address.city)}\n"
        f"- State: {monospace(fake_address.state)}\n"
        f"- Postal Code: {monospace(fake_address.postal_code)}\n"
        f"- Phone: {monospace(fake_address.phone)}\n"
        f"{ssn_line}"
        f"- Country: {monospace(country.name)}\n"
        "------------------------------"
        f"{fallback_note}"
    )


def format_fake_iban(fake_iban: FakeIban) -> str:
    return (
        f"{escape(fake_iban.country.name)} Random IBAN\n"
        "------------------------------\n"
        f"- IBAN (Random): {monospace(fake_iban.iban)}\n"
        f"- Country: {monospace(fake_iban.country.name)}\n"
        "------------------------------"
    )


def monospace(value: str) -> str:
    return f"<code>{escape(value)}</code>"

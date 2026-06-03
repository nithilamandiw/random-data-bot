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
    "SG": "en_GB",
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
    "AE": [
        {"state": "Dubai", "city": "Dubai", "postal_code": "N/A"},
        {"state": "Abu Dhabi", "city": "Abu Dhabi", "postal_code": "N/A"},
        {"state": "Sharjah", "city": "Sharjah", "postal_code": "N/A"},
        {"state": "Ajman", "city": "Ajman", "postal_code": "N/A"},
        {"state": "Ras Al Khaimah", "city": "Ras Al Khaimah", "postal_code": "N/A"},
        {"state": "Fujairah", "city": "Fujairah", "postal_code": "N/A"},
    ],
    "AU": [
        {"state": "New South Wales", "city": "Sydney", "postal_code": "2000"},
        {"state": "Victoria", "city": "Melbourne", "postal_code": "3000"},
        {"state": "Queensland", "city": "Brisbane", "postal_code": "4000"},
        {"state": "Western Australia", "city": "Perth", "postal_code": "6000"},
        {"state": "South Australia", "city": "Adelaide", "postal_code": "5000"},
        {"state": "Tasmania", "city": "Hobart", "postal_code": "7000"},
        {"state": "Northern Territory", "city": "Darwin", "postal_code": "0800"},
        {"state": "Australian Capital Territory", "city": "Canberra", "postal_code": "2600"},
        {"state": "Queensland", "city": "Gold Coast", "postal_code": "4217"},
        {"state": "New South Wales", "city": "Newcastle", "postal_code": "2300"},
    ],
    "AR": [
        {"state": "Ciudad Autónoma de Buenos Aires", "city": "Buenos Aires", "postal_code": "C1001"},
        {"state": "Córdoba", "city": "Córdoba", "postal_code": "X5000"},
        {"state": "Santa Fe", "city": "Rosario", "postal_code": "S2000"},
        {"state": "Mendoza", "city": "Mendoza", "postal_code": "M5500"},
        {"state": "Buenos Aires", "city": "La Plata", "postal_code": "B1900"},
        {"state": "Buenos Aires", "city": "Mar del Plata", "postal_code": "B7600"},
    ],
    "BR": [
        {"state": "São Paulo", "city": "São Paulo", "postal_code": "01000-000"},
        {"state": "Rio de Janeiro", "city": "Rio de Janeiro", "postal_code": "20000-000"},
        {"state": "Distrito Federal", "city": "Brasília", "postal_code": "70000-000"},
        {"state": "Bahia", "city": "Salvador", "postal_code": "40000-000"},
        {"state": "Minas Gerais", "city": "Belo Horizonte", "postal_code": "30000-000"},
        {"state": "Paraná", "city": "Curitiba", "postal_code": "80000-000"},
        {"state": "Rio Grande do Sul", "city": "Porto Alegre", "postal_code": "90000-000"},
        {"state": "Pernambuco", "city": "Recife", "postal_code": "50000-000"},
        {"state": "Ceará", "city": "Fortaleza", "postal_code": "60000-000"},
        {"state": "Amazonas", "city": "Manaus", "postal_code": "69000-000"},
    ],
    "CA": [
        {"state": "Ontario", "city": "Toronto", "postal_code": "M5H 2N2"},
        {"state": "British Columbia", "city": "Vancouver", "postal_code": "V6B 1A1"},
        {"state": "Quebec", "city": "Montreal", "postal_code": "H3B 1A1"},
        {"state": "Alberta", "city": "Calgary", "postal_code": "T2P 1J9"},
        {"state": "Ontario", "city": "Ottawa", "postal_code": "K1P 1J1"},
        {"state": "Alberta", "city": "Edmonton", "postal_code": "T5J 0N3"},
        {"state": "Manitoba", "city": "Winnipeg", "postal_code": "R3C 0V8"},
        {"state": "Quebec", "city": "Quebec City", "postal_code": "G1R 4S9"},
        {"state": "Nova Scotia", "city": "Halifax", "postal_code": "B3J 3K5"},
        {"state": "British Columbia", "city": "Victoria", "postal_code": "V8W 1P6"},
    ],
    "CN": [
        {"state": "Beijing", "city": "Beijing", "postal_code": "100000"},
        {"state": "Shanghai", "city": "Shanghai", "postal_code": "200000"},
        {"state": "Guangdong", "city": "Guangzhou", "postal_code": "510000"},
        {"state": "Guangdong", "city": "Shenzhen", "postal_code": "518000"},
        {"state": "Sichuan", "city": "Chengdu", "postal_code": "610000"},
        {"state": "Zhejiang", "city": "Hangzhou", "postal_code": "310000"},
        {"state": "Jiangsu", "city": "Nanjing", "postal_code": "210000"},
        {"state": "Hubei", "city": "Wuhan", "postal_code": "430000"},
        {"state": "Shaanxi", "city": "Xi'an", "postal_code": "710000"},
        {"state": "Tianjin", "city": "Tianjin", "postal_code": "300000"},
    ],
    "IN": [
        {"state": "Maharashtra", "city": "Mumbai", "postal_code": "400001"},
        {"state": "Delhi", "city": "New Delhi", "postal_code": "110001"},
        {"state": "Karnataka", "city": "Bengaluru", "postal_code": "560001"},
        {"state": "Tamil Nadu", "city": "Chennai", "postal_code": "600001"},
        {"state": "West Bengal", "city": "Kolkata", "postal_code": "700001"},
        {"state": "Telangana", "city": "Hyderabad", "postal_code": "500001"},
        {"state": "Maharashtra", "city": "Pune", "postal_code": "411001"},
        {"state": "Gujarat", "city": "Ahmedabad", "postal_code": "380001"},
        {"state": "Rajasthan", "city": "Jaipur", "postal_code": "302001"},
        {"state": "Uttar Pradesh", "city": "Lucknow", "postal_code": "226001"},
    ],
    "JP": [
        {"state": "Tokyo", "city": "Tokyo", "postal_code": "100-0001"},
        {"state": "Osaka", "city": "Osaka", "postal_code": "530-0001"},
        {"state": "Kyoto", "city": "Kyoto", "postal_code": "600-0001"},
        {"state": "Aichi", "city": "Nagoya", "postal_code": "450-0001"},
        {"state": "Fukuoka", "city": "Fukuoka", "postal_code": "810-0001"},
        {"state": "Hokkaido", "city": "Sapporo", "postal_code": "060-0001"},
        {"state": "Kanagawa", "city": "Yokohama", "postal_code": "220-0001"},
        {"state": "Hyogo", "city": "Kobe", "postal_code": "650-0001"},
        {"state": "Hiroshima", "city": "Hiroshima", "postal_code": "730-0001"},
        {"state": "Miyagi", "city": "Sendai", "postal_code": "980-0001"},
    ],
    "SG": [
        {"state": "Central Region", "city": "Singapore", "postal_code": "018956"},
        {"state": "Central Region", "city": "Singapore", "postal_code": "238801"},
        {"state": "Central Region", "city": "Singapore", "postal_code": "049213"},
        {"state": "Central Region", "city": "Singapore", "postal_code": "179098"},
        {"state": "Central Region", "city": "Singapore", "postal_code": "189559"},
        {"state": "East Region", "city": "Singapore", "postal_code": "529536"},
        {"state": "North Region", "city": "Singapore", "postal_code": "738099"},
        {"state": "North-East Region", "city": "Singapore", "postal_code": "544886"},
        {"state": "West Region", "city": "Singapore", "postal_code": "609731"},
        {"state": "Central Region", "city": "Singapore", "postal_code": "307591"},
    ],
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
    "VN": [
        {"state": "Hà Nội", "city": "Hà Nội", "postal_code": "100000"},
        {"state": "Hồ Chí Minh", "city": "Ho Chi Minh City", "postal_code": "700000"},
        {"state": "Đà Nẵng", "city": "Da Nang", "postal_code": "550000"},
        {"state": "Hải Phòng", "city": "Hai Phong", "postal_code": "180000"},
        {"state": "Cần Thơ", "city": "Can Tho", "postal_code": "900000"},
        {"state": "Thừa Thiên Huế", "city": "Hue", "postal_code": "530000"},
    ],
    "MT": [
        {"state": "South Eastern Region", "city": "Valletta", "postal_code": "VLT 1111"},
        {"state": "Northern Harbour Region", "city": "Sliema", "postal_code": "SLM 1010"},
        {"state": "Northern Harbour Region", "city": "St Julian's", "postal_code": "STJ 1010"},
        {"state": "Northern Region", "city": "Mosta", "postal_code": "MST 9010"},
        {"state": "Northern Harbour Region", "city": "Birkirkara", "postal_code": "BKR 1000"},
        {"state": "Northern Region", "city": "Mdina", "postal_code": "MDN 1010"},
    ],
}

STREET_NAMES_BY_COUNTRY_AND_CITY = {
    "AE": {
        "Dubai": ["Sheikh Zayed Road", "Al Wasl Road", "Jumeirah Beach Road"],
        "Abu Dhabi": ["Corniche Road", "Sheikh Rashid Bin Saeed Street", "Hamdan Bin Mohammed Street"],
        "Sharjah": ["Al Wahda Street", "King Faisal Street", "Corniche Street"],
        "Ajman": ["Sheikh Khalifa Bin Zayed Street", "Sheikh Rashid Bin Humaid Street", "Corniche Road"],
        "Ras Al Khaimah": ["Al Muntasir Road", "Sheikh Mohammed Bin Salem Road", "Corniche Road"],
        "Fujairah": ["Hamad Bin Abdulla Road", "Sheikh Hamad Bin Abdullah Street", "Corniche Street"],
    },
    "AU": {
        "Sydney": ["George Street", "Pitt Street", "Oxford Street"],
        "Melbourne": ["Collins Street", "Swanston Street", "Bourke Street"],
        "Brisbane": ["Queen Street", "Adelaide Street", "Ann Street"],
        "Perth": ["St Georges Terrace", "Hay Street", "Murray Street"],
        "Adelaide": ["King William Street", "Rundle Street", "North Terrace"],
        "Hobart": ["Elizabeth Street", "Davey Street", "Macquarie Street"],
        "Darwin": ["Mitchell Street", "Smith Street", "Knuckey Street"],
        "Canberra": ["Northbourne Avenue", "London Circuit", "Constitution Avenue"],
        "Gold Coast": ["Cavill Avenue", "Gold Coast Highway", "Surfers Paradise Boulevard"],
        "Newcastle": ["Hunter Street", "King Street", "Darby Street"],
    },
    "AR": {
        "Buenos Aires": ["Avenida 9 de Julio", "Avenida Corrientes", "Avenida Santa Fe"],
        "Córdoba": ["Avenida Colón", "Avenida General Paz", "Bulevar Chacabuco"],
        "Rosario": ["Bulevar Oroño", "Calle Córdoba", "Avenida Pellegrini"],
        "Mendoza": ["Avenida San Martín", "Avenida Las Heras", "Avenida Arístides Villanueva"],
        "La Plata": ["Avenida 7", "Calle 12", "Avenida 13"],
        "Mar del Plata": ["Avenida Luro", "Avenida Colón", "Avenida Independencia"],
    },
    "BR": {
        "São Paulo": ["Avenida Paulista", "Rua Augusta", "Rua Oscar Freire"],
        "Rio de Janeiro": ["Avenida Atlântica", "Rua Visconde de Pirajá", "Avenida Rio Branco"],
        "Brasília": ["Eixo Monumental", "Via W3 Sul", "Setor Comercial Sul"],
        "Salvador": ["Avenida Sete de Setembro", "Rua Chile", "Avenida Tancredo Neves"],
        "Belo Horizonte": ["Avenida Afonso Pena", "Rua da Bahia", "Avenida do Contorno"],
        "Curitiba": ["Rua XV de Novembro", "Avenida Sete de Setembro", "Rua Marechal Deodoro"],
        "Porto Alegre": ["Avenida Borges de Medeiros", "Rua dos Andradas", "Avenida Ipiranga"],
        "Recife": ["Avenida Boa Viagem", "Rua do Bom Jesus", "Avenida Conde da Boa Vista"],
        "Fortaleza": ["Avenida Beira Mar", "Rua Senador Pompeu", "Avenida Santos Dumont"],
        "Manaus": ["Avenida Eduardo Ribeiro", "Rua Guilherme Moreira", "Avenida Djalma Batista"],
    },
    "CA": {
        "Toronto": ["Yonge Street", "Queen Street West", "Bay Street"],
        "Vancouver": ["Robson Street", "Granville Street", "West Georgia Street"],
        "Montreal": ["Rue Sainte-Catherine", "Boulevard Saint-Laurent", "Rue Sherbrooke"],
        "Calgary": ["Stephen Avenue", "17 Avenue SW", "Centre Street"],
        "Ottawa": ["Wellington Street", "Bank Street", "Elgin Street"],
        "Edmonton": ["Jasper Avenue", "Whyte Avenue", "109 Street NW"],
        "Winnipeg": ["Portage Avenue", "Main Street", "Broadway"],
        "Quebec City": ["Grande Allée", "Rue Saint-Jean", "Boulevard René-Lévesque"],
        "Halifax": ["Barrington Street", "Spring Garden Road", "Argyle Street"],
        "Victoria": ["Government Street", "Douglas Street", "Fort Street"],
    },
    "CN": {
        "Beijing": ["Chang'an Avenue", "Wangfujing Street", "Jianguomen Outer Street"],
        "Shanghai": ["Nanjing Road", "Huaihai Road", "Zhongshan Road"],
        "Guangzhou": ["Zhongshan Road", "Beijing Road", "Tianhe Road"],
        "Shenzhen": ["Shennan Avenue", "Huaqiang North Road", "Binhe Avenue"],
        "Chengdu": ["Renmin South Road", "Chunxi Road", "Shudu Avenue"],
        "Hangzhou": ["Yan'an Road", "Tiyuchang Road", "Qingchun Road"],
        "Nanjing": ["Zhongshan Road", "Hanzhong Road", "Beijing East Road"],
        "Wuhan": ["Jiefang Avenue", "Zhongshan Avenue", "Jianghan Road"],
        "Xi'an": ["Chang'an Road", "Jiefang Road", "East Street"],
        "Tianjin": ["Nanjing Road", "Heping Road", "Jiefang North Road"],
    },
    "DE": {
        "Berlin": ["Unter den Linden", "Friedrichstraße", "Kurfürstendamm"],
        "Munich": ["Leopoldstraße", "Maximilianstraße", "Sonnenstraße"],
        "Hamburg": ["Mönckebergstraße", "Reeperbahn", "Jungfernstieg"],
        "Cologne": ["Hohe Straße", "Schildergasse", "Aachener Straße"],
        "Frankfurt am Main": ["Zeil", "Kaiserstraße", "Berliner Straße"],
        "Stuttgart": ["Königstraße", "Theodor-Heuss-Straße", "Rotebühlstraße"],
        "Düsseldorf": ["Königsallee", "Schadowstraße", "Immermannstraße"],
        "Leipzig": ["Grimmaische Straße", "Karl-Liebknecht-Straße", "Petersstraße"],
        "Bremen": ["Obernstraße", "Am Wall", "Böttcherstraße"],
        "Hannover": ["Georgstraße", "Lister Meile", "Karmarschstraße"],
    },
    "FR": {
        "Paris": ["Rue de Rivoli", "Avenue de l'Opéra", "Boulevard Saint-Germain"],
        "Marseille": ["La Canebière", "Rue Paradis", "Avenue du Prado"],
        "Lyon": ["Rue de la République", "Cours Lafayette", "Avenue Jean Jaurès"],
        "Toulouse": ["Rue d'Alsace-Lorraine", "Allées Jean Jaurès", "Rue Saint-Rome"],
        "Nice": ["Promenade des Anglais", "Avenue Jean Médecin", "Rue Masséna"],
        "Nantes": ["Rue Crébillon", "Cours des 50 Otages", "Boulevard Guist'hau"],
        "Strasbourg": ["Grand'Rue", "Avenue des Vosges", "Rue des Grandes Arcades"],
        "Bordeaux": ["Rue Sainte-Catherine", "Cours de l'Intendance", "Quai des Chartrons"],
        "Montpellier": ["Rue de la Loge", "Boulevard du Jeu de Paume", "Avenue de Toulouse"],
        "Lille": ["Rue Nationale", "Rue Faidherbe", "Boulevard de la Liberté"],
    },
    "GB": {
        "London": ["Oxford Street", "Regent Street", "Baker Street"],
        "Manchester": ["Deansgate", "Market Street", "Oxford Road"],
        "Birmingham": ["New Street", "Corporation Street", "Broad Street"],
        "Edinburgh": ["Princes Street", "George Street", "Royal Mile"],
        "Glasgow": ["Buchanan Street", "Sauchiehall Street", "Argyle Street"],
        "Cardiff": ["Queen Street", "St Mary Street", "Castle Street"],
        "Belfast": ["Royal Avenue", "Donegall Place", "Great Victoria Street"],
        "Liverpool": ["Bold Street", "Dale Street", "Castle Street"],
        "Leeds": ["Briggate", "The Headrow", "Boar Lane"],
        "Bristol": ["Park Street", "Corn Street", "Broadmead"],
    },
    "IN": {
        "Mumbai": ["Marine Drive", "Mahatma Gandhi Road", "Linking Road"],
        "New Delhi": ["Janpath", "Rajpath", "Connaught Place"],
        "Bengaluru": ["Mahatma Gandhi Road", "Brigade Road", "Residency Road"],
        "Chennai": ["Anna Salai", "Mount Road", "Radhakrishnan Salai"],
        "Kolkata": ["Park Street", "Chowringhee Road", "Camac Street"],
        "Hyderabad": ["Banjara Hills Road", "Tank Bund Road", "Abids Road"],
        "Pune": ["Fergusson College Road", "Jangli Maharaj Road", "Laxmi Road"],
        "Ahmedabad": ["Ashram Road", "C. G. Road", "S. G. Highway"],
        "Jaipur": ["M. I. Road", "Johari Bazaar Road", "Tonk Road"],
        "Lucknow": ["Hazratganj Road", "Vidhan Sabha Marg", "Mahatma Gandhi Marg"],
    },
    "LK": {
        "Colombo": ["Galle Road", "R. A. De Mel Mawatha", "Bauddhaloka Mawatha"],
        "Gampaha": ["Colombo Road", "Ja Ela Road", "Yakkala Road"],
        "Kalutara": ["Galle Road", "Main Street", "Panadura Road"],
        "Negombo": ["Colombo Road", "Sea Street", "Lewis Place"],
        "Kandy": ["Dalada Veediya", "Peradeniya Road", "D. S. Senanayake Veediya"],
        "Matale": ["Kandy Road", "Main Street", "Trincomalee Street"],
        "Nuwara Eliya": ["Queen Elizabeth Drive", "Badulla Road", "Park Road"],
        "Galle": ["Wakwella Road", "Colombo Road", "Lighthouse Street"],
        "Matara": ["Anagarika Dharmapala Mawatha", "Beach Road", "Main Street"],
        "Hambantota": ["Tissa Road", "Main Street", "New Road"],
        "Jaffna": ["Hospital Road", "Kandy Road", "Stanley Road"],
        "Vavuniya": ["Kandy Road", "Station Road", "Horowpathana Road"],
        "Mannar": ["Main Street", "Talaimannar Road", "Hospital Road"],
        "Trincomalee": ["Dockyard Road", "Kandy Road", "Main Street"],
        "Batticaloa": ["Trinco Road", "Bar Road", "Central Road"],
        "Ampara": ["D. S. Senanayake Street", "Main Street", "Kandy Road"],
        "Kurunegala": ["Dambulla Road", "Colombo Road", "Negombo Road"],
        "Puttalam": ["Mannar Road", "Kurunegala Road", "Main Street"],
        "Chilaw": ["Colombo Road", "Puttalam Road", "Sea Street"],
        "Anuradhapura": ["Maithripala Senanayake Mawatha", "Harischandra Mawatha", "Stage 1 Road"],
        "Polonnaruwa": ["New Town Road", "Batticaloa Road", "Hospital Road"],
        "Badulla": ["Lower Street", "Bandarawela Road", "Passara Road"],
        "Bandarawela": ["Badulla Road", "Welimada Road", "Main Street"],
        "Monaragala": ["Wellawaya Road", "Pottuvil Road", "Main Street"],
        "Ratnapura": ["Main Street", "Colombo Road", "Bandaranaike Mawatha"],
        "Kegalle": ["Colombo Road", "Kandy Road", "Bulathkohupitiya Road"],
    },
    "JP": {
        "Tokyo": ["Marunouchi", "Ginza", "Shinjuku-dori"],
        "Osaka": ["Umeda", "Midosuji", "Dotonbori"],
        "Kyoto": ["Kawaramachi-dori", "Shijo-dori", "Karasuma-dori"],
        "Nagoya": ["Sakura-dori", "Hirokoji-dori", "Otsu-dori"],
        "Fukuoka": ["Watanabe-dori", "Meiji-dori", "Tenjin"],
        "Sapporo": ["Odori", "Ekimae-dori", "Tanukikoji"],
        "Yokohama": ["Minato Mirai", "Bashamichi", "Motomachi"],
        "Kobe": ["Sannomiya", "Flower Road", "Motomachi-dori"],
        "Hiroshima": ["Aioi-dori", "Heiwa Odori", "Hondori"],
        "Sendai": ["Aoba-dori", "Jozenji-dori", "Ichibancho"],
    },
    "MT": {
        "Valletta": ["Republic Street", "Merchants Street", "St Paul Street"],
        "Sliema": ["Tower Road", "The Strand", "Manuel Dimech Street"],
        "St Julian's": ["Triq Santu Wistin", "George Borg Olivier Street", "Spinola Road"],
        "Mosta": ["Constitution Street", "Main Street", "Eucharistic Congress Road"],
        "Birkirkara": ["Valley Road", "Naxxar Road", "Mannarino Road"],
        "Mdina": ["Villegaignon Street", "Mesquita Street", "Inguanez Street"],
    },
    "MX": {
        "Cuauhtémoc": ["Paseo de la Reforma", "Avenida Juárez", "Calle Madero"],
        "Guadalajara": ["Avenida Vallarta", "Avenida Chapultepec", "Calle Pedro Moreno"],
        "Monterrey": ["Avenida Constitución", "Avenida Pino Suárez", "Calle Padre Mier"],
        "Puebla": ["Avenida Juárez", "Boulevard 5 de Mayo", "Calle 16 de Septiembre"],
        "Mérida": ["Paseo de Montejo", "Calle 60", "Avenida Colón"],
        "Cancún": ["Avenida Tulum", "Avenida Cobá", "Boulevard Kukulcán"],
    },
    "US": {
        "New York": ["Broadway", "Fifth Avenue", "Madison Avenue"],
        "Los Angeles": ["Sunset Boulevard", "Wilshire Boulevard", "Hollywood Boulevard"],
        "Chicago": ["Michigan Avenue", "State Street", "Wacker Drive"],
        "Houston": ["Main Street", "Westheimer Road", "Fannin Street"],
        "Phoenix": ["Central Avenue", "Camelback Road", "Van Buren Street"],
        "Philadelphia": ["Market Street", "Broad Street", "Chestnut Street"],
        "San Antonio": ["Commerce Street", "Broadway", "Alamo Plaza"],
        "San Diego": ["Broadway", "University Avenue", "India Street"],
        "Dallas": ["Elm Street", "Main Street", "McKinney Avenue"],
        "Seattle": ["Pine Street", "First Avenue", "Yesler Way"],
    },
    "SG": {
        "Singapore": ["Orchard Road", "Shenton Way", "North Bridge Road"],
    },
    "VN": {
        "Hà Nội": ["Phố Huế", "Hàng Bài", "Tràng Tiền"],
        "Ho Chi Minh City": ["Nguyễn Huệ", "Lê Lợi", "Đồng Khởi"],
        "Da Nang": ["Bạch Đằng", "Nguyễn Văn Linh", "Trần Phú"],
        "Hai Phong": ["Trần Phú", "Lạch Tray", "Điện Biên Phủ"],
        "Can Tho": ["Đại lộ Hòa Bình", "Nguyễn Trãi", "30 Tháng 4"],
        "Hue": ["Lê Lợi", "Trần Hưng Đạo", "Nguyễn Huệ"],
    },
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
    uses_curated_street_name: bool = False


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
    has_curated_street_name = (
        city_details["city"] in STREET_NAMES_BY_COUNTRY_AND_CITY.get(country.code, {})
    )

    return FakeAddress(
        name=generate_name(country.code)[0],
        street=generate_curated_street(country.code, city_details, fake),
        city=city_details["city"],
        state=city_details["state"],
        postal_code=city_details["postal_code"],
        phone=generate_phone(country.code, fake),
        country=country,
        neighborhood=city_details.get("neighborhood"),
        ssn=generate_fake_ssn(fake) if country.code == "US" else None,
        uses_curated_street_name=has_curated_street_name,
    )


def generate_curated_street(
    country_code: str, city_details: dict[str, str], fake: Faker
) -> str:
    street_names_by_city = STREET_NAMES_BY_COUNTRY_AND_CITY.get(country_code, {})
    street_names = street_names_by_city.get(city_details["city"])

    if not street_names:
        return single_line(fake.street_address())

    street_name = fake.random_element(street_names)
    building_number = fake.random_int(min=1, max=250)

    if country_code == "BR":
        return f"{street_name}, {building_number}"

    if country_code in {"DE", "FR", "MT"}:
        return f"{building_number} {street_name}"

    if country_code == "JP":
        block = fake.random_int(min=1, max=9)
        lot = fake.random_int(min=1, max=30)
        return f"{block}-{lot} {street_name}"

    if country_code == "MX":
        return f"{street_name} {building_number}"

    if country_code == "VN":
        return f"{building_number} {street_name}"

    return f"{building_number} {street_name}"


def generate_sri_lankan_address(country: ResolvedCountry) -> FakeAddress:
    fake = Faker()
    city_details = fake.random_element(SRI_LANKAN_CITY_DETAILS)
    street_details = {
        "city": city_details["city"],
        "state": city_details["province"],
        "postal_code": city_details["postal_code"],
    }

    return FakeAddress(
        name=generate_sri_lankan_name(),
        street=generate_curated_street(country.code, street_details, fake),
        city=city_details["city"],
        state=city_details["province"],
        postal_code=city_details["postal_code"],
        phone=generate_sri_lankan_phone(),
        country=country,
        uses_curated_street_name=True,
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
    elif fake_address.uses_curated_street_name:
        fallback_note = "\n\nNote: Street name is curated; house number is random and not delivery-verified."

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

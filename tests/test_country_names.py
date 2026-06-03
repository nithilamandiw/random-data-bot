import unittest
import re

import phonenumbers
import pycountry

from random_name_bot.country_names import (
    ADDRESS_DETAILS_BY_COUNTRY,
    EU_IBAN_SPECS,
    SRI_LANKAN_CITY_DETAILS,
    calculate_iban_check_digits,
    format_fake_address,
    format_fake_iban,
    generate_fake_address,
    generate_fake_iban,
    generate_name,
    get_calling_code,
    resolve_country,
)


class CountryNameTests(unittest.TestCase):
    def test_resolves_standard_country_code(self):
        country = resolve_country("us")

        self.assertEqual(country.code, "US")
        self.assertEqual(country.locale, "en_US")

    def test_resolves_alias(self):
        country = resolve_country("uk")

        self.assertEqual(country.code, "GB")
        self.assertEqual(country.locale, "en_GB")

    def test_rejects_invalid_country_code(self):
        with self.assertRaises(ValueError):
            resolve_country("xx")

    def test_generates_sri_lankan_name(self):
        name, country = generate_name("lk")

        self.assertEqual(country.code, "LK")
        self.assertIn(" ", name)

    def test_generates_fake_address(self):
        address = generate_fake_address("gb")

        self.assertEqual(address.country.code, "GB")
        self.assertTrue(address.name)
        self.assertTrue(address.street)
        self.assertTrue(address.city)
        self.assertTrue(address.postal_code)
        self.assertTrue(address.phone)

    def test_formats_fake_address(self):
        address = generate_fake_address("lk")
        formatted = format_fake_address(address)

        self.assertIn("Sri Lanka Address", formatted)
        self.assertIn("- Name:", formatted)
        self.assertIn("- Street:", formatted)
        self.assertIn("- Postal Code:", formatted)
        self.assertIn("- Phone:", formatted)

    def test_sri_lankan_city_matches_postal_code(self):
        postal_code_by_city = {
            details["city"]: details["postal_code"] for details in SRI_LANKAN_CITY_DETAILS
        }

        for _ in range(100):
            address = generate_fake_address("lk")
            self.assertEqual(address.postal_code, postal_code_by_city[address.city])

    def test_curated_country_city_matches_postal_code(self):
        for country_code in ("mx", "us", "gb", "de", "fr"):
            postal_code_by_city = {
                details["city"]: details["postal_code"]
                for details in ADDRESS_DETAILS_BY_COUNTRY[country_code.upper()]
            }

            for _ in range(100):
                address = generate_fake_address(country_code)
                self.assertEqual(address.postal_code, postal_code_by_city[address.city])

    def test_mexico_address_includes_matching_neighborhood(self):
        details_by_neighborhood = {
            details["neighborhood"]: details for details in ADDRESS_DETAILS_BY_COUNTRY["MX"]
        }

        for _ in range(100):
            address = generate_fake_address("mx")
            self.assertIsNotNone(address.neighborhood)
            expected = details_by_neighborhood[address.neighborhood]
            self.assertEqual(address.city, expected["city"])
            self.assertEqual(address.state, expected["state"])
            self.assertEqual(address.postal_code, expected["postal_code"])

    def test_us_address_includes_fake_invalid_ssn(self):
        address = generate_fake_address("us")

        self.assertIsNotNone(address.ssn)
        self.assertRegex(address.ssn, r"^9\d{2}-\d{2}-\d{4}$")

    def test_non_us_address_does_not_include_ssn(self):
        self.assertIsNone(generate_fake_address("lk").ssn)
        self.assertIsNone(generate_fake_address("mx").ssn)

    def test_phone_numbers_are_compact_with_country_code(self):
        expected_prefixes = {
            "fr": "+33",
            "mx": "+52",
            "lk": "+94",
            "us": "+1",
            "pl": "+48",
            "mt": "+356",
        }

        for country_code, prefix in expected_prefixes.items():
            for _ in range(25):
                phone = generate_fake_address(country_code).phone
                self.assertTrue(phone.startswith(prefix), phone)
                self.assertRegex(phone, r"^\+[0-9]+$")
                self.assertFalse(phone.startswith("+330"), phone)
                self.assertLessEqual(len(phone), 16, phone)

    def test_all_supported_country_phones_are_compact_international_numbers(self):
        for country_code in ("de", "fr", "gb", "lk", "mt", "mx", "pl", "us"):
            for _ in range(10):
                phone = generate_fake_address(country_code).phone
                self.assertRegex(phone, r"^\+[0-9]+$", f"{country_code}: {phone}")

    def test_calling_code_lookup_covers_phone_metadata_regions(self):
        missing = []
        for country in pycountry.countries:
            country_code = country.alpha_2
            if phonenumbers.country_code_for_region(country_code):
                if not get_calling_code(country_code):
                    missing.append(country_code)

        self.assertEqual([], missing)

    def test_all_phone_metadata_regions_generate_compact_phone_numbers(self):
        bad = []
        for country in pycountry.countries:
            country_code = country.alpha_2
            if not phonenumbers.country_code_for_region(country_code):
                continue

            phone = generate_fake_address(country_code).phone
            if not re.match(r"^\+[0-9]{4,15}$", phone):
                bad.append((country_code, phone))

        self.assertEqual([], bad)

    def test_generates_fake_eu_iban(self):
        fake_iban = generate_fake_iban("de")

        self.assertEqual(fake_iban.country.code, "DE")
        self.assertTrue(fake_iban.iban.startswith("DE"))
        self.assertFalse(fake_iban.iban.startswith("DE00"))
        self.assertEqual(len(fake_iban.iban), iban_length("DE"))
        self.assertNotIn(" ", fake_iban.iban)

        check_digits = fake_iban.iban[2:4]
        bban = fake_iban.iban[4:]
        self.assertNotEqual(check_digits, calculate_iban_check_digits("DE", bban))

    def test_fake_iban_rejects_non_eu_country(self):
        with self.assertRaises(ValueError):
            generate_fake_iban("us")

    def test_formats_fake_iban(self):
        formatted = format_fake_iban(generate_fake_iban("fr"))

        self.assertIn("France Fake IBAN", formatted)
        self.assertIn("- IBAN (Fake):", formatted)
        self.assertNotIn("intentionally invalid", formatted)


def iban_length(country_code):
    return 4 + sum(
        int(length) for length in re.findall(r"(\d+)[anc]", EU_IBAN_SPECS[country_code])
    )


if __name__ == "__main__":
    unittest.main()

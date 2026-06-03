import unittest

from random_data_bot.bot import (
    MODE_ADDRESS,
    MODE_IBAN,
    MODE_NAME,
    build_fake_address_response,
    build_fake_iban_response,
    parse_mode_selection,
)


class BotTests(unittest.TestCase):
    def test_builds_fake_address_response_with_regenerate_button_only(self):
        message_text, keyboard = build_fake_address_response("us")
        keyboard_data = keyboard.to_dict()

        self.assertIn("United States Address", message_text)
        self.assertIn("- Phone:", message_text)
        self.assertNotIn("copy_text", str(keyboard_data))
        self.assertIn("Regenerate", str(keyboard_data))

    def test_builds_fake_iban_response_with_copy_button(self):
        message_text, keyboard = build_fake_iban_response("de")
        keyboard_data = keyboard.to_dict()

        self.assertIn("Germany Random IBAN", message_text)
        self.assertIn("- IBAN (Random):", message_text)
        self.assertIn("Copy Random IBAN", str(keyboard_data))
        self.assertIn("Regenerate IBAN", str(keyboard_data))

    def test_parses_menu_modes(self):
        self.assertEqual(parse_mode_selection("Address"), MODE_ADDRESS)
        self.assertEqual(parse_mode_selection("Name"), MODE_NAME)
        self.assertEqual(parse_mode_selection("IBAN"), MODE_IBAN)
        self.assertIsNone(parse_mode_selection("us"))


if __name__ == "__main__":
    unittest.main()

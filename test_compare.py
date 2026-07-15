import random
import unittest

from compare import BASE, acceptance_check, compare, mutate, parse_time


class AcceptanceTests(unittest.TestCase):
    def check(self, text, reason=None):
        self.assertEqual(acceptance_check(text.encode("utf-8")), reason)

    def test_accepted_formats(self):
        self.assertIsNone(acceptance_check(BASE))
        self.check('\ufeffSTAFF;Shift Date;START TIME;End Time;PUBLIC_HOLIDAY\r\n'
                   '\r\n"Renée; ""Ren"" Dubois";1/7/2026;11:00 PM;1:00 AM;YES\r\n')
        self.check('employee name\tdate\tstart\tend\n'
                   '"Mia\tChen"\t2026-06-30\t00:00\t12:00 PM\n\n')
        for holiday in ("true", "TRUE", "yes", "1", "false", "NO", "0", ""):
            with self.subTest(holiday=holiday):
                self.check("employee,date,start,end,holiday\n"
                           f"Liam Walsh,2026-07-01,09:00,17:00,{holiday}\n")

    def test_rejected_files(self):
        header = "employee,date,start,end\n"
        valid = "Liam Walsh,2026-07-01,09:00,17:00\n"
        cases = [
            ("", "empty_file"),
            (header, "empty_data"),
            ("employee|date|start|end\n" + valid, "header_delimiter"),
            ("employee,date,start\nLiam Walsh,2026-07-01,09:00\n", "missing_header"),
            ("employee,date,start,end,notes\n" + valid.rstrip() + ",x\n", "unknown_header"),
            ("employee,date,start,end,staff\n" + valid.rstrip() + ",Liam\n", "duplicate_header"),
            (header + "Liam Walsh;2026-07-01;09:00;17:00\n", "row_width"),
            (header + valid.rstrip() + ",extra\n", "row_width"),
            (header + valid.replace("Liam Walsh", " "), "empty_employee"),
            (header + valid.replace("2026-07-01", "31/6/2026"), "date"),
            (header + valid.replace("2026-07-01", "2026-7-1"), "date"),
            (header + valid.replace("09:00", "24:00"), "time"),
            (header + valid.replace("09:00", "9:60 AM"), "time"),
            (header + valid.replace("09:00", "0:00 AM"), "time"),
            (header + valid.replace("17:00", "9:00 AM"), "zero_duration"),
            ("employee,date,start,end,holiday\n" + valid.rstrip() + ",maybe\n", "holiday"),
            (header + valid.replace("Liam", "\ufeffLiam"), "interior_bom"),
            (header + valid.replace("Liam", "Li\ram"), "bare_cr"),
            (header + '"' + valid, "invalid_csv"),
            (header + valid.replace("Liam Walsh", '"Liam\nWalsh"'), "quoted_newline"),
        ]
        for text, reason in cases:
            with self.subTest(reason=reason, text=text):
                self.check(text, reason)
        self.assertEqual(acceptance_check(b"\xff"), "utf8")

    def test_noon_and_midnight(self):
        self.assertEqual(parse_time("12:00 AM"), 0)
        self.assertEqual(parse_time("12:00 PM"), 12 * 60)

    def test_comparison_is_reproducible(self):
        self.assertEqual(compare(30, 7), compare(30, 7))
        with self.assertRaisesRegex(ValueError, "budget must be positive"):
            compare(0, 7)

    def test_mutation_includes_all_three_edit_types(self):
        class FixedRandom:
            def __init__(self, operation):
                self.operation = operation

            def randint(self, low, high):
                return 1

            def choice(self, options):
                return self.operation

            def randrange(self, stop):
                return 0

        self.assertEqual(mutate(FixedRandom("overwrite")), b"\0" + BASE[1:])
        self.assertEqual(mutate(FixedRandom("insert")), b"\0" + BASE)
        self.assertEqual(mutate(FixedRandom("delete")), BASE[1:])
        self.assertEqual(mutate(random.Random(7)), mutate(random.Random(7)))


if __name__ == "__main__":
    unittest.main()

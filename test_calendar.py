#!/usr/bin/env python
import unittest
from datetime import date, timedelta
from calendar import get_date, to_ints, true_for_all, true_for_some, get_dates, true_for_weeks, atleast, splice


class TestGetDate(unittest.TestCase):
    def test_get_date(self):
        self.assertEqual(type(get_date('2013-11-03')), date)


class TestGetDates(unittest.TestCase):
    def test_get_dates(self):
        first_date = get_date('2013-11-03')
        arr = [1, 0, 0, 1]
        res = get_dates(arr, first_date)

        self.assertEqual(res[0], first_date)
        self.assertEqual(res[1], first_date + timedelta(days=3))


class TestToInts(unittest.TestCase):
    def test_to_ints(self):
        self.assertEqual(to_ints(list('101')), [1, 0, 1])


class TestTrueForWeeks(unittest.TestCase):
    def test_true_for_weeks_on_monday(self):
        d = get_date('2013-11-04')
        days = [1, 0, 0, 1, 0, 0, 0, 1]
        overlaps = true_for_all(days)

        self.assertEqual(true_for_weeks(days, d), days)

    def test_true_for_weeks_on_monday_half(self):
        d = get_date('2013-11-04')
        days = [1, 0, 0]
        overlaps = true_for_all(days)

        self.assertEqual(true_for_weeks(days, d), [1, 0, 0, 0, 0, 0, 0])

    def test_true_for_weeks_on_friday(self):
        d = get_date('2013-11-08')
        days = [1, 0, 0, 1, 0, 0, 0, 1]
        overlaps = true_for_all(days)

        self.assertEqual(true_for_weeks(days, d), [0, 0, 0, 1, 0, 0, 1, 0])


class TestTrueForAll(unittest.TestCase):
    def test_true_for_all_full(self):
        arr = [1, 0, 0, 0, 0, 0, 1,
               1, 1, 0, 0, 1, 1, 0]

        self.assertEqual(true_for_all(arr), [1, 0, 0, 0, 0, 0, 0,
                                             1, 0, 0, 0, 0, 0, 0])

    def test_true_for_all_not_full(self):
        arr = [1, 0, 0, 0, 0, 0, 1,
               1, 1]

        self.assertEqual(true_for_all(arr), [1, 0, 0, 0, 0, 0, 1, 1, 0])


class TestTrueForSome(unittest.TestCase):
    def test_true_for_some(self):
        days = [1, 0, 1, 0, 0, 0, 0, 1, 1]

        self.assertEqual(true_for_some(days), [0, 0, 0, 0, 0, 0, 0, 0, 1])


class TestAtleast(unittest.TestCase):
    def test_atleast(self):
        self.assertEqual(atleast([4], 3), [4, 0, 0])

    def test_atleast_value(self):
        self.assertEqual(atleast([4], 3, 1), [4, 1, 1])


class TestSplice(unittest.TestCase):
    def test_single(self):
        self.assertEqual(splice([1, 2], 1), [[1], [2]])

    def test_multiple(self):
        self.assertEqual(splice([1, 2, 3, 4], 2), [[1, 2], [3, 4]])

    def test_shorter(self):
        self.assertEqual(splice([1, 0], 5), [[1, 0]])

if __name__ == '__main__':
        unittest.main()

"""
Automated tests for the functions module of VBOA

Written by DEIMOS Space S.L.

module vboa
"""
# Import python utilities
import unittest
import traceback
import sys

# Import the VBOA functions module
import vboa.tests.functions as functions_vboa

class TestVboaFunctions(unittest.TestCase):

    def test_assert_equal_list_dictionaries_items_no_list(self):

        test_success = False
        try:
            functions_vboa.assert_equal_list_dictionaries("not_a_list", [])
        except AssertionError:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success

    def test_assert_equal_list_dictionaries_expected_items_no_list(self):

        test_success = False
        try:
            functions_vboa.assert_equal_list_dictionaries([], "not_a_list")
        except AssertionError:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success

    def test_assert_equal_list_dictionaries_lists_same_length(self):

        functions_vboa.assert_equal_list_dictionaries([], [])

    def test_assert_equal_list_dictionaries_lists_different_length(self):

        test_success = False
        try:
            functions_vboa.assert_equal_list_dictionaries([], [{"key": "value"}])
        except AssertionError:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success

    def test_assert_equal_list_dictionaries_expected_items_no_id(self):
        
        test_success = False
        try:
            functions_vboa.assert_equal_list_dictionaries([{"key": "value"}], [{"key": "value"}])
        except AssertionError:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success

    def test_assert_equal_list_dictionaries_items_no_dict(self):
        
        test_success = False
        try:
            functions_vboa.assert_equal_list_dictionaries(["not_a_dict"], [{"id": "value"}])
        except AssertionError:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success
        
    def test_assert_equal_list_dictionaries_items_no_id(self):
        
        test_success = False
        try:
            functions_vboa.assert_equal_list_dictionaries([{"key": "value"}], [{"id": "value"}])
        except AssertionError:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success

    def test_assert_equal_list_dictionaries_items_id_not_matching(self):
        
        test_success = False
        try:
            functions_vboa.assert_equal_list_dictionaries([{"id": "value_not_matching"}], [{"id": "value"}])
        except AssertionError:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success

    def test_assert_equal_list_dictionaries_items_id_matching_content_different(self):
        
        test_success = False
        try:
            functions_vboa.assert_equal_list_dictionaries([{"id": "value", "key": "value_not_matching"}], [{"id": "value"}])
        except AssertionError:
            traceback.print_exc(file=sys.stdout)
            test_success = True
        # end try

        assert test_success

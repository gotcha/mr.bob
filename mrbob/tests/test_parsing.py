# -*- coding: utf-8 -*-
import os
import unittest

import six


class parse_configTest(unittest.TestCase):

    def call_FUT(self, configname='example.ini'):
        import mrbob
        from mrbob.parsing import parse_config

        f = os.path.abspath(os.path.join(os.path.dirname(mrbob.__file__),
                          'tests', configname))
        return parse_config(f)

    def test_parse_variable(self):
        c = self.call_FUT()
        self.assertEqual(c['variables']['name'], 'Bob')

    def test_parse_nested_variable(self):
        c = self.call_FUT()
        self.assertEqual(c['variables']['host.ip_addr'], '10.0.10.120')

    def test_parse_2nd_level_nested_variable(self):
        c = self.call_FUT()
        self.assertEqual(c['variables']['webserver.foo.bar'], 'barf')

    def test_parse_nested_variable_out_of_order(self):
        c = self.call_FUT('example2.ini')
        self.assertEqual(c['variables']['webserver.foo.bar'], 'barf2')
        self.assertEqual(c['variables']['webserver.ip_addr'], '127.0.0.3')

    def test_parse_deeply_nested_variables(self):
        c = self.call_FUT('example5.ini')
        expected_config = {
            'mr.bob': {},
            'variables': {'a.b.c.d': 'foo', 'a.b.c.f': 'bar', 'name': 'Bob'},
            'questions': {'a': {'b': {'c': {'d': 'foo', 'f': 'bar'}}}, 'name': 'Bob'},
            'template': {},
            'questions_order': [],
        }
        self.assertEqual(c, expected_config)

    def test_overwrite_dict_with_value(self):
        """ providing a value for a key that already contains a
        dictionary raises a ConfigurationError """
        from ..configurator import ConfigurationError
        self.assertRaises(ConfigurationError, self.call_FUT, 'example3.ini')

    def test_overwrite_value_with_dict(self):
        """ providing a dict for a key that already contains a
        string raises a ConfigurationError """
        from ..configurator import ConfigurationError
        self.assertRaises(ConfigurationError, self.call_FUT, 'example4.ini')

    def test_parse_config_utf8(self):
        from ..parsing import pretty_format_config
        c = self.call_FUT('example6.ini')
        output_variables = pretty_format_config(c['variables'])
        output_questions = pretty_format_config(c['questions'])
        if six.PY3:  # pragma: no cover
            expected_output = [
                'name = Čebula',
            ]
        else:  # pragma: no cover
            expected_output = [
                'name = Čebula'.decode('utf-8'),
            ]

        self.assertEqual(output_variables, expected_output)
        self.assertEqual(output_questions, expected_output)

    def test_parse_config(self):
        from ..parsing import pretty_format_config
        c = self.call_FUT()
        output = pretty_format_config(c['variables'])
        expected_output = [
            'host.ip_addr = 10.0.10.120',
            'name = Bob',
            'webserver.foo.bar = barf',
            'webserver.fqdn = mrbob.10.0.10.120.xip.io',
            'webserver.ip_addr = 127.0.0.2',
        ]
        self.assertEqual(output, expected_output)


class update_configTest(unittest.TestCase):

    def call_FUT(self, config, newconfig):
        from ..parsing import update_config
        return update_config(config, newconfig)

    def test_update_config_override_one_option(self):
        config = {
            'foo': 'bar',
            'foo1': 'mar'
        }
        new_config = {
            'foo1': 'bar'
        }
        self.call_FUT(config, new_config)

        expected_config = {
            'foo': 'bar',
            'foo1': 'bar'
        }

        self.assertEqual(config, expected_config)

    def test_update_config_override_nested(self):
        config = {
            'foo': 'bar',
            'bar': {
                'foo': 'bar',
                'foo1': 'foo',
            }
        }
        new_config = {
            'foo1': 'bar',
            'bar': {
                'foo1': 'moo',
                'moo': 'moo',
            }
        }
        self.call_FUT(config, new_config)

        expected_config = {
            'foo': 'bar',
            'foo1': 'bar',
            'bar': {
                'foo': 'bar',
                'foo1': 'moo',
                'moo': 'moo',
            }
        }

        self.assertEqual(config, expected_config)

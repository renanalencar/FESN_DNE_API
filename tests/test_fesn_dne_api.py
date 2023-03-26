#!/usr/bin/env python

"""Tests for `fesn_dne_api` package."""


import unittest
from click.testing import CliRunner

from fesn_dne_api import fesn_dne_api
from fesn_dne_api import cli


class TestFesn_dne_api(unittest.TestCase):
    """Tests for `fesn_dne_api` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'fesn_dne_api.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from ndcn.stroke.testing import NDCN_STROKE_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that ndcn.stroke is properly installed."""

    layer = NDCN_STROKE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ndcn.stroke is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('ndcn.stroke'))

    def test_browserlayer(self):
        """Test that INdcnStrokeLayer is registered."""
        from ndcn.stroke.interfaces import INdcnStrokeLayer
        from plone.browserlayer import utils
        self.assertIn(INdcnStrokeLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = NDCN_STROKE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['ndcn.stroke'])

    def test_product_uninstalled(self):
        """Test if ndcn.stroke is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled('ndcn.stroke'))

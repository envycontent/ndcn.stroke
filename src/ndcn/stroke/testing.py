# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import ndcn.stroke


class NdcnStrokeLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=ndcn.stroke)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ndcn.stroke:default')


NDCN_STROKE_FIXTURE = NdcnStrokeLayer()


NDCN_STROKE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(NDCN_STROKE_FIXTURE,),
    name='NdcnStrokeLayer:IntegrationTesting'
)


NDCN_STROKE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(NDCN_STROKE_FIXTURE,),
    name='NdcnStrokeLayer:FunctionalTesting'
)


NDCN_STROKE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        NDCN_STROKE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='NdcnStrokeLayer:AcceptanceTesting'
)

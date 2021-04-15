# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import psycopg2
from odoo_test_helper import FakeModelLoader

from odoo import exceptions, fields, models
from odoo.tools import mute_logger

from odoo.addons.base_rest.tests.common import RestServiceRegistryCase
from odoo.addons.base_url.tests.models_mixin import TestMixin
from odoo.addons.component.core import Component
from odoo.addons.shopinvader_rating_abstract.services.rating import (
    RatingAbstractService,
)

from .common import CommonRatingCase

# class FakeModel(models.Model, TestMixin):
#     _inherit = 'rating.rating'
#     _name = 'rating.abstract.test.model'
#     name = fields.Char()


class RatingCase(CommonRatingCase, RestServiceRegistryCase):
    # @classmethod
    # def setUpClass(cls):
    #     super().setUpClass()
    #     FakeModel._test_setup_model(cls.env)
    #
    # @classmethod
    # def tearDownClass(cls):
    #     FakeModel._test_teardown_model(cls.env)
    #     super().tearDownClass()

    def tearDown(self):
        super().tearDown()
        RestServiceRegistryCase._teardown_registry(self)

    def setUp(self):
        super().setUp()
        RestServiceRegistryCase._setup_registry(self)
        self.record = self.env["rating.rating"].create(self.params)

        with self.work_on_services(partner=self.partner1) as work:
            self.rate_service = work.component(usage="test_rating")

        def _mock_synchronize(self):
            return None

        self.record._patch_method("synchronize_rating", _mock_synchronize)
        self.addCleanup(self.record._revert_method, "synchronize_rating")

    def test_create_rating(self):
        class TestService(Component):
            _inherit = "shopinvader.abstract.rating.service"
            _name = "test.rating.service"
            _usage = "test_rating"
            _description = "test"
            _rating_model = "rating.abstract.test.model"

        self._build_services(TestService)

        # create rating as a logged user
        res = self.rate_service.dispatch("create", params=self.data.copy())
        self.assertTrue(res["created"])
        record = self.env["rating.rating"].search(
            [
                ("res_id", "=", self.product2.id),
                ("partner_id", "=", self.partner1.id),
                ("res_model", "=", "product.product"),
            ],
            limit=1,
        )
        self.assertEqual("Feedback text", record.feedback)
        # create rating as an Anonymous user
        with self.work_on_services(partner=None) as work:
            self.rate_service = work.component(usage="test_rating")

        with self.assertRaises(exceptions.UserError) as em:
            self.rate_service.dispatch("create", params=self.data.copy())
        self.assertEqual(
            "Must be authenticated to create a rating", em.exception.args[0]
        )

    # @mute_logger("odoo.sql_db")
    # def test_sql_constraint_range(self):
    #     data = self.data.copy()
    #     data["rating"] = 0
    #     with self.assertRaises(psycopg2.IntegrityError) as em:
    #         self.rate_service.dispatch("create", params=data)
    #     self.assertEqual(em.exception.pgerror.split('\"')[3], 'rating_rating_rating_range_shopinvader')
    #
    # @mute_logger("odoo.sql_db")
    # def test_sql_constraint_unique(self):
    #     self.rate_service.dispatch("create", params=self.data.copy())
    #     with self.assertRaises(psycopg2.IntegrityError) as em:
    #         self.rate_service.dispatch("create", params=self.data.copy())
    #     self.assertEqual(em.exception.pgerror.split('\"')[1], 'rating_rating_rating_unique')
    #
    # def test_delete_rating(self):
    #     res = self.rate_service.dispatch("delete", self.record.id)
    #     self.assertTrue(res["deleted"])
    #     self.assertFalse(self.record.active)
    #     # a partner cannot delete the rating of another
    #     with self.work_on_services(partner=self.partner2) as work:
    #         self.rate_service = work.component(usage="test_rating")
    #
    #     with self.assertRaises(exceptions.UserError) as em:
    #         self.rate_service.dispatch("delete", self.record.id)
    #     self.assertEqual('The record does not exist or you cannot delete it', em.exception.args[0])
    #
    # def test_update(self):
    #     params = {"rating": 1, "feedback": "test"}
    #     res = self.rate_service.dispatch("update", self.record.id, params=params)
    #     self.assertTrue(res["updated"])
    #     self.assertEqual(1, self.record.rating)
    #     self.assertEqual("test", self.record.feedback)
    #     # a partner cannot update the rating of another
    #     with self.work_on_services(partner=self.partner2) as work:
    #         self.rate_service = work.component(usage="test_rating")
    #
    #     with self.assertRaises(exceptions.UserError) as em:
    #         self.rate_service.dispatch("update", self.record.id, params=params)
    #     self.assertEqual('The record does not exist or you cannot update it', em.exception.args[0])

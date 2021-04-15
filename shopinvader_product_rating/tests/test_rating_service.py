# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import psycopg2

from odoo import exceptions, fields
from odoo.tools import mute_logger

from .common import CommonRatingCase


class RatingCase(CommonRatingCase):
    def setUp(self):
        super().setUp()
        self.record = self.env["rating.rating"].create(self.params)
        with self.work_on_services(partner=self.partner1) as work:
            self.rate_service = work.component(usage="product_rating")

        def _mock_synchronize(self):
            return None

        self.record._patch_method("synchronize_rating", _mock_synchronize)
        self.addCleanup(self.record._revert_method, "synchronize_rating")

    def test_create_rating(self):
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
            self.rate_service = work.component(usage="product_rating")

        with self.assertRaises(exceptions.UserError) as em:
            self.rate_service.dispatch("create", params=self.data.copy())
        self.assertEqual(
            "Must be authenticated to create a rating", em.exception.args[0]
        )

    @mute_logger("odoo.sql_db")
    def test_sql_constraint_range(self):
        data = self.data.copy()
        data["rating"] = 0
        with self.assertRaises(psycopg2.IntegrityError) as em:
            self.rate_service.dispatch("create", params=data)
        self.assertEqual(
            em.exception.pgerror.split('"')[3], "rating_rating_rating_range_shopinvader"
        )

    @mute_logger("odoo.sql_db")
    def test_sql_constraint_unique(self):
        self.rate_service.dispatch("create", params=self.data.copy())
        with self.assertRaises(psycopg2.IntegrityError) as em:
            self.rate_service.dispatch("create", params=self.data.copy())
        self.assertEqual(
            em.exception.pgerror.split('"')[1], "rating_rating_rating_unique"
        )

    def test_delete_rating(self):
        res = self.rate_service.dispatch("delete", self.record.id)
        self.assertTrue(res["deleted"])
        self.assertFalse(self.record.active)
        # a partner cannot delete the rating of another
        with self.work_on_services(partner=self.partner2) as work:
            self.rate_service = work.component(usage="product_rating")

        with self.assertRaises(exceptions.UserError) as em:
            self.rate_service.dispatch("delete", self.record.id)
        self.assertEqual(
            "The record does not exist or you cannot delete it", em.exception.args[0]
        )

    def test_update(self):
        params = {"rating": 1, "feedback": "test"}
        res = self.rate_service.dispatch("update", self.record.id, params=params)
        self.assertTrue(res["updated"])
        self.assertEqual(1, self.record.rating)
        self.assertEqual("test", self.record.feedback)
        # a partner cannot update the rating of another
        with self.work_on_services(partner=self.partner2) as work:
            self.rate_service = work.component(usage="product_rating")

        with self.assertRaises(exceptions.UserError) as em:
            self.rate_service.dispatch("update", self.record.id, params=params)
        self.assertEqual(
            "The record does not exist or you cannot update it", em.exception.args[0]
        )

    def test_verified(self):
        self.assertFalse(self.record.verified)
        invoice = self._create_invoice()
        with self.work_on_services(partner=self.partner2) as work:
            self.rate_service = work.component(usage="product_rating")
            self.rate_service.dispatch("create", params=self.data.copy())
        res = self.env["rating.rating"].search(
            [
                ("res_id", "=", self.product2.id),
                ("partner_id", "=", self.partner2.id),
                ("res_model", "=", "product.product"),
            ],
            limit=1,
        )
        # the invoice was not paid so the purchase is not verified
        self.assertFalse(res.verified)
        self._make_payment(invoice)
        data = self.data.copy()
        data["product_id"] = self.product1.id
        self.rate_service.dispatch("create", params=data)
        res = self.env["rating.rating"].search(
            [
                ("res_id", "=", self.product1.id),
                ("partner_id", "=", self.partner2.id),
                ("res_model", "=", "product.product"),
            ],
            limit=1,
        )
        self.assertTrue(res.verified)

    def test_verified2(self):
        """
        this test makes sure that the 'verified' field is true only if res_model is product.product
        """
        invoice = self._create_invoice()
        with self.work_on_services(partner=self.partner2) as work:
            self.rate_service = work.component(usage="product_rating")
            self.rate_service.dispatch("create", params=self.data.copy())
        res = self.env["rating.rating"].search(
            [
                ("res_id", "=", self.product2.id),
                ("partner_id", "=", self.partner2.id),
                ("res_model", "=", "product.product"),
            ],
            limit=1,
        )

        self.assertTrue(res)
        self.assertFalse(res.verified)
        self._make_payment(invoice)

        data = self.params.copy()
        data["product_id"] = self.product1.id
        data["res_model_id"] = self.env.ref("base.model_res_partner").id
        data["res_model"] = "res.partner"
        data["partner_id"] = self.partner2.id
        data["feedback"] = "does not work"
        self.rate_service.dispatch("create", params=data)
        res = self.env["rating.rating"].search(
            [
                ("res_id", "=", self.product1.id),
                ("partner_id", "=", self.partner2.id),
                ("res_model", "=", "res.partner"),
            ],
            limit=1,
        )
        self.assertTrue(res)
        self.assertFalse(res.verified)

    def _create_invoice(self):
        values = {
            "partner_id": self.partner2.id,
            "partner_shipping_id": self.partner2.id,
            "shopinvader_backend_id": self.backend.id,
            "invoice_date": fields.Date.today(),
            "move_type": "out_invoice",
            "invoice_line_ids": [
                (
                    0,
                    False,
                    {
                        "product_id": self.product2.id,
                        "quantity": 10,
                        "price_unit": 1250,
                        "account_id": self.product2.categ_id.property_account_expense_categ_id,
                        "name": self.product2.display_name,
                    },
                ),
                (
                    0,
                    False,
                    {
                        "product_id": self.product1.id,
                        "quantity": 10,
                        "price_unit": 1250,
                        "account_id": self.product1.categ_id.property_account_expense_categ_id,
                        "name": self.product1.display_name,
                    },
                ),
            ],
        }
        invoice = self.env["account.move"].create(values)
        invoice.state = "posted"
        return invoice

    def _make_payment(self, invoice, journal=False, amount=False):
        """
        Make payment for given invoice
        :param invoice: account.invoice recordset
        :param amount: float
        :return: bool
        """
        ctx = {"active_model": invoice._name, "active_ids": invoice.ids}
        wizard_obj = self.env["account.payment.register"].with_context(ctx)
        self.bank_journal_euro = self.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK67"}
        )
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )
        register_payments = wizard_obj.create(
            {
                "payment_date": fields.Date.today(),
                "journal_id": self.bank_journal_euro.id,
                "payment_method_id": self.payment_method_manual_in.id,
            }
        )
        if journal:
            register_payments.write({"journal_id": journal.id})
        if amount:
            register_payments.write({"amount": amount})
        register_payments.action_create_payments()

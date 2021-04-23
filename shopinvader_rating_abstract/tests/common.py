# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.shopinvader.tests.common import CommonCase


class CommonRatingCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner1 = cls.env.ref("shopinvader.partner_1")
        cls.partner2 = cls.env.ref("shopinvader.partner_2")
        cls.product1 = cls.env.ref("shopinvader.product_product_chair_vortex_white")
        cls.product2 = cls.env.ref("shopinvader.product_product_chair_vortex_blue")
        cls.params = {
            "rating": 5,
            "feedback": "test",
            "res_id": cls.product1.id,
            "res_model_id": cls.env.ref("product.model_product_product").id,
            "shopinvader_backend_id": cls.env.ref("shopinvader.backend_1").id,
            "partner_id": cls.partner1.id,
            "lang_id": cls.env.ref("base.lang_en").id,
            "consumed": True,
        }
        cls.data = {
            "rating": 5,
            "feedback": "Feedback text",
            "id": cls.product2.id,
        }

# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _get_shop_data(self):
        # without this test_get_cart_image_info in shopinvader_image
        # fails because the parser does not recognize 'images_webp'
        # from this module
        values = super()._get_shop_data()
        exporter = self.env.ref("shopinvader.ir_exp_shopinvader_variant")
        values_webp = self.jsonify(exporter.get_json_parser(), one=True)
        values.update(values_webp)
        return values

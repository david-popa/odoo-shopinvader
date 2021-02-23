from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def _get_shop_data(self):
        """"""
        values = super()._get_shop_data()
        exporter = self.env.ref(
            "shopinvader_image_webp.ir_exp_shopinvader_variant_webp"
        )
        values_webp = self.jsonify(exporter.get_json_parser(), one=True)
        values.update(values_webp)
        return values

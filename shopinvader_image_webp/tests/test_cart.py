# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class ShopinvaderCartCase(CommonConnectedCartCase):
    def test_get_cart_image_info(self):
        response = self.service.dispatch("search")
        print("==WEBP==")
        print(response["data"]["lines"]["items"][0]["product"])
        self.assertIn(
            "images_webp", response["data"]["lines"]["items"][0]["product"]
        )

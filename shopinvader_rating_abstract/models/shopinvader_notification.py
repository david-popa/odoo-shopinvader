# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools.translate import _


class ShopinvaderNotification(models.Model):
    _inherit = "shopinvader.notification"

    def _get_all_notification(self):
        res = super()._get_all_notification()
        res.update(
            {
                "rating_created": {
                    "name": _("New rating created"),
                    "model": "rating.rating",
                },
                "rating_publisher_response": {
                    "name": _("Publisher responded to a rating"),
                    "model": "rating.rating",
                },
            }
        )
        return res

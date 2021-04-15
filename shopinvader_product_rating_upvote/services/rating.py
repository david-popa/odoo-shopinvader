# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, exceptions
from odoo.addons.component.core import Component


class ProductRatingUpvoteService(Component):
    _inherit = "shopinvader.product.rating.service"

    def upvote(self, _id):
        """
        Upvote an existing rating
        :param _id: int
        :return: dict/json
        """
        record = self.env['rating.rating'].browse(_id)
        if record.exists() and self.partner.id != record.partner_id.id:
            record.votes = record.votes + 1
            return {"upvoted": True, "message": "The rating has been upvoted"}
        raise exceptions.UserError(
            _("The record does not exist or you cannot upvote it")
        )

    def _validator_upvote(self):
        return {}

    def _validator_return_upvote(self):
        schema = {
            "upvoted": {"type": "boolean"},
            "message": {"type": "string"}
        }
        return schema

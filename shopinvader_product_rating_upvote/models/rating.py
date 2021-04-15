# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class RatingVote(models.Model):
    _inherit = ["shopinvader.rating.product", "shopinvader.rating.abstract"]

    upvotes = fields.Integer(default=0)

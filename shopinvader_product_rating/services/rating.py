# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class ProductRatingService(Component):
    """Shopinvader service to create and edit customer's product ratings."""

    _inherit = "shopinvader.abstract.rating.service"
    _name = "shopinvader.product.rating.service"
    _usage = "product_rating"
    _description = __doc__
    _rating_model = "product.product"

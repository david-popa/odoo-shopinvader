# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class Product(models.Model):
    _inherit = ["product.product", "rating.mixin"]
    _name = "product.product"

    # def _compute_rating_average(self):
    #     stats = self.rating_get_stats()
    #     self.avg_rating = stats.get('avg')
    #
    # def action_view_reviews(self):
    #     self.ensure_one()
    #     action = self.env.ref('rating.rating_rating_view').read()[0]
    #     action.update({'domain': [('res_id', 'in', self.ids), ('res_model', '=', self._name)]})
    #     return action
    #
    # rating_ids = fields.One2many(comodel_name="rating.rating", inverse_name="res_id", domain="[('res_model', '=', 'product.product'), ('is_internal', '=', False)]",
    #                           string="Ratings", readonly=True)
    #
    # avg_rating = fields.Float(compute='_compute_rating_average', string='Average Rating')

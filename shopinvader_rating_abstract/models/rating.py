# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class Rating(models.Model):
    _inherit = "rating.rating"

    _sql_constraints = [
        ("rating_range", "CHECK(1=1)", "Rating should be between 0 and 5"),
        (
            "rating_range_shopinvader",
            "check(rating >= 1 and rating <= 5)",
            "Rating should be between 1 and 5",
        ),
        (
            "rating_unique",
            "unique(res_model, res_id, partner_id)",
            "You can only rate this resource once",
        ),
    ]

    @api.depends("rating")
    def _compute_rating_str(self):
        for record in self:
            record.rating_str = str(record.rating)

    def _inverse_rating_str(self):
        for record in self:
            record.rating = float(record.rating_str)

    def synchronize_rating(self):
        res_model = fields.first(self).res_model
        records = self.env[res_model].browse(self.mapped("res_id"))
        records.synchronize()

    shopinvader_backend_id = fields.Many2one(
        "shopinvader.backend", string="Backend", required=True
    )
    lang_id = fields.Many2one("res.lang", string="Language", required=True)
    active = fields.Boolean(default=True)
    rating_str = fields.Selection(
        [
            ("0.0", "0"),
            ("1.0", "1"),
            ("2.0", "2"),
            ("3.0", "3"),
            ("4.0", "4"),
            ("5.0", "5"),
        ],
        string="Rating string",
        compute="_compute_rating_str",
        store=True,
        inverse="_inverse_rating_str",
        readonly=True,
    )

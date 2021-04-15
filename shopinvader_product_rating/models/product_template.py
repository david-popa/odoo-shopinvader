from odoo import models


class ProductTemplate(models.Model):
    _inherit = ["product.template", "rating.mixin"]
    _name = "product.template"

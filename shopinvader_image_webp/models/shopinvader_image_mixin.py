# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


import base64
from io import BytesIO

from odoo import api, fields, models
from odoo.addons.base_sparse_field.models.fields import Serialized
from PIL import Image


class ShopinvaderImageMixin(models.AbstractModel):
    _inherit = "shopinvader.image.mixin"

    images_webp = Serialized(
        compute="_compute_images_webp", string="Shopinvader Image WebP"
    )
    images_webp_stored = Serialized()
    images_webp_store_hash = fields.Char()

    @api.depends("images")
    def _compute_images_webp(self):
        # Force computation if needed
        self.filtered(
            lambda x: x._images_webp_must_recompute()
        )._compute_images_webp_stored()
        for record in self:
            record.images_webp = record.images_webp_stored

    def _compute_images_webp_stored(self):
        super()._compute_images_stored()
        for record in self:
            record.images_webp_stored = (
                record._get_image_webp_data_for_record()
            )
            record.images_webp_store_hash = record._get_images_store_hash()

    def _images_webp_must_recompute(self):
        return self.images_webp_store_hash != self._get_images_store_hash()

    def _create_storage_image(self, image, url_key):
        storage_image_ctx = self.env["storage.image"].with_context(
            skip_generate_odoo_thumbnail=True
        )
        img = BytesIO(base64.b64decode(image))
        im = Image.open(img).convert("RGB")
        with BytesIO() as output:
            im.save(output, "webp")
            return storage_image_ctx.create(
                {
                    "name": url_key,
                    "image_medium_url": base64.b64encode(output.getvalue()),
                }
            )

    def _get_image_webp_data_for_record(self):
        # By default Odoo preloads PIL with only the basic image formats
        # This allows PIL to load all the image formats available
        Image._initialized = 1

        res = []
        resizes = self._resize_scales()
        for image_relation in self[self._image_field]:
            url_key = self._get_image_url_key(image_relation) + ".webp"
            thumbnail_exists = self.env["storage.thumbnail"].search(
                [("url_key", "=", url_key)], limit=1
            )
            if not thumbnail_exists:
                webp = self._create_storage_image(
                    image_relation.image_id.data, url_key
                )
                image_data = {}
                for resize in resizes:
                    thumbnail = webp.get_or_create_thumbnail(
                        resize.size_x, resize.size_y, url_key=url_key
                    )
                    image_data[resize.key] = self._prepare_data_resize(
                        thumbnail, image_relation
                    )
                res.append(image_data)
        return res

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError, AccessError
import logging


class SaleOrder(models.Model):
    _inherit = "sale.order"

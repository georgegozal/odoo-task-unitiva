from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    internal_contact = fields.Boolean(string="internal contact")
    # legal_representative
    # date_of_birth this exists by default .dob
    birth_place = fields.Char(string="Birth Place")
    document_type = fields.Selection([
        ('id_card', 'Identity Card'),
        ('driver_license', "Driver's License"),
        ('passport', 'Passport')
    ], string="Document Type")
    document_number = fields.Char(string="Document Number")
    document_expiry_date = fields.Date(string="Document Expiry Date")
    document_issue_date = fields.Date(string="Document Issue Date")

    # - Industry category (dictionary based on ATECO codes)
    # - Internal contact (dictionary of 'Individual' contacts with 'Internal Contact' flag activated)
    # - Legal representative (dictionary of 'Individual' contacts with 'Legal Representative' flag activated)
    approved = fields.Selection([
        ('to_be_approved', 'To Be Approved'),
        ('approved', 'Approved')
    ], string='Approved', default='to_be_approved', tracking=True)

    codice_fiscale = fields.Char(
        string="Codice Fiscale",
        size=16,
        copy=False,
    )

    _sql_constraints = [
        ('codice_fiscale_unique', 'unique(codice_fiscale)', 'The Codice Fiscale must be unique.')
    ]
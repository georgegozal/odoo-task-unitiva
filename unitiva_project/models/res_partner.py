from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError, AccessError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    internal_contact = fields.Boolean(string="internal contact")
    legal_representative = fields.Boolean(string="Legal Representative")
    birth_date = fields.Date(string="Date of Birth")
    birth_place = fields.Char(string="Place of Birth")
    document_type = fields.Selection([
        ('id_card', 'Identity Card'),
        ('driver_license', "Driver's License"),
        ('passport', 'Passport')
    ], string="Document Type")
    document_number = fields.Char(string="Document Number")
    document_expiry_date = fields.Date(string="Document Expiry Date")
    document_issue_date = fields.Date(string="Document Issue Date")
    codice_fiscale = fields.Char(
        string="Codice Fiscale",
        size=16,
        copy=False,
    )

    # - Industry category (dictionary based on ATECO codes)
    approved = fields.Selection([
        ('to_be_approved', 'To Be Approved'),
        ('approved', 'Approved')
    ], string='Approved', default='to_be_approved', tracking=True)

    industry_category = fields.Many2one('industry.category', string="Industry Category")
    customer_id = fields.Char(string="Customer ID", readonly=True, copy=False, default=lambda self: 'New')

    internal_contacts = fields.Many2many(
        'res.partner',
        'res_partner_internal_rel',
        'partner_id', 'internal_contact_id',
        string="Internal Contacts",
        domain=[('internal_contact', '=', True)]
    )

    legal_representatives = fields.Many2many(
        'res.partner',
        'res_partner_legal_rel',
        'partner_id', 'legal_representative_id',
        string="Legal Representatives",
        domain=[('legal_representative', '=', True)]
    )

    def action_approve(self):
        for record in self:
            if record.company_type == 'company' and not record.internal_contacts and not record.legal_representatives:
                raise ValidationError(
                    "A company must have at least one Internal Contact or Legal Representative before approval.")
            record.approved = 'approved'

    def action_reset_to_be_approved(self):
        self.approved = 'to_be_approved'

    @api.constrains('vat', 'codice_fiscale')
    def _check_unique_identifiers(self):
        for record in self:
            if record.vat and self.search_count([('vat', '=', record.vat), ('id', '!=', record.id)]) > 0:
                raise ValidationError("The VAT number must be unique.")
            if record.codice_fiscale and self.search_count(
                    [('codice_fiscale', '=', record.codice_fiscale), ('id', '!=', record.id)]) > 0:
                raise ValidationError("The Codice Fiscale must be unique.")

    @api.model
    def create(self, vals):
        if vals.get('company_type') == 'company' and not vals.get('customer_id'):
            vals['customer_id'] = self.env['ir.sequence'].next_by_code('res.partner.customer') or 'New'
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        restricted_fields = ['vat', 'codice_fiscale', 'street', 'city', 'zip', 'country_id']
        for record in self:
            if record.approved == 'approved' and any(field in vals for field in restricted_fields):
                raise ValidationError("You cannot modify VAT, Fiscal Code, or Address when the contact is Approved.")
        return super(ResPartner, self).write(vals)

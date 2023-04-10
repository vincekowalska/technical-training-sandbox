from odoo import api,fields,models
from odoo.exceptions import UserError
from odoo.tools import float_compare
from datetime import timedelta,datetime

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"
    _sql_constraints = [
        ("price", "check(price  >= 0 )", "The Offer Price Must Be Strictly Positive"),
        ("price", "check(price  >= 0 )", "The Offer Price Must Be Strictly Positive"),
    ]
    
    price = fields.Float()
    status = fields.Selection(
        string="Status",
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False
    )
    partner_id = fields.Many2one('res.partner' , required=True)
    property_id = fields.Many2one('estate.property')
    start_date = fields.Date(string='Start Date', default=fields.Date.today())
    validity = fields.Integer(default=7, string= "Validity (days)")
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline', string='Deadline', store=True)
    accepted = fields.Boolean(string="Accept")
    refused = fields.Boolean(string = "Refuse")
    property_type_id = fields.Many2one('estate.property.type',related ="property_id.property_type_id", string = "Property Type",store=True)

    @api.depends("validity","start_date")
    def _compute_date_deadline(self):
        self.date_deadline = self.start_date + timedelta(days=self.validity)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "n"
        else:
            self.garden_area = 0
            self.garden_orientation = False
                   
    def _inverse_date_deadline(self):
        for rec in self:
            self.validity = (self.date_deadline - self.start_date).days

    def accept_act(self):
        for act in self :
            if self.status == "accepted":
                raise UserError("An offer as already been Accepted.")
            else:
                self.status = "accepted"
        return self.mapped("property_id").write(
            {
                "state": "offer_accepted",
                "selling_price": self.price,
                "buyer_id": self.partner_id
            }
        )

    def refuse_act(self):
        for act in self :
            if self.status == "refused":
                raise UserError("An offer as already been Refused.")
            else:
                self.status = "refused"
    
    @api.model
    def create(self, vals):
        if vals.get("property_id") and vals.get("price"):
            prop = self.env["estate.property"].browse(vals["property_id"])
            if prop.offer_ids:
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals["price"], max_offer, precision_rounding=0.01) <= 0:
                    raise UserError("The offer must be higher than %.2f" % max_offer)
            prop.state = "offer_received"
        return super().create(vals)

    

from odoo import api,fields,models
from dateutil.relativedelta import relativedelta

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "name"
    sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name must be unique"),
    ]

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Property')
    sequence = fields.Integer('sequence',  default = 10)
    offer_count = fields.Integer(string = "Offer Counts", compute = "_compute_offer")
    offer_ids = fields.Many2many ("estate.property.offer", string = "Offers", compute = "_compute_offer")

    @api.depends('offer_ids')
    def _compute_offer(self):
        data = self.env["estate.property.offer"].read_group(
            [("property_id.state", "!=", "canceled"), ("property_type_id", "!=", False)],
            ["ids:array_agg(id)", "property_type_id"],
            ["property_type_id"],
        )
        mapped_count = {d["property_type_id"][0]: d["property_type_id_count"] for d in data}
        mapped_ids = {d["property_type_id"][0]: d["ids"] for d in data}
        for prop_type in self :
            prop_type.offer_count = mapped_count.get(prop_type.id ,0)
            prop_type.offer_ids = mapped_ids.get(prop_type.id, [])

    def action_view_offers(self):
        res = self.env.ref("estate.estate_property_offer_action").read()[0]
        res["domain"] = [("id", "in", self.offer_ids.ids)]
        return res
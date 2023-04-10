from odoo import api,fields,models
from odoo.exceptions import ValidationError,UserError
from odoo.tools import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc" 
    _sql_constraints = [
        ("expected_price", "check(expected_price >= 0)", "The Expected Price Must Be Strictly Positive"),
    ]
    _sql_constraints = [
        ("selling_price_", "check(selling_price >= 0)", "The Selling Price Must Be Strictly Positive"),
    ]
    
    name = fields.Char(required=True)
    property_type_id = fields.Many2one('estate.property.type', string = "Property Type")
    description = fields.Text()
    postcode =  fields.Char()
    date_availability = fields.Date(copy=False,default = lambda self : fields.datetime.now()+relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default = 2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('west', 'West'), ('east', 'East')]
    )
    # active = fields.Boolean()
    state = fields.Selection(
        string = 'Status',
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        default = 'new',
        copy=False,
        required=True
    )
    buyer_id = fields.Many2one('res.partner', string='Buyer',readonly=True, copy=False)
    user_id = fields.Many2one('res.users', string ="Salesman", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offer')
    total_area = fields.Integer(compute ="_compute_total_area", string="Total Area (sqm)" )
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")   
    color = fields.Integer(string='Color Index', compute='_compute_property_color')
    
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        self.total_area = self.garden_area + self.living_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        self.best_price = max(self.offer_ids.mapped("price"), default = 0)

    @api.onchange('garden')
    def _onchange_garden(self):
        for i in self:
            if i.garden:
                i.garden_area = 10
                i.garden_orientation = "north"
            else :
                i.garden_area = False
                i.garden_orientation = False
    
    @api.constrains("selling_price","expected_price")
    def _check_selling_price(self):
        for  i in self:
            if (
                not float_is_zero(i.selling_price, precision_rounding=0.01)
                and float_compare(i.selling_price, i.expected_price * 90.0 / 100.0, precision_rounding=0.01) < 0
            ) :
                raise ValidationError ("The selling price must be at least 90% of the expected price!")

    def sold_act(self) :
        for i in self:
           if i.state == "canceled":
                raise ValidationError("A canceled property cannot be set as sold")
           else:   
                i.state = "sold"
        return True

    def cancel_act(self) :
        for i in self:
            if i.state == "sold":
                raise ValidationError("A sold property cannot be canceled")
            else:
                i.state = "canceled"
        return True
    
    def unlink(self) :
        if not set(self.mapped("state")) <= {"new", "canceled"} :
            raise UserError("Only new and canceled properties can be deleted.")
        return super().unlink()
from odoo import models

class EstateProperty(models.Model) :
    _inherit = "estate.property"

    def sold_act(self):
        res = super().sold_act()
        journal = self.env["account.journal"].search([("type", "=", "sale")], limit=1)
        for i in self:
            self.env["account.move"].create(
                {
                    "partner_id": i.buyer_id.id,
                    "move_type": "out_invoice",
                    "journal_id": journal.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": i.name,
                                "quantity": 1.0,
                                "price_unit": i.selling_price * 6.0 / 100.0,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Administrative fees",
                                "quantity": 1.0,
                                "price_unit": 100.0,
                            },
                        ),
                    ],
                }
            )
        return 
# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _, _lt
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta
from itertools import chain
import io
from odoo.tools.misc import xlsxwriter
import pytz
from odoo.exceptions import ValidationError, UserError
import warnings
import logging

_logger = logging.getLogger(__name__)


class MrpProductionSchedule(models.Model):
    _inherit = 'mrp.production.schedule'

    def action_replenish(self, based_on_lead_time=False):
        """ Run the procurement for production schedule in self. Once the
        procurements are launched, mark the forecast as launched (only used
        for state 'to_relaunch')

        :param based_on_lead_time: 2 replenishment options exists in MPS.
        based_on_lead_time means that the procurement for self will be launched
        based on lead times.
        e.g. period are daily and the product have a manufacturing period
        of 5 days, then it will try to run the procurements for the 5 first
        period of the schedule.
        If based_on_lead_time is False then it will run the procurement for the
        first period that need a replenishment
        """
        production_schedule_states = self.get_production_schedule_view_state()
        production_schedule_states = {mps['id']: mps for mps in production_schedule_states}
        procurements = []
        forecasts_values = []
        forecasts_to_set_as_launched = self.env['mrp.product.forecast']
        for production_schedule in self:
            production_schedule_state = production_schedule_states[production_schedule.id]
            # Check for kit. If a kit and its component are both in the MPS we want to skip the
            # the kit procurement but instead only refill the components not in MPS
            bom = self.env['mrp.bom']._bom_find(
                product=production_schedule.product_id, company_id=production_schedule.company_id.id,
                bom_type='phantom')
            product_ratio = []
            if bom:
                dummy, bom_lines = bom.explode(production_schedule.product_id, 1)
                product_ids = [l[0].product_id.id for l in bom_lines]
                product_ids_with_forecast = self.env['mrp.production.schedule'].search([
                    ('company_id', '=', production_schedule.company_id.id),
                    ('warehouse_id', '=', production_schedule.warehouse_id.id),
                    ('product_id', 'in', product_ids)
                ]).product_id.ids
                product_ratio += [
                    (l[0], l[0].product_qty * l[1]['qty'])
                    for l in bom_lines if l[0].product_id.id not in product_ids_with_forecast
                ]

            # Cells with values 'to_replenish' means that they are based on
            # lead times. There is at maximum one forecast by schedule with
            # 'forced_replenish', it's the cell that need a modification with
            #  the smallest start date.
            replenishment_field = based_on_lead_time and 'to_replenish' or 'forced_replenish'
            forecasts_to_replenish = filter(lambda f: f[replenishment_field], production_schedule_state['forecast_ids'])
            for forecast in forecasts_to_replenish:
                existing_forecasts = production_schedule.forecast_ids.filtered(lambda p:
                                                                               p.date >= forecast[
                                                                                   'date_start'] and p.date <= forecast[
                                                                                   'date_stop']
                                                                               )
                extra_values = production_schedule._get_procurement_extra_values(forecast)
                # check minimum quantity of supplier
                min_quantity = production_schedule.product_id.seller_ids[0].min_qty if len(production_schedule.product_id.seller_ids) > 0 else 0
                quantity = forecast['replenish_qty'] - forecast['incoming_qty']
                if min_quantity > quantity:
                    quantity = min_quantity
                # end check minimum quantity of supplier
                if not bom:
                    procurements.append(self.env['procurement.group'].Procurement(
                        production_schedule.product_id,
                        quantity,
                        production_schedule.product_uom_id,
                        production_schedule.warehouse_id.lot_stock_id,
                        production_schedule.product_id.name,
                        'MPS', production_schedule.company_id, extra_values
                    ))
                else:
                    for bom_line, qty_ratio in product_ratio:
                        procurements.append(self.env['procurement.group'].Procurement(
                            bom_line.product_id,
                            quantity * qty_ratio,
                            bom_line.product_uom_id,
                            production_schedule.warehouse_id.lot_stock_id,
                            bom_line.product_id.name,
                            'MPS', production_schedule.company_id, extra_values
                        ))

                if existing_forecasts:
                    forecasts_to_set_as_launched |= existing_forecasts
                else:
                    forecasts_values.append({
                        'forecast_qty': 0,
                        'date': forecast['date_stop'],
                        'procurement_launched': True,
                        'production_schedule_id': production_schedule.id
                    })
        if procurements:
            self.env['procurement.group'].with_context(skip_lead_time=True).run(procurements)

        forecasts_to_set_as_launched.write({
            'procurement_launched': True,
        })
        if forecasts_values:
            self.env['mrp.product.forecast'].create(forecasts_values)

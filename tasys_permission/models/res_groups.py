# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools
import logging
import re
import psycopg2
from ast import literal_eval
from collections import defaultdict
from collections.abc import Mapping
from operator import itemgetter

from psycopg2 import sql

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import pycompat, unique
from odoo.tools.safe_eval import safe_eval, datetime, dateutil, time

_logger = logging.getLogger(__name__)


class ResGroups(models.Model):
    _inherit = ['res.groups']

    is_partner_permission = fields.Boolean('Is partner permission', default=False)
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


class IrModelAccess(models.Model):
    _inherit = ['ir.model.access']

    # The context parameter is useful when the method translates error messages.
    # But as the method raises an exception in that case,  the key 'lang' might
    # not be really necessary as a cache key, unless the `ormcache_context`
    # decorator catches the exception (it does not at the moment.)
    @api.model
    @tools.ormcache_context('self.env.uid', 'self.env.su', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check_by_groups(self, model, mode='read', raise_exception=True, group_ids = []):
        if self.env.su:
            # User root have all accesses
            return True

        assert isinstance(model, str), 'Not a model name: %s' % (model,)
        assert mode in ('read', 'write', 'create', 'unlink'), 'Invalid access mode'

        # TransientModel records have no access rights, only an implicit access rule
        if model not in self.env:
            _logger.error('Missing model %s', model)

        self.flush(self._fields)

        # We check if a specific rule exists
        self._cr.execute("""SELECT MAX(CASE WHEN perm_{mode} THEN 1 ELSE 0 END)
                                  FROM ir_model_access a
                                  JOIN ir_model m ON (m.id = a.model_id)
                                  JOIN res_groups_users_rel gu ON (gu.gid = a.group_id)
                                 WHERE m.model = %s
                                   AND gu.uid = %s
                                   AND a.group_id IN %s
                                   AND a.active IS TRUE""".format(mode=mode),
                         [model, self._uid,  tuple(group_ids)])
        r = self._cr.fetchone()[0]

        # need fix
        # if not r:
        #     # there is no specific rule. We check the generic rule
        #     self._cr.execute("""SELECT MAX(CASE WHEN perm_{mode} THEN 1 ELSE 0 END)
        #                                       FROM ir_model_access a
        #                                       JOIN ir_model m ON (m.id = a.model_id)
        #                                      WHERE a.group_id IS NULL
        #                                        AND m.model = %s
        #                                        AND a.active IS TRUE""".format(mode=mode),
        #                      (model,))
        #     r = self._cr.fetchone()[0]

        if not r and raise_exception:
            groups = '\n'.join('\t- %s' % g for g in self.group_names_with_access(model, mode))
            document_kind = self.env['ir.model']._get(model).name or model
            msg_heads = {
                # Messages are declared in extenso so they are properly exported in translation terms
                'read': _("You are not allowed to access '%(document_kind)s' (%(document_model)s) records.",
                          document_kind=document_kind, document_model=model),
                'write': _("You are not allowed to modify '%(document_kind)s' (%(document_model)s) records.",
                           document_kind=document_kind, document_model=model),
                'create': _("You are not allowed to create '%(document_kind)s' (%(document_model)s) records.",
                            document_kind=document_kind, document_model=model),
                'unlink': _("You are not allowed to delete '%(document_kind)s' (%(document_model)s) records.",
                            document_kind=document_kind, document_model=model),
            }
            operation_error = msg_heads[mode]

            if groups:
                group_info = _("This operation is allowed for the following groups:\n%(groups_list)s",
                               groups_list=groups)
            else:
                group_info = _("No group currently allows this operation.")

            resolution_info = _("Contact your administrator to request access if necessary.")

            _logger.info('Access Denied by ACLs for operation: %s, uid: %s, model: %s', mode, self._uid, model)
            msg = """{operation_error}

    {group_info}

    {resolution_info}""".format(
                operation_error=operation_error,
                group_info=group_info,
                resolution_info=resolution_info)

            raise AccessError(msg)

        return bool(r)


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def check_access_rights_by_groups(self, operation, raise_exception=True, group_ids=[]):
        """ Verifies that the operation given by ``operation`` is allowed for
            the current user according to the access rights.
        """
        return self.env['ir.model.access'].check_by_groups(self._name, operation, raise_exception, group_ids)



class View(models.Model):
    _inherit = 'ir.ui.view'

    def _postprocess_access_rights(self, model, node):
        """ Compute and set on node access rights based on view type. Specific
        views can add additional specific rights like creating columns for
        many2one-based grouping views. """
        super(View, self)._postprocess_access_rights(model, node)

        # testing ACL as real user
        Model = self.env[model].sudo(False)
        is_base_model = self.env.context.get('base_model_name', model) == model

        if node.tag in ('kanban', 'tree', 'form', 'activity'):
            for action, operation in (('create', 'create'), ('delete', 'unlink'), ('edit', 'write')):
                group_ids = self.env['res.groups'].search([('is_partner_permission', '=', True)])
                print('tungnt')
                print(group_ids)
                if self.env.user.login == 'admin':
                    node.set(action, 'true')
                elif (not node.get(action) and
                      not Model.check_access_rights_by_groups(operation, raise_exception=False, group_ids=group_ids.ids) or
                      not self._context.get(action, True) and is_base_model):
                    node.set(action, 'false')


class TasysCommonModel(models.Model):
    _name = 'tasys.common.model'

    name = fields.Char()
    def _has_group(self, group_name):
        return self.env.user.sudo().has_group(group_name)

    is_category_manager = fields.Boolean(compute="_compute_is_category_manager")

    @api.depends('name')
    def _compute_is_category_manager(self):
        for record in self:
            record.is_category_manager = self._has_group('tasys_permission.category_manager')

    is_category_executive = fields.Boolean(compute="_compute_is_category_executive")

    @api.depends('name')
    def _compute_is_category_executive(self):
        for record in self:
            record.is_category_executive = self._has_group('tasys_permission.category_executive')

    is_cs_manager = fields.Boolean(compute="_compute_is_cs_manager")

    @api.depends('name')
    def _compute_is_cs_manager(self):
        for record in self:
            record.is_cs_manager = self._has_group('tasys_permission.cs_manager')

    is_cs_executive = fields.Boolean(compute="_compute_is_cs_executive")

    @api.depends('name')
    def _compute_is_cs_executive(self):
        for record in self:
            record.is_category_executive = self._has_group('tasys_permission.cs_executive')

    is_wh_supervisor = fields.Boolean(compute="_compute_is_wh_supervisor")

    @api.depends('name')
    def _compute_is_wh_supervisor(self):
        for record in self:
            record.is_wh_supervisor = self._has_group('tasys_permission.wh_supervisor')

    is_wh_user = fields.Boolean(compute="_compute_is_wh_user")

    @api.depends('name')
    def _compute_is_wh_user(self):
        for record in self:
            record.is_wh_user = self._has_group('tasys_permission.wh_user')

    is_sourcing = fields.Boolean(compute="_compute_is_sourcing")

    @api.depends('name')
    def _compute_is_sourcing(self):
        for record in self:
            record.is_sourcing = self._has_group('tasys_permission.sourcing')

    is_accountant_manager = fields.Boolean(compute="_compute_is_accountant_manager")

    @api.depends('name')
    def _compute_is_accountant_manager(self):
        for record in self:
            record.is_accountant_manager = self._has_group('tasys_permission.accountant_manager')

    is_accountant_executive = fields.Boolean(compute="_compute_is_accountant_executive")

    @api.depends('name')
    def _compute_is_accountant_executive(self):
        for record in self:
            record.is_accountant_executive = self._has_group('tasys_permission.accountant_executive')

    is_sales_lead = fields.Boolean(compute="_compute_is_sales_lead")

    @api.depends('name')
    def _compute_is_sales_lead(self):
        for record in self:
            record.is_sales_lead = self._has_group('tasys_permission.sales_lead')

    is_sales_executive = fields.Boolean(compute="_compute_is_sales_executive")

    @api.depends('name')
    def _compute_is_sales_executive(self):
        for record in self:
            record.is_sales_executive = self._has_group('tasys_permission.sales_executive')


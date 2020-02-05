# -*- coding: utf-8 -*-


from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class TestBusinessIdConstrains(TransactionCase):
    """To run tests, use similar command to following one:
    ./odoo-bin -d <database-name> --test-enable
    -i l10n_fi_business_code_duplicate_check --stop-after-init
    --addons-path="/opt/odoo/10/server/addons"
    Put all needed dependencies to '--addons-path=' after which testing
    should work. Tests will run at least when all repositories from
    conf-folder are added to addons-path."""

    def setUp(self):
        super(TestBusinessIdConstrains, self).setUp()
        self.res_partner_model = self.env['res.partner']

        self.first_company = self.res_partner_model.create(dict(
            id='10000000',
            name='First Company',
        ))

        self.second_company = self.res_partner_model.create(dict(
            id='10000001',
            name='Second Company',
        ))

    def test_business_id_constrains(self):
        business_id = '1234567-1'

        with self.assertRaises(ValidationError):
            _logger.info(
                "-----Testing method: 'test_business_id_constrains'-----"
            )
            self.first_company.business_id = business_id
            self.second_company.business_id = business_id

    def test_business_id_onchange(self):
        business_id = '1234567-1'

        with self.assertRaises(ValidationError):
            _logger.info(
                "-----Testing method: 'test_business_id_onchange'-----"
            )
            self.first_company.play_onchanges({
                'business_id': business_id
            }, ['business_id'])
            self.second_company.play_onchanges({
                'business_id': business_id
            }, ['business_id'])

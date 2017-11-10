# -*- coding: utf-8 -*-
import logging
import sys
import datetime
import StringIO
import re

from dateutil.tz import tzlocal
from odoo import api, fields, models

# Finvoice imports
from finvoice.finvoice201 import Finvoice

# Message transmission details
from finvoice.finvoice201 import MessageTransmissionDetailsType
from finvoice.finvoice201 import MessageSenderDetailsType
from finvoice.finvoice201 import MessageReceiverDetailsType
from finvoice.finvoice201 import MessageDetailsType

# Seller party details
from finvoice.finvoice201 import SellerPartyDetailsType
from finvoice.finvoice201 import SellerPostalAddressDetailsType

# Seller information details
from finvoice.finvoice201 import SellerInformationDetailsType
from finvoice.finvoice201 import SellerAccountDetailsType
from finvoice.finvoice201 import SellerAccountIDType
from finvoice.finvoice201 import SellerBicType

# Buyer party details
from finvoice.finvoice201 import BuyerPartyDetailsType
from finvoice.finvoice201 import BuyerPostalAddressDetailsType

# Delivery party details
from finvoice.finvoice201 import DeliveryPartyDetailsType
from finvoice.finvoice201 import DeliveryPostalAddressDetailsType

# Invoice details
from finvoice.finvoice201 import InvoiceDetailsType
from finvoice.finvoice201 import InvoiceTypeCodeType
from finvoice.finvoice201 import VatSpecificationDetailsType
from finvoice.finvoice201 import PaymentTermsDetailsType
from finvoice.finvoice201 import PaymentOverDueFineDetailsType

# Payment status details
from finvoice.finvoice201 import PaymentStatusDetailsType

# Invoice rows
from finvoice.finvoice201 import InvoiceRowType
from finvoice.finvoice201 import QuantityType

# EPI details
from finvoice.finvoice201 import EpiDetailsType
from finvoice.finvoice201 import EpiIdentificationDetailsType
from finvoice.finvoice201 import EpiPartyDetailsType
from finvoice.finvoice201 import EpiBfiPartyDetailsType
from finvoice.finvoice201 import EpiBeneficiaryPartyDetailsType
from finvoice.finvoice201 import EpiAccountIDType
from finvoice.finvoice201 import EpiBfiIdentifierType
from finvoice.finvoice201 import EpiPaymentInstructionDetailsType
from finvoice.finvoice201 import EpiRemittanceInfoIdentifierType
from finvoice.finvoice201 import EpiChargeType

# General imports
from finvoice.finvoice201 import date
from finvoice.finvoice201 import amount
from finvoice.soap.envelope import Envelope, Header, Body
from finvoice.soap.msgheader import MessageHeader, From, To, PartyId, Service, MessageData
from finvoice.soap.msgheader import Manifest, Reference, Schema

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    # Please do not add this field to any view, as the computation is resource-intense
    # This is only to act as a helper
    invoice_number = fields.Char(
        string='Invoice number',
        compute='compute_invoice_number',
    )

    finvoice_xml = fields.Text(
        string='Finvoice XML',
        compute='compute_finvoice_xml'
    )

    def compute_invoice_number(self):
        for record in self:
            if record.number:
                record.invoice_number = re.sub(r'\D', '', record.number)

    def compute_finvoice_xml(self):
        for record in self:
            _logger.debug('Generating Finvoice for %s', self.name)

            finvoice_xml = record._get_finvoice_xml()
            record.finvoice_xml = finvoice_xml

    def _get_finvoice_xml(self):
        output = StringIO.StringIO()

        finvoice_object = Finvoice('2.01')

        self.add_message_transmission_details(finvoice_object)

        self.add_seller_party_details(finvoice_object)
        self.add_seller_information_details(finvoice_object)

        self.add_buyer_party_details(finvoice_object)

        self.add_delivery_party_details(finvoice_object)

        self.add_invoice_details(finvoice_object)

        self.add_invoice_rows(finvoice_object)

        self.add_epi_details(finvoice_object)

        finvoice_xml = finvoice_object.export(output, 0, name_='Finvoice', pretty_print=True)

        return output.getvalue()

    def add_message_transmission_details(self, finvoice_object):

        MessageSenderDetails = MessageSenderDetailsType(
            FromIdentifier=self.company_id.company_registry,  # Business id
            FromIntermediator='',
        )

        MessageReceiverDetails = MessageReceiverDetailsType(
            ToIdentifier=self.partner_id.edicode,
            ToIntermediator=self.partner_id.einvoice_operator_identifier,
        )

        message_timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+00:00')

        MessageDetails = MessageDetailsType(
            MessageIdentifier=self.invoice_number,
            MessageTimeStamp=message_timestamp,
        )

        MessageTransmissionDetails = MessageTransmissionDetailsType(
            MessageSenderDetails=MessageSenderDetails,
            MessageReceiverDetails=MessageReceiverDetails,
            MessageDetails=MessageDetails,
        )

        finvoice_object.set_MessageTransmissionDetails(MessageTransmissionDetails)

    def add_seller_party_details(self, finvoice_object):
        company = self.company_id

        SellerPostalAddressDetails = SellerPostalAddressDetailsType(
            SellerStreetName=[company.street, company.street2],
            SellerTownName=company.city,
            SellerPostCodeIdentifier=company.zip,
            CountryCode=company.country_id.code,
            CountryName=company.country_id.name,
        )

        SellerPartyDetails = SellerPartyDetailsType(
            SellerPartyIdentifier=company.company_registry,  # Business id
            SellerPartyIdentifierUrlText=company.website,
            SellerOrganisationName=[company.name],
            SellerOrganisationTaxCode=company.vat,
            SellerOrganisationTaxCodeUrlText='',
            SellerPostalAddressDetails=SellerPostalAddressDetails,
        )

        finvoice_object.set_SellerPartyDetails(SellerPartyDetails)

    def add_seller_information_details(self, finvoice_object):
        SellerAccountID = SellerAccountIDType(
            IdentificationSchemeName='IBAN',
            valueOf_=self.partner_bank_id.acc_number,
        )
        SellerBic = SellerBicType(
            IdentificationSchemeName='BIC',
            valueOf_=self.partner_bank_id.bank_bic,
        )

        SellerAccountDetails = SellerAccountDetailsType(
            SellerAccountID=SellerAccountID,
            SellerBic=SellerBic,
        )

        SellerInformationDetails = SellerInformationDetailsType(
            SellerAccountDetails=[SellerAccountDetails],
        )

        finvoice_object.set_SellerInformationDetails(SellerInformationDetails)

    def add_buyer_party_details(self, finvoice_object):
        partner = self.partner_id

        BuyerPostalAddressDetails = BuyerPostalAddressDetailsType(
            BuyerStreetName=[partner.street, partner.street2],
            BuyerTownName=partner.city,
            BuyerPostCodeIdentifier=partner.zip,
            CountryCode=partner.country_id.code,
            CountryName=partner.country_id.name,
        )

        BuyerPartyDetails = BuyerPartyDetailsType(
            BuyerPartyIdentifier=partner.business_id,
            BuyerOrganisationName=[partner.name],
            BuyerOrganisationDepartment='',
            BuyerOrganisationTaxCode=partner.vat,
            BuyerPostalAddressDetails=BuyerPostalAddressDetails,
        )

        finvoice_object.set_BuyerPartyDetails(BuyerPartyDetails)

    def add_delivery_party_details(self, finvoice_object):
        partner = self.partner_shipping_id or self.partner_id

        DeliveryPostalAddressDetails = DeliveryPostalAddressDetailsType(
            DeliveryStreetName=[partner.street, partner.street2],
            DeliveryTownName=partner.city,
            DeliveryPostCodeIdentifier=partner.zip,
            CountryCode=partner.country_id.code,
            CountryName=partner.country_id.name,
        )

        DeliveryPartyDetails = DeliveryPartyDetailsType(
            DeliveryPartyIdentifier=partner.business_id,
            DeliveryOrganisationName=[partner.name],
            DeliveryPostalAddressDetails=DeliveryPostalAddressDetails,
        )

        finvoice_object.set_DeliveryPartyDetails(DeliveryPartyDetails)

    def add_invoice_details(self, finvoice_object):

        # Normal invoices
        CodeListAgencyIdentifier = ''
        TypeCode = 'INV01'
        OriginCode = 'Original'

        # Refund invoice
        if self.type == 'out_refund':
            TypeCode = 'INV02'
            CodeListAgencyIdentifier = 'SPY'
            OriginCode = 'Cancel'

        InvoiceTypeCode = InvoiceTypeCodeType(
            CodeListAgencyIdentifier=CodeListAgencyIdentifier,
            valueOf_=TypeCode,
        )

        InvoiceTotalVatExcludedAmount = amount(
            AmountCurrencyIdentifier=self.currency_id.name,
            valueOf_=self.amount_untaxed,
        )

        InvoiceTotalVatAmount = amount(
            AmountCurrencyIdentifier=self.currency_id.name,
            valueOf_=self.amount_tax,
        )

        InvoiceTotalVatIncludedAmount = amount(
            AmountCurrencyIdentifier=self.currency_id.name,
            valueOf_=self.amount_total,
        )

        # TODO: separate different VAT rates
        VatSpecificationDetails = VatSpecificationDetailsType(
            VatBaseAmount=InvoiceTotalVatExcludedAmount,
            VatRateAmount=InvoiceTotalVatAmount,
        )

        PaymentTermsDetails = PaymentTermsDetailsType(
            PaymentTermsFreeText=[self.payment_term_id.name],
            InvoiceDueDate=date('CCYYMMDD', self.get_date_unhyphenated(self.date_due)),
        )

        PaymentOverDueFineDetails = PaymentOverDueFineDetailsType(
            PaymentOverDueFineFreeText='',  # TODO
            PaymentOverDueFinePercent='',  # TODO
        )

        InvoiceDetails = InvoiceDetailsType(
            InvoiceTypeCode=InvoiceTypeCode,
            InvoiceTypeText=self.get_invoice_finvoice_type_text(TypeCode),
            OriginCode=OriginCode,
            InvoiceNumber=self.invoice_number,
            InvoiceDate=date('CCYYMMDD', self.get_date_unhyphenated(self.date_invoice)),
            OrderIdentifier=self.invoice_number,
            InvoiceTotalVatExcludedAmount=InvoiceTotalVatExcludedAmount,
            InvoiceTotalVatAmount=InvoiceTotalVatAmount,
            InvoiceTotalVatIncludedAmount=InvoiceTotalVatIncludedAmount,
            VatSpecificationDetails=[VatSpecificationDetails],
            PaymentTermsDetails=[PaymentTermsDetails],
            # PaymentOverDueFineDetails = PaymentOverDueFineDetails,
        )

        finvoice_object.set_InvoiceDetails(InvoiceDetails)

    def add_payment_status_details(self, finvoice_object):
        # TODO: get PaymentStatusCode based on invoice payments and reconcile state

        PaymentStatusDetails = PaymentStatusDetailsType(
            PaymentStatusCode='NOTPAID',
        )

        finvoice_object.set_PaymentStatusDetails(PaymentStatusDetails)

    def add_invoice_rows(self, finvoice_object):
        InvoiceRows = list()

        for line in self.invoice_line_ids:
            DeliveredQuantity = QuantityType(
                QuantityUnitCode=line.uom_id.name.encode('utf-8'),  # TODO: fix this in the library
                valueOf_=line.quantity,
            )

            UnitPriceAmount = amount(
                AmountCurrencyIdentifier=self.currency_id.name,
                valueOf_=line.price_unit,
            )

            RowVatExcludedAmount = amount(
                AmountCurrencyIdentifier=self.currency_id.name,
                valueOf_=(line.quantity * line.price_unit),
            )

            InvoiceRow = InvoiceRowType(
                ArticleIdentifier=line.product_id.default_code,
                ArticleName=line.product_id.name,
                DeliveredQuantity=[DeliveredQuantity],
                UnitPriceAmount=UnitPriceAmount,
                RowFreeText=[line.name],
                RowVatExcludedAmount=RowVatExcludedAmount,
            )

            InvoiceRows.append(InvoiceRow)

        finvoice_object.set_InvoiceRow([InvoiceRow])

    def add_epi_details(self, finvoice_object):
        EpiIdentificationDetails = EpiIdentificationDetailsType(
            EpiDate=date('CCYYMMDD', datetime.datetime.now().strftime("%Y%m%d")),
        )

        EpiDetails = EpiDetailsType(
            EpiIdentificationDetails=EpiIdentificationDetails,
            EpiPartyDetails=self._get_epi_party_details(),
            EpiPaymentInstructionDetails=self._get_epi_payment_instruction_details(),
        )

        finvoice_object.set_EpiDetails(EpiDetails)

    def _get_epi_party_details(self):
        BfiEpiAccountID = EpiBfiIdentifierType(
            IdentificationSchemeName='BIC',
            valueOf_=self.partner_bank_id.bank_bic,
        )

        # Sellers bank
        EpiBfiPartyDetails = EpiBfiPartyDetailsType(
            EpiBfiIdentifier=BfiEpiAccountID,
        )

        BeneficiaryEpiAccountID = EpiAccountIDType(
            IdentificationSchemeName='IBAN',
            valueOf_=self.partner_bank_id.acc_number,
        )

        # Seller
        EpiBeneficiaryPartyDetails=EpiBeneficiaryPartyDetailsType(
            EpiNameAddressDetails=self.partner_id.name,
            EpiBei=self.company_id.company_registry,
            EpiAccountID=BeneficiaryEpiAccountID,
        )

        EpiPartyDetails = EpiPartyDetailsType(
            EpiBfiPartyDetails=EpiBfiPartyDetails,
            EpiBeneficiaryPartyDetails=EpiBeneficiaryPartyDetails,
        )

        return EpiPartyDetails

    def _get_epi_payment_instruction_details(self):
        EpiRemittanceInfoIdentifier = EpiRemittanceInfoIdentifierType(
            IdentificationSchemeName='ISO',
            valueOf_=self.invoice_number.zfill(20)  # TODO: change to invoice ref number
        )

        EpiInstructedAmount = amount(
            AmountCurrencyIdentifier=self.currency_id.name,
            valueOf_=self.amount_total,
        )

        EpiCharge = EpiChargeType(
            ChargeOption='SHA',  # TODO: add SLEV-option for non-domestic invoices
            valueOf_='SHA',
        )

        EpiPaymentInstructionDetails = EpiPaymentInstructionDetailsType(
            EpiPaymentInstructionId=self.invoice_number,  # TODO: change this to invoice ref number and add a sequence?
            EpiRemittanceInfoIdentifier=EpiRemittanceInfoIdentifier,
            EpiInstructedAmount=EpiInstructedAmount,
            EpiCharge=EpiCharge,
            EpiDateOptionDate=date('CCYYMMDD', self.get_date_unhyphenated(self.date_due)),
        )

        return EpiPaymentInstructionDetails

    def test(self):
        _sellerOrganisationName = {
            'FI': 'Pullis Musiken Oy',
            'SV': 'Pullis Musiken Ab',
            'EN': 'Pullis Musiken Ltd',
        }
        _sellerAddress = 'Puukatu 2 F'
        _sellerTown = 'HELSINKI'
        _sellerPostCode = '00112'
        _sellerCountryCode = 'FI'
        _sellerCountryName = 'Suomi'
        _sellerAccounts = [
            {'IBAN': 'FI2757800750155448', 'BIC': 'OKOYFIHH'},
            {'IBAN': 'FI2721221222212227', 'BIC': 'NDEAFIHH'},
            {'IBAN': 'FI2781232323312334', 'BIC': 'PSPBFIHH'},
        ]

        _sellerWebAddressNameText = _sellerOrganisationName['FI']
        _sellerWebAddress = 'https://www.pullinmusiikki.fi/'
        _sellerInvoiceAddress = '00371999207'
        _sellerInvoiceIntermediatorAddress = 'OKOYFIHH'
        _sellerYTunnus = '0199920-7'
        _sellerIndustryCode = '62020'

        _sellerInvoiceTypeDetails = {
            'FI': {
                'text': 'Kirjanpito palvelu',
                'validation':
                    [
                        {
                            'type': '02',
                            'min': None,
                            'hyphens': None,
                            'spaces': None,
                            'max': None,
                            'text': 'Viitenumero'
                        },
                        {
                            'type': '09',
                            'min': 10,
                            'hyphens': True,
                            'spaces': None,
                            'max': 10,
                            'text': 'Asiakasnumero'
                        },
                    ],
            },
        }

        _paymentInstructionId = 'Bookkeeping service'

        _proposedDueDate = 'NO'
        _proposedPaymentPeriod = 'YES'

        _messageId = '001'
        _messageActionCode = 'ADD'


        # Date
        nowDate = date("CCYYMMDD", datetime.datetime.now(tzlocal()).date().strftime("%Y%m%d"))

        # Seller Postal Address
        # SellerStreetName=None, SellerTownName=None, SellerPostCodeIdentifier=None, CountryCode=None, CountryName=None, SellerPostOfficeBoxIdentifier=None
        sellerPostalAddress = SellerPostalAddressDetailsType(_sellerAddress, _sellerTown, _sellerPostCode,
                                                             _sellerCountryCode, _sellerCountryName)

        sellerOrganisationNames = {}
        # Seller Organization Name
        # LanguageCode=None, SellerOrganisationName=None
        for (_langCode, _orgName) in _sellerOrganisationName.items():
            sellerOrganisationNames[_langCode] = SellerOrganisationNamesType(_langCode)
            sellerOrganisationNames[_langCode].add_SellerOrganisationName(_orgName)

        sellerAccountDetails = []
        # SellerAccountID=None, SellerBic=None, NewSellerAccountID=None, NewSellerBic=None
        for _account in _sellerAccounts:
            sellerAccountDetails.append(SellerAccountDetailsType(SellerAccountIDType('IBAN', _account['IBAN']),
                                                                 SellerBicType('BIC', _account['BIC'])))

        # Sender Information
        # Version=None, MessageDetails=None, SellerPartyDetails=None, SellerOrganisationUnitNumber=None, InvoiceSenderInformationDetails=None,
        # SellerAccountDetails=None, SellerInvoiceDetails=None, ProposedDueDateAccepted=None, ProposedInvoicePeriodAccepted=None
        senderInfo = FinvoiceSenderInfo('2.0')

        # Message Details
        # MessageTypeCode=None, MessageTypeText=None, MessageActionCode=None, MessageActionCodeIdentifier=None, MessageDate=None, SenderInfoIdentifier=None
        senderInfo.set_MessageDetails(
            MessageDetailsType('SENDERINFO', 'INVOICER NOTIFICATION', _messageActionCode, None, nowDate, _messageId))

        # Seller Party Details
        # SellerPartyIdentifier=None, SellerOrganisationNames=None, SellerOrganisationBankName=None, SellerPostalAddressDetails=None, IndustryCode=None
        sellerPartyDetails = SellerPartyDetailsType(_sellerYTunnus, None, None, sellerPostalAddress,
                                                    _sellerIndustryCode)

        for (_langCode, _orgName) in sellerOrganisationNames.items():
            sellerPartyDetails.add_SellerOrganisationNames(_orgName)

        senderInfo.set_SellerPartyDetails(sellerPartyDetails)

        # SellerWebaddressNameText=None, SellerWebaddressText=None, InvoiceSenderAddress=None, InvoiceSenderIntermediatorAddress=None, NewInvoiceSenderAddress=None, NewInvoiceSenderIntermediatorAddress=None
        senderInfo.set_InvoiceSenderInformationDetails(
            InvoiceSenderInformationDetailsType(_sellerWebAddressNameText, _sellerWebAddress, _sellerInvoiceAddress,
                                                _sellerInvoiceIntermediatorAddress))

        for _account in sellerAccountDetails:
            senderInfo.add_SellerAccountDetails(_account)

        # SellerDirectDebitIdentifier=None, PaymentInstructionIdentifier=None, SellerInstructionFreeText=None, SellerInvoiceTypeDetails=None, SellerServiceCode=None
        sellerInvoiceDetails = SellerInvoiceDetailsType(None, _paymentInstructionId)

        sellerInvoiceTypeDetails = {}
        for (_langCode, _type) in _sellerInvoiceTypeDetails.items():
            # SellerInvoiceTypeText=None, SellerInvoiceIdentifierText=None
            sellerInvoiceTypeDetails[_langCode] = SellerInvoiceTypeDetailsType(
                SellerInvoiceTypeTextType(_langCode, _type['text']))

            for _validation in _type['validation']:
                # LanguageCode=None, SellerInvoiceIdentifierType=None, SellerInvoiceIdentifierMinLength=1, SellerInvoiceIdentifierHyphens=False, SellerInvoiceIdentifierSpaces=False, SellerInvoiceIdentifierMaxLength=35, valueOf_=None, extensiontype_=None
                sellerInvoiceTypeDetails[_langCode].add_SellerInvoiceIdentifierText(
                    SellerInvoiceIdentifierTextType(_langCode, _validation['type'], _validation['min'],
                                                    _validation['hyphens'], _validation['spaces'], _validation['max'],
                                                    _validation['text']))

            sellerInvoiceDetails.add_SellerInvoiceTypeDetails(sellerInvoiceTypeDetails[_langCode])

        # = e-invoicer
        sellerInvoiceDetails.set_SellerServiceCode('00')

        senderInfo.set_SellerInvoiceDetails(sellerInvoiceDetails)

        senderInfo.set_ProposedDueDateAccepted(_proposedDueDate)
        senderInfo.set_ProposedInvoicePeriodAccepted(_proposedPaymentPeriod)

        _recepients = [
            {
                'Receiver': 'SENDERINFO',
                'Intermediator': 'OKOYFIHH',
            },
        ]

        _now = datetime.datetime.now(tzlocal())
        _nowS = datetime.datetime(_now.year, _now.month, _now.day, _now.hour, _now.minute, _now.second, 0, _now.tzinfo)

        for (i, _recepient) in enumerate(_recepients):
            envelope = Envelope()

            # mustUnderstand=None, version=None, From=None, To=None, CPAId=None, ConversationId=None, Service=None, Action=None, MessageData=None
            messageHeader = MessageHeader(1, "2.0")

            # Header=None, Body=None
            header = Header()
            header.add_anytypeobjs_(messageHeader)

            # PartyId=None, Role=None
            msgFrom = From(None, "Sender")
            msgFrom.add_PartyId(PartyId(None, _sellerInvoiceAddress))

            msgFromI = From(None, "Intermediator")
            msgFromI.add_PartyId(PartyId(None, _sellerInvoiceIntermediatorAddress))

            messageHeader.add_anytypeobjs_(msgFrom)
            messageHeader.add_anytypeobjs_(msgFromI)

            msgTo = To(None, "Receiver")
            msgTo.add_PartyId(PartyId(None, _recepient['Receiver']))

            msgToI = To(None, "Intermediator")
            msgToI.add_PartyId(PartyId(None, _recepient['Intermediator']))

            messageHeader.add_anytypeobjs_(msgTo)
            messageHeader.add_anytypeobjs_(msgToI)

            messageHeader.set_CPAId("yoursandmycpa")

            messageHeader.set_Service(Service(None, "Routing"))
            messageHeader.set_Action("ProcessInvoice")

            msgData = MessageData('{0}/{1}'.format(_messageId, i + 1), _nowS)

            messageHeader.set_MessageData(msgData)

            envelope.set_Header(header)

            manifest = Manifest("2.0", "Manifest")
            reference = Reference(None, _messageId, None, "FinvoiceSenderInfo")
            manifest.add_Reference(reference)
            reference.add_Schema(
                Schema("2.0", "http://www.pankkiyhdistys.fi/verkkolasku/finvoice/FinvoiceSenderInfo.xsd"))

            body = Body()
            body.add_anytypeobjs_(manifest)

            envelope.set_Body(body)

            envelope.export(sys.stdout, 0, pretty_print=True)

            encodingHeader = '<?xml version="1.0" encoding="' + ExternalEncoding + '" ?>\n'
            output.write(encodingHeader)
            output.write('<?xml-stylesheet type="text/xsl" href="FinvoiceSenderInfo.xsl"?>\n')

        finvoice_xml = senderInfo.export(output, 0, name_='FinvoiceSenderInfo',
                          namespacedef_='xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="FinvoiceSenderInfo.xsd"',
                          pretty_print=True)

        return output.getvalue()

    @staticmethod
    def get_invoice_finvoice_type_text(InvoiceTypeCode):
        # Returns Finvoice 2.01 InvoiceTypeText if applicable

        InvoiceTypeText = False

        InvoiceTypes = {
            'REQ01': 'TARJOUSPYYNTÖ',
            'QUO01': 'TARJOUS',
            'ORD01': 'TILAUS',
            'ORC01': 'TILAUSVAHVISTUS',
            'DEV01': 'TOIMITUSILMOITUS',
            'INV01': 'LASKU',
            'INV02': 'HYVITYSLASKU',
            'INV03': 'KORKOLASKU',
            'INV04': 'SISÄINEN LASKU',
            'INV05': 'PERINTÄLASKU',
            'INV06': 'PROFORMALASKU',
            'INV07': 'ITSELASKUTUS',
            'INV08': 'HUOMAUTUSLASKU',
            'INV09': 'SUORAMAKSU',
            'TES01': 'TESTILASKU',
            'PRI01': 'HINNASTO',
            'INF01': 'TIEDOTE',
            'DEN01': 'TOIMITUSVIRHEILMOITUS',
            'SEI01-09': 'TURVALASKU',
        }

        if InvoiceTypeCode in InvoiceTypes:
            InvoiceTypeText = InvoiceTypes[InvoiceTypeCode]

        return InvoiceTypeText

    @staticmethod
    def get_date_unhyphenated(date_string):
        # Returns unhyphenated ISO-8601 date
        # CCYY-MM-DD becomes CCYYMMDD
        # 2020-01-02 becomes 20200102

        if not date_string:
            return False

        # This only validates the format. Not if the string is actually a valid date
        iso_8601_format = re.compile('[0-9]{4}[-][0-9]{2}[-][0-9]{2}')

        if not iso_8601_format.match(date_string):
            return False

        return date_string.replace('-', '')

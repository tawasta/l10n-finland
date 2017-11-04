# -*- coding: utf-8 -*-
import logging
import sys
import datetime
import StringIO

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

from finvoice.sender.senderinfo import ExternalEncoding
from finvoice.sender.senderinfo import FinvoiceSenderInfo
# from finvoice.sender.senderinfo import MessageDetailsType
# from finvoice.sender.senderinfo import SellerPartyDetailsType
# from finvoice.sender.senderinfo import SellerPostalAddressDetailsType
from finvoice.sender.senderinfo import SellerOrganisationNamesType
from finvoice.sender.senderinfo import InvoiceSenderInformationDetailsType
from finvoice.sender.senderinfo import SellerAccountDetailsType
from finvoice.sender.senderinfo import SellerAccountIDType
from finvoice.sender.senderinfo import SellerBicType
#from finvoice.sender.senderinfo import SellerInvoiceDetailsType
from finvoice.sender.senderinfo import SellerInvoiceTypeDetailsType
from finvoice.sender.senderinfo import SellerInvoiceTypeTextType
from finvoice.sender.senderinfo import SellerInvoiceIdentifierTextType
from finvoice.sender.senderinfo import date

from finvoice.soap.envelope import Envelope, Header, Body
from finvoice.soap.msgheader import MessageHeader, From, To, PartyId, Service, MessageData
from finvoice.soap.msgheader import Manifest, Reference, Schema

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    # Please do not add this field to any view, as the computation is resource-intense
    # This is only to act as a helper
    finvoice_xml = fields.Text(
        string='Finvoice XML',
        compute='compute_finvoice_xml'
    )

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
            MessageIdentifier=self.number,
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


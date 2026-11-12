.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================================================
Partner: Mark Invoice Addresses with Company ID as Companies
============================================================

* An invoice address that has a Company ID (y-tunnus) is set as a company 
  (i.e. company_type = "company", not "person") when it is created or edited 
  in Contacts. 
* Intended for situations where e.g. an individual person may
  buy goods or have subscriptions, but invoice them to different companies. This 
  way each invoice address of that individual keeps their own
  own Company Registry
* Note: an invoice address whose Company ID is the same as its parent partner's
  still stays an individual, as the value is synced from the parent.

Configuration
=============
* Optionally: go to Settings > General Settings > Contacts and enable
  "Suggest Company Invoice Address". Odoo then suggests the partner's
  invoice address that is a company as the invoice address, e.g. on sale
  orders, if the partner has exactly one such address. The suggestion
  can be changed on the document. Without the setting, Odoo suggests the
  partner itself.

Usage
=====
* Open a partner in Contacts and add an invoice address under
  Contacts & Addresses, filling in its Company ID. After saving, the 
  invoice address is now a company.
* Optionally: to mass update existing invoice addresses, go to 
  Settings > General Settings > Contacts and click 
  "Mark as Companies" under setting "Invoice Addresses with Company ID"

Known issues / Roadmap
======================
* An invoice address with its own Company ID is kept as a company. Changing
  it back to an individual, removing the Company ID or changing the address
  type does not revert it automatically.
* Odoo does not suggest company-type invoice addresses (e.g. on sale
  orders) when the setting "Suggest Company Invoice Address" is off, or
  when the partner has several of them. 
* Only the partner's own invoice addresses are considered, not those of
  its parent company.
* Note that with this module, an invoice address is its own commercial partner.
  Its invoices, receivables and follow-ups are on the address itself, and
  accounting settings such as payment terms and fiscal position are not
  synced from the parent partner.  

Credits
=======

Contributors
------------

* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: https://futural.fi/

This module is maintained by Futural Oy

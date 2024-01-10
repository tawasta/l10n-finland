def post_init_hook(env):
    print("HOOKETY HOOK")
    # Migrate data from old "business_code"-field
    # This is done in hook instead of migration script, as this is a new standalone module
    env.cr.execute(
        "UPDATE res_partner SET company_registry = business_code WHERE company_registry IS NULL"
    )

    # Auto-compute company registry from VAT
    env["res.partner"]._compute_company_registry_from_vat()

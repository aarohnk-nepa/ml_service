from typing import Optional
import datetime
import decimal

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, Double, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class AccountMoveSales(Base):
    __tablename__ = 'account_move_sales'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='account_move_sales_pkey'),
        Index('idx_ams_campaign', 'campaign_id', postgresql_where='(campaign_id IS NOT NULL)'),
        Index('idx_ams_invoice_date_company_posted', 'invoice_date', 'company_id', postgresql_where="((state)::text = 'posted'::text)"),
        Index('idx_ams_invoice_origin', 'invoice_origin', postgresql_where='(invoice_origin IS NOT NULL)'),
        Index('idx_ams_medium', 'medium_id', postgresql_where='(medium_id IS NOT NULL)'),
        Index('idx_ams_posted_partner_date', 'partner_id', 'invoice_date', postgresql_where="(((state)::text = 'posted'::text) AND ((move_type)::text = ANY (ARRAY[('out_invoice'::character varying)::text, ('out_refund'::character varying)::text])))"),
        Index('idx_ams_posted_payment_date', 'payment_state', 'invoice_date', postgresql_where="(((state)::text = 'posted'::text) AND ((move_type)::text = 'out_invoice'::text))"),
        Index('idx_ams_posted_type_date_company', 'invoice_date', 'company_id', 'move_type', postgresql_where="(((state)::text = 'posted'::text) AND ((move_type)::text = ANY (ARRAY[('out_invoice'::character varying)::text, ('out_refund'::character varying)::text])))"),
        Index('idx_ams_posted_user_date', 'invoice_user_id', 'invoice_date', postgresql_where="(((state)::text = 'posted'::text) AND ((move_type)::text = ANY (ARRAY[('out_invoice'::character varying)::text, ('out_refund'::character varying)::text])))"),
        Index('idx_sales_company_state_date', 'company_id', 'state', 'invoice_date'),
        Index('ix_account_move_sales_id', 'id'),
        Index('ix_account_move_sales_invoice_date', 'invoice_date'),
        Index('ix_account_move_sales_write_date', 'write_date'),
        Index('ix_ams_name_invoice', 'name', postgresql_where="((move_type)::text = 'out_invoice'::text)")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    delivery_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    name: Mapped[Optional[str]] = mapped_column(String)
    payment_reference: Mapped[Optional[str]] = mapped_column(String)
    state: Mapped[Optional[str]] = mapped_column(String)
    payment_state: Mapped[Optional[str]] = mapped_column(String)
    ref: Mapped[Optional[str]] = mapped_column(String)
    move_type: Mapped[Optional[str]] = mapped_column(String)
    invoice_origin: Mapped[Optional[str]] = mapped_column(String)
    nepa_shipped_by_nepa: Mapped[Optional[bool]] = mapped_column(Boolean)
    nepa_is_shipped: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_delivery: Mapped[Optional[bool]] = mapped_column(Boolean)
    nepa_shpping_amount: Mapped[Optional[float]] = mapped_column(Double(53))
    amount_commission: Mapped[Optional[float]] = mapped_column(Double(53))
    amount_commission_discount: Mapped[Optional[float]] = mapped_column(Double(53))
    amount_commission_shipping: Mapped[Optional[float]] = mapped_column(Double(53))
    net_commission: Mapped[Optional[float]] = mapped_column(Double(53))
    amount_untaxed_signed: Mapped[Optional[float]] = mapped_column(Double(53))
    amount_tax_signed: Mapped[Optional[float]] = mapped_column(Double(53))
    amount_total_signed: Mapped[Optional[float]] = mapped_column(Double(53))
    amount_residual_signed: Mapped[Optional[float]] = mapped_column(Double(53))
    prime_tracking_code: Mapped[Optional[str]] = mapped_column(Text)
    prime_tracking_no: Mapped[Optional[str]] = mapped_column(String)
    campaign_id: Mapped[Optional[int]] = mapped_column(Integer)
    medium_id: Mapped[Optional[int]] = mapped_column(Integer)
    source_id: Mapped[Optional[int]] = mapped_column(Integer)
    partner_id: Mapped[Optional[int]] = mapped_column(Integer)
    company_id: Mapped[Optional[int]] = mapped_column(Integer)
    invoice_user_id: Mapped[Optional[int]] = mapped_column(Integer)
    nepa_sales_person_id: Mapped[Optional[int]] = mapped_column(Integer)
    team_id: Mapped[Optional[int]] = mapped_column(Integer)
    journal_id: Mapped[Optional[int]] = mapped_column(Integer)
    partner_bank_id: Mapped[Optional[int]] = mapped_column(Integer)
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    nepa_commission_paid: Mapped[Optional[bool]] = mapped_column(Boolean)
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))


class AccountMoveSalesLine(Base):
    __tablename__ = 'account_move_sales_line'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='account_move_sales_line_pkey'),
        Index('idx_amsl_account_id', 'account_id'),
        Index('idx_amsl_account_move_price', 'account_id', 'account_move_id', postgresql_include=['price_subtotal']),
        Index('idx_amsl_account_product', 'account_id', 'product_id'),
        Index('idx_amsl_move_id', 'account_move_id'),
        Index('idx_amsl_product_id', 'product_id'),
        Index('idx_amsl_product_move', 'product_id', 'account_move_id'),
        Index('idx_sales_line_move_product', 'account_move_id', 'product_id'),
        Index('ix_account_move_sales_line_id', 'id'),
        Index('ix_account_move_sales_line_move', 'account_move_id'),
        Index('ix_ams_line_write_date', 'write_date'),
        Index('ix_amsl_moveid_product', 'move_id', 'product_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_move_id: Mapped[Optional[int]] = mapped_column(Integer)
    product_id: Mapped[Optional[int]] = mapped_column(Integer)
    standard_price: Mapped[Optional[float]] = mapped_column(Double(53))
    quantity: Mapped[Optional[float]] = mapped_column(Double(53))
    price_unit: Mapped[Optional[float]] = mapped_column(Double(53))
    price_subtotal: Mapped[Optional[float]] = mapped_column(Double(53))
    nepa_cogs_price: Mapped[Optional[float]] = mapped_column(Double(53))
    discount: Mapped[Optional[float]] = mapped_column(Double(53))
    nepa_tax_multiplier: Mapped[Optional[float]] = mapped_column(Double(53))
    price_commission: Mapped[Optional[float]] = mapped_column(Double(53))
    account_id: Mapped[Optional[int]] = mapped_column(Integer)
    debit: Mapped[Optional[float]] = mapped_column(Double(53))
    credit: Mapped[Optional[float]] = mapped_column(Double(53))
    balance: Mapped[Optional[float]] = mapped_column(Double(53))
    amount_residual: Mapped[Optional[float]] = mapped_column(Double(53))
    amount_currency: Mapped[Optional[float]] = mapped_column(Double(53))
    move_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[Optional[str]] = mapped_column(Text)
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    pos_price_commission: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    partner_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    company_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    currency_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    price_total: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))


class CrmTeam(Base):
    __tablename__ = 'crm_team'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='crm_team_pkey'),
        Index('ix_crm_team_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[Optional[str]] = mapped_column(String)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class ProductCategory(Base):
    __tablename__ = 'product_category'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='product_category_pkey'),
        Index('ix_product_category_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    parent_id: Mapped[Optional[int]] = mapped_column(Integer)
    parent_name: Mapped[Optional[str]] = mapped_column(String)
    parent2_id: Mapped[Optional[int]] = mapped_column(Integer)
    parent2_name: Mapped[Optional[str]] = mapped_column(String)
    parent3_id: Mapped[Optional[int]] = mapped_column(Integer)
    parent3_name: Mapped[Optional[str]] = mapped_column(String)
    complete_name: Mapped[Optional[str]] = mapped_column(Text)
    nepa_licence_type_ids: Mapped[Optional[str]] = mapped_column(Text)
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    _sync_session_id: Mapped[Optional[str]] = mapped_column(Text)
    _content_hash: Mapped[Optional[str]] = mapped_column(Text)


class ProductProduct(Base):
    __tablename__ = 'product_product'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='product_product_pkey'),
        Index('idx_pp_barcode', 'barcode'),
        Index('idx_pp_categ_id', 'categ_id'),
        Index('idx_pp_display_name_trgm', 'display_name', postgresql_ops={'display_name': 'gin_trgm_ops'}, postgresql_using='gin'),
        Index('ix_product_product_display_name_trgm', 'display_name', postgresql_ops={'display_name': 'gin_trgm_ops'}, postgresql_using='gin'),
        Index('ix_product_product_id', 'id'),
        Index('product_display_name_trgm_idx', 'display_name', postgresql_ops={'display_name': 'gin_trgm_ops'}, postgresql_using='gin')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    active: Mapped[Optional[bool]] = mapped_column(Boolean)
    allow_out_of_stock_order: Mapped[Optional[bool]] = mapped_column(Boolean)
    display_name: Mapped[Optional[str]] = mapped_column(String)
    barcode: Mapped[Optional[str]] = mapped_column(String)
    detailed_type: Mapped[Optional[str]] = mapped_column(String)
    invoice_policy: Mapped[Optional[str]] = mapped_column(String)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    lst_price: Mapped[Optional[float]] = mapped_column(Double(53))
    is_published: Mapped[Optional[bool]] = mapped_column(Boolean)
    purchase_ok: Mapped[Optional[bool]] = mapped_column(Boolean)
    sale_ok: Mapped[Optional[bool]] = mapped_column(Boolean)
    can_be_expensed: Mapped[Optional[bool]] = mapped_column(Boolean)
    product_commission_type: Mapped[Optional[str]] = mapped_column(String)
    qty_available: Mapped[Optional[float]] = mapped_column(Double(53))
    show_availability: Mapped[Optional[bool]] = mapped_column(Boolean)
    type: Mapped[Optional[str]] = mapped_column(String)
    virtual_available: Mapped[Optional[float]] = mapped_column(Double(53))
    categ_id: Mapped[Optional[int]] = mapped_column(Integer)
    product_tmpl_id: Mapped[Optional[int]] = mapped_column(Integer)
    website_id: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[Optional[str]] = mapped_column(Text)
    default_code: Mapped[Optional[str]] = mapped_column(Text)
    list_price: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    standard_price: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    nepa_last_purchase_price: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    nepa_need_licence_check: Mapped[Optional[bool]] = mapped_column(Boolean)
    public_categ_ids: Mapped[Optional[str]] = mapped_column(Text)
    website_sequence: Mapped[Optional[int]] = mapped_column(BigInteger)
    weight: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    height: Mapped[Optional[str]] = mapped_column(Text)
    width: Mapped[Optional[str]] = mapped_column(Text)
    length: Mapped[Optional[str]] = mapped_column(Text)
    volume: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    nepa_allowed_company_ids: Mapped[Optional[str]] = mapped_column(Text)
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    _content_hash: Mapped[Optional[str]] = mapped_column(Text)
    _sync_session_id: Mapped[Optional[int]] = mapped_column(BigInteger)


class ProductTemplate(Base):
    __tablename__ = 'product_template'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='product_template_pkey'),
        Index('ix_product_template_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    display_name: Mapped[Optional[str]] = mapped_column(String)
    active: Mapped[Optional[bool]] = mapped_column(Boolean)
    type: Mapped[Optional[str]] = mapped_column(String)
    detailed_type: Mapped[Optional[str]] = mapped_column(String)
    default_code: Mapped[Optional[str]] = mapped_column(String)
    barcode: Mapped[Optional[str]] = mapped_column(String)
    list_price: Mapped[Optional[float]] = mapped_column(Double(53))
    standard_price: Mapped[Optional[float]] = mapped_column(Double(53))
    sale_ok: Mapped[Optional[bool]] = mapped_column(Boolean)
    purchase_ok: Mapped[Optional[bool]] = mapped_column(Boolean)
    can_be_expensed: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_published: Mapped[Optional[bool]] = mapped_column(Boolean)
    categ_id: Mapped[Optional[int]] = mapped_column(Integer)
    company_id: Mapped[Optional[int]] = mapped_column(Integer)
    uom_id: Mapped[Optional[int]] = mapped_column(Integer)
    uom_po_id: Mapped[Optional[int]] = mapped_column(Integer)
    tracking: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    description_sale: Mapped[Optional[str]] = mapped_column(Text)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    _sync_session_id: Mapped[Optional[str]] = mapped_column(Text)
    _content_hash: Mapped[Optional[str]] = mapped_column(Text)
    website_meta_description: Mapped[Optional[str]] = mapped_column(Text)
    website_description: Mapped[Optional[str]] = mapped_column(Text)
    description_ecommerce: Mapped[Optional[str]] = mapped_column(Text)
    weight: Mapped[Optional[str]] = mapped_column(Text)
    volume: Mapped[Optional[str]] = mapped_column(Text)


class ResCompany(Base):
    __tablename__ = 'res_company'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='res_company_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[Optional[str]] = mapped_column(Text)
    display_name: Mapped[Optional[str]] = mapped_column(Text)
    active: Mapped[Optional[bool]] = mapped_column(Boolean)
    partner_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    email: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(Text)
    mobile: Mapped[Optional[str]] = mapped_column(Text)
    website: Mapped[Optional[str]] = mapped_column(Text)
    street: Mapped[Optional[str]] = mapped_column(Text)
    street2: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(Text)
    zip: Mapped[Optional[str]] = mapped_column(Text)
    state_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    country_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    currency_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    vat: Mapped[Optional[str]] = mapped_column(Text)
    create_uid: Mapped[Optional[int]] = mapped_column(BigInteger)
    write_uid: Mapped[Optional[int]] = mapped_column(BigInteger)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))


class ResPartner(Base):
    __tablename__ = 'res_partner'
    __table_args__ = (
        PrimaryKeyConstraint('partner_id', name='res_partner_pkey'),
        Index('idx_rp_company_partner', 'partner_id', postgresql_include=['display_name', 'create_date', 'user_id'], postgresql_where='(is_company = true)'),
        Index('idx_rp_email_lower', postgresql_where="((email IS NOT NULL) AND ((email)::text <> ''::text))"),
        Index('idx_rp_last_invoice_date_active', 'nepa_last_invoice_date', postgresql_where='((active = true) AND (nepa_last_invoice_date IS NOT NULL))'),
        Index('idx_rp_nepa_customer_type', 'nepa_customer_type', postgresql_where='(active = true)'),
        Index('idx_rp_state_id', 'state_id')
    )

    partner_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    active: Mapped[Optional[bool]] = mapped_column(Boolean)
    display_name: Mapped[Optional[str]] = mapped_column(String)
    nepa_legal_name_id: Mapped[Optional[int]] = mapped_column(Integer)
    vat: Mapped[Optional[str]] = mapped_column(String)
    ref: Mapped[Optional[str]] = mapped_column(String)
    function: Mapped[Optional[str]] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
    mobile: Mapped[Optional[str]] = mapped_column(String)
    whatsapp_phone: Mapped[Optional[str]] = mapped_column(String)
    street: Mapped[Optional[str]] = mapped_column(String)
    street2: Mapped[Optional[str]] = mapped_column(String)
    city: Mapped[Optional[str]] = mapped_column(String)
    zip: Mapped[Optional[str]] = mapped_column(String)
    nepa_customer_type: Mapped[Optional[str]] = mapped_column(String)
    is_company: Mapped[Optional[bool]] = mapped_column(Boolean)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    partner_latitude: Mapped[Optional[float]] = mapped_column(Double(53))
    partner_longitude: Mapped[Optional[float]] = mapped_column(Double(53))
    nepa_last_invoice_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    prime_ship_type: Mapped[Optional[str]] = mapped_column(String)
    nepa_unreconciled_payments: Mapped[Optional[float]] = mapped_column(Double(53))
    nepa_customer_credit: Mapped[Optional[float]] = mapped_column(Double(53))
    state_id: Mapped[Optional[int]] = mapped_column(Integer)
    country_id: Mapped[Optional[int]] = mapped_column(Integer)
    create_uid: Mapped[Optional[int]] = mapped_column(Integer)
    write_uid: Mapped[Optional[int]] = mapped_column(Integer)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    team_id: Mapped[Optional[int]] = mapped_column(Integer)
    property_product_pricelist: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[Optional[str]] = mapped_column(Text)
    company_name: Mapped[Optional[str]] = mapped_column(Text)
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    commercial_partner_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    company_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    title: Mapped[Optional[str]] = mapped_column(Text)
    customer_rank: Mapped[Optional[int]] = mapped_column(BigInteger)
    supplier_rank: Mapped[Optional[int]] = mapped_column(BigInteger)
    category_id: Mapped[Optional[str]] = mapped_column(Text)
    lang: Mapped[Optional[str]] = mapped_column(Text)
    tz: Mapped[Optional[str]] = mapped_column(Text)
    website: Mapped[Optional[str]] = mapped_column(Text)
    barcode: Mapped[Optional[str]] = mapped_column(Text)
    credit_limit: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    nepa_customer_limit: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    nepa_apply_customer_limit: Mapped[Optional[bool]] = mapped_column(Boolean)
    nepa_licence_ids: Mapped[Optional[str]] = mapped_column(Text)
    has_ach_form: Mapped[Optional[bool]] = mapped_column(Boolean)
    has_credit_card_form: Mapped[Optional[bool]] = mapped_column(Boolean)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    nepa_block_partner: Mapped[Optional[bool]] = mapped_column(Boolean)
    nepa_block_reason: Mapped[Optional[str]] = mapped_column(Text)
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    _sync_session_id: Mapped[Optional[str]] = mapped_column(Text)
    _content_hash: Mapped[Optional[str]] = mapped_column(Text)


class ResUsers(Base):
    __tablename__ = 'res_users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='res_users_pkey'),
        Index('ix_res_users_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    active: Mapped[Optional[bool]] = mapped_column(Boolean)
    name: Mapped[Optional[str]] = mapped_column(String)
    login: Mapped[Optional[str]] = mapped_column(String)
    state: Mapped[Optional[str]] = mapped_column(String)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    login_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    last_backend_access: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    backend_access_days: Mapped[Optional[int]] = mapped_column(Integer)
    partner_id: Mapped[Optional[int]] = mapped_column(Integer)
    company_id: Mapped[Optional[int]] = mapped_column(Integer)
    create_uid: Mapped[Optional[int]] = mapped_column(Integer)
    write_uid: Mapped[Optional[int]] = mapped_column(Integer)
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    _sync_session_id: Mapped[Optional[str]] = mapped_column(Text)
    _content_hash: Mapped[Optional[str]] = mapped_column(Text)


class SaleOrder(Base):
    __tablename__ = 'sale_order'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='sale_order_pkey'),
        Index('idx_so_campaign', 'campaign_id', postgresql_where='(campaign_id IS NOT NULL)'),
        Index('idx_so_campaign_date', 'campaign_id', 'date_order', postgresql_where='(campaign_id IS NOT NULL)'),
        Index('idx_so_date_order', 'date_order'),
        Index('idx_so_medium', 'medium_id', postgresql_where='(medium_id IS NOT NULL)'),
        Index('idx_so_partner', 'partner_id'),
        Index('idx_so_state_date', 'state', 'date_order'),
        Index('idx_so_team', 'team_id', postgresql_where='(team_id IS NOT NULL)'),
        Index('idx_so_user_date', 'user_id', 'date_order'),
        Index('idx_so_warehouse_date', 'warehouse_id', 'date_order'),
        Index('ix_sale_order_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nepa_invoice_number: Mapped[Optional[str]] = mapped_column(String)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    date_order: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    display_name: Mapped[Optional[str]] = mapped_column(String)
    validity_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    state: Mapped[Optional[str]] = mapped_column(String)
    origin: Mapped[Optional[str]] = mapped_column(String)
    nepa_is_old_order: Mapped[Optional[bool]] = mapped_column(Boolean)
    nepa_sales_rep: Mapped[Optional[str]] = mapped_column(String)
    sellit_is_mobile_delivery_order: Mapped[Optional[bool]] = mapped_column(Boolean)
    client_order_ref: Mapped[Optional[str]] = mapped_column(String)
    effective_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    commitment_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    invoice_status: Mapped[Optional[str]] = mapped_column(String)
    delivery_status: Mapped[Optional[str]] = mapped_column(String)
    shipping_weight: Mapped[Optional[float]] = mapped_column(Double(53))
    partner_id: Mapped[Optional[int]] = mapped_column(Integer)
    opportunity_id: Mapped[Optional[int]] = mapped_column(Integer)
    campaign_id: Mapped[Optional[int]] = mapped_column(Integer)
    medium_id: Mapped[Optional[int]] = mapped_column(Integer)
    source_id: Mapped[Optional[int]] = mapped_column(Integer)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    team_id: Mapped[Optional[int]] = mapped_column(Integer)
    company_id: Mapped[Optional[int]] = mapped_column(Integer)
    warehouse_id: Mapped[Optional[int]] = mapped_column(Integer)
    warehouse_name: Mapped[Optional[str]] = mapped_column(String)
    pricelist_id: Mapped[Optional[int]] = mapped_column(Integer)
    amount_total: Mapped[Optional[float]] = mapped_column(Double(53))
    amount_tax: Mapped[Optional[float]] = mapped_column(Double(53))
    nepa_is_return_order: Mapped[Optional[bool]] = mapped_column(Boolean)
    name: Mapped[Optional[str]] = mapped_column(Text)
    amount_untaxed: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    currency_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    _sync_session_id: Mapped[Optional[str]] = mapped_column(Text)
    _content_hash: Mapped[Optional[str]] = mapped_column(Text)


class SaleOrderLine(Base):
    __tablename__ = 'sale_order_line'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='sale_order_line_pkey'),
        Index('idx_sol_order', 'order_id'),
        Index('idx_sol_product', 'product_id', postgresql_where='(product_id IS NOT NULL)'),
        Index('idx_sol_product_order', 'product_id', 'order_id'),
        Index('ix_sale_order_line_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_order_id: Mapped[Optional[int]] = mapped_column(Integer)
    product_id: Mapped[Optional[int]] = mapped_column(Integer)
    price_unit: Mapped[Optional[float]] = mapped_column(Double(53))
    product_qty: Mapped[Optional[float]] = mapped_column(Double(53))
    product_uom_qty: Mapped[Optional[float]] = mapped_column(Double(53))
    qty_delivered: Mapped[Optional[float]] = mapped_column(Double(53))
    qty_invoiced: Mapped[Optional[float]] = mapped_column(Double(53))
    price_subtotal: Mapped[Optional[float]] = mapped_column(Double(53))
    discount: Mapped[Optional[float]] = mapped_column(Double(53))
    price_commission: Mapped[Optional[float]] = mapped_column(Double(53))
    order_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[Optional[str]] = mapped_column(Text)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    price_total: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    _sync_session_id: Mapped[Optional[str]] = mapped_column(Text)
    _content_hash: Mapped[Optional[str]] = mapped_column(Text)


class StockLocation(Base):
    __tablename__ = 'stock_location'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='stock_location_pkey'),
        Index('idx_stock_location_location_id', 'location_id')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    complete_name: Mapped[Optional[str]] = mapped_column(Text)
    location_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    company_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    usage: Mapped[Optional[str]] = mapped_column(Text)
    active: Mapped[Optional[bool]] = mapped_column(Boolean)
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    _sync_session_id: Mapped[Optional[str]] = mapped_column(Text)
    _content_hash: Mapped[Optional[str]] = mapped_column(Text)


class StockQuant(Base):
    __tablename__ = 'stock_quant'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='stock_quant_pkey'),
        Index('idx_sq_internal_company_product', 'company_id', 'product_id', postgresql_where="((location_usage)::text = 'internal'::text)"),
        Index('idx_sq_internal_prod_company', 'product_id', 'company_id', postgresql_where="((location_usage)::text = 'internal'::text)"),
        Index('idx_stock_quant_company_product', 'company_id', 'product_id', postgresql_include=['quantity']),
        Index('idx_stock_quant_product', 'product_id'),
        Index('idx_stock_quant_product_loc_company', 'product_id', 'location_id', 'company_id'),
        Index('ix_stock_quant_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity: Mapped[Optional[float]] = mapped_column(Double(53))
    reserved_quantity: Mapped[Optional[float]] = mapped_column(Double(53))
    value: Mapped[Optional[float]] = mapped_column(Double(53))
    create_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    write_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    product_id: Mapped[Optional[int]] = mapped_column(Integer)
    company_id: Mapped[Optional[int]] = mapped_column(Integer)
    location_id: Mapped[Optional[int]] = mapped_column(Integer)
    location_name: Mapped[Optional[str]] = mapped_column(String)
    location_display_name: Mapped[Optional[str]] = mapped_column(String)
    location_usage: Mapped[Optional[str]] = mapped_column(String)
    lot_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    available_quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    _synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))
    _sync_session_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    _content_hash: Mapped[Optional[str]] = mapped_column(Text)


class WarehouseSalesScope(Base):
    __tablename__ = 'warehouse_sales_scope'
    __table_args__ = (
        CheckConstraint("scope_type = ANY (ARRAY['journal'::text, 'company'::text])", name='warehouse_sales_scope_scope_type_check'),
        PrimaryKeyConstraint('warehouse_id', name='warehouse_sales_scope_pkey')
    )

    warehouse_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scope_type: Mapped[str] = mapped_column(Text, nullable=False)
    journal_id: Mapped[Optional[int]] = mapped_column(Integer)
    company_id: Mapped[Optional[int]] = mapped_column(Integer)

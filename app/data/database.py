from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker
from functools import lru_cache
from app.core.config import settings


@lru_cache(maxsize=2)
def get_engine(local: bool = False):
    """
    database engine builder
    """
    if local:
        DB_USER = settings.LOCAL_DB_USER
        DB_PASSWORD = settings.LOCAL_DB_PASSWORD
        DB_HOST = settings.LOCAL_DB_HOST
        DB_PORT = settings.LOCAL_DB_PORT
        DB_NAME = settings.LOCAL_DB_NAME
    else:
        DB_USER = settings.DB_USER
        DB_PASSWORD = settings.DB_PASSWORD
        DB_HOST = settings.DB_HOST
        DB_PORT = settings.DB_PORT
        DB_NAME = settings.DB_NAME
        
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(
        DATABASE_URL,
        pool_size=1,
        max_overflow=1,
        pool_timeout=60,
        pool_pre_ping=True,
    )

    _test_connection(engine)

    return engine

def _test_connection(engine):
    """
    test connection to database
    """
    try:
        with engine.connect() as conn:
            version = conn.scalar(text("SELECT version();"))
            print(f"connected successfully; version {version}")
    except Exception as e:
        print(f"connection failed; reason {e}")
        raise

def canonical_rev_query(select_statement: str, joins: str = "", wheres: str = "", limit: int=None, start_date: str=None, end_date: str=None, signed: bool=True):
    """
    add just the SELECT part of the query;\n \n
    limit, are optional;\n \n
    DO NOT end with comma\n \n
    signed_revnue and signed_quantity are auto added by default set, signed = False to remove\n \n
    if further joins required pass the joins parameter\n \n
    if further filtering required pass the wheres parameter; \n
    write statement assuming where statement has already been passed continue wiith AND...,\n
    for multiple filters continue with AND\n \n
    add start and end date if you want a date slice else leave it empty
    """

    signed_query = f"""
        CASE WHEN ams.move_type = 'out_refund'\n
            THEN -amsl.price_subtotal\n
            ELSE  amsl.price_subtotal\n
        END  AS revenue_signed,\n
        CASE WHEN ams.move_type = 'out_refund'\n
            THEN -amsl.quantity\n
            ELSE  amsl.quantity\n
        END AS qty_signed\n
    """ if signed else ""

    date = f"AND ams.invoice_date >= '{start_date}' AND ams.invoice_date < '{end_date}'\n" if start_date is not None and end_date is not None else ""

    limit = f"LIMIT {limit} \n" if limit is not None else ""

    query = f"""
        SET LOCAL statement_timeout = '2min';
        WITH revenue_accounts AS (\n
            SELECT unnest(ARRAY[{settings.DB_rev_accounts}]) AS account_id\n
        )\n
        {select_statement},\n

        {signed_query}

        FROM account_move_sales_line amsl\n
        JOIN account_move_sales ams ON ams.id = amsl.move_id\n
        JOIN warehouse_sales_scope wss \n
            ON (wss.scope_type = 'journal' AND wss.journal_id = ams.journal_id)\n
            OR (wss.scope_type = 'company' AND wss.company_id = ams.company_id)\n
        {joins}
        WHERE ams.state = 'posted'\n
        AND amsl.account_id IN (SELECT account_id FROM revenue_accounts)\n
        AND ams.partner_id NOT IN ({settings.DB_partners_exclude})\n
        AND ams.id NOT IN ({settings.DB_invoice_exclude})\n
        {wheres}
        {date}
        {limit}
        ;
    """
    return text(query)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

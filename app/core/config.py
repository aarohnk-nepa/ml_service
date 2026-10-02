import os

class Settings:
    def __init__(self):
        # DB creds and truths
        self.DB_HOST = os.environ["DB_HOST"]
        self.DB_PORT = os.environ["DB_PORT"]
        self.DB_USER = os.environ["DB_USER"]
        self.DB_PASSWORD = os.environ["DB_PASSWORD"]
        self.DB_NAME = os.environ["DB_NAME"]

        self.DB_partners_exclude = "15436,1,55657,56001,65388,54176,76773,15310,23364,15308,54095,15421,15,54568,62331"
        self.DB_rev_accounts = "24,636,684,822,1085,1158,1982,205"
        self.DB_van_journals = "332,351,354,375,379,405"
        self.DB_invoice_exclude = "4303730, 4315300"

        # Local DB
        self.LOCAL_DB_HOST = "localhost"
        self.LOCAL_DB_PORT = 5432
        self.LOCAL_DB_USER = "shigpi"
        self.LOCAL_DB_PASSWORD = ""
        self.LOCAL_DB_NAME = "nepa_analytics_dw"

settings = Settings()
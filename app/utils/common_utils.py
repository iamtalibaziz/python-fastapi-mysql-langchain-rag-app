import re

def clean_company_name(company_name: str) -> str:
    """
    Cleans the company name by removing spaces and special characters.
    """
    return re.sub(r'[\s\W]+', '', company_name)

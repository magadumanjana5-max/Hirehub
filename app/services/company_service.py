from app.repositories.company_repository import CompanyRepository


class CompanyService:
    def __init__(self):
        self.companies = CompanyRepository()

    def create_company(self, payload):
        return self.companies.create(payload)

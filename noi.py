from typing import Optional
from dataclasses import dataclass
from textwrap import dedent


@dataclass
class NOI:
    # Income fields
    gross_potential_rent: Optional[float] = None
    vacancy_rate: Optional[float] = None  # as decimal (e.g., 0.05 for 5%)
    collection_loss: Optional[float] = None
    other_income: Optional[float] = None
    
    # Operating Expense fields
    property_taxes: Optional[float] = None
    insurance: Optional[float] = None
    maintenance_repairs: Optional[float] = None
    management_fees: Optional[float] = None
    utilities: Optional[float] = None
    marketing_leasing: Optional[float] = None
    administrative: Optional[float] = None
    contract_services: Optional[float] = None
    
    # Internal calculated values
    _vacancy_loss: float = 0.0
    _effective_gross_income: float = 0.0
    _total_gross_income: float = 0.0
    _total_opEx: float = 0.0
    _noi: float = 0.0

    def _prompt(self, field_name: str, current_value: Optional[float]) -> float:
        """Prompt user for a missing value."""
        display_name = field_name.replace('_', ' ').title()
        if current_value is not None:
            return current_value
        
        while True:
            try:
                value = input(f"{display_name}: $").strip().replace(',', '')
                if value == '':
                    return 0.0
                return float(value)
            except ValueError:
                print("  Please enter a valid number.")

    def calculate(self) -> str:
        """
        Calculate NOI, prompting for any missing values.
        Returns formatted string with results and assumptions.
        """
        print("\n" + "="*50)
        print("REAL ESTATE NOI CALCULATOR")
        print("="*50)
        print("Enter values (press Enter for $0):\n")
        
        # Collect all inputs
        self.gross_potential_rent = self._prompt("Gross Potential Rent", self.gross_potential_rent)
        
        # Vacancy can be entered as rate or absolute dollar amount
        if self.vacancy_rate is None:
            vacancy_input = input("Vacancy Rate % (or enter absolute $ amount): ").strip().replace('%', '')
            if vacancy_input.startswith('$'):
                self._vacancy_loss = float(vacancy_input[1:].replace(',', ''))
                self.vacancy_rate = self._vacancy_loss / self.gross_potential_rent if self.gross_potential_rent else 0
            else:
                try:
                    self.vacancy_rate = float(vacancy_input) / 100 if float(vacancy_input) > 1 else float(vacancy_input)
                except ValueError:
                    self.vacancy_rate = 0.0
                self._vacancy_loss = self.gross_potential_rent * self.vacancy_rate
        else:
            self._vacancy_loss = self.gross_potential_rent * self.vacancy_rate
        
        self.collection_loss = self._prompt("Collection Loss", self.collection_loss)
        self.other_income = self._prompt("Other Income (parking, laundry, etc.)", self.other_income)
        
        # Operating Expenses
        self.property_taxes = self._prompt("Property Taxes", self.property_taxes)
        self.insurance = self._prompt("Insurance", self.insurance)
        self.maintenance_repairs = self._prompt("Maintenance/Repairs", self.maintenance_repairs)
        self.management_fees = self._prompt("Management Fees", self.management_fees)
        self.utilities = self._prompt("Utilities", self.utilities)
        self.marketing_leasing = self._prompt("Marketing/Leasing", self.marketing_leasing)
        self.administrative = self._prompt("Administrative", self.administrative)
        self.contract_services = self._prompt("Contract Services", self.contract_services)
        
        # Calculations
        self._effective_gross_income = self.gross_potential_rent - self._vacancy_loss - (self.collection_loss or 0)
        self._total_gross_income = self._effective_gross_income + (self.other_income or 0)
        
        self._total_opEx = sum([
            self.property_taxes or 0,
            self.insurance or 0,
            self.maintenance_repairs or 0,
            self.management_fees or 0,
            self.utilities or 0,
            self.marketing_leasing or 0,
            self.administrative or 0,
            self.contract_services or 0
        ])
        
        self._noi = self._total_gross_income - self._total_opEx
        
        return self._format_results()

    def _format_currency(self, value: float) -> str:
        return f"${value:,.2f}"

    def _format_results(self) -> str:
        """Return pretty-printed NOI statement."""
        
        # Calculate ratios
        opEx_ratio = (self._total_opEx / self._total_gross_income * 100) if self._total_gross_income else 0
        noi_margin = (self._noi / self._total_gross_income * 100) if self._total_gross_income else 0
        
        report = dedent(f"""
        {'='*60}
                          NOI STATEMENT
        {'='*60}
        
        INCOME
        ──────────────────────────────────────────────────────────
        Gross Potential Rent          {self._format_currency(self.gross_potential_rent):>15}
        Less: Vacancy Loss ({self.vacancy_rate*100:.1f}%)      {self._format_currency(self._vacancy_loss):>15}
        Less: Collection Loss         {self._format_currency(self.collection_loss or 0):>15}
        ──────────────────────────────────────────────────────────
        Effective Gross Income        {self._format_currency(self._effective_gross_income):>15}
        
        Plus: Other Income            {self._format_currency(self.other_income or 0):>15}
        ──────────────────────────────────────────────────────────
        TOTAL GROSS INCOME            {self._format_currency(self._total_gross_income):>15}
        
        OPERATING EXPENSES
        ──────────────────────────────────────────────────────────
        Property Taxes                {self._format_currency(self.property_taxes or 0):>15}
        Insurance                     {self._format_currency(self.insurance or 0):>15}
        Maintenance/Repairs           {self._format_currency(self.maintenance_repairs or 0):>15}
        Management Fees               {self._format_currency(self.management_fees or 0):>15}
        Utilities                     {self._format_currency(self.utilities or 0):>15}
        Marketing/Leasing             {self._format_currency(self.marketing_leasing or 0):>15}
        Administrative                {self._format_currency(self.administrative or 0):>15}
        Contract Services             {self._format_currency(self.contract_services or 0):>15}
        ──────────────────────────────────────────────────────────
        TOTAL OPERATING EXPENSES      {self._format_currency(self._total_opEx):>15}
                                    {'='*30}
        NET OPERATING INCOME          {self._format_currency(self._noi):>15}
                                    {'='*30}
        
        METRICS
        ──────────────────────────────────────────────────────────
        OpEx Ratio:                   {opEx_ratio:>14.1f}%
        NOI Margin:                   {noi_margin:>14.1f}%
        
        {'='*60}
        """).strip()
        
        print(report)
        return report


# Example usage:
if __name__ == "__main__":
    # Option 1: Start with nothing (all prompts)
    deal = NOI()
    deal.calculate()
    
    # Option 2: Pre-fill some known values, prompt for rest
    # deal = NOI(
    #     gross_potential_rent=120000,
    #     property_taxes=8000,
    #     insurance=2400
    # )
    # deal.calculate()
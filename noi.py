from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from textwrap import dedent

@dataclass
class NOI:
    # Income fields
    gross_potential_rent: Optional[float] = None
    vacancy_rate: Optional[float] = None
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

    # Property details for analysis
    purchase_price: Optional[float] = None
    loan_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    loan_term_years: Optional[int] = None

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

    def _prompt_percent(self, field_name: str, current_value: Optional[float]) -> float:
        """Prompt for percentage fields."""
        display_name = field_name.replace('_', ' ').title()
        if current_value is not None:
            return current_value

        while True:
            try:
                value = input(f"{display_name} (%): ").strip().replace('%', '')
                if value == '':
                    return 0.0
                return float(value) / 100
            except ValueError:
                print("  Please enter a valid percentage (e.g., 5 for 5%).")

    def calculate(self) -> str:
        """Calculate NOI and analyze results."""
        print("\n" + "="*50)
        print("REAL ESTATE NOI CALCULATOR")
        print("="*50)
        print("Enter values (press Enter for $0):\n")

        # Collect income inputs
        self.gross_potential_rent = self._prompt("Gross Potential Rent", self.gross_potential_rent)
        self.vacancy_rate = self._prompt_percent("Vacancy Rate", self.vacancy_rate)
        self._vacancy_loss = self.gross_potential_rent * self.vacancy_rate
        self.collection_loss = self._prompt("Collection Loss", self.collection_loss)
        self.other_income = self._prompt("Other Income (parking, laundry, etc.)", self.other_income)

        # Collect expense inputs
        self.property_taxes = self._prompt("Property Taxes", self.property_taxes)
        self.insurance = self._prompt("Insurance", self.insurance)
        self.maintenance_repairs = self._prompt("Maintenance/Repairs", self.maintenance_repairs)
        self.management_fees = self._prompt("Management Fees", self.management_fees)
        self.utilities = self._prompt("Utilities", self.utilities)
        self.marketing_leasing = self._prompt("Marketing/Leasing", self.marketing_leasing)
        self.administrative = self._prompt("Administrative", self.administrative)
        self.contract_services = self._prompt("Contract Services", self.contract_services)

        # Collect financing inputs (for analysis)
        self.purchase_price = self._prompt("Purchase Price (for analysis)", self.purchase_price)
        self.loan_amount = self._prompt("Loan Amount (for analysis)", self.loan_amount)
        if self.loan_amount and self.loan_amount > 0:
            self.interest_rate = self._prompt_percent("Interest Rate", self.interest_rate)
            self.loan_term_years = int(input("Loan Term (years): ") or 30)

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

        # Generate and print results
        noi_statement = self._format_noi_statement()
        analysis = self._analyze_results()

        return f"{noi_statement}\n\n{analysis}"

    def _format_currency(self, value: float) -> str:
        return f"${value:,.2f}"

    def _format_noi_statement(self) -> str:
        """Return pretty-printed NOI statement."""
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
        """).strip()
        return report

    def _analyze_results(self) -> str:
        """Analyze the NOI results in plain English."""
        analysis = []

        # Calculate key metrics
        opEx_ratio = (self._total_opEx / self._total_gross_income * 100) if self._total_gross_income else 0
        noi_margin = (self._noi / self._total_gross_income * 100) if self._total_gross_income else 0

        # Cap Rate Analysis
        cap_rate = (self._noi / self.purchase_price * 100) if self.purchase_price and self.purchase_price > 0 else None

        # DSCR Analysis
        dscr = None
        if self.loan_amount and self.loan_amount > 0 and self.interest_rate and self.loan_term_years:
            monthly_payment = (self.loan_amount * (self.interest_rate/12) * (1 + self.interest_rate/12)**(self.loan_term_years*12)) / ((1 + self.interest_rate/12)**(self.loan_term_years*12) - 1)
            annual_debt_service = monthly_payment * 12
            dscr = self._noi / annual_debt_service

        # 1% Rule Check
        one_percent_rule = self.gross_potential_rent / 12 / (self.purchase_price or 1) >= 0.01 if self.purchase_price else None

        # Start analysis
        analysis.append("\n" + "="*60)
        analysis.append("PLAIN ENGLISH ANALYSIS")
        analysis.append("="*60)

        # NOI Strength
        if self._noi <= 0:
            analysis.append("\n⚠️  CRITICAL WARNING: This property is losing money on operations!")
            analysis.append("   You're spending more to operate the property than it generates in income.")
            analysis.append("   This is only acceptable if you have a clear turnaround plan.")
        elif self._noi < self._total_gross_income * 0.3:
            analysis.append("\n⚠️  CAUTION: This property has thin margins.")
            analysis.append("   Your NOI is less than 30% of gross income, meaning 70%+ is eaten by expenses.")
            analysis.append("   Small increases in expenses or vacancies could wipe out your profits.")
        elif self._noi < self._total_gross_income * 0.5:
            analysis.append("\n✅ SOLID: This property has healthy but not exceptional margins.")
            analysis.append("   Your NOI is 30-50% of gross income, which is typical for well-run properties.")
        else:
            analysis.append("\n💰  EXCELLENT: This property has strong cash flow!")
            analysis.append("   Your NOI is more than 50% of gross income, meaning you keep over half")
            analysis.append("   of every dollar collected after expenses. This is outstanding.")

        # Expense Analysis
        analysis.append(f"\n📊 EXPENSE BREAKDOWN: {opEx_ratio:.1f}% of income goes to operating expenses")
        if opEx_ratio > 60:
            analysis.append("   ⚠️  Your expenses are very high relative to income. Look for ways to:")
            analysis.append("       - Reduce property taxes (appeal assessment)")
            analysis.append("       - Shop for better insurance rates")
            analysis.append("       - Bring maintenance in-house if currently outsourced")
        elif opEx_ratio > 50:
            analysis.append("   🔍 Your expenses are somewhat high. Typical well-run properties")
            analysis.append("     spend 40-50% of income on expenses. Review your largest expense")
            analysis.append(f"     categories (currently: {self._format_currency(self._total_opEx)})")
        else:
            analysis.append("   ✅ Your expenses are well-controlled relative to income")

        # Vacancy Analysis
        analysis.append(f"\n🏠 VACANCY: {self.vacancy_rate*100:.1f}% ({self._format_currency(self._vacancy_loss)})")
        if self.vacancy_rate > 0.15:
            analysis.append("   ⚠️  High vacancy is eating into your profits. Consider:")
            analysis.append("       - Adjusting rent prices")
            analysis.append("       - Improving marketing/leasing efforts")
            analysis.append("       - Property upgrades to attract tenants")
        elif self.vacancy_rate > 0.08:
            analysis.append("   🔍 Your vacancy is moderate. Typical well-managed properties")
            analysis.append("     have 5-8% vacancy. There may be room for improvement.")
        else:
            analysis.append("   ✅ Your vacancy is low - great job keeping units occupied!")

        # Cap Rate Analysis
        if cap_rate:
            analysis.append(f"\n🏢 CAP RATE: {cap_rate:.2f}% (NOI of {self._format_currency(self._noi)} ÷ {self._format_currency(self.purchase_price)} purchase price)")
            if cap_rate < 4:
                analysis.append("   🏆 This is a premium cap rate (low risk, stable asset class like Class A in major cities)")
                analysis.append("   - Expect slower appreciation but very stable income")
                analysis.append("   - Financing will be easy to obtain")
            elif cap_rate < 6:
                analysis.append("   ✅ This is a typical cap rate for good quality properties in decent markets")
                analysis.append("   - Balanced risk/reward profile")
            elif cap_rate < 8:
                analysis.append("   💼 This is a value-add cap rate (higher risk, potential for improvement)")
                analysis.append("   - Property likely needs management/operational improvements")
                analysis.append("   - Potential for forced appreciation")
            else:
                analysis.append("   ⚠️  High cap rate indicates higher risk (distressed property or weak market)")
                analysis.append("   - Due diligence is critical - why is this cap rate so high?")
                analysis.append("   - Potential for high rewards if you can improve operations")

        # 1% Rule
        if one_percent_rule is not None:
            analysis.append(f"\n📏 1% RULE: {'✅ PASSES' if one_percent_rule else '❌ FAILS'}")
            if not one_percent_rule:
                analysis.append("   The monthly rent is less than 1% of purchase price, which may indicate:")
                analysis.append("   - Overpriced property")
                analysis.append("   - Below-market rents that could be increased")
                analysis.append("   - High expense ratios eating into cash flow")

        # DSCR Analysis
        if dscr is not None:
            analysis.append(f"\n🏦 DEBT SERVICE COVERAGE RATIO (DSCR): {dscr:.2f}")
            if dscr < 1.0:
                analysis.append("   ❌ CRITICAL: You cannot cover your debt payments with current NOI!")
                analysis.append("   This property cannot be financed as-is - you need to:")
                analysis.append("   - Increase income (raise rents, reduce vacancy)")
                analysis.append("   - Decrease expenses")
                analysis.append("   - Put more money down to reduce loan amount")
            elif dscr < 1.2:
                analysis.append("   ⚠️  TIGHT: Most lenders want to see at least 1.25x coverage")
                analysis.append("   You might qualify for financing but at less favorable terms")
            elif dscr < 1.5:
                analysis.append("   ✅ GOOD: You comfortably cover your debt payments")
                analysis.append("   Most lenders will be happy with this level of coverage")
            else:
                analysis.append("   💪  STRONG: Excellent debt coverage")
                analysis.append("   You should qualify for the best financing terms")

        # Value-Add Opportunities
        analysis.append("\n🔧 POTENTIAL IMPROVEMENTS:")
        if self.vacancy_rate > 0.05:
            analysis.append("   - Reducing vacancy from {self.vacancy_rate*100:.1f}% to 5% would add {self._format_currency(self.gross_potential_rent * (self.vacancy_rate - 0.05))} to NOI")
        if self.other_income < self.gross_potential_rent * 0.05:
            analysis.append("   - Adding ancillary income (parking, laundry, storage) could boost NOI")
        if self.maintenance_repairs > self.gross_potential_rent * 0.05:
            analysis.append("   - High maintenance costs suggest deferred maintenance - addressing this could improve NOI")
        if self.management_fees > self.gross_potential_rent * 0.06:
            analysis.append("   - Management fees over 6% of GPR may indicate an opportunity for self-management")

        # Final Recommendation
        analysis.append("\n" + "="*60)
        analysis.append("FINAL ASSESSMENT")
        analysis.append("="*60)

        if self._noi <= 0:
            analysis.append("\n❌ AVOID/REHAB REQUIRED: This property loses money operationally.")
            analysis.append("   Only consider if you have a clear plan to dramatically improve income")
            analysis.append("   or reduce expenses.")
        elif cap_rate and cap_rate < 4 and dscr and dscr > 1.5:
            analysis.append("\n🏆 PREMIUM ASSET: Stable, low-risk property with strong cash flow.")
            analysis.append("   - Ideal for conservative investors")
            analysis.append("   - Expect steady but not spectacular returns")
        elif (cap_rate and 4 <= cap_rate < 7) and (dscr and dscr >= 1.2):
            analysis.append("\n✅ SOLID INVESTMENT: Good balance of cash flow and appreciation potential.")
            analysis.append("   - Suitable for most investors")
            analysis.append("   - May benefit from moderate improvements")
        elif cap_rate and cap_rate >= 7 and (dscr and dscr >= 1.2):
            analysis.append("\n💰 VALUE-ADD OPPORTUNITY: Higher risk but with strong cash flow.")
            analysis.append("   - Potential for significant appreciation if you can improve operations")
            analysis.append("   - Requires active management")
        else:
            analysis.append("\n🔍 CAUTIOUS CONSIDERATION: This deal has some red flags.")
            analysis.append("   - May require specialized knowledge or significant improvements")
            analysis.append("   - Conduct thorough due diligence before proceeding")

        return "\n".join(analysis)

# Example usage
if __name__ == "__main__":
    # Start with empty NOI and let it prompt for everything
    deal = NOI()
    results = deal.calculate()
    print(results)
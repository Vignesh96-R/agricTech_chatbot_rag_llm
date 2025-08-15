"""
Centralized constants for the backend layer.
"""

# Role to folder name mapping for resources directory
ROLE_FOLDER_MAPPING = {
    "Agriculture Expert": "agriculture expert",
    "Farmer": "farmer",
    "Field Worker": "field worker",
    "Finance Officer": "finance officer",
    "HR": "hr",
    "Market Analysis": "market analysis",
    "Sales Person": "salesperson",
    "Supply Chain Manager": "supply chain manager",
}

# Role to uploads directory name mapping
UPLOADS_ROLE_MAPPING = {
    "Agriculture Expert": "Agriculture Expert",
    "Farmer": "Farmer",
    "Field Worker": "Field Worker",
    "Finance Officer": "Finance Officer",
    "HR": "HR",
    "Market Analysis": "Market Analysis",
    "Sales Person": "Sales Person",
    "Supply Chain Manager": "Supply Chain Manager",
}

# Domain-specific blocking patterns used for quick access validation
FINANCE_BLOCKING_PATTERNS = (
    "quarterly financial report",
    "revenue analysis",
    "profit margins",
    "budget allocation",
    "investment portfolio",
    "financial statements",
    "cost analysis report",
)

MARKET_BLOCKING_PATTERNS = (
    "market competition analysis",
    "demand forecasting report",
    "supply chain market analysis",
    "competitive pricing analysis",
)

HR_BLOCKING_PATTERNS = (
    "employee salary",
    "personnel records",
    "staffing budget",
    "compensation structure",
    "recruitment pipeline",
)

SUPPLY_CHAIN_BLOCKING_PATTERNS = (
    "warehouse inventory levels",
    "logistics cost analysis",
    "distribution network optimization",
    "transportation contracts",
)

# Agriculture domain context indicators to narrow cross-role checks
AGRICULTURE_CONTEXT_INDICATORS = (
    "crop", "soil", "farming", "agriculture", "harvest", "irrigation",
    "fertilizer", "pesticide", "field", "plant", "seed", "yield", "rice", "wheat",
    "corn", "vegetables", "fruits", "livestock", "poultry", "dairy", "organic",
    "pest control", "weed management", "soil fertility", "crop rotation",
)

# Role-based blocking patterns for RAG validation
ROLE_BLOCKING_PATTERNS = {
    "Admin": [],  # Admin can access everything
    "Agriculture Expert": [
        "employee salary", "personnel records", "hr policies", "financial statements",
        "investment portfolio", "budget allocation", "sales commission", "market pricing",
        "supply chain costs", "crop insurance claims", "farmer payment details",
        "field worker wages", "expert consultation fees", "hr hiring", "payroll",
        "performance review", "market analysis", "supply chain logistics"
    ],
    "Farmer": [
        "employee salary", "personnel records", "hr policies", "financial statements",
        "investment portfolio", "budget allocation", "sales commission", "market pricing",
        "supply chain costs", "crop insurance claims", "field worker wages",
        "expert consultation fees", "hr hiring", "payroll", "performance review",
        "market analysis", "supply chain logistics", "hr recruitment"
    ],
    "Field Worker": [
        "employee salary", "personnel records", "hr policies", "financial statements",
        "investment portfolio", "budget allocation", "sales commission", "market pricing",
        "supply chain costs", "crop insurance claims", "farmer payment details",
        "expert consultation fees", "hr hiring", "payroll", "performance review",
        "market analysis", "supply chain logistics", "hr recruitment"
    ],
    "Finance Officer": [
        "employee salary", "personnel records", "hr policies", "hr hiring",
        "hr recruitment", "performance review", "sales commission", "market pricing",
        "crop insurance claims", "farmer payment details", "field worker wages",
        "expert consultation fees", "agriculture techniques", "crop management",
        "soil fertility", "pest control", "irrigation methods", "harvest techniques"
    ],
    "HR": [
        "financial statements", "investment portfolio", "budget allocation",
        "sales commission", "market pricing", "supply chain costs", "crop insurance",
        "agriculture techniques", "crop management", "soil fertility", "pest control",
        "irrigation methods", "harvest techniques", "crop rotation", "fertilizer",
        "pesticide management", "livestock care", "dairy management"
    ],
    "Market Analysis": [
        "employee salary", "personnel records", "hr policies", "hr hiring",
        "hr recruitment", "payroll", "performance review", "sales commission",
        "crop insurance claims", "farmer payment details", "field worker wages",
        "expert consultation fees", "agriculture techniques", "crop management",
        "soil fertility", "pest control", "irrigation methods", "harvest techniques"
    ],
    "Sales Person": [
        "employee salary", "personnel records", "hr policies", "hr hiring",
        "hr recruitment", "payroll", "performance review", "financial statements",
        "investment portfolio", "budget allocation", "crop insurance claims",
        "farmer payment details", "field worker wages", "expert consultation fees",
        "agriculture techniques", "crop management", "soil fertility", "pest control",
        "irrigation methods", "harvest techniques", "crop rotation"
    ],
    "Supply Chain Manager": [
        "employee salary", "personnel records", "hr policies", "hr hiring",
        "hr recruitment", "payroll", "performance review", "sales commission",
        "market pricing", "crop insurance claims", "farmer payment details",
        "field worker wages", "expert consultation fees", "agriculture techniques",
        "crop management", "soil fertility", "pest control", "irrigation methods",
        "harvest techniques", "crop rotation", "fertilizer management"
    ]
}



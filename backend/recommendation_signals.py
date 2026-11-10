"""Evidence-backed lexical signals for the recommendation relevance screen.

Target references point to the official UN SDG target data stored in
``backend/data/sdg_targets/``. These terms identify possible topical relevance;
they do not establish project impact or verify an SDG contribution.
"""

from typing import Dict, Tuple, TypedDict


class SDGSignalGroup(TypedDict):
    targets: Tuple[str, ...]
    rationale: str
    keywords: Tuple[str, ...]


SDG_SIGNAL_GROUPS: Dict[int, SDGSignalGroup] = {
    1: {
        "targets": ("1.1", "1.3", "1.4", "1.5"),
        "rationale": "Poverty, social protection, access to resources, and resilience.",
        "keywords": (
            "extreme poverty", "income poverty", "poverty line", "poverty reduction",
            "poverty alleviation", "poverty eradication", "social protection",
            "cash transfer", "social safety net", "basic income", "homelessness",
            "economic hardship", "access to basic services",
        ),
    },
    2: {
        "targets": ("2.1", "2.2", "2.3", "2.4"),
        "rationale": "Food access, nutrition, small-scale producers, and sustainable agriculture.",
        "keywords": (
            "food security", "food insecurity", "food assistance", "food bank",
            "malnutrition", "child stunting", "dietary diversity", "smallholder farmer",
            "smallholder farmers", "crop yield", "crop yields", "sustainable agriculture",
            "agricultural productivity", "agroecology", "sustainable food production",
            "food distribution", "food system", "food systems",
        ),
    },
    3: {
        "targets": ("3.1", "3.2", "3.3", "3.4", "3.7", "3.8"),
        "rationale": "Maternal and child health, disease prevention, well-being, and care access.",
        "keywords": (
            "maternal health", "child mortality", "public health", "primary health care",
            "health services", "universal health coverage", "mental health",
            "reproductive health", "vaccine access", "disease surveillance",
            "maternal mortality", "child health", "healthcare access",
            "health care access", "communicable disease", "communicable diseases",
            "non-communicable disease", "non-communicable diseases",
        ),
    },
    4: {
        "targets": ("4.1", "4.3", "4.4", "4.5", "4.6"),
        "rationale": "Inclusive learning, education access, skills, and literacy.",
        "keywords": (
            "learning outcomes", "school attendance", "school completion",
            "early childhood education", "inclusive education", "vocational training",
            "technical education", "digital literacy", "adult literacy",
            "foundational skills", "teacher training", "education access",
            "student learning", "students learn", "online learning", "learning platform",
            "quality education", "education equity", "educational access",
            "education program", "education programme",
        ),
    },
    5: {
        "targets": ("5.1", "5.2", "5.4", "5.5", "5.6"),
        "rationale": (
            "Ending discrimination and violence and advancing women's rights "
            "and participation."
        ),
        "keywords": (
            "gender equality", "gender-based violence", "violence against women",
            "women's rights", "girls' education", "women's leadership",
            "women in leadership", "equal pay", "unpaid care work",
            "reproductive rights", "child marriage", "rights of women and girls",
            "women's economic empowerment",
        ),
    },
    6: {
        "targets": ("6.1", "6.2", "6.3", "6.4"),
        "rationale": "Safe drinking water, sanitation, hygiene, and sustainable water management.",
        "keywords": (
            "safe drinking water", "water access", "water quality", "water scarcity",
            "water treatment", "wastewater treatment", "water reuse",
            "safe water", "water supply", "sanitation", "sanitation services",
            "hygiene promotion", "open defecation", "handwashing facilities",
            "water resource management",
        ),
    },
    7: {
        "targets": ("7.1", "7.2", "7.3"),
        "rationale": "Energy access, renewable sources, and efficiency.",
        "keywords": (
            "energy access", "energy poverty", "clean cooking", "clean energy",
            "renewable energy", "solar power", "wind power", "off-grid electricity",
            "renewable electricity", "clean cooking fuels", "energy services",
            "energy efficiency", "electricity access",
        ),
    },
    8: {
        "targets": ("8.3", "8.5", "8.6", "8.7", "8.8", "8.10"),
        "rationale": (
            "Decent employment, workers' rights, youth employment, and inclusive "
            "economic activity."
        ),
        "keywords": (
            "decent work", "job creation", "youth employment", "living wage",
            "forced labour", "child labour", "human trafficking", "worker rights",
            "labour rights", "informal economy", "financial inclusion",
            "small business", "workers' rights", "decent employment",
            "productive employment", "employment opportunities", "forced labor",
            "child labor", "labor rights", "labor market",
            "workplace safety", "youth unemployment",
        ),
    },
    9: {
        "targets": ("9.1", "9.4", "9.5", "9.a"),
        "rationale": (
            "Resilient infrastructure, sustainable industry, research, and "
            "innovation capacity."
        ),
        "keywords": (
            "resilient infrastructure", "rural infrastructure", "sustainable industry",
            "industrial innovation", "research and development", "technology access",
            "public transport infrastructure", "small-scale industry",
            "disaster-resilient infrastructure", "digital public infrastructure",
            "rural connectivity", "broadband access", "research infrastructure",
        ),
    },
    10: {
        "targets": ("10.2", "10.3", "10.7"),
        "rationale": "Social and economic inclusion, equal opportunity, and safe migration.",
        "keywords": (
            "social inclusion", "equal opportunity", "income inequality",
            "wealth inequality", "disability inclusion", "anti-discrimination",
            "migrant rights", "refugee inclusion", "safe migration",
            "social mobility", "reduced inequalities", "economic inclusion",
            "income disparity", "disability rights", "ethnic discrimination",
        ),
    },
    11: {
        "targets": ("11.1", "11.2", "11.3", "11.5", "11.6", "11.7"),
        "rationale": (
            "Inclusive settlements, housing, mobility, disaster resilience, and "
            "public spaces."
        ),
        "keywords": (
            "affordable housing", "informal settlements", "urban planning",
            "public transport", "sustainable mobility", "disaster risk reduction",
            "urban resilience", "air pollution", "municipal waste",
            "accessible public spaces", "cultural heritage",
            "slum upgrading", "urban green space", "sustainable settlements",
            "sustainable cities", "sustainable urban development", "public space",
        ),
    },
    12: {
        "targets": ("12.2", "12.3", "12.4", "12.5", "12.6", "12.8"),
        "rationale": (
            "Resource efficiency, food loss, waste prevention, and responsible "
            "production and consumption."
        ),
        "keywords": (
            "circular economy", "sustainable consumption", "sustainable production",
            "food waste", "food loss", "hazardous waste", "e-waste recycling",
            "material footprint", "resource efficiency", "supply chain sustainability",
            "sustainable procurement", "plastic waste", "plastic pollution",
            "single-use plastics",
        ),
    },
    13: {
        "targets": ("13.1", "13.2", "13.3"),
        "rationale": "Climate resilience, emissions reduction, adaptation, and climate education.",
        "keywords": (
            "climate change", "climate adaptation", "climate mitigation",
            "climate resilience", "greenhouse gas emissions", "carbon emissions",
            "extreme weather", "climate risk", "climate finance",
            "early warning systems", "climate action", "climate education",
            "greenhouse gas emission",
        ),
    },
    14: {
        "targets": ("14.1", "14.2", "14.4", "14.5", "14.7"),
        "rationale": (
            "Marine pollution, ocean ecosystems, sustainable fisheries, and "
            "coastal livelihoods."
        ),
        "keywords": (
            "marine pollution", "ocean pollution", "marine biodiversity",
            "sustainable fisheries", "overfishing", "coral reef",
            "coastal ecosystem", "ocean acidification", "marine protected area",
            "plastic pollution", "marine conservation", "coastal communities",
            "marine resources",
        ),
    },
    15: {
        "targets": ("15.1", "15.2", "15.3", "15.5", "15.9"),
        "rationale": "Terrestrial ecosystems, forests, land restoration, and biodiversity.",
        "keywords": (
            "biodiversity conservation", "habitat restoration", "forest conservation",
            "deforestation", "land degradation", "desertification",
            "wildlife trafficking", "endangered species", "invasive species",
            "terrestrial ecosystem", "ecosystem restoration", "reforestation",
            "wildlife conservation", "forest restoration",
        ),
    },
    16: {
        "targets": ("16.1", "16.3", "16.5", "16.6", "16.7", "16.10"),
        "rationale": (
            "Safety, access to justice, accountable institutions, and fundamental "
            "freedoms."
        ),
        "keywords": (
            "access to justice", "legal aid", "rule of law", "public accountability",
            "government transparency", "public sector corruption",
            "human rights protection", "press freedom", "civil registration",
            "violence prevention", "peacebuilding", "anti-corruption",
            "access to information", "civic participation",
        ),
    },
    17: {
        "targets": ("17.1", "17.3", "17.6", "17.16", "17.17"),
        "rationale": "Development finance, technology transfer, and cross-sector partnerships.",
        "keywords": (
            "development finance", "official development assistance",
            "technology transfer", "international cooperation",
            "multi-stakeholder partnership", "public-private partnership",
            "south-south cooperation", "capacity building",
            "development partnership", "partnerships for sustainable development",
            "global partnership", "development cooperation",
            "multi stakeholder partnership",
        ),
    },
}

CROSS_CUTTING_SIGNAL_KEYWORDS: Tuple[str, ...] = (
    "underserved communities",
    "low-income households",
    "people with disabilities",
    "persons with disabilities",
    "indigenous peoples",
    "displaced people",
    "human rights",
    "rural livelihoods",
)

EXPLICIT_SDG_KEYWORDS: Tuple[str, ...] = (
    "sdg",
    "sustainable development",
) + tuple(f"goal {number}" for number in range(1, 18))

TECHNICAL_KEYWORDS: Tuple[str, ...] = (
    "python", "javascript", "react", "api", "database", "framework", "library",
    "container", "docker", "cls", "function", "import", "class", "module",
)

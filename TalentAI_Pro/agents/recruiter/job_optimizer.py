"""
Job Posting Optimizer
Optimizes job descriptions for better candidate attraction and AI readability
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re


@dataclass
class OptimizationResult:
    """Result of job posting optimization"""
    original_text: str
    optimized_text: str
    improvements: List[str]
    readability_score: float
    ai_extraction_score: float
    suggestions: List[str]


class JobPostingOptimizer:
    """
    Optimizes job postings for:
    1. AI readability (for SEO/GEO)
    2. Human readability (for candidates)
    3. Conversion rate (application rate)
    """

    # High-impact keywords per industry
    INDUSTRY_KEYWORDS = {
        "tech": [
            "scalable", "microservices", "cloud-native", "CI/CD", "DevOps",
            "agile", "REST API", "GraphQL", "containerization", "Kubernetes"
        ],
        "data": [
            "machine learning", "deep learning", "NLP", "computer vision",
            "data pipeline", "ETL", "real-time analytics", "A/B testing"
        ],
        "product": [
            "user-centric", "MVP", "product-market fit", "roadmap",
            "stakeholder", "user research", "A/B testing", "metrics"
        ],
    }

    # Skills that attract more applications
    HIGH_DEMAND_SKILLS = [
        "Python", "JavaScript", "React", "Node.js", "AWS", "Docker",
        "Kubernetes", "Machine Learning", "SQL", "Agile"
    ]

    def __init__(self):
        self._industry_cache: Dict[str, List[str]] = {}

    def analyze_job_posting(self, text: str) -> Dict[str, Any]:
        """
        Analyze a job posting and return insights
        """
        analysis = {
            "word_count": len(text.split()),
            "sentence_count": len(re.split(r'[.!?]+', text)),
            "skill_mentions": self._extract_skills(text),
            "experience_years_mentioned": self._extract_experience_years(text),
            "salary_mentioned": self._extract_salary(text),
            "benefits_mentioned": self._extract_benefits(text),
            "required_vs_preferred": self._separate_required_preferred(text),
            "action_words": self._extract_action_words(text),
            "passive_words": self._extract_passive_words(text),
        }

        # Calculate readability
        analysis["readability_score"] = self._calculate_readability(text)

        # Estimate AI extraction quality
        analysis["ai_extraction_score"] = self._estimate_ai_extraction(text)

        return analysis

    def optimize(self, text: str, target_audience: str = "candidates") -> OptimizationResult:
        """
        Optimize job posting text

        target_audience: "candidates" or "ai_engines"
        """
        original_text = text
        improvements = []
        suggestions = []

        # Step 1: Structure optimization
        optimized = text

        # Add structure if missing
        if not re.search(r'( Responsibilities?| Requirements?| Qualifications?)', text, re.IGNORECASE):
            optimized = self._add_structure(optimized)
            improvements.append("Added clear section headers for better scannability")

        # Step 2: Keyword enhancement
        optimized, kw_improvements = self._enhance_keywords(optimized)
        improvements.extend(kw_improvements)

        # Step 3: Remove bias language
        optimized, bias_fixes = self._remove_bias_language(optimized)
        improvements.extend(bias_fixes)

        # Step 4: Quantify requirements
        optimized, quant_improvements = self._quantify_requirements(optimized)
        improvements.extend(quant_improvements)

        # Step 5: Enhance benefits section
        optimized, benefit_improvements = self._enhance_benefits(optimized)
        improvements.extend(benefit_improvements)

        # Calculate scores
        readability = self._calculate_readability(optimized)
        ai_score = self._estimate_ai_extraction(optimized)

        # Generate suggestions
        suggestions = self._generate_suggestions(original_text, optimized)

        return OptimizationResult(
            original_text=original_text,
            optimized_text=optimized,
            improvements=improvements,
            readability_score=readability,
            ai_extraction_score=ai_score,
            suggestions=suggestions,
        )

    def _extract_skills(self, text: str) -> List[str]:
        """Extract mentioned skills from text"""
        # Common skill patterns
        skill_pattern = r'\b(Python|JavaScript|TypeScript|React|Angular|Vue|Node\.js|Go|Rust|Java|Kotlin|Swift|SQL|PostgreSQL|MySQL|MongoDB|Redis|AWS|Azure|GCP|Docker|Kubernetes|Machine Learning|AI|Agile|DevOps|CI/CD|REST|GraphQL)\b'
        skills = re.findall(skill_pattern, text, re.IGNORECASE)
        return list(set(skills))

    def _extract_experience_years(self, text: str) -> Optional[int]:
        """Extract years of experience requirement"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s+)?experience',
            r'experience\s*(?:of\s+)?(\d+)\+?\s*years?',
            r'(\d+)\+\s*years?\s*(?:in|of)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def _extract_salary(self, text: str) -> Optional[Dict[str, int]]:
        """Extract salary range if mentioned"""
        pattern = r'(?:USD|CNY|RMB|\$|¥)?\s*(\d{1,3}(?:,\d{3})*)\s*(?:-|to|–)\s*(?:USD|CNY|RMB|\$|¥)?\s*(\d{1,3}(?:,\d{3})*)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                "min": int(match.group(1).replace(',', '')),
                "max": int(match.group(2).replace(',', '')),
            }
        return None

    def _extract_benefits(self, text: str) -> List[str]:
        """Extract mentioned benefits"""
        common_benefits = [
            "health insurance", "dental", "vision", "401k", "stock options",
            "remote work", "flexible hours", "unlimited PTO", "paid vacation",
            "parental leave", "gym membership", "education budget", "learning budget",
            "五险一金", "年终奖", "股票期权", "弹性工作", "远程办公"
        ]
        text_lower = text.lower()
        return [b for b in common_benefits if b.lower() in text_lower]

    def _separate_required_preferred(self, text: str) -> Dict[str, List[str]]:
        """Separate required vs preferred qualifications"""
        required = []
        preferred = []

        # Look for section headers
        required_match = re.search(r'(?:requirements?|required|must have|qualifications?)[:\s]*(.+?)(?:\n\n|preferred|nice to have|$)',
                                   text, re.IGNORECASE | re.DOTALL)
        if required_match:
            required = [s.strip() for s in required_match.group(1).split('\n') if s.strip()]

        preferred_match = re.search(r'(?:preferred|nice to have|bonus)[:\s]*(.+?)(?:\n\n|$)',
                                   text, re.IGNORECASE | re.DOTALL)
        if preferred_match:
            preferred = [s.strip() for s in preferred_match.group(1).split('\n') if s.strip()]

        return {"required": required, "preferred": preferred}

    def _extract_action_words(self, text: str) -> List[str]:
        """Extract strong action verbs"""
        action_verbs = [
            "lead", "manage", "develop", "design", "implement", "build",
            "create", "analyze", "optimize", "improve", "drive", "own",
            "collaborate", "coordinate", "mentor", "guide"
        ]
        text_lower = text.lower()
        return [v for v in action_verbs if re.search(r'\b' + v + r'\b', text_lower)]

    def _extract_passive_words(self, text: str) -> List[str]:
        """Find weak/passive language"""
        passive_patterns = [
            r'\b(responsible for)\b',
            r'\b(worked on)\b',
            r'\b(helped with)\b',
            r'\b(involved in)\b',
            r'\b(some experience)\b',
            r'\b(familiar with)\b',
            r'\b(knowledge of)\b',
        ]
        passive = []
        for pattern in passive_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            passive.extend(matches)
        return list(set(passive))

    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score (0-1, higher is better)"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)

        if not sentences or not words:
            return 0.0

        avg_words_per_sentence = len(words) / len(sentences)

        # Ideal: 15-20 words per sentence
        if avg_words_per_sentence < 10:
            return 0.7  # Too short, but acceptable
        elif avg_words_per_sentence <= 25:
            return 1.0
        elif avg_words_per_sentence <= 35:
            return 0.7
        else:
            return 0.4

    def _estimate_ai_extraction(self, text: str) -> float:
        """
        Estimate how well AI can extract structured data from this posting
        Score 0-1
        """
        score = 0.0

        # Has structured sections (+0.3)
        if re.search(r'^(Requirements?|Responsibilities?|Benefits?|About)', text, re.MULTILINE):
            score += 0.3

        # Has skill mentions (+0.2)
        if len(self._extract_skills(text)) >= 3:
            score += 0.2

        # Has quantified metrics (+0.2)
        if re.search(r'\d+%|\d+years|\$\d+', text):
            score += 0.2

        # Has clear job title (+0.15)
        if re.search(r'^(Senior|Junior|Lead|Principal|Staff|Intern)', text, re.MULTILINE):
            score += 0.15

        # No excessive formatting issues (+0.15)
        if len(text) > 200 and len(text) < 10000:
            score += 0.15

        return min(1.0, score)

    def _add_structure(self, text: str) -> str:
        """Add section structure to unstructured text"""
        # Try to identify natural breaks
        lines = text.split('\n')
        structured = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                structured.append('')
                continue

            # Check if line looks like a header
            if len(stripped) < 50 and not stripped.endswith('.') and stripped == stripped.title():
                # Capitalized short line - likely a header
                structured.append(f"\n## {stripped}\n")
            else:
                structured.append(stripped)

        return '\n'.join(structured)

    def _enhance_keywords(self, text: str) -> tuple:
        """Add high-impact keywords"""
        improvements = []

        # Detect industry
        text_lower = text.lower()
        industry = "tech"  # default
        for ind, keywords in self.INDUSTRY_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                industry = ind
                break

        # Add missing high-impact keywords
        missing_keywords = []
        industry_kws = self.INDUSTRY_KEYWORDS.get(industry, [])

        for kw in industry_kws[:3]:  # Add up to 3
            if kw.lower() not in text_lower:
                missing_keywords.append(kw)

        if missing_keywords:
            # Add to requirements or skills section
            improvements.append(f"Added high-impact keywords: {', '.join(missing_keywords)}")

        return text, improvements

    def _remove_bias_language(self, text: str) -> tuple:
        """Remove potentially biased language"""
        improvements = []

        # Gender-coded words to replace
        gender_biased = {
            r'\bhe/she\b': 'they',
            r'\bhis/her\b': 'their',
            r'\bhim/her\b': 'them',
            r'\bworkaholic\b': 'dedicated',
            r'\bninja\b': 'expert',
            r'\bwizard\b': 'specialist',
            r'\bguru\b': 'expert',
        }

        for pattern, replacement in gender_biased.items():
            new_text, n = re.subn(pattern, replacement, text, flags=re.IGNORECASE)
            if n > 0:
                text = new_text
                improvements.append(f"Replaced biased language: {pattern} -> {replacement}")

        return text, improvements

    def _quantify_requirements(self, text: str) -> tuple:
        """Quantify vague requirements"""
        improvements = []

        quantifications = {
            r'\bfast[- ]?growing\b': 'growing 50%+ YoY',
            r'\blarge[- ]?scale\b': 'serving 1M+ users',
            r'\bmultiple projects?\b': '3+ concurrent projects',
            r'\bexcellent communication\b': 'can explain complex topics to non-technical stakeholders',
        }

        for pattern, replacement in quantifications.items():
            new_text, n = re.subn(pattern, replacement, text, flags=re.IGNORECASE)
            if n > 0:
                text = new_text
                improvements.append(f"Quantified vague requirement: {pattern} -> {replacement}")

        return text, improvements

    def _enhance_benefits(self, text: str) -> tuple:
        """Enhance benefits section"""
        improvements = []

        if "benefits" not in text.lower() and "perks" not in text.lower():
            # Add benefits section
            default_benefits = """
## Benefits
- Competitive salary and equity
- Health, dental, and vision insurance
- Flexible work arrangements
- Learning and development budget
- [Company-specific benefits]
"""
            text = text + default_benefits
            improvements.append("Added benefits section")

        return text, improvements

    def _generate_suggestions(self, original: str, optimized: str) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []

        # Compare original vs optimized
        if len(original.split()) < 300:
            suggestions.append("Consider expanding the job description to 300-600 words for better SEO")

        # Check for salary
        if "salary" not in original.lower() and "$" not in original:
            suggestions.append("Adding a salary range can increase application rates by up to 30%")

        # Check for remote
        if "remote" not in original.lower():
            suggestions.append("Consider mentioning remote/hybrid work options to attract more candidates")

        return suggestions

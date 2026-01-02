#!/usr/bin/env python3
"""
Concept Extractor - Pharmaceutical concept identification and hierarchy building

Extracts key pharmaceutical concepts from educational content including:
- Drug names (brand/generic)
- Mechanisms of action
- Drug classes
- Indications/conditions
- Adverse effects
- Drug interactions
- Pharmacokinetic parameters
- Clinical correlations
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Set, Tuple
from enum import Enum
from collections import defaultdict


class ConceptType(Enum):
    """Types of pharmaceutical concepts."""
    DRUG_NAME = "drug_name"
    DRUG_CLASS = "drug_class"
    MECHANISM = "mechanism"
    INDICATION = "indication"
    ADVERSE_EFFECT = "adverse_effect"
    INTERACTION = "interaction"
    PK_PARAMETER = "pk_parameter"
    DOSING = "dosing"
    MONITORING = "monitoring"
    CONTRAINDICATION = "contraindication"
    CLINICAL_PEARL = "clinical_pearl"
    DEFINITION = "definition"


@dataclass
class Concept:
    """Represents an extracted pharmaceutical concept."""
    name: str
    type: ConceptType
    definition: str = ""
    related_concepts: List[str] = field(default_factory=list)
    source_chunks: List[str] = field(default_factory=list)
    importance: str = "medium"  # low, medium, high, critical
    bloom_level: str = "remember"  # remember, understand, apply, analyze, evaluate, create

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['type'] = self.type.value
        return result


@dataclass
class ConceptHierarchy:
    """Hierarchical organization of concepts."""
    root: str
    children: Dict[str, 'ConceptHierarchy'] = field(default_factory=dict)
    concepts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "children": {k: v.to_dict() for k, v in self.children.items()},
            "concepts": self.concepts
        }

    def to_tree_string(self, prefix: str = "", is_last: bool = True) -> str:
        """Generate tree visualization string."""
        lines = []
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{self.root}")

        child_prefix = prefix + ("    " if is_last else "│   ")

        # Add concepts
        for i, concept in enumerate(self.concepts):
            is_last_item = (i == len(self.concepts) - 1) and not self.children
            item_connector = "└── " if is_last_item else "├── "
            lines.append(f"{child_prefix}{item_connector}• {concept}")

        # Add children
        child_items = list(self.children.items())
        for i, (name, child) in enumerate(child_items):
            is_last_child = i == len(child_items) - 1
            lines.append(child.to_tree_string(child_prefix, is_last_child))

        return "\n".join(lines)


@dataclass
class ExtractionResult:
    """Result of concept extraction."""
    concepts: List[Concept]
    hierarchy: ConceptHierarchy
    statistics: Dict[str, int]
    prerequisites: Dict[str, List[str]]


class ConceptExtractor:
    """
    Extracts and organizes pharmaceutical concepts from educational content.

    Uses pattern matching, keyword detection, and context analysis to
    identify key concepts and build learning hierarchies.
    """

    # Drug class suffixes for identification
    DRUG_CLASS_SUFFIXES = [
        # ACE inhibitors, ARBs
        'pril', 'sartan',
        # Beta blockers
        'olol', 'alol',
        # Calcium channel blockers
        'dipine', 'pamil', 'diltiazem',
        # Statins
        'statin',
        # Proton pump inhibitors
        'prazole',
        # Antibiotics
        'cillin', 'cycline', 'mycin', 'floxacin', 'azole',
        # Antidiabetics
        'gliptin', 'glutide', 'gliflozin', 'glitazone',
        # Anticoagulants
        'xaban', 'gatran',
        # Antipsychotics
        'apine', 'idone', 'piprazole',
        # Benzodiazepines
        'azepam', 'azolam',
        # Opioids
        'done', 'codone', 'morphone',
        # NSAIDs
        'profen', 'oxicam',
        # Corticosteroids
        'sone', 'solone', 'nide',
    ]

    # PK parameter patterns
    PK_PATTERNS = {
        'half_life': r't[½1/2]\s*[=:≈]\s*[\d.]+\s*(?:hr?|hour|min|day)',
        'bioavailability': r'(?:bioavailability|F)\s*[=:≈]\s*[\d.]+\s*%?',
        'volume_distribution': r'V[d]?\s*[=:≈]\s*[\d.]+\s*L(?:/kg)?',
        'clearance': r'(?:Cl|clearance)\s*[=:≈]\s*[\d.]+\s*(?:mL|L)/(?:min|hr)',
        'protein_binding': r'(?:protein binding|PPB)\s*[=:≈]\s*[\d.]+\s*%',
        'cmax': r'C[max]\s*[=:≈]\s*[\d.]+\s*(?:ng|µg|mg)/(?:mL|L)',
        'tmax': r'T[max]\s*[=:≈]\s*[\d.]+\s*(?:hr?|hour|min)',
        'auc': r'AUC\s*[=:≈]\s*[\d.]+',
    }

    # Mechanism keywords
    MECHANISM_KEYWORDS = [
        'inhibit', 'block', 'antagonist', 'agonist', 'activate',
        'stimulate', 'suppress', 'modulate', 'bind', 'receptor',
        'enzyme', 'channel', 'transporter', 'pathway', 'cascade',
        'signal', 'mediate', 'potentiate', 'synergize',
    ]

    # Adverse effect keywords
    ADVERSE_EFFECT_KEYWORDS = [
        'side effect', 'adverse', 'toxicity', 'risk', 'caution',
        'warning', 'contraindicated', 'nausea', 'vomiting', 'diarrhea',
        'headache', 'dizziness', 'fatigue', 'rash', 'hypotension',
        'hypertension', 'bradycardia', 'tachycardia', 'hepatotoxicity',
        'nephrotoxicity', 'ototoxicity', 'cardiotoxicity', 'bleeding',
    ]

    # Clinical pearl indicators
    CLINICAL_PEARL_KEYWORDS = [
        'clinical tip', 'pearl', 'remember', 'important', 'key point',
        'note that', 'always', 'never', 'avoid', 'prefer', 'first-line',
        'drug of choice', 'gold standard', 'monitor for',
    ]

    # Hierarchy templates for pharmacy education
    HIERARCHY_TEMPLATES = {
        'pharmacology': {
            'Pharmacokinetics': ['Absorption', 'Distribution', 'Metabolism', 'Excretion'],
            'Pharmacodynamics': ['Mechanisms', 'Receptor Interactions', 'Dose-Response'],
            'Drug Classes': [],
            'Therapeutics': ['Indications', 'Dosing', 'Monitoring'],
            'Safety': ['Adverse Effects', 'Interactions', 'Contraindications'],
        },
        'therapeutics': {
            'Disease State': ['Pathophysiology', 'Diagnosis', 'Classification'],
            'Treatment': ['Goals', 'Non-pharmacologic', 'Pharmacologic'],
            'Drug Therapy': ['First-line', 'Alternatives', 'Special Populations'],
            'Monitoring': ['Efficacy', 'Safety', 'Adherence'],
        }
    }

    def __init__(
        self,
        drug_database: Optional[Dict[str, Any]] = None,
        custom_patterns: Optional[Dict[str, str]] = None,
        min_concept_length: int = 3,
        max_concept_length: int = 100
    ):
        """
        Initialize concept extractor.

        Args:
            drug_database: Optional database of known drugs
            custom_patterns: Additional regex patterns for extraction
            min_concept_length: Minimum concept name length
            max_concept_length: Maximum concept name length
        """
        self.drug_database = drug_database or {}
        self.custom_patterns = custom_patterns or {}
        self.min_concept_length = min_concept_length
        self.max_concept_length = max_concept_length

        # Compile patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.compiled_pk_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.PK_PATTERNS.items()
        }

        # Drug class suffix pattern
        suffix_pattern = '|'.join(self.DRUG_CLASS_SUFFIXES)
        self.drug_suffix_pattern = re.compile(
            rf'\b[A-Z]?[a-z]*({suffix_pattern})\b',
            re.IGNORECASE
        )

        # Definition patterns
        self.definition_patterns = [
            re.compile(r'([A-Z][^.]+)\s+(?:is|are|refers to|defined as)\s+([^.]+\.)', re.MULTILINE),
            re.compile(r'([A-Z][^:]+):\s+([^.]+\.)', re.MULTILINE),
        ]

    def extract(
        self,
        text: str,
        source_id: Optional[str] = None,
        context_type: str = "pharmacology"
    ) -> ExtractionResult:
        """
        Extract concepts from text.

        Args:
            text: Content to analyze
            source_id: Identifier for the source
            context_type: Type of content (pharmacology, therapeutics)

        Returns:
            ExtractionResult with concepts and hierarchy
        """
        concepts = []
        seen_names = set()

        # Extract different concept types
        concepts.extend(self._extract_drug_names(text, source_id, seen_names))
        concepts.extend(self._extract_mechanisms(text, source_id, seen_names))
        concepts.extend(self._extract_pk_parameters(text, source_id, seen_names))
        concepts.extend(self._extract_adverse_effects(text, source_id, seen_names))
        concepts.extend(self._extract_definitions(text, source_id, seen_names))
        concepts.extend(self._extract_clinical_pearls(text, source_id, seen_names))

        # Build hierarchy
        hierarchy = self._build_hierarchy(concepts, context_type)

        # Calculate prerequisites
        prerequisites = self._calculate_prerequisites(concepts)

        # Generate statistics
        statistics = self._calculate_statistics(concepts)

        return ExtractionResult(
            concepts=concepts,
            hierarchy=hierarchy,
            statistics=statistics,
            prerequisites=prerequisites
        )

    def _extract_drug_names(
        self,
        text: str,
        source_id: Optional[str],
        seen: Set[str]
    ) -> List[Concept]:
        """Extract drug names from text."""
        concepts = []

        # Find drugs by suffix patterns
        for match in self.drug_suffix_pattern.finditer(text):
            name = match.group(0).strip()
            if self._is_valid_concept(name, seen):
                seen.add(name.lower())
                concepts.append(Concept(
                    name=name,
                    type=ConceptType.DRUG_NAME,
                    source_chunks=[source_id] if source_id else [],
                    importance="high",
                    bloom_level="remember"
                ))

        # Check against drug database
        for drug_name in self.drug_database.keys():
            if drug_name.lower() in text.lower() and drug_name.lower() not in seen:
                seen.add(drug_name.lower())
                drug_info = self.drug_database[drug_name]
                concepts.append(Concept(
                    name=drug_name,
                    type=ConceptType.DRUG_NAME,
                    definition=drug_info.get('definition', ''),
                    related_concepts=drug_info.get('related', []),
                    source_chunks=[source_id] if source_id else [],
                    importance="high",
                    bloom_level="remember"
                ))

        return concepts

    def _extract_mechanisms(
        self,
        text: str,
        source_id: Optional[str],
        seen: Set[str]
    ) -> List[Concept]:
        """Extract mechanism of action concepts."""
        concepts = []

        # Find sentences containing mechanism keywords
        sentences = re.split(r'[.!?]', text)

        for sentence in sentences:
            mechanism_score = sum(
                1 for keyword in self.MECHANISM_KEYWORDS
                if keyword.lower() in sentence.lower()
            )

            if mechanism_score >= 2:  # At least 2 mechanism keywords
                # Extract key phrase
                name = self._extract_key_phrase(sentence, "mechanism")
                if name and self._is_valid_concept(name, seen):
                    seen.add(name.lower())
                    concepts.append(Concept(
                        name=name,
                        type=ConceptType.MECHANISM,
                        definition=sentence.strip(),
                        source_chunks=[source_id] if source_id else [],
                        importance="high",
                        bloom_level="understand"
                    ))

        return concepts

    def _extract_pk_parameters(
        self,
        text: str,
        source_id: Optional[str],
        seen: Set[str]
    ) -> List[Concept]:
        """Extract pharmacokinetic parameters."""
        concepts = []

        for param_name, pattern in self.compiled_pk_patterns.items():
            for match in pattern.finditer(text):
                value = match.group(0)
                name = f"{param_name}: {value}"

                if self._is_valid_concept(name, seen, allow_special=True):
                    seen.add(name.lower())
                    concepts.append(Concept(
                        name=name,
                        type=ConceptType.PK_PARAMETER,
                        definition=value,
                        source_chunks=[source_id] if source_id else [],
                        importance="high",
                        bloom_level="apply"
                    ))

        return concepts

    def _extract_adverse_effects(
        self,
        text: str,
        source_id: Optional[str],
        seen: Set[str]
    ) -> List[Concept]:
        """Extract adverse effects and safety information."""
        concepts = []
        sentences = re.split(r'[.!?]', text)

        for sentence in sentences:
            ae_score = sum(
                1 for keyword in self.ADVERSE_EFFECT_KEYWORDS
                if keyword.lower() in sentence.lower()
            )

            if ae_score >= 1:
                name = self._extract_key_phrase(sentence, "adverse_effect")
                if name and self._is_valid_concept(name, seen):
                    seen.add(name.lower())
                    concepts.append(Concept(
                        name=name,
                        type=ConceptType.ADVERSE_EFFECT,
                        definition=sentence.strip(),
                        source_chunks=[source_id] if source_id else [],
                        importance="high",
                        bloom_level="remember"
                    ))

        return concepts

    def _extract_definitions(
        self,
        text: str,
        source_id: Optional[str],
        seen: Set[str]
    ) -> List[Concept]:
        """Extract definitions and key terms."""
        concepts = []

        for pattern in self.definition_patterns:
            for match in pattern.finditer(text):
                term = match.group(1).strip()
                definition = match.group(2).strip()

                if self._is_valid_concept(term, seen):
                    seen.add(term.lower())
                    concepts.append(Concept(
                        name=term,
                        type=ConceptType.DEFINITION,
                        definition=definition,
                        source_chunks=[source_id] if source_id else [],
                        importance="medium",
                        bloom_level="remember"
                    ))

        return concepts

    def _extract_clinical_pearls(
        self,
        text: str,
        source_id: Optional[str],
        seen: Set[str]
    ) -> List[Concept]:
        """Extract clinical pearls and key points."""
        concepts = []
        sentences = re.split(r'[.!?]', text)

        for sentence in sentences:
            pearl_score = sum(
                1 for keyword in self.CLINICAL_PEARL_KEYWORDS
                if keyword.lower() in sentence.lower()
            )

            if pearl_score >= 1:
                # Create a shortened name from the sentence
                name = sentence[:60].strip()
                if len(sentence) > 60:
                    name += "..."

                if self._is_valid_concept(name, seen, allow_special=True):
                    seen.add(name.lower())
                    concepts.append(Concept(
                        name=name,
                        type=ConceptType.CLINICAL_PEARL,
                        definition=sentence.strip(),
                        source_chunks=[source_id] if source_id else [],
                        importance="high",
                        bloom_level="apply"
                    ))

        return concepts

    def _extract_key_phrase(self, sentence: str, concept_type: str) -> Optional[str]:
        """Extract a key phrase from a sentence to use as concept name."""
        # Remove common stopwords and extract meaningful phrase
        sentence = sentence.strip()

        # Limit to reasonable length
        if len(sentence) > 80:
            # Find a natural break point
            break_points = [
                sentence.find(','),
                sentence.find(';'),
                sentence.find(' - '),
            ]
            break_point = min(p for p in break_points if p > 20) if any(p > 20 for p in break_points) else 80
            sentence = sentence[:break_point].strip()

        return sentence if sentence else None

    def _is_valid_concept(
        self,
        name: str,
        seen: Set[str],
        allow_special: bool = False
    ) -> bool:
        """Check if concept name is valid."""
        if not name:
            return False

        name_lower = name.lower()

        # Check length
        if len(name) < self.min_concept_length or len(name) > self.max_concept_length:
            return False

        # Check if already seen
        if name_lower in seen:
            return False

        # Check for stopwords (unless special allowed)
        if not allow_special:
            stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been'}
            if name_lower in stopwords:
                return False

        return True

    def _build_hierarchy(
        self,
        concepts: List[Concept],
        context_type: str
    ) -> ConceptHierarchy:
        """Build concept hierarchy from extracted concepts."""
        # Use template for context type
        template = self.HIERARCHY_TEMPLATES.get(context_type, self.HIERARCHY_TEMPLATES['pharmacology'])

        # Create root
        root = ConceptHierarchy(root="Pharmaceutical Concepts")

        # Group concepts by type
        by_type = defaultdict(list)
        for concept in concepts:
            by_type[concept.type].append(concept)

        # Map concept types to hierarchy categories
        type_to_category = {
            ConceptType.DRUG_NAME: "Drug Classes",
            ConceptType.DRUG_CLASS: "Drug Classes",
            ConceptType.MECHANISM: "Pharmacodynamics",
            ConceptType.PK_PARAMETER: "Pharmacokinetics",
            ConceptType.ADVERSE_EFFECT: "Safety",
            ConceptType.INTERACTION: "Safety",
            ConceptType.CONTRAINDICATION: "Safety",
            ConceptType.INDICATION: "Therapeutics",
            ConceptType.DOSING: "Therapeutics",
            ConceptType.MONITORING: "Therapeutics",
            ConceptType.CLINICAL_PEARL: "Clinical Pearls",
            ConceptType.DEFINITION: "Definitions",
        }

        # Build hierarchy
        for category, subcategories in template.items():
            category_node = ConceptHierarchy(root=category)

            # Add subcategories
            for subcategory in subcategories:
                subcategory_node = ConceptHierarchy(root=subcategory)
                category_node.children[subcategory] = subcategory_node

            # Add concepts to appropriate category
            for concept_type, concepts_of_type in by_type.items():
                if type_to_category.get(concept_type) == category:
                    for concept in concepts_of_type:
                        category_node.concepts.append(concept.name)

            if category_node.concepts or category_node.children:
                root.children[category] = category_node

        # Add any unmapped concepts
        unmapped = ConceptHierarchy(root="Other")
        for concept_type, concepts_of_type in by_type.items():
            if type_to_category.get(concept_type) not in template:
                for concept in concepts_of_type:
                    unmapped.concepts.append(concept.name)

        if unmapped.concepts:
            root.children["Other"] = unmapped

        return root

    def _calculate_prerequisites(
        self,
        concepts: List[Concept]
    ) -> Dict[str, List[str]]:
        """Calculate prerequisite relationships between concepts."""
        prerequisites = {}

        # Basic prerequisite rules for pharmacy
        prerequisite_rules = {
            ConceptType.MECHANISM: [ConceptType.DRUG_NAME, ConceptType.DRUG_CLASS],
            ConceptType.PK_PARAMETER: [ConceptType.DRUG_NAME],
            ConceptType.ADVERSE_EFFECT: [ConceptType.DRUG_NAME, ConceptType.MECHANISM],
            ConceptType.INTERACTION: [ConceptType.DRUG_NAME, ConceptType.MECHANISM],
            ConceptType.DOSING: [ConceptType.DRUG_NAME, ConceptType.PK_PARAMETER],
            ConceptType.MONITORING: [ConceptType.DRUG_NAME, ConceptType.ADVERSE_EFFECT],
        }

        # Index concepts by type
        by_type = defaultdict(list)
        for concept in concepts:
            by_type[concept.type].append(concept.name)

        # Calculate prerequisites
        for concept in concepts:
            if concept.type in prerequisite_rules:
                prereq_types = prerequisite_rules[concept.type]
                prereqs = []
                for prereq_type in prereq_types:
                    prereqs.extend(by_type.get(prereq_type, [])[:3])  # Limit to 3 per type

                if prereqs:
                    prerequisites[concept.name] = prereqs

        return prerequisites

    def _calculate_statistics(self, concepts: List[Concept]) -> Dict[str, int]:
        """Calculate statistics about extracted concepts."""
        stats = {
            "total_concepts": len(concepts),
            "by_type": {},
            "by_importance": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "by_bloom_level": {},
        }

        for concept in concepts:
            # By type
            type_name = concept.type.value
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1

            # By importance
            stats["by_importance"][concept.importance] += 1

            # By Bloom's level
            stats["by_bloom_level"][concept.bloom_level] = stats["by_bloom_level"].get(concept.bloom_level, 0) + 1

        return stats


def main():
    """CLI interface for concept extractor."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract pharmaceutical concepts from educational content"
    )
    parser.add_argument("input", help="Input file or text")
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "tree"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--context",
        choices=["pharmacology", "therapeutics"],
        default="pharmacology",
        help="Content context type"
    )

    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if input_path.exists():
        text = input_path.read_text()
        source_id = input_path.name
    else:
        text = args.input
        source_id = "cli_input"

    # Extract concepts
    extractor = ConceptExtractor()
    result = extractor.extract(text, source_id, args.context)

    # Format output
    if args.format == "json":
        output = json.dumps({
            "concepts": [c.to_dict() for c in result.concepts],
            "hierarchy": result.hierarchy.to_dict(),
            "statistics": result.statistics,
            "prerequisites": result.prerequisites
        }, indent=2)
    elif args.format == "tree":
        output = result.hierarchy.to_tree_string()
    else:  # markdown
        lines = ["# Extracted Concepts\n"]
        lines.append(f"**Total concepts**: {result.statistics['total_concepts']}\n")

        lines.append("\n## Concepts by Type\n")
        for concept_type, count in result.statistics['by_type'].items():
            lines.append(f"- {concept_type}: {count}")

        lines.append("\n\n## Concept Hierarchy\n")
        lines.append("```")
        lines.append(result.hierarchy.to_tree_string())
        lines.append("```")

        lines.append("\n\n## Detailed Concepts\n")
        for concept in result.concepts:
            lines.append(f"\n### {concept.name}")
            lines.append(f"- **Type**: {concept.type.value}")
            lines.append(f"- **Importance**: {concept.importance}")
            lines.append(f"- **Bloom's Level**: {concept.bloom_level}")
            if concept.definition:
                lines.append(f"- **Definition**: {concept.definition}")

        output = "\n".join(lines)

    # Write output
    if args.output:
        Path(args.output).write_text(output)
        print(f"Written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()

"""Debate Orchestrator

Coordinates multi-LLM debates with constitutional rules.
"""
from __future__ import annotations

import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .debate_tree import (
    DebateTree,
    DebateRound,
    Claim,
    Challenge,
    Consensus,
    Dissent,
    Evidence,
    ModelType,
    create_debate_id
)
from .charter import Charter
from .debater import Debater, create_debater
from .config import Config as MainConfig


@dataclass
class DebateConfig:
    """Configuration for a debate."""
    models: List[ModelType]
    workspace: str
    max_rounds: int = 3
    enable_memory: bool = True
    memory_top_k: int = 10
    consensus_threshold: float = 0.75


class Orchestrator:
    """Orchestrates constitutional debates between multiple LLMs."""

    def __init__(self, charter: Charter, config: DebateConfig, main_config: MainConfig):
        self.charter = charter
        self.config = config
        self.main_config = main_config

        # Create debaters
        self.debaters: Dict[ModelType, Debater] = {}
        for model_type in config.models:
            self.debaters[model_type] = create_debater(model_type, main_config, charter)

        # Evidence memory (will integrate with Adaptive Memory)
        self.evidence_cache: Dict[str, List[Evidence]] = {}

    async def start_debate(self, query: str) -> DebateTree:
        """Start a new debate.

        Args:
            query: The question to debate

        Returns:
            DebateTree with initial round
        """
        debate_id = create_debate_id()
        tree = DebateTree(
            debate_id=debate_id,
            query=query,
            workspace=self.config.workspace
        )

        # Run initial round
        await self.run_round(tree, round_num=0)

        return tree

    async def run_round(self, tree: DebateTree, round_num: int) -> DebateRound:
        """Run a single debate round.

        Round types:
        - Round 0: Initial claims
        - Round 1+: Challenges and refinements
        - Final: Consensus building

        Args:
            tree: Debate tree
            round_num: Round number

        Returns:
            DebateRound with new nodes
        """
        round_obj = tree.add_round(round_num)

        if round_num == 0:
            # Round 0: Initial claims from all models
            await self._round_initial_claims(tree, round_obj)
        else:
            # Round 1+: Challenges and refinements
            await self._round_challenges(tree, round_obj)

        # Check for consensus
        await self._check_consensus(tree, round_obj)

        return round_obj

    async def _round_initial_claims(self, tree: DebateTree, round_obj: DebateRound) -> None:
        """Round 0: Collect initial claims from all models."""
        # Get evidence from memory if enabled
        evidence_pool = await self._get_evidence_from_memory(tree.query)

        # Generate claims in parallel
        claim_tasks = []
        for model_type, debater in self.debaters.items():
            task = debater.generate_claim(
                query=tree.query,
                evidence_pool=evidence_pool
            )
            claim_tasks.append((model_type, task))

        # Collect claims
        claims = []
        for model_type, task in claim_tasks:
            claim = await task
            tree.add_node(claim, round_num=round_obj.round_num)
            claims.append(claim)

            # Validate against charter
            validation = self.charter.validate_claim(claim)
            if not validation.is_valid:
                print(f"Warning: Claim from {model_type.value} violates rules: {validation.violations}")

        print(f"Round {round_obj.round_num}: Collected {len(claims)} initial claims")

    async def _round_challenges(self, tree: DebateTree, round_obj: DebateRound) -> None:
        """Round 1+: Generate challenges to previous round's claims."""
        # Get previous round's claims
        prev_round = tree.get_round(round_obj.round_num - 1)
        if not prev_round:
            return

        prev_claims = prev_round.get_claims()
        if not prev_claims:
            return

        # Get evidence pool
        evidence_pool = await self._get_evidence_from_memory(tree.query)

        # Build context from previous rounds
        context = self._build_context(tree, round_obj.round_num)

        # Each model reviews previous claims and may challenge
        challenge_tasks = []
        for model_type, debater in self.debaters.items():
            for claim in prev_claims:
                # Don't challenge own claims
                if claim.model == model_type:
                    continue

                task = debater.generate_challenge(
                    target_claim=claim,
                    context=context,
                    evidence_pool=evidence_pool
                )
                challenge_tasks.append((model_type, claim, task))

        # Collect challenges
        challenges = []
        for model_type, target_claim, task in challenge_tasks:
            challenge = await task
            if challenge:  # Only add if model actually challenges
                challenge.target_id = target_claim.node_id
                tree.add_node(challenge, round_num=round_obj.round_num)
                challenges.append(challenge)

                # Validate
                validation = self.charter.validate_challenge(challenge, tree.nodes)
                if not validation.is_valid:
                    print(f"Warning: Challenge from {model_type.value} violates rules: {validation.violations}")

        print(f"Round {round_obj.round_num}: Generated {len(challenges)} challenges")

    async def _check_consensus(self, tree: DebateTree, round_obj: DebateRound) -> None:
        """Check if consensus has been reached."""
        claims = round_obj.get_claims()
        if not claims:
            return

        # Simple consensus detection: group similar positions
        # TODO: Use embeddings to cluster similar claims
        # For now, use placeholder logic

        position_groups = self._group_claims_by_position(claims)

        # Find largest group
        largest_group = max(position_groups, key=lambda g: len(position_groups[g]))
        supporting_models = position_groups[largest_group]

        agreement_pct = (len(supporting_models) / len(self.debaters)) * 100

        if agreement_pct >= self.config.consensus_threshold * 100:
            # We have consensus
            consensus = Consensus(
                consensus_id=f"consensus_{round_obj.round_num}",
                position=largest_group,
                supporting_models=supporting_models,
                supporting_evidence=self._collect_evidence(claims, supporting_models),
                agreement_pct=agreement_pct,
                round_reached=round_obj.round_num
            )

            # Validate consensus
            validation = self.charter.validate_consensus(
                consensus,
                total_models=len(self.debaters)
            )

            if validation.is_valid:
                round_obj.consensus = consensus
                print(f"Consensus reached: {agreement_pct:.0f}% agreement on '{consensus.position}'")

                # Document dissents
                dissenting_models = set(self.debaters.keys()) - set(supporting_models)
                for model in dissenting_models:
                    # TODO: Ask dissenting models to document their disagreement
                    pass

    def _group_claims_by_position(self, claims: List[Claim]) -> Dict[str, List[ModelType]]:
        """Group claims by similar positions.

        TODO: Use embeddings for semantic similarity
        For now, use simple string matching
        """
        groups = {}
        for claim in claims:
            position = claim.position or claim.content[:50]  # Use position or first 50 chars

            # Simple grouping (TODO: improve with embeddings)
            if position not in groups:
                groups[position] = []
            groups[position].append(claim.model)

        return groups

    def _collect_evidence(self, claims: List[Claim], supporting_models: List[ModelType]) -> List[Evidence]:
        """Collect all evidence from supporting claims."""
        all_evidence = []
        seen_sources = set()

        for claim in claims:
            if claim.model in supporting_models:
                for ev in claim.evidence:
                    if ev.source not in seen_sources:
                        all_evidence.append(ev)
                        seen_sources.add(ev.source)

        return all_evidence

    def _build_context(self, tree: DebateTree, up_to_round: int) -> str:
        """Build context string from previous rounds."""
        lines = [f"Debate: {tree.query}\n"]

        for i in range(up_to_round):
            round_obj = tree.get_round(i)
            if not round_obj:
                continue

            lines.append(f"\nRound {i}:")

            # Add claims
            for claim in round_obj.get_claims():
                lines.append(f"- {claim.model.value}: {claim.content}")

            # Add challenges
            for challenge in round_obj.get_challenges():
                lines.append(f"- {challenge.model.value} challenges: {challenge.content}")

        return "\n".join(lines)

    async def _get_evidence_from_memory(self, query: str) -> List[Evidence]:
        """Get relevant evidence from Adaptive Memory.

        TODO: Integrate with actual Adaptive Memory
        """
        # Check cache
        if query in self.evidence_cache:
            return self.evidence_cache[query]

        # TODO: Query Adaptive Memory
        # For now, return empty list
        evidence_pool = []

        self.evidence_cache[query] = evidence_pool
        return evidence_pool

    async def run_full_debate(self, query: str) -> DebateTree:
        """Run a complete debate with all configured rounds.

        Args:
            query: The question to debate

        Returns:
            Completed DebateTree with consensus or documented dissent
        """
        tree = await self.start_debate(query)

        # Run remaining rounds
        for round_num in range(1, self.config.max_rounds):
            # Check if consensus reached
            current_round = tree.get_current_round()
            if current_round and current_round.consensus:
                print(f"Consensus reached in round {round_num - 1}. Stopping debate.")
                break

            await self.run_round(tree, round_num)

        # Final consensus check
        final_round = tree.get_current_round()
        if final_round and final_round.consensus:
            tree.final_consensus = final_round.consensus

        # Validate full tree
        validation = self.charter.validate_debate_tree(tree)
        print(f"\nDebate constitutional compliance: {validation.score:.2f}")
        if validation.violations:
            print(f"Violations: {validation.violations}")

        return tree

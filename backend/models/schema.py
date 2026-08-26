from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

DatasetLabel = Literal["public_source", "demo_sample"]
RecordStatus = Literal["included", "excluded"]
ClaimType = Literal["FACT", "PATTERN", "HYPOTHESIS", "OPPORTUNITY"]


class Observation(BaseModel):
    observation_id: str
    source: str
    source_id: str
    source_url: str
    date: Optional[str] = None
    rating: Optional[float] = None
    title: Optional[str] = None
    text_original: str
    text_clean: str = ""
    language: Optional[str] = None
    translated_text: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    collected_at: str
    dataset_label: DatasetLabel = "public_source"


class QualityRecord(BaseModel):
    observation_id: str
    status: RecordStatus
    reason: Optional[str] = None
    stage: str
    notes: Optional[str] = None


class RelevanceResult(BaseModel):
    observation_id: str
    relevant_to_discovery: bool
    relevance_categories: list[str] = Field(default_factory=list)
    relevance_rationale: str = ""
    confidence: float = 0.0
    method: str = "heuristic"


class BehavioralExtraction(BaseModel):
    observation_id: str
    user_intent: str = "unclear"
    wishlist_behavior: str = "no evidence"
    consider_reasons: list[str] = Field(default_factory=list)
    purchase_outcome: str = "unknown"
    barriers: list[str] = Field(default_factory=list)
    uncertainty_present: bool = False
    uncertainty_type: list[str] = Field(default_factory=list)
    uncertainty_description: Optional[str] = None
    workaround_present: bool = False
    workaround_type: list[str] = Field(default_factory=list)
    workaround_description: Optional[str] = None
    external_platform: list[str] = Field(default_factory=list)
    external_research: bool = False
    external_research_platform: list[str] = Field(default_factory=list)
    external_research_purpose: list[str] = Field(default_factory=list)
    segment_signals: list[str] = Field(default_factory=list)
    evidence_spans: dict[str, list[str]] = Field(default_factory=dict)
    method: str = "heuristic"
    confidence: float = 0.0


class Theme(BaseModel):
    theme_id: str
    theme_name: str
    description: str
    frequency: int = 0
    frequency_percentage: float = 0.0
    source_count: int = 0
    source_diversity: list[str] = Field(default_factory=list)
    segments: list[str] = Field(default_factory=list)
    purchase_outcomes: dict[str, int] = Field(default_factory=dict)
    barriers: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    workarounds: list[str] = Field(default_factory=list)
    external_research: list[str] = Field(default_factory=list)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    confidence: str = "low"
    confidence_score: float = 0.0
    research_gap: str = ""
    potential_user_value: str = ""
    potential_business_relevance: str = ""
    claim_type: ClaimType = "PATTERN"
    cluster_id: Optional[int] = None


class Opportunity(BaseModel):
    opportunity_id: str
    rank: int = 0
    title: str
    description: str
    theme_ids: list[str] = Field(default_factory=list)
    frequency: int = 0
    frequency_percentage: float = 0.0
    purchase_association: float = 0.0
    postponement_association: float = 0.0
    abandonment_association: float = 0.0
    alternative_purchase_association: float = 0.0
    user_segment: list[str] = Field(default_factory=list)
    evidence_strength: float = 0.0
    confidence: str = "low"
    confidence_score: float = 0.0
    existing_workaround: list[str] = Field(default_factory=list)
    research_gap: str = ""
    scores: dict[str, float] = Field(default_factory=dict)
    composite_score: float = 0.0
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    claim_type: ClaimType = "OPPORTUNITY"
    why_ranked_higher: str = ""
    scoring_notes: str = ""


class SegmentProfile(BaseModel):
    segment_id: str
    name: str
    definition: str
    observation_count: int = 0
    percentage: float = 0.0
    major_barriers: list[str] = Field(default_factory=list)
    major_uncertainties: list[str] = Field(default_factory=list)
    workarounds: list[str] = Field(default_factory=list)
    external_research: list[str] = Field(default_factory=list)
    purchase_outcomes: dict[str, int] = Field(default_factory=dict)
    dominant_opportunity_themes: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    discovered: bool = True

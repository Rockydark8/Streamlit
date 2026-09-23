from typing import List, Optional
from pydantic import BaseModel, Field

# --- INPUT SCHEMAS FROM MILESTONES 1 & 2 ---

class BugSubmission(BaseModel):
    bug_id: str
    title: str
    description: str

class TriageOutput(BaseModel):
    severity: str
    priority: str
    affected_component: str
    confidence_score: float
    reasoning: str

class LogAnalysisOutput(BaseModel):
    exception_type: Optional[str] = None
    error_message: Optional[str] = None
    failure_point: Optional[str] = None
    affected_code_path: Optional[str] = None
    confidence_score: float

class PipelineInput(BaseModel):
    submission: BugSubmission
    triage: TriageOutput
    log_analysis: LogAnalysisOutput

# --- HISTORICAL KNOWLEDGE BASE SCHEMA ---

class HistoricalDefect(BaseModel):
    defect_id: str
    title: str
    description: str
    affected_component: str
    exception_type: Optional[str] = None
    root_cause: str
    resolution_summary: str
    code_path: Optional[str] = None

# --- AGENT OUTPUT SCHEMAS (M3.1, M3.2, M3.3) ---

class RootCauseHypothesis(BaseModel):
    hypothesis: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    retrieved_evidence: List[str]
    agent_reasoning: str

class RootCauseOutput(BaseModel):
    hypotheses: List[RootCauseHypothesis]
    top_confidence_score: float
    status: str = "Success"

class DuplicateMatch(BaseModel):
    defect_id: str
    title: str
    affected_component: str
    similarity_score: float
    root_cause: str
    resolution_summary: str
    match_reasoning: str

class DuplicateDetectionOutput(BaseModel):
    duplicate_status: str  # "Likely Duplicate", "Related Issue", "New/Unmatched Issue"
    top_matches: List[DuplicateMatch]

class RemediationOption(BaseModel):
    recommendation: str
    target_module_or_file: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    source_type: str  # "Historical Evidence" or "General Best Practice"
    supporting_references: List[str]
    validation_steps: List[str]

class RemediationOutput(BaseModel):
    options: List[RemediationOption]
    status: str = "Success"

# --- AGGREGATED REPORT SCHEMA (M3.4) ---

class ComprehensiveDiagnosisReport(BaseModel):
    input_data: PipelineInput
    root_cause_analysis: RootCauseOutput
    duplicate_detection: DuplicateDetectionOutput
    remediation_plan: RemediationOutput
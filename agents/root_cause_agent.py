from models import PipelineInput, RootCauseOutput, RootCauseHypothesis
from vector_store import KnowledgeBase

class RootCauseAgent:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def analyze(self, pipeline_input: PipelineInput) -> RootCauseOutput:
        # Construct retrieval query
        query = (
            f"{pipeline_input.submission.title} "
            f"{pipeline_input.triage.affected_component} "
            f"{pipeline_input.log_analysis.exception_type or ''} "
            f"{pipeline_input.log_analysis.error_message or ''}"
        )

        matches = self.kb.query_similar_defects(query, top_k=2)

        if not matches or matches[0][1] < 0.30:
            return RootCauseOutput(
                hypotheses=[],
                top_confidence_score=0.0,
                status="Insufficient Evidence"
            )

        hypotheses = []
        for defect, similarity in matches:
            reasoning = (
                f"Assessed failure mode in '{pipeline_input.log_analysis.affected_code_path or 'unknown module'}' "
                f"matching exception class '{pipeline_input.log_analysis.exception_type}'. "
                f"Historical record {defect.defect_id} demonstrates an identical root cause pattern."
            )

            evidence = [
                f"Retrieved Record [{defect.defect_id}]: {defect.title}",
                f"KB Root Cause: {defect.root_cause}",
                f"Historical Affected Path: {defect.code_path}"
            ]

            confidence = round(min(0.95, similarity * 1.1), 2)

            hypotheses.append(
                RootCauseHypothesis(
                    hypothesis=f"Probable failure in {defect.affected_component}: {defect.root_cause}",
                    confidence_score=confidence,
                    retrieved_evidence=evidence,
                    agent_reasoning=reasoning
                )
            )

        top_conf = max(h.confidence_score for h in hypotheses)
        return RootCauseOutput(
            hypotheses=hypotheses,
            top_confidence_score=top_conf,
            status="Success"
        )
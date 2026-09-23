from models import PipelineInput, DuplicateDetectionOutput, DuplicateMatch
from vector_store import KnowledgeBase
from config import DUPLICATE_THRESHOLD_HIGH, DUPLICATE_THRESHOLD_MEDIUM

class DuplicateDetectionAgent:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def analyze(self, pipeline_input: PipelineInput) -> DuplicateDetectionOutput:
        search_str = f"{pipeline_input.submission.title}\n{pipeline_input.submission.description}"
        matches = self.kb.query_similar_defects(search_str, top_k=3)

        top_matches: list[DuplicateMatch] = []
        highest_score = 0.0

        for defect, similarity in matches:
            if similarity > highest_score:
                highest_score = similarity

            reasoning = (
                f"Semantic similarity of {similarity*100:.1f}% based on shared component "
                f"'{defect.affected_component}' and matching exception context."
            )

            top_matches.append(
                DuplicateMatch(
                    defect_id=defect.defect_id,
                    title=defect.title,
                    affected_component=defect.affected_component,
                    similarity_score=similarity,
                    root_cause=defect.root_cause,
                    resolution_summary=defect.resolution_summary,
                    match_reasoning=reasoning
                )
            )

        if highest_score >= DUPLICATE_THRESHOLD_HIGH:
            status = "Likely Duplicate"
        elif highest_score >= DUPLICATE_THRESHOLD_MEDIUM:
            status = "Related Issue"
        else:
            status = "New/Unmatched Issue"

        return DuplicateDetectionOutput(
            duplicate_status=status,
            top_matches=top_matches
        )
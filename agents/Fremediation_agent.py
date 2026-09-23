from models import PipelineInput, RootCauseOutput, DuplicateDetectionOutput, RemediationOutput, RemediationOption

class RemediationAgent:
    def analyze(
        self,
        pipeline_input: PipelineInput,
        root_cause_output: RootCauseOutput,
        duplicate_output: DuplicateDetectionOutput
    ) -> RemediationOutput:
        
        if root_cause_output.status == "Insufficient Evidence" or not root_cause_output.hypotheses:
            return RemediationOutput(
                options=[
                    RemediationOption(
                        recommendation="Perform additional manual debugging and capture full thread stack trace.",
                        target_module_or_file=pipeline_input.log_analysis.affected_code_path or "Unknown",
                        confidence_score=0.30,
                        source_type="General Best Practice",
                        supporting_references=["Standard Operational Playbook - Diagnostic Logs"],
                        validation_steps=[
                            "Enable DEBUG log level on affected module",
                            "Reproduce issue with test payload"
                        ]
                    )
                ],
                status="Insufficient Evidence"
            )

        options = []
        top_hypothesis = root_cause_output.hypotheses[0]
        
        # Grounding recommendation on top matching duplicate or historical evidence if available
        matched_resolution = None
        ref_id = "Generic"
        if duplicate_output.top_matches:
            top_match = duplicate_output.top_matches[0]
            matched_resolution = top_match.resolution_summary
            ref_id = top_match.defect_id

        if matched_resolution:
            rec = f"Apply historical fix pattern from [{ref_id}]: {matched_resolution}"
            source_type = "Historical Evidence"
            refs = [f"Historical Defect Record: {ref_id}"]
            conf = min(0.92, top_hypothesis.confidence_score)
        else:
            rec = f"Implement defensive error handling and null-guards around: {top_hypothesis.hypothesis}"
            source_type = "General Best Practice"
            refs = ["Software Architecture Quality Guidelines v2.1"]
            conf = 0.65

        options.append(
            RemediationOption(
                recommendation=rec,
                target_module_or_file=pipeline_input.log_analysis.affected_code_path or pipeline_input.triage.affected_component,
                confidence_score=conf,
                source_type=source_type,
                supporting_references=refs,
                validation_steps=[
                    "Write regression unit test covering missing/malformed parameter payload.",
                    "Verify exception is caught cleanly and converted to proper error contract.",
                    "Run regression test suite across affected integration endpoints."
                ]
            )
        )

        return RemediationOutput(
            options=options,
            status="Success"
        )
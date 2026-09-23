from models import (
    BugSubmission, TriageOutput, LogAnalysisOutput, 
    PipelineInput, ComprehensiveDiagnosisReport
)
from vector_store import KnowledgeBase
from agents.root_cause_agent import RootCauseAgent
from agents.duplicate_agent import DuplicateDetectionAgent
from agents.remediation_agent import RemediationAgent
from ui.app import render_dashboard

def main():
    # 1. Initialize DB and Seed Data
    kb = KnowledgeBase()
    kb.seed_mock_data()

    # 2. Instantiate Agents
    rc_agent = RootCauseAgent(kb)
    dup_agent = DuplicateDetectionAgent(kb)
    rem_agent = RemediationAgent()

    # 3. Create Sample Pipeline Input (Output from Milestones 1 & 2)
    sample_input = PipelineInput(
        submission=BugSubmission(
            bug_id="BUG-2026-881",
            title="NullPointerException in UserAuthService when OAuth scope is omitted",
            description="Users encounter internal server errors during OAuth authentication callback when the identity provider returns a null scope attribute."
        ),
        triage=TriageOutput(
            severity="High",
            priority="P1",
            affected_component="AuthModule",
            confidence_score=0.91,
            reasoning="Blocks authentication flow for subset of SSO users."
        ),
        log_analysis=LogAnalysisOutput(
            exception_type="NullPointerException",
            error_message="java.lang.NullPointerException: Cannot invoke String.split() because scope is null",
            failure_point="UserAuthService.java:142",
            affected_code_path="com.service.auth.UserAuthService",
            confidence_score=0.95
        )
    )

    # 4. Execute Multi-Agent Milestone 3 Workflow
    rc_results = rc_agent.analyze(sample_input)
    dup_results = dup_agent.analyze(sample_input)
    rem_results = rem_agent.analyze(sample_input, rc_results, dup_results)

    # 5. Assemble Consolidated Report
    report = ComprehensiveDiagnosisReport(
        input_data=sample_input,
        root_cause_analysis=rc_results,
        duplicate_detection=dup_results,
        remediation_plan=rem_results
    )

    # 6. Render UI
    render_dashboard(report)

if __name__ == "__main__":
    main()
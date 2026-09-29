import time
from typing import Dict, Any, Tuple
from playwright.sync_api import sync_playwright, Page, Locator as PlaywrightLocator
from schema import CapabilityArtifact, Step, LocatorStrategy, ActionType
from guardrails import GuardrailEngine
from hitl import HumanInTheLoopManager

class ReplayResult(dict):
    """Result object containing execution status, extracted data, or error details."""
    pass

class DeterministicReplayEngine:
    def __init__(self, artifact: CapabilityArtifact, hitl_manager: HumanInTheLoopManager):
        self.artifact = artifact
        self.guardrail = GuardrailEngine(allowed_domains=artifact.allowed_domains)
        self.hitl = hitl_manager

    def _resolve_element(self, page: Page, step: Step) -> PlaywrightLocator:
        """Tries locators sequentially (TestID -> CSS -> XPath)."""
        for loc in step.locators:
            try:
                if loc.strategy == LocatorStrategy.TEST_ID:
                    el = page.get_by_test_id(loc.value)
                elif loc.strategy == LocatorStrategy.CSS:
                    el = page.locator(loc.value)
                elif loc.strategy == LocatorStrategy.XPATH:
                    el = page.locator(f"xpath={loc.value}")
                else:
                    continue

                if el.count() > 0 and el.first.is_visible(timeout=step.timeout_ms):
                    return el.first
            except Exception:
                continue

        raise Exception(f"Failed to resolve element for step '{step.step_id}' using fallbacks.")

    def execute(self, target_url: str, input_params: Dict[str, Any]) -> ReplayResult:
        self.guardrail.validate_url(target_url)
        extracted_outputs = {}

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(target_url)

            for step in self.artifact.steps:
                self.guardrail.inspect_step(step)

                try:
                    if step.action == ActionType.TYPE:
                        el = self._resolve_element(page, step)
                        # Substitute parameters
                        val = step.value_template.replace("{{inputs.member_id}}", str(input_params.get("member_id", "")))
                        el.fill(val)

                    elif step.action == ActionType.CLICK:
                        el = self._resolve_element(page, step)
                        el.click()

                    elif step.action == ActionType.EXTRACT:
                        el = self._resolve_element(page, step)
                        text_val = el.text_content().strip()
                        if step.extract_key:
                            extracted_outputs[step.extract_key] = float(text_val)

                except Exception as ex:
                    # Check for explicit business error on the UI page first
                    error_el = page.get_by_test_id("error-message")
                    if error_el.count() > 0 and error_el.is_visible():
                        browser.close()
                        return ReplayResult(
                            status="BUSINESS_OUTCOME",
                            message=error_el.text_content().strip(),
                            outputs={}
                        )
                    
                    # Trigger HITL Escalation Seam
                    print(f"[REPLAY ERROR] Step failed: {ex}")
                    resolved = self.hitl.request_intervention(page, str(ex), {"step": step.step_id})
                    if not resolved:
                        browser.close()
                        return ReplayResult(status="HARD_FAILURE", error=str(ex))

            # Verify Checkpoints
            for cp in self.artifact.checkpoints:
                chk_el = page.get_by_test_id(cp.locator.value)
                if chk_el.count() == 0 or not chk_el.is_visible():
                    browser.close()
                    return ReplayResult(status="CHECKPOINT_FAILED", error="Checkpoint verification failed.")

            browser.close()
            return ReplayResult(
                status="SUCCESS",
                outputs=GuardrailEngine.redact_sensitive_data(extracted_outputs)
            )
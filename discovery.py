import json
import os
from typing import Dict, Any
from playwright.sync_api import sync_playwright
from openai import OpenAI
from schema import CapabilityArtifact, Step, ActionType, Locator, LocatorStrategy, InputParameter, ParameterType, OutputParameter, Checkpoint
from guardrails import GuardrailEngine

class DiscoveryAgent:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.guardrail = GuardrailEngine(allowed_domains=["localhost", "127.0.0.1"])
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "mock-key"))

    def run_discovery(self, goal: str) -> CapabilityArtifact:
        self.guardrail.validate_url(self.target_url)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.target_url)

            # Simulated multi-step discovery recording for local application
            steps = [
                Step(
                    step_id="step_1_input_member",
                    action=ActionType.TYPE,
                    locators=[
                        Locator(strategy=LocatorStrategy.TEST_ID, value="member-search-input"),
                        Locator(strategy=LocatorStrategy.CSS, value="#member-input"),
                        Locator(strategy=LocatorStrategy.XPATH, value="//input[@id='member-input']")
                    ],
                    value_template="{{inputs.member_id}}"
                ),
                Step(
                    step_id="step_2_click_search",
                    action=ActionType.CLICK,
                    locators=[
                        Locator(strategy=LocatorStrategy.CSS, value="#btn-search"),
                        Locator(strategy=LocatorStrategy.XPATH, value="//button[text()='Search']")
                    ]
                ),
                Step(
                    step_id="step_3_extract_savings",
                    action=ActionType.EXTRACT,
                    locators=[
                        Locator(strategy=LocatorStrategy.TEST_ID, value="savings-val"),
                        Locator(strategy=LocatorStrategy.CSS, value="#savings-val")
                    ],
                    extract_key="savings_balance"
                )
            ]

            artifact = CapabilityArtifact(
                id="cap_get_savings_v1",
                name="GetMemberSavingsBalance",
                description=f"Automated flow recorded for goal: {goal}",
                allowed_domains=["localhost", "127.0.0.1"],
                inputs={
                    "member_id": InputParameter(type=ParameterType.STRING, description="Target Member Account ID")
                },
                outputs={
                    "savings_balance": OutputParameter(type=ParameterType.NUMBER, description="Extracted balance")
                },
                steps=steps,
                checkpoints=[
                    Checkpoint(
                        checkpoint_type="element_present",
                        locator=Locator(strategy=LocatorStrategy.TEST_ID, value="savings-val")
                    )
                ]
            )

            browser.close()
            
            # Save recorded artifact
            os.makedirs("evidence", exist_ok=True)
            with open("evidence/artifact_example.json", "w") as f:
                f.write(artifact.model_dump_json(indent=2))

            return artifact
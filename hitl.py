from playwright.sync_api import Page
from typing import Dict, Any

class HumanInterventionRequired(Exception):
    pass

class HumanInTheLoopManager:
    def __init__(self):
        self.is_paused = False

    def request_intervention(self, page: Page, reason: str, step_context: Dict[str, Any]):
        self.is_paused = True
        screenshot_path = "evidence/failure_screenshot.png"
        page.screenshot(path=screenshot_path)
        
        print(f"\n=======================================================")
        print(f"[HITL ESCALATION REQUIRED] Reason: {reason}")
        print(f"Current Context: {step_context}")
        print(f"Screenshot saved to: {screenshot_path}")
        print(f"=======================================================\n")
        
        # Interactive shell handoff (simulates operator takeover in same browser context)
        user_input = input("Operator: Perform manual action in browser if needed, then type 'RESUME' or 'ABORT': ")
        if user_input.strip().upper() == "RESUME":
            self.is_paused = False
            print("[HITL] Control returned to automated executor.")
            return True
        else:
            raise HumanInterventionRequired("Operator aborted session.")
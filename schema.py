from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    CLICK = "click"
    TYPE = "type"
    EXTRACT = "extract"
    NAVIGATE = "navigate"
    WAIT = "wait"


class LocatorStrategy(str, Enum):
    TEST_ID = "test-id"
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"
    ARIA = "aria"


class Locator(BaseModel):
    strategy: LocatorStrategy
    value: str


class ParameterType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"


class InputParameter(BaseModel):
    type: ParameterType
    required: bool = True
    description: str


class OutputParameter(BaseModel):
    type: ParameterType
    description: str


class Step(BaseModel):
    step_id: str
    action: ActionType
    locators: List[Locator] = Field(default_factory=list)
    value_template: Optional[str] = None  # e.g., "{{inputs.member_id}}"
    extract_key: Optional[str] = None     # Name of output variable to save
    timeout_ms: int = 5000
    is_risky: bool = False               # Requires confirmation guardrail check


class Checkpoint(BaseModel):
    checkpoint_type: str  # e.g., "element_present"
    locator: Locator
    expected_value: Optional[str] = None


class CapabilityArtifact(BaseModel):
    id: str
    name: str
    version: str = "1.0.0"
    description: str
    allowed_domains: List[str]
    inputs: Dict[str, InputParameter]
    outputs: Dict[str, OutputParameter]
    steps: List[Step]
    checkpoints: List[Checkpoint]
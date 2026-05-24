from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """Agent状态定义"""
    messages: List[Dict[str, Any]]
    user_input: str
    user_id: str
    parsed_intent: Optional[Dict[str, Any]]
    tool_results: Optional[Dict[str, Any]]
    final_response: Optional[str]
    current_step: str  # idle, parsing, calling_apis, responding, done
    error: Optional[str]

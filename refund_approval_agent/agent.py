from google.adk import Agent, Workflow, Event, Context
from google.adk.workflow import node
from google.adk.events.request_input import RequestInput
from pydantic import BaseModel, Field

class RefundRequest(BaseModel):
    customer_id: str = Field(description="Customer ID, 'unknown' if not provided")
    amount_usd: float = Field(description="Amount in USD")
    reason: str = Field(description="Reason for refund")

class RefundDecision(BaseModel):
    approved: bool
    amount_usd: float
    reason: str

extractor = Agent(
    name="extractor",
    model="gemini-2.5-flash",
    output_schema=RefundRequest,
    instruction="Extract the refund details from the text. Ensure amount_usd is a float."
)

refund_analyzer = Agent(
    name="refund_analyzer",
    model="gemini-2.5-flash",
    input_schema=RefundRequest,
    output_schema=RefundDecision,
    instruction="Analyze the refund request. Approve if reason is legitimate (e.g. Duplicate charge, Service down). Deny otherwise. Keep the same amount."
)

#Decortor; Converts any python function into a workflow step
@node(name="process_refund")
def process_refund(decision: RefundDecision):
    if decision.approved:
        return f"Refund processed successfully for ${decision.amount_usd}. TxID: FAKE_TX_123. Reason: {decision.reason}"
    else:
        return f"Refund denied. Reason: {decision.reason}"

@node(name="refund_workflow", rerun_on_resume=True)
async def refund_workflow(ctx: Context, node_input: str):
    # Retrieve or compute the decision
    if "decision" not in ctx.state:
        request_obj = await ctx.run_node(extractor, node_input)
        decision_raw = await ctx.run_node(refund_analyzer, request_obj)
        decision = RefundDecision.model_validate(decision_raw) if isinstance(decision_raw, dict) else decision_raw
        ctx.state["decision"] = decision
    else:
        stored = ctx.state["decision"]
        decision = RefundDecision.model_validate(stored) if isinstance(stored, dict) else stored

    # HITL logic
    if decision.approved and decision.amount_usd > 100:
        if not ctx.resume_data:
            return RequestInput(message=f"Large refund of ${decision.amount_usd} requested. Approve? (yes/no) ")

        human_input = ctx.resume_data
        if human_input and str(human_input).lower().strip() == "no":
            decision.approved = False
            decision.reason = "Denied by human reviewer"

    # Process
    result = await ctx.run_node(process_refund, decision)
    return result

root_agent = Workflow(
    name="root_agent",
    edges=[("START", refund_workflow)]
)
# multi_step_agent.py
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool

# --- System A: Database Connector ---
def query_database(sql: str) -> dict:
    """Runs a query against the source database and returns rows."""
    from google.cloud import bigquery  # or Cloud SQL, Spanner, etc.
    client = bigquery.Client()
    rows = [dict(r) for r in client.query(sql).result()]
    return {"rows": rows}

system_a = LlmAgent(
    name="system_a_db_connector",
    model="gemini-flash-latest",
    instruction="Call query_database with the given SQL and return only the raw rows.",
    tools=[FunctionTool(query_database)],
    output_key="db_rows",          # written to shared session state
)

# --- Content Writer Agent ---
content_writer = LlmAgent(
    name="content_writer_agent",
    model="gemini-2.5-pro",
    instruction=(
        "Using {db_rows} from state, write a short, clear narrative "
        "(2-3 paragraphs) summarizing the data and its key insight."
    ),
    output_key="written_content",
)

# --- Image Generator Tool ---
def generate_image(prompt: str) -> dict:
    """Generates an image via Imagen based on a text prompt."""
    from google import genai
    client = genai.Client()
    result = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
    )
    return {"image_uri": result.generated_images[0].image.uri}

image_generator = LlmAgent(
    name="image_generator_agent",
    model="gemini-flash-latest",
    instruction=(
        "Derive a short visual prompt from {written_content} that "
        "illustrates the summary, then call generate_image with it."
    ),
    tools=[FunctionTool(generate_image)],
    output_key="generated_image",
)

# --- Orchestrator: runs the chain in strict order, state flows through ---
orchestrator = SequentialAgent(
    name="orchestrator",
    sub_agents=[system_a, content_writer, image_generator],
)

root_agent = orchestrator  # entry point ADK looks for
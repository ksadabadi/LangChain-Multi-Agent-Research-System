import streamlit as st

from src.pipeline.pipeline import run_research_pipeline


st.set_page_config(
	page_title="Research Control Room",
	page_icon="◈",
	layout="wide",
	initial_sidebar_state="expanded",
)

st.markdown(
	"""
	<style>
	@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
	:root { --ink: #18212b; --muted: #64717c; --teal: #0c7c86; --mint: #dff4ee; --gold: #e5a84b; --paper: #f6f8f7; }
	html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
	.stApp { background: radial-gradient(circle at 90% 0%, #e4f2ef 0, #f6f8f7 34rem, #f6f8f7 100%); }
	h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: 0 !important; }
	h1 { font-size: 3.1rem !important; line-height: 1.03 !important; margin-bottom: .5rem !important; }
	.eyebrow { color: var(--teal); font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
	.subtitle { color: var(--muted); font-size: 1.05rem; max-width: 650px; margin-bottom: 1.8rem; }
	.panel { background: rgba(255,255,255,.78); border: 1px solid #dce7e3; border-radius: 8px; padding: 1.1rem 1.25rem; }
	.agent-card { background: #fff; border: 1px solid #dce7e3; border-left: 4px solid #c8d5d1; border-radius: 7px; padding: .9rem 1rem; min-height: 92px; }
	.agent-card.active { border-left-color: var(--gold); box-shadow: 0 8px 24px rgba(24,33,43,.07); }
	.agent-card.done { border-left-color: var(--teal); }
	.agent-name { font-family: 'Space Grotesk'; font-weight: 700; font-size: 1rem; }
	.agent-meta { color: var(--muted); font-size: .84rem; margin-top: .3rem; }
	.stButton > button { background: var(--teal); border: 0; color: white; border-radius: 6px; font-weight: 700; min-height: 3rem; }
	.stButton > button:hover { background: #09636b; color: white; }
	section[data-testid="stSidebar"] { background: #17252b; }
	section[data-testid="stSidebar"] * { color: #edf6f3 !important; }
	section[data-testid="stSidebar"] .stTextArea textarea { background: #24363c; border-color: #456169; }
	.result-label { color: var(--teal); font-size: .76rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
	</style>
	""",
	unsafe_allow_html=True,
)


STAGES = {
	"search": ("01", "Search agent", "Finds current, credible sources"),
	"reader": ("02", "Reader agent", "Extracts the useful detail"),
	"writer": ("03", "Writer chain", "Builds the research report"),
	"critic": ("04", "Critic chain", "Stress-tests the final draft"),
}


def render_agent_cards(stage_state: dict[str, dict]) -> None:
	columns = st.columns(4)
	for column, stage in zip(columns, STAGES):
		number, name, description = STAGES[stage]
		status = stage_state[stage]["status"]
		label = "Running" if status == "running" else "Complete" if status == "complete" else "Queued"
		column.markdown(
			f'<div class="agent-card {"active" if status == "running" else "done" if status == "complete" else ""}"><div class="agent-name">{number} · {name}</div>'
			f'<div class="agent-meta">{label} · {description}</div></div>',
			unsafe_allow_html=True,
		)


def main() -> None:
	if "pipeline_state" not in st.session_state:
		st.session_state.pipeline_state = None

	with st.sidebar:
		st.markdown("## ◈ Research room")
		st.caption("A four-stage multi-agent research workflow")
		st.divider()
		st.markdown("**Workflow**")
		st.markdown("Search → Read → Write → Critique")
		st.divider()
		st.caption("Results are generated live from your configured model and search tools.")

	st.markdown('<div class="eyebrow">Multi-agent intelligence desk</div>', unsafe_allow_html=True)
	st.title("Research Control Room")
	st.markdown(
		'<div class="subtitle">Turn a question into a sourced report with visible progress at every stage.</div>',
		unsafe_allow_html=True,
	)

	with st.form("research_form"):
		topic = st.text_area(
			"Research brief",
			placeholder="What should the agents investigate? e.g. The impact of AI on the job market in 2026",
			height=105,
			label_visibility="visible",
		)
		submitted = st.form_submit_button("Run research pipeline  →", use_container_width=True)

	if submitted:
		if not topic.strip():
			st.warning("Add a research brief to begin.")
			return

		stage_state = {
			stage: {"status": "queued", "output": "", "message": "Waiting to run"}
			for stage in STAGES
		}
		st.session_state.pipeline_state = None
		st.markdown("### Live pipeline")
		cards_placeholder = st.empty()
		status_placeholder = st.empty()
		output_placeholders = {stage: st.empty() for stage in STAGES}

		def on_progress(event: dict) -> None:
			stage = event["stage"]
			stage_state[stage].update(event)
			cards_placeholder.empty()
			with cards_placeholder.container():
				render_agent_cards(stage_state)
			status_placeholder.info(f"**{STAGES[stage][1]}** · {event['message']}")
			if event.get("output"):
				with output_placeholders[stage].container():
					with st.expander(f"{STAGES[stage][1]} output", expanded=False):
						st.write(event["output"])

		cards_placeholder.empty()
		with cards_placeholder.container():
			render_agent_cards(stage_state)
		try:
			result = run_research_pipeline(topic.strip(), progress_callback=on_progress)
			st.session_state.pipeline_state = result
			status_placeholder.success("Pipeline complete · report and critique are ready")
		except Exception as error:
			status_placeholder.error(f"The pipeline stopped: {error}")
			st.exception(error)
			return

	if st.session_state.pipeline_state:
		result = st.session_state.pipeline_state
		st.divider()
		st.markdown('<div class="result-label">Final synthesis</div>', unsafe_allow_html=True)
		st.subheader("Research report")
		st.markdown(result["report"])
		st.markdown('<div class="result-label">Quality review</div>', unsafe_allow_html=True)
		st.subheader("Critic results")
		st.markdown(result["feedback"])

		with st.expander("View complete research state"):
			st.markdown("**Search results**")
			st.write(result["search_result"])
			st.markdown("**Scraped content**")
			st.write(result["scraped_content"])


if __name__ == "__main__":
	main()

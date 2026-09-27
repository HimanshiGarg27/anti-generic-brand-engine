import sys
import os
import time
import streamlit as st
from google import genai
from google.genai import errors
from pydantic import BaseModel, Field


# ==========================================
# 0. WINDOWS ENCODING PATCH
# ==========================================

if sys.platform == "win32":
    os.environ["PYTHONUTF8"] = "1"
    os.environ["PYTHONIOENCODING"] = "utf-8"

    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ==========================================
# 1. PAGE CONFIG & PREMIUM CSS (UI/UX)
# ==========================================

st.set_page_config(
    page_title="Anti-Generic Engine | Inkloom",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* Global Theme */
    .stApp {
        background: radial-gradient(circle at 15% 50%, #120b29, #09090b);
        color: #f4f4f5;
        font-family: 'Inter', sans-serif;
    }

    /* Typography */
    h1 {
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #c026d3, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
    }

    h2, h3 {
        font-weight: 600;
        color: #e4e4e7;
    }

    /* Premium Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s ease;
        height: 100%;
    }

    .glass-card:hover {
        transform: translateY(-2px);
    }

    /* Primary Action Button */
    .stButton > button {
        background: linear-gradient(135deg, #c026d3 0%, #7e22ce 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        width: 100%;
        height: 54px;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(192, 38, 211, 0.3);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #a21caf 0%, #6b21a8 100%);
        box-shadow: 0 6px 20px rgba(192, 38, 211, 0.5);
        transform: scale(1.02);
    }

    /* Badges */
    .cliche-badge {
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .success-badge {
        background: rgba(16, 185, 129, 0.15);
        color: #6ee7b7;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.3);
        display: inline-block;
        margin-top: 10px;
    }

    /* Subtle glowing line */
    hr {
        border-color: rgba(255, 255, 255, 0.1);
    }

    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. STRUCTURED DATA SCHEMAS
# ==========================================

class BrandIdentity(BaseModel):
    brand_name: str = Field(
        description="A distinctive, memorable brand name."
    )

    tagline: str = Field(
        description="A punchy, non-boring one-line tagline."
    )

    value_proposition: str = Field(
        description="Clear explanation of why this product matters."
    )

    personality_traits: list[str] = Field(
        description="3-5 highly specific brand personality traits."
    )

    visual_direction: str = Field(
        description="Typography, color mood, and shapes to use."
    )

    audience_mismatch_warning: str = Field(
        description="Potential risks in how the audience might misinterpret this brand."
    )


class CritiqueResult(BaseModel):
    is_cliche: bool = Field(
        description="True if generic startup cliches are detected."
    )

    detected_cliches: list[str] = Field(
        description="Specific overused words or concepts found."
    )

    originality_score: int = Field(
        description="Score from 0 to 100 based on distinctiveness."
    )

    harsh_feedback: str = Field(
        description="Direct, constructive feedback demanding improvements."
    )


# ==========================================
# 3. AI MODEL CONFIGURATION
# ==========================================

# Primary model first.
# If it is temporarily unavailable, the app will retry
# and then try the fallback models.

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]


# ==========================================
# 4. GEMINI RETRY ENGINE
# ==========================================

def generate_with_retry(
    client: genai.Client,
    prompt: str,
    response_schema
):
    """
    Generates structured output from Gemini.

    Handles temporary server errors such as:
    503 UNAVAILABLE
    429 RESOURCE EXHAUSTED

    It retries with exponential backoff and
    switches to fallback models if necessary.
    """

    last_error = None

    for model in MODELS:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": response_schema,
                    }
                )

                if response.parsed is None:
                    raise ValueError(
                        f"Gemini returned an empty response from {model}."
                    )

                return response.parsed

            except errors.ServerError as e:

                last_error = e

                # Temporary server problem.
                # Retry using exponential backoff.

                if attempt < 2:

                    wait_time = 2 ** (attempt + 1)

                    time.sleep(wait_time)

                else:

                    # Try the next model.
                    break

            except errors.APIError as e:

                last_error = e

                error_code = getattr(e, "code", None)

                # Handle rate limiting.
                if error_code == 429:

                    if attempt < 2:

                        wait_time = 2 ** (attempt + 1)

                        time.sleep(wait_time)

                        continue

                    else:

                        break

                # Other API errors should not
                # be hidden.

                raise

            except Exception as e:

                last_error = e
                raise

    # If every model failed
    raise RuntimeError(
        "Gemini is temporarily unavailable. "
        "Please wait a few seconds and try again."
    ) from last_error


# ==========================================
# 5. AGENT 1 — BRAND STRATEGIST
# ==========================================

def generate_draft(
    client: genai.Client,
    idea: str,
    previous_feedback: str = ""
) -> BrandIdentity:

    prompt = f"""
You are a world-class brand strategist.

Turn this raw idea into a launch-ready brand:

"{idea}"

Create a distinctive brand identity.

Avoid generic startup language such as:

- Smart
- Connect
- AI-powered
- Innovative
- Seamless
- Next-generation
- Disruptive
- Synergy

The brand name must be memorable and original.

The tagline must be short and distinctive.

The value proposition must clearly explain why
the product matters.

The personality traits must be specific rather
than generic.

The visual direction should include typography,
color mood and visual shapes.

Also identify possible audience misunderstanding.
"""

    if previous_feedback:

        prompt += f"""

CRITICAL FIX REQUIRED:

The previous draft was rejected.

Previous critic feedback:

{previous_feedback}

You MUST create an entirely new brand name
and concept.

Do not repeat the failed draft.
"""


    return generate_with_retry(
        client=client,
        prompt=prompt,
        response_schema=BrandIdentity
    )


# ==========================================
# 6. AGENT 2 — BRAND CRITIC
# ==========================================

def evaluate_draft(
    client: genai.Client,
    draft: BrandIdentity
) -> CritiqueResult:

    prompt = f"""
You are a ruthless, anti-generic brand critic.

Analyze this proposed brand.

Name:
{draft.brand_name}

Tagline:
{draft.tagline}

Traits:
{draft.personality_traits}

Value Proposition:
{draft.value_proposition}

Detect ANY startup clichés.

Examples include:

- -ify suffixes
- "connecting the world"
- disrupt
- synergy
- seamless
- smart
- innovative
- AI-powered
- next generation
- future-ready
- revolutionary

If it sounds generic:

is_cliche = true

originality_score should be below 75

If it is genuinely distinct and interesting:

is_cliche = false

originality_score should be above 85

Give direct and constructive feedback.

The purpose is to force the strategist to
produce a genuinely distinctive brand.
"""


    return generate_with_retry(
        client=client,
        prompt=prompt,
        response_schema=CritiqueResult
    )


# ==========================================
# 7. SIDEBAR SETTINGS
# ==========================================

with st.sidebar:

    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg",
        width=40
    )

    st.markdown("### Engine Config")

    api_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        help="Securely enter your Gemini API key."
    )

    st.markdown(
        "<br><br>",
        unsafe_allow_html=True
    )

    st.markdown("### 🏆 Inkloom Criteria")

    st.checkbox(
        "Multi-stage AI Workflow",
        value=True,
        disabled=True
    )

    st.checkbox(
        "Anti-Generic Engine",
        value=True,
        disabled=True
    )

    st.checkbox(
        "Structured JSON Output",
        value=True,
        disabled=True
    )

    st.checkbox(
        "Polished UI/UX",
        value=True,
        disabled=True
    )


# ==========================================
# 8. MAIN HERO SECTION
# ==========================================

st.markdown(
    "<h1>THE ANTI-GENERIC ENGINE</h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style='color: #a1a1aa; font-size: 1.1rem; margin-bottom: 2rem;'>
    An autonomous debate loop that forces AI to stop acting like a boring startup.
    </p>
    """,
    unsafe_allow_html=True
)


user_idea = st.text_area(
    "Initial Concept",
    placeholder=(
        "Enter a rough app or product idea "
        "(e.g., A web portal mapping academic skills to industry)..."
    ),
    height=100,
    label_visibility="collapsed"
)


# ==========================================
# 9. DYNAMIC EXECUTION ENGINE
# ==========================================

if st.button("IGNITE BRAND ENGINE ⚡"):

    # --------------------------------------
    # API KEY
    # --------------------------------------

    active_key = (
        api_key_input
        or os.environ.get("GEMINI_API_KEY")
    )

    if not active_key:

        st.toast(
            "⚠️ Missing API Key in the sidebar!",
            icon="🛑"
        )

        st.error(
            "Please enter your Gemini API Key in the sidebar "
            "or set GEMINI_API_KEY as an environment variable."
        )

        st.stop()


    # --------------------------------------
    # USER IDEA
    # --------------------------------------

    if not user_idea.strip():

        st.warning(
            "Please enter a rough idea first."
        )

        st.stop()


    # --------------------------------------
    # CREATE GEMINI CLIENT
    # --------------------------------------

    try:

        client = genai.Client(
            api_key=active_key
        )

    except Exception as e:

        st.error(
            f"Unable to initialize Gemini client: {e}"
        )

        st.stop()


    # --------------------------------------
    # TERMINAL HEADER
    # --------------------------------------

    st.markdown("---")

    st.markdown(
        "### ⚙️ Autonomous Debate Terminal"
    )


    # --------------------------------------
    # ENGINE SETTINGS
    # --------------------------------------

    max_retries = 3

    iteration = 1

    success = False

    feedback = ""

    final_brand = None

    draft = None


    debate_container = st.container()


    # ======================================
    # AUTONOMOUS DEBATE LOOP
    # ======================================

    try:

        with debate_container:

            while (
                iteration <= max_retries
                and not success
            ):

                st.caption(
                    f"Round {iteration} / {max_retries}"
                )


                # ==================================
                # AGENT 1 — STRATEGIST
                # ==================================

                with st.chat_message(
                    "ai",
                    avatar="✨"
                ):

                    st.markdown(
                        "**Agent 1 (Strategist):** "
                        "Synthesizing identity..."
                    )

                    with st.spinner(
                        "Drafting brand identity..."
                    ):

                        draft = generate_draft(
                            client,
                            user_idea,
                            feedback
                        )


                    st.markdown(
                        f"Proposed Name: "
                        f"**`{draft.brand_name}`**"
                    )

                    st.markdown(
                        f"*{draft.tagline}*"
                    )


                # ==================================
                # AGENT 2 — CRITIC
                # ==================================

                with st.chat_message(
                    "user",
                    avatar="🧐"
                ):

                    st.markdown(
                        "**Agent 2 (Critic):** "
                        "Scanning for cliches..."
                    )


                    with st.spinner(
                        "Evaluating brand..."
                    ):

                        eval_result = evaluate_draft(
                            client,
                            draft
                        )


                    # --------------------------------
                    # SCORE
                    # --------------------------------

                    score = max(
                        0,
                        min(
                            100,
                            eval_result.originality_score
                        )
                    )


                    st.metric(
                        label="Originality Score",
                        value=f"{score}/100"
                    )


                    # ==================================
                    # REJECTED
                    # ==================================

                    if eval_result.is_cliche:

                        if eval_result.detected_cliches:

                            cliche_tags = " ".join(
                                [
                                    (
                                        f"<span class='cliche-badge'>"
                                        f"{c}"
                                        f"</span>"
                                    )
                                    for c in eval_result.detected_cliches
                                ]
                            )

                            st.markdown(
                                f"**Rejected!** "
                                f"Cliches found: "
                                f"{cliche_tags}",
                                unsafe_allow_html=True
                            )

                        else:

                            st.markdown(
                                "**Rejected!** "
                                "Generic language detected."
                            )


                        st.markdown(
                            f"> {eval_result.harsh_feedback}"
                        )


                        feedback = (
                            eval_result.harsh_feedback
                        )


                        iteration += 1


                        st.divider()


                    # ==================================
                    # APPROVED
                    # ==================================

                    else:

                        st.markdown(
                            """
                            <div class='success-badge'>
                            ✓ Approved for Launch
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        success = True

                        final_brand = draft

                        break


            # ======================================
            # MAX ITERATIONS
            # ======================================

            if not success:

                st.warning(
                    "Engine reached maximum debate "
                    "iterations."
                )

                if draft is not None:

                    final_brand = draft


    # ==========================================
    # GEMINI SERVER ERROR
    # ==========================================

    except errors.ServerError:

        st.error(
            """
            ⚠️ Gemini is temporarily experiencing
            high demand.

            Please wait a little and click
            **IGNITE BRAND ENGINE** again.
            """
        )

        st.stop()


    # ==========================================
    # GENERAL ERROR
    # ==========================================

    except RuntimeError as e:

        st.error(
            f"⚠️ {str(e)}"
        )

        st.stop()


    except Exception as e:

        st.error(
            "⚠️ Something went wrong while "
            "running the brand engine."
        )

        st.exception(e)

        st.stop()


    # ==========================================
    # SAFETY CHECK
    # ==========================================

    if final_brand is None:

        st.error(
            "No brand identity was generated. "
            "Please try again."
        )

        st.stop()


    # ==========================================
    # 10. FINAL EXPORTABLE DELIVERABLE
    # ==========================================

    st.markdown("---")

    st.markdown(
        "### 🚀 Final Launch Identity"
    )


    col1, col2 = st.columns(2)


    # ==========================================
    # LEFT CARD
    # ==========================================

    with col1:

        st.markdown(
            "<div class='glass-card'>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <h2 style='margin-top:0;'>
            {final_brand.brand_name}
            </h2>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"**Tagline:** {final_brand.tagline}"
        )

        st.markdown(
            f"""
            **Value Proposition:**<br>
            {final_brand.value_proposition}
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ==========================================
    # RIGHT CARD
    # ==========================================

    with col2:

        st.markdown(
            "<div class='glass-card'>",
            unsafe_allow_html=True
        )

        st.markdown(
            "**Core Personality:**"
        )

        for trait in final_brand.personality_traits:

            st.markdown(
                f"- {trait}"
            )


        st.markdown(
            f"""
            <br>
            **Visual Direction:**<br>
            {final_brand.visual_direction}
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <br>
            **Audience Warning:**<br>
            {final_brand.audience_mismatch_warning}
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ==========================================
    # DOWNLOAD JSON
    # ==========================================

    st.markdown("<br>", unsafe_allow_html=True)


    st.download_button(
        label="Download JSON Brand Kit 📦",

        data=final_brand.model_dump_json(
            indent=2
        ),

        file_name=(
            f"{final_brand.brand_name.replace(' ', '_').lower()}"
            f"_brand_kit.json"
        ),

        mime="application/json"
    )
"""
Quiz - Minimal
"""

import streamlit as st
import json


def render_quiz_interface(api_client):
    """Quiz setup."""
    col1, col2 = st.columns([3, 1])
    with col1:
        n = st.slider("Questions:", 1, 20, 5)
    with col2:
        if st.button("Start", use_container_width=True):
            with st.spinner("..."):
                try:
                    quiz = api_client.generate_quiz(n)
                    st.session_state.quiz_active = True
                    st.session_state.quiz_data = quiz
                    st.session_state.quiz_answers = {}
                    st.rerun()
                except Exception as e:
                    st.error(str(e))


def render_quiz_mode(api_client):
    """Quiz taking."""
    qs = st.session_state.get("quiz_data", {}).get("questions", [])
    if not qs:
        st.warning("No questions")
        return
    
    ans = len([v for v in st.session_state.quiz_answers.values() if v])
    st.progress(ans / len(qs), f"{ans}/{len(qs)}")
    
    tabs = st.tabs([f"Q{i+1}" for i in range(len(qs))])
    for idx, (tab, q) in enumerate(zip(tabs, qs)):
        with tab:
            st.write(q.get("question", ""))
            a = st.radio("A:", ["A", "B", "C", "D"], key=f"q{idx}", label_visibility="collapsed")
            st.session_state.quiz_answers[idx] = a
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit", use_container_width=True):
            show_quiz_results(qs)
    with col2:
        if st.button("Reset", use_container_width=True):
            st.session_state.quiz_active = False
            st.rerun()


def show_quiz_results(qs):
    """Results."""
    ans = st.session_state.get("quiz_answers", {})
    ok = sum(1 for i, q in enumerate(qs) if ans.get(i) == q.get("correct_answer"))
    tot = len(qs)
    score = (ok / tot * 100) if tot > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{score:.0f}%")
    col2.metric("Correct", f"{ok}/{tot}")
    col3.metric("Wrong", f"{tot - ok}")
    
    st.divider()
    for i, q in enumerate(qs):
        u = ans.get(i)
        c = q.get("correct_answer")
        s = "✅" if u == c else "❌"
        st.write(f"{s} Q{i+1}: {u} {'✓' if u == c else f'({c})'}")
    
    if st.button("Download", use_container_width=True):
        st.download_button("", json.dumps({"score": score, "ok": ok, "total": tot}), "results.json")
    
    if st.button("New", use_container_width=True):
        st.session_state.quiz_active = False
        st.rerun()

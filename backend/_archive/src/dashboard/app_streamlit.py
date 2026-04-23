from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


def main() -> None:
    st.set_page_config(page_title="Vehicle Counter Dashboard", layout="wide")
    st.title("Vehicle Counter Dashboard")

    events_csv = Path("outputs/csv/events.csv")
    daily_csv = Path("outputs/csv/daily_counts.csv")
    annotated_video = Path("outputs/videos/annotated.mp4")

    if annotated_video.exists():
        st.subheader("Recognition video")
        st.video(str(annotated_video))
    else:
        st.info("No annotated video yet. Run the pipeline first.")

    if events_csv.exists():
        st.subheader("Events")
        st.dataframe(pd.read_csv(events_csv), use_container_width=True)
    else:
        st.info("No events CSV yet. Run the pipeline first.")

    if daily_csv.exists():
        st.subheader("Daily counts")
        daily_df = pd.read_csv(daily_csv)
        st.dataframe(daily_df, use_container_width=True)
        if not daily_df.empty:
            st.line_chart(daily_df.set_index("date")[["motorcycles", "vehicles", "total"]])
    else:
        st.info("No daily counts CSV yet. Generate daily report first.")


if __name__ == "__main__":
    main()

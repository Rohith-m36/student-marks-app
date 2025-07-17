import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# --- Streamlit setup ---
st.set_page_config(page_title="Student Marks Analyzer", layout="wide")
st.title("📊 Student Marks Analyzer")

# --- File Upload ---
uploaded_file = st.file_uploader("📁 Upload your CSV file (Name, Subject, Marks)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # --- Clean and validate data ---
    df.columns = df.columns.str.strip().str.capitalize()
    if not {'Name', 'Subject', 'Marks'}.issubset(df.columns):
        st.error("❌ The CSV must contain columns: Name, Subject, Marks")
        st.stop()

    df["Marks"] = pd.to_numeric(df["Marks"], errors='coerce')
    df.dropna(subset=["Marks"], inplace=True)

    # --- Add Grades ---
    def assign_grade(mark):
        if mark >= 90: return 'A+'
        elif mark >= 80: return 'A'
        elif mark >= 70: return 'B'
        elif mark >= 60: return 'C'
        elif mark >= 50: return 'D'
        else: return 'F'

    def remarks(grade):
        return {
            'A+': "Excellent! 🎉",
            'A': "Great work! 👍",
            'B': "Good, keep going!",
            'C': "Needs improvement!",
            'D': "Focus needed!",
            'F': "At risk 🚨"
        }.get(grade, "")

    df["Grade"] = df["Marks"].apply(assign_grade)
    df["Remarks"] = df["Grade"].apply(remarks)

    st.success("✅ File uploaded and processed!")
    st.markdown("---")

    # --- Filters ---
    st.markdown("### 🔍 Filter Data")
    col1, col2 = st.columns(2)
    selected_student = col1.selectbox("Select Student", ["All"] + sorted(df["Name"].unique()))
    selected_subject = col2.selectbox("Select Subject", ["All"] + sorted(df["Subject"].unique()))

    filtered_df = df.copy()
    if selected_student != "All":
        filtered_df = filtered_df[filtered_df["Name"] == selected_student]
    if selected_subject != "All":
        filtered_df = filtered_df[filtered_df["Subject"] == selected_subject]

    with st.expander("📋 View Filtered Data"):
        st.dataframe(filtered_df, use_container_width=True)

    # --- KPIs ---
    st.markdown("### 📈 Overall Performance Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("🔢 Average Marks", f"{filtered_df['Marks'].mean():.2f}")
    col2.metric("🏆 Highest Marks", f"{filtered_df['Marks'].max()}")
    col3.metric("📉 Lowest Marks", f"{filtered_df['Marks'].min()}")
    st.markdown("---")

    # --- Bar Chart: Student Averages ---
    st.markdown("### 👨‍🎓 Average Marks per Student")
    student_avg = filtered_df.groupby("Name")["Marks"].mean().reset_index()
    fig_bar = px.bar(student_avg, x="Name", y="Marks", color="Marks", color_continuous_scale="viridis")
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Pie Chart: Subject Averages ---
    st.markdown("### 📚 Average Marks per Subject")
    subject_avg = filtered_df.groupby("Subject")["Marks"].mean().reset_index()
    fig_pie = px.pie(subject_avg, names="Subject", values="Marks", title="Avg Marks by Subject")
    st.plotly_chart(fig_pie, use_container_width=True)

    # --- Heatmap: Student vs Subject ---
    st.markdown("### 🧠 Student-Subject Heatmap")
    pivot_df = filtered_df.pivot_table(index="Name", columns="Subject", values="Marks")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_df, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=0.5, ax=ax)
    st.pyplot(fig)

    # --- Histogram of Marks ---
    st.markdown("### 📉 Distribution of Marks")
    fig_hist = px.histogram(filtered_df, x="Marks", nbins=10, color="Subject", barmode="overlay")
    st.plotly_chart(fig_hist, use_container_width=True)

    # --- Top Performers by Subject ---
    st.markdown("### 🏅 Top Performer per Subject")
    top_subject = filtered_df.loc[filtered_df.groupby("Subject")["Marks"].idxmax()]
    st.dataframe(top_subject[["Name", "Subject", "Marks", "Grade", "Remarks"]], use_container_width=True)

    # --- Export Data ---
    st.markdown("### 📤 Export Data")

    # Enhanced data export (with grade and remarks)
    export_df = filtered_df.copy()
    export_csv = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Data with Grades (CSV)",
        data=export_csv,
        file_name='full_student_data.csv',
        mime='text/csv'
    )

    # Student-wise average
    student_avg_csv = student_avg.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Student Averages (CSV)",
        data=student_avg_csv,
        file_name='student_averages.csv',
        mime='text/csv'
    )

    # Subject-wise average
    subject_avg_csv = subject_avg.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Subject Averages (CSV)",
        data=subject_avg_csv,
        file_name='subject_averages.csv',
        mime='text/csv'
    )

    # Pivot table export
    pivot_export = pivot_df.reset_index().fillna("").round(1)
    pivot_csv = pivot_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Student vs Subject Matrix (CSV)",
        data=pivot_csv,
        file_name='student_subject_matrix.csv',
        mime='text/csv'
    )

else:
    st.info("👆 Please upload a `.csv` file with `Name`, `Subject`, and `Marks` columns.")

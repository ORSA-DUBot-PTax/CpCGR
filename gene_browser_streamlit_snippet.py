# gene_browser.py
# Streamlit gene sequence browser section for C. paniculatum Cp genome.
# Put this file in the same folder as:
# C_paniculatum_gene_sequences_with_composition.csv
#
# In your app.py, you can either paste this code into a tab or import it.

import textwrap
import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache_data
def load_gene_sequences(csv_path="C_paniculatum_gene_sequences_with_composition.csv"):
    return pd.read_csv(csv_path)

def wrap_sequence(seq, width=80):
    return "\n".join(textwrap.wrap(str(seq), width))

def render_gene_browser(csv_path="C_paniculatum_gene_sequences_with_composition.csv"):
    st.header("Gene Sequence Browser")
    st.markdown(
        "Search protein-coding genes, tRNAs, and rRNAs. Select a gene to view its "
        "sequence, length, GC percentage, AT percentage, and nucleotide composition."
    )

    df = load_gene_sequences(csv_path)

    col1, col2 = st.columns([1, 2])
    with col1:
        gene_type = st.selectbox(
            "Filter by gene type",
            ["All"] + sorted(df["Gene_type"].dropna().unique().tolist())
        )

    filtered = df.copy()
    if gene_type != "All":
        filtered = filtered[filtered["Gene_type"] == gene_type]

    with col2:
        search_text = st.text_input("Search gene name", "")

    if search_text:
        filtered = filtered[
            filtered["Gene"].str.contains(search_text, case=False, na=False)
        ]

    st.dataframe(
        filtered[
            ["Gene", "Gene_type", "Length_bp", "A_count", "T_count", "G_count", "C_count", "AT_percent", "GC_percent"]
        ],
        use_container_width=True,
        hide_index=True
    )

    if filtered.empty:
        st.warning("No gene matched your search.")
        return

    selected_gene = st.selectbox("Select a gene to display sequence", filtered["Gene"].tolist())
    row = filtered[filtered["Gene"] == selected_gene].iloc[0]

    st.subheader(f"{row['Gene']}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gene type", row["Gene_type"])
    m2.metric("Length", f"{int(row['Length_bp'])} bp")
    m3.metric("GC content", f"{row['GC_percent']:.2f}%")
    m4.metric("AT content", f"{row['AT_percent']:.2f}%")

    comp_df = pd.DataFrame({
        "Base": ["A", "T", "G", "C"],
        "Count": [row["A_count"], row["T_count"], row["G_count"], row["C_count"]]
    })

    fig = px.bar(
        comp_df,
        x="Base",
        y="Count",
        text="Count",
        title=f"Nucleotide composition of {row['Gene']}"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Sequence")
    st.code(wrap_sequence(row["Sequence"]), language="text")

    fasta_text = row["FASTA"]
    st.download_button(
        label=f"Download {row['Gene']} FASTA",
        data=fasta_text,
        file_name=f"{row['Gene']}.fasta",
        mime="text/plain"
    )

# Example use in app.py:
# from gene_browser import render_gene_browser
# render_gene_browser()

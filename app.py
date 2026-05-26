# app.py
# CpCGR: An Interactive Chloroplast Genome Resource for Clerodendrum paniculatum
# Put this file in C:\C_pani_website with your data files, then run:
# python -m streamlit run app.py

import base64
import re
import textwrap
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
except Exception:
    px = None

try:
    from streamlit_pdf_viewer import pdf_viewer
except Exception:
    pdf_viewer = None


# ============================================================
# Page configuration
# ============================================================
st.set_page_config(
    page_title="CpCGR",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent

# ============================================================
# CpCGR home styling
# ============================================================
def render_title_block():
    """Render a clean text-only CpCGR title."""
    st.markdown(
        """
        <div class="cpcgr-title-wrap">
            <h1 class="cpcgr-title">CpCGR</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_intro_box():
    """Render compact home-page introduction."""
    st.markdown(
        """
        <div class="cpcgr-intro">
            CpCGR (<em>Clerodendrum paniculatum</em> Chloroplast Genome Resource) is an interactive web platform for
            <em>Clerodendrum paniculatum</em> that provides access to assembled and annotated cp genome, its gene locations,
            gene sequences, nucleotide composition, codon usage, SSR profiles,
            exon-intron organization, mVISTA genome divergence, IR junction analysis,
            phylogenetic inference, molecular dating outputs, and downloadable source files.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_compact_metrics():
    """Render compact genome summary table for the left side of Home page."""
    rows = [
        ("Genome size", "152,278 bp"),
        ("Total genes", "128"),
        ("Unique genes", "107"),
        ("Protein-coding genes", "83 / 76 unique"),
        ("tRNA genes", "37 / 28 unique"),
        ("rRNA genes", "8 / 4 unique"),
    ]

    row_html = "".join(
        f"""
        <div class="home-table-row">
            <div class="home-table-label">{label}</div>
            <div class="home-table-value">{value}</div>
        </div>
        """
        for label, value in rows
    )

    st.markdown(
        f"""
        <div class="home-section-title">Genome summary</div>
        <div class="home-compact-table">
            {row_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_image():
    """Display workflow image in a controlled, screenshot-friendly size."""
    path = file_path("workflow")
    if not path.exists():
        st.warning("workflow.png was not found in the app folder.")
        return

    import base64
    img_b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    st.markdown(
        f"""
        <div class="workflow-wrap">
            <img src="data:image/png;base64,{img_b64}" class="workflow-img" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_developer_footer():
    """Render compact developer information in a fixed footer."""
    st.markdown(
        """
        <div class="cpcgr-footer">
            <div class="cpcgr-footer-main">
                Developed by Sheikh Sunzid Ahmed and M. Oliur Rahman
            </div>
            <div class="cpcgr-footer-sub">
                Plant Taxonomy and Ethnobotany Laboratory &bull; Department of Botany, University of Dhaka
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.55rem;
        padding-bottom: 3.9rem;
        max-width: 1580px;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F6FFF8 0%, #FFFFFF 100%);
    }
    .cpcgr-title-wrap {
        margin: 0.55rem 0 0.22rem 0;
        padding: 0;
    }
    .cpcgr-title {
        color: #1B4332;
        font-size: 2.0rem;
        line-height: 1.05;
        font-weight: 800;
        margin: 0;
        padding: 0;
        letter-spacing: -0.02em;
    }
    .cpcgr-intro {
        background: linear-gradient(90deg, #F1FAF4 0%, #FFFFFF 100%);
        border: 1px solid #B7E4C7;
        border-left: 5px solid #2D6A4F;
        border-radius: 10px;
        padding: 0.55rem 0.75rem;
        margin: 0.28rem 0 0.55rem 0;
        box-shadow: 0 1px 3px rgba(27, 67, 50, 0.06);
        font-size: 0.84rem;
        line-height: 1.42;
        color: #1B4332;
    }
    .home-section-title {
        color: #1B4332;
        font-size: 0.98rem;
        font-weight: 800;
        margin: 0.25rem 0 0.35rem 0;
    }
    .home-compact-table {
        border: 1px solid #D8F3DC;
        border-radius: 11px;
        overflow: hidden;
        margin-top: 0.25rem;
        box-shadow: 0 1px 4px rgba(27, 67, 50, 0.06);
    }
    .home-table-row {
        display: flex;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.44rem 0.65rem;
        border-bottom: 1px solid #E9F7EF;
        background: #FFFFFF;
        align-items: center;
    }
    .home-table-row:nth-child(even) {
        background: #F8FFF9;
    }
    .home-table-row:last-child {
        border-bottom: none;
    }
    .home-table-label {
        font-size: 0.80rem;
        color: #48505A;
        font-weight: 600;
    }
    .home-table-value {
        font-size: 0.92rem;
        color: #1B4332;
        font-weight: 800;
        text-align: right;
        white-space: nowrap;
    }
    .workflow-heading {
        color: #1B4332;
        font-size: 0.98rem;
        font-weight: 800;
        margin: 0.58rem 0 0.28rem 0;
    }
    .workflow-wrap {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        margin-top: 2.35rem;
    }
    .workflow-img {
        width: 88%;
        max-width: 660px;
        height: auto;
        border-radius: 9px;
        border: 1px solid #D8F3DC;
        box-shadow: 0 1px 5px rgba(27, 67, 50, 0.08);
    }
    .cpcgr-footer {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 999;
        background: rgba(246, 255, 248, 0.96);
        border-top: 1px solid #B7E4C7;
        box-shadow: 0 -2px 10px rgba(27, 67, 50, 0.06);
        padding: 0.42rem 1rem 0.38rem 1rem;
        text-align: center;
        backdrop-filter: blur(6px);
    }
    .cpcgr-footer-main {
        color: #1B4332;
        font-size: 0.78rem;
        line-height: 1.22;
        font-weight: 800;
        letter-spacing: 0.01em;
    }
    .cpcgr-footer-sub {
        color: #4A5C52;
        font-size: 0.69rem;
        line-height: 1.20;
        font-weight: 600;
        margin-top: 0.08rem;
    }
    @media (max-width: 1100px) {
        .workflow-img {
            width: 92%;
            max-width: 100%;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# File names
# ============================================================
FILES = {
    "workflow": "workflow.png",
    "genome_map": "Clerodendrum paniculatum Orbicular Cp genome map.jpg",
    "ir_junction": "IR_Junction_Sites_IRPlus_results.jpg",
    "mvista": "mVISTA analysis figure C_paniculatum.jpg",
    "phylogeny": "Phylogenetic_analysis_ML.jpg",
    "dating": "Molecular dating tree.jpg",
    "ssr_chart": "SSR analysis_Barchart.jpg",
    "cis_pdf": "cis_splicing_genes_C_paniculatum.pdf",
    "trans_pdf": "trans_splicing_genes_C_paniculatum.pdf",
    "gene_sequences": "C_paniculatum_gene_sequences_with_composition.csv",
    "gene_stats": "C_paniculatum_gene_sequence_stats_compact.csv",
    "gene_type_summary": "C_paniculatum_gene_sequence_type_summary.csv",
    "pcg_stats": "C_paniculatum_PCG_sequence_stats.csv",
    "trna_stats": "C_paniculatum_tRNA_sequence_stats.csv",
    "rrna_stats": "C_paniculatum_rRNA_sequence_stats.csv",
    "codon": "Codon usage bias.txt",
    "misa": "MISA_SSR_results.txt",
    "exon_intron": "Exon_intron_distribution.txt",
    "cpgview": "Results of CPGview server.txt",
    "feature_table": "Five_column_feature_table.txt",
    "genbank": "GenBank_file.txt",
    "fasta": "C_paniculatum_fasta_sequence.txt",
    "pcg_fasta": "PCG.txt",
    "trna_fasta": "tRNA.txt",
    "rrna_fasta": "rRNA.txt",
    "workbook": "C_paniculatum_website_tables_workbook.xlsx",
}


# ============================================================
# Corrected gene-coordinate data
# These tables are used directly for the Gene Coordinates page.
# ============================================================

PCG_COORDINATE_TEXT = """
accD 1482 [57313:58794](+)
atpA 1524 [10394:11917](-)
atpB 1497 [52870:54366](-)
atpE 402 [52472:52873](-)
atpF 555 [13097:13241](-) [12020:12429](-)
atpH 246 [13627:13872](-)
atpI 744 [14897:15640](-)
ccsA 966 [112844:113809](+)
cemA 690 [61165:61854](+)
clpP 591 [71565:71635](-) [70544:70837](-) [69692:69917](-)
infA 234 [79311:79544](-)
matK 1518 [2012:3529](-)
ndhA 1092 [119628:120180](-) [118166:118704](-)
ndhB 1533 [95294:96068](-) [93857:94614](-)
ndhB_copy2 1533 [139746:140520](+) [141200:141957](+)
ndhC 363 [50114:50476](-)
ndhD 1530 [114054:115583](-)
ndhE 306 [116179:116484](-)
ndhF 2235 [109255:111489](-)
ndhG 531 [116696:117226](-)
ndhH 1182 [120182:121363](-)
ndhI 507 [117579:118085](-)
ndhJ 477 [48806:49282](-)
ndhK 678 [49383:50060](-)
petA 963 [62064:63026](+)
petG 114 [65887:66000](+)
petL 96 [65615:65710](+)
petN 90 [28983:29072](+)
psaA 2253 [39464:41716](-)
psaB 2205 [37234:39438](-)
psaC 246 [115683:115928](-)
psaI 111 [59400:59510](+)
psaJ 135 [66711:66845](+)
psbA 1059 [446:1504](-)
psbB 1527 [72057:73583](+)
psbC 1422 [33841:35262](+)
psbD 1062 [32832:33893](+)
psbE 252 [64452:64703](-)
psbF 120 [64318:64437](-)
psbH 222 [74166:74387](+)
psbI 111 [8270:8380](+)
psbJ 123 [63922:64044](-)
psbK 186 [7678:7863](+)
psbL 117 [64178:64294](-)
psbM 105 [29991:30095](-)
psbN 132 [73929:74060](-)
psbT 108 [73761:73868](+)
psbZ 189 [35943:36131](+)
rbcL 1440 [55168:56607](+)
rpl14 369 [80235:80603](-)
rpl2 825 [84731:85121](-) [83630:84063](-)
rpl20 408 [68209:68616](-)
rpl22 468 [82775:83242](-)
rpl23 282 [85140:85421](-)
rpl23_copy2 282 [150393:150674](+)
rpl2_copy2 825 [150693:151083](+) [151751:152184](+)
rpl32 177 [112042:112218](+)
rpl33 201 [67317:67517](+)
rpl36 114 [79101:79214](-)
rpoA 1014 [77493:78506](-)
rpoB 3213 [23939:27151](-)
rpoC1 2115 [23483:23912](-) [21038:22722](-)
rpoC2 4182 [16767:20948](-)
rps11 417 [78583:78999](-)
rps12 372 [69449:69562](-) [97429:97660](-) [96864:96889](-)
rps12_copy2 372 [69449:69562](-) [138154:138385](+) [138925:138950](+)
rps14 303 [36807:37109](-)
rps15 273 [121460:121732](-)
rps18 306 [67689:67994](+)
rps19 279 [83298:83576](-)
rps2 711 [15845:16555](-)
rps3 657 [82134:82790](-)
rps4 606 [45480:46085](-)
rps7 468 [96343:96810](-)
rps7_copy2 468 [139004:139471](+)
rps8 405 [79669:80073](-)
ycf1 5565 [122103:127667](-)
ycf15 204 [92742:92945](+)
ycf15_copy2 204 [142869:143072](-)
ycf2 6852 [85749:92600](+)
ycf2_copy2 6852 [143214:150065](-)
ycf3 507 [44253:44378](-) [43310:43537](-) [42444:42596](-)
ycf4 555 [59940:60494](+)
"""

TRNA_COORDINATE_TEXT = """
trnH-GUG [2:75](-)
trnK-UUU [4234:4270](-) [1719:1754](-)
trnQ-UUG [7258:7329](-)
trnS-GCU [8504:8591](-)
trnS-CGA [9262:9293](+) [9973:10032](+)
trnR-UCU [10218:10289](+)
trnC-GCA [28370:28440](+)
trnD-GUC [30619:30692](-)
trnY-GUA [30811:30894](-)
trnE-UUC [30954:31026](-)
trnT-GGU [31583:31654](+)
trnS-UGA [35523:35615](-)
trnG-GCC [36348:36418](+)
trnM-CAU [36589:36662](-)
trnS-GGA [45074:45160](+)
trnT-UGU [46473:46545](-)
trnL-UAA [47237:47271](+) [47755:47804](+)
trnF-GAA [48099:48171](+)
trnV-UAC [51950:51987](-) [51323:51357](-)
trnM-CAU_copy2 [52168:52240](+)
trnW-CCA [66121:66194](-)
trnP-UGG [66357:66430](-)
trnM-CAU_copy3 [85587:85660](-)
trnL-CAA [93218:93298](-)
trnV-GAC [99247:99318](+)
trnE-UUC_copy2 [101334:101365](+) [102316:102355](+)
trnA-UGC [102420:102456](+) [103264:103299](+)
trnR-ACG [107097:107170](+)
trnN-GUU [107734:107805](-)
trnL-UAG [112674:112753](+)
trnN-GUU_copy2 [128009:128080](+)
trnR-ACG_copy2 [128644:128717](-)
trnA-UGC_copy2 [133358:133394](-) [132515:132550](-)
trnE-UUC_copy3 [134449:134480](-) [133459:133498](-)
trnV-GAC_copy2 [136496:136567](-)
trnL-CAA_copy2 [142516:142596](+)
trnM-CAU_copy4 [150154:150227](+)
"""

RRNA_COORDINATE_TEXT = """
rrn16S [99546:101036](+)
rrn23S [103464:106273](+)
rrn4.5S [106372:106474](+)
rrn5S [106735:106855](+)
rrn5S_copy2 [128959:129079](-)
rrn4.5S_copy2 [129340:129442](-)
rrn23S_copy2 [129541:132350](-)
rrn16S_copy2 [134778:136268](-)
"""


# ============================================================
# Utility functions
# ============================================================
def file_path(key_or_name: str) -> Path:
    name = FILES.get(key_or_name, key_or_name)
    return BASE_DIR / name


def exists(key_or_name: str) -> bool:
    return file_path(key_or_name).exists()


def read_text_file(key_or_name: str, max_chars: int | None = None) -> str:
    path = file_path(key_or_name)
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if max_chars is not None and len(text) > max_chars:
        text = text[:max_chars] + "\n\n...[truncated for display]..."
    return text


@st.cache_data
def load_csv_file(filename: str) -> pd.DataFrame:
    path = BASE_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def show_download_button(path: Path, label: str | None = None):
    if not path.exists():
        return
    with open(path, "rb") as f:
        st.download_button(
            label=label or f"Download {path.name}",
            data=f,
            file_name=path.name,
            mime="application/octet-stream",
            use_container_width=True,
        )


def show_image(key: str, caption: str):
    path = file_path(key)
    if not path.exists():
        st.warning(f"File not found: {path.name}")
        return
    st.image(str(path), caption=caption, use_container_width=True)
    show_download_button(path, f"Download {path.name}")


def wrap_sequence(seq: str, width: int = 80) -> str:
    seq = str(seq).replace("\n", "").replace(" ", "")
    return "\n".join(textwrap.wrap(seq, width))


def split_locations(location_text: str) -> list[str]:
    if pd.isna(location_text):
        return []
    return re.findall(r"\[\d+:\d+\]\([+-]\)", str(location_text))


def parse_single_location(loc: str) -> dict:
    m = re.match(r"\[(\d+):(\d+)\]\(([+-])\)", loc)
    if not m:
        return {}
    start, end, strand = int(m.group(1)), int(m.group(2)), m.group(3)
    return {
        "Start": start,
        "End": end,
        "Strand": strand,
        "Location": loc,
        "Segment_length_bp": abs(end - start) + 1,
    }


@st.cache_data
def build_gene_coordinate_tables() -> dict[str, pd.DataFrame]:
    tables = {}

    def parse_block(text: str, gene_type: str, has_length: bool) -> pd.DataFrame:
        rows = []
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            gene = parts[0]
            if has_length:
                length_bp = int(parts[1])
                loc_text = " ".join(parts[2:])
            else:
                length_bp = None
                loc_text = " ".join(parts[1:])

            locs = split_locations(loc_text)
            parsed_locs = [parse_single_location(x) for x in locs]
            starts = [x["Start"] for x in parsed_locs if x]
            ends = [x["End"] for x in parsed_locs if x]
            strands = sorted(set(x["Strand"] for x in parsed_locs if x))

            rows.append({
                "Gene": gene,
                "Gene_type": gene_type,
                "Length_bp": length_bp,
                "Number_of_locations": len(locs),
                "Genomic_span_start": min(starts) if starts else None,
                "Genomic_span_end": max(ends) if ends else None,
                "Strand": ", ".join(strands),
                "Location_1": locs[0] if len(locs) >= 1 else "",
                "Location_2": locs[1] if len(locs) >= 2 else "",
                "Location_3": locs[2] if len(locs) >= 3 else "",
                "All_locations": "; ".join(locs),
                "Copy_status": "Copy" if "copy" in gene.lower() else "Primary/unique",
            })
        return pd.DataFrame(rows)

    tables["pcg"] = parse_block(PCG_COORDINATE_TEXT, "Protein-coding gene", True)
    tables["trna"] = parse_block(TRNA_COORDINATE_TEXT, "tRNA", False)
    tables["rrna"] = parse_block(RRNA_COORDINATE_TEXT, "rRNA", False)

    all_df = pd.concat([tables["pcg"], tables["trna"], tables["rrna"]], ignore_index=True)
    tables["all"] = all_df
    return tables


def parse_fasta_text(text: str) -> pd.DataFrame:
    records = []
    if not text.strip():
        return pd.DataFrame()

    chunks = re.split(r"\n(?=>)", text.strip())
    for chunk in chunks:
        lines = chunk.strip().splitlines()
        if not lines or not lines[0].startswith(">"):
            continue
        header = lines[0][1:].strip()
        gene = header.split()[0].strip()
        seq = "".join(line.strip() for line in lines[1:] if line.strip())
        seq = re.sub(r"[^ACGTNacgtn]", "", seq).upper()
        if not seq:
            continue
        a, t, g, c, n = seq.count("A"), seq.count("T"), seq.count("G"), seq.count("C"), seq.count("N")
        length = len(seq)
        records.append({
            "Gene": gene,
            "Header": header,
            "Length_bp": length,
            "A_count": a,
            "T_count": t,
            "G_count": g,
            "C_count": c,
            "N_count": n,
            "AT_percent": round(((a + t) / length) * 100, 2) if length else 0,
            "GC_percent": round(((g + c) / length) * 100, 2) if length else 0,
            "Sequence": seq,
        })
    return pd.DataFrame(records)


@st.cache_data
def load_gene_sequences() -> pd.DataFrame:
    path = file_path("gene_sequences")
    if path.exists():
        df = pd.read_csv(path)
        for col in ["Gene", "Gene_type", "Length_bp", "A_count", "T_count", "G_count", "C_count", "AT_percent", "GC_percent", "Sequence"]:
            if col not in df.columns:
                df[col] = ""
        return df

    combined = []
    for gene_type, key in [("Protein-coding gene", "pcg_fasta"), ("tRNA", "trna_fasta"), ("rRNA", "rrna_fasta")]:
        txt = read_text_file(key)
        df = parse_fasta_text(txt)
        if not df.empty:
            df["Gene_type"] = gene_type
            combined.append(df)
    if combined:
        return pd.concat(combined, ignore_index=True)
    return pd.DataFrame()


@st.cache_data
def parse_codon_usage() -> tuple[pd.DataFrame, pd.DataFrame]:
    text = read_text_file("codon")
    if not text:
        return pd.DataFrame(), pd.DataFrame()

    summary_rows = []
    table_rows = []
    in_table = False

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("#CdsCount"):
            parts = line.replace("#", "").split(":")
            if len(parts) == 2:
                summary_rows.append({"Metric": "CDS count used for codon analysis", "Value": parts[1].strip()})
        elif line.startswith("#Coding GC"):
            summary_rows.append({"Metric": "Coding GC", "Value": line.replace("#Coding GC", "").strip()})
        elif line.startswith("#1st letter GC"):
            summary_rows.append({"Metric": "GC at first codon position", "Value": line.replace("#1st letter GC", "").strip()})
        elif line.startswith("#2nd letter GC"):
            summary_rows.append({"Metric": "GC at second codon position", "Value": line.replace("#2nd letter GC", "").strip()})
        elif line.startswith("#3rd letter GC"):
            summary_rows.append({"Metric": "GC at third codon position", "Value": line.replace("#3rd letter GC", "").strip()})
        elif line.startswith("#Codon"):
            in_table = True
            continue
        elif in_table:
            parts = line.split()
            if len(parts) >= 5:
                try:
                    table_rows.append({
                        "Codon": parts[0],
                        "Amino_acid": parts[1],
                        "Fraction": float(parts[2]),
                        "Frequency": float(parts[3]),
                        "Number": int(float(parts[4])),
                    })
                except Exception:
                    pass

    return pd.DataFrame(summary_rows), pd.DataFrame(table_rows)


@st.cache_data
def parse_misa_summary() -> dict[str, pd.DataFrame]:
    """
    Updated MISA SSR summary based on the revised MISA output supplied by the user.

    Updated MISA summary:
    - Total SSRs: 72
    - Compound SSRs: 10
    - Maximum interruption for compound SSRs: 100 bp
    """
    results = {}

    results["summary"] = pd.DataFrame([
        {"Metric": "Total number of sequences examined", "Value": "1"},
        {"Metric": "Total size of examined sequences bp", "Value": "152278"},
        {"Metric": "Total number of identified SSRs", "Value": "72"},
        {"Metric": "Number of SSR-containing sequences", "Value": "1"},
        {"Metric": "Sequences containing more than 1 SSR", "Value": "1"},
        {"Metric": "SSRs in compound formation", "Value": "10"},
        {"Metric": "Maximum interruption between compound SSRs bp", "Value": "100"},
    ])

    results["unit_distribution"] = pd.DataFrame([
        {"Unit_size": 1, "Repeat_class": "Mono", "Number_of_SSRs": 53},
        {"Unit_size": 2, "Repeat_class": "Di", "Number_of_SSRs": 5},
        {"Unit_size": 3, "Repeat_class": "Tri", "Number_of_SSRs": 4},
        {"Unit_size": 4, "Repeat_class": "Tetra", "Number_of_SSRs": 8},
        {"Unit_size": 5, "Repeat_class": "Penta", "Number_of_SSRs": 2},
    ])

    results["identified_motif_frequency"] = pd.DataFrame([
        {"Motif": "A", "Repeat_count_summary": "10:7; 11:7; 12:3; 13:2", "Total": 19},
        {"Motif": "C", "Repeat_count_summary": "10:1; 12:1", "Total": 2},
        {"Motif": "G", "Repeat_count_summary": "13:1; 14:1", "Total": 2},
        {"Motif": "T", "Repeat_count_summary": "10:15; 11:8; 12:3; 13:1; 14:1; 16:1; 26:1", "Total": 30},
        {"Motif": "AT", "Repeat_count_summary": "5:1; 6:1; 8:1", "Total": 3},
        {"Motif": "TA", "Repeat_count_summary": "7:2", "Total": 2},
        {"Motif": "ATA", "Repeat_count_summary": "4:1; 5:1", "Total": 2},
        {"Motif": "TAA", "Repeat_count_summary": "4:1", "Total": 1},
        {"Motif": "TTC", "Repeat_count_summary": "4:1", "Total": 1},
        {"Motif": "AATA", "Repeat_count_summary": "3:1", "Total": 1},
        {"Motif": "ATAA", "Repeat_count_summary": "3:2", "Total": 2},
        {"Motif": "GTCT", "Repeat_count_summary": "3:1", "Total": 1},
        {"Motif": "TAAA", "Repeat_count_summary": "3:1", "Total": 1},
        {"Motif": "TCTA", "Repeat_count_summary": "3:1", "Total": 1},
        {"Motif": "TTTA", "Repeat_count_summary": "3:1", "Total": 1},
        {"Motif": "TTTC", "Repeat_count_summary": "3:1", "Total": 1},
        {"Motif": "AATAA", "Repeat_count_summary": "3:1", "Total": 1},
        {"Motif": "ATAAG", "Repeat_count_summary": "3:1", "Total": 1},
    ])

    results["classified_repeat_frequency"] = pd.DataFrame([
        {"Classified_repeat_type": "A/T", "Repeat_count_summary": "10:22; 11:15; 12:6; 13:3; 14:1; 16:1; 26:1", "Total": 49},
        {"Classified_repeat_type": "C/G", "Repeat_count_summary": "10:1; 12:1; 13:1; 14:1", "Total": 4},
        {"Classified_repeat_type": "AT/AT", "Repeat_count_summary": "5:1; 6:1; 7:2; 8:1", "Total": 5},
        {"Classified_repeat_type": "AAG/CTT", "Repeat_count_summary": "4:1", "Total": 1},
        {"Classified_repeat_type": "AAT/ATT", "Repeat_count_summary": "4:2; 5:1", "Total": 3},
        {"Classified_repeat_type": "AAAG/CTTT", "Repeat_count_summary": "3:1", "Total": 1},
        {"Classified_repeat_type": "AAAT/ATTT", "Repeat_count_summary": "3:5", "Total": 5},
        {"Classified_repeat_type": "ACAG/CTGT", "Repeat_count_summary": "3:1", "Total": 1},
        {"Classified_repeat_type": "AGAT/ATCT", "Repeat_count_summary": "3:1", "Total": 1},
        {"Classified_repeat_type": "AAAAT/ATTTT", "Repeat_count_summary": "3:1", "Total": 1},
        {"Classified_repeat_type": "AAGAT/ATCTT", "Repeat_count_summary": "3:1", "Total": 1},
    ])

    return results


@st.cache_data
def parse_exon_intron_table() -> pd.DataFrame:
    text = read_text_file("exon_intron")
    if not text:
        return pd.DataFrame()

    rows = []
    capture = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Gene") and "Strand" in line and "ExonI" in line:
            capture = True
            continue
        if capture:
            if not line or line.startswith("_") or line.startswith("#"):
                continue
            if line.startswith("Table 3"):
                break
            parts = line.split()
            if len(parts) >= 7:
                row = {
                    "Gene": parts[0],
                    "Strand": parts[1],
                    "Start": parts[2],
                    "End": parts[3],
                    "ExonI": parts[4],
                    "IntronI": parts[5],
                    "ExonII": parts[6],
                    "IntronII": parts[7] if len(parts) > 7 else "",
                    "ExonIII": parts[8] if len(parts) > 8 else "",
                }
                rows.append(row)

    return pd.DataFrame(rows)


def pdf_download_and_viewer(key: str, title: str):
    """Download and preview PDFs in a deployment-friendly way.

    Streamlit Community Cloud / Edge can block base64 data-PDF iframes.
    The streamlit-pdf-viewer component avoids the Edge-blocked iframe issue.
    """
    path = file_path(key)
    st.subheader(title)
    if not path.exists():
        st.warning(f"File not found: {path.name}")
        return

    show_download_button(path, f"Download {path.name}")

    if pdf_viewer is None:
        st.info(
            "PDF preview component is not installed on this deployment. "
            "Add `streamlit-pdf-viewer` to requirements.txt, redeploy, "
            "or use the download button above."
        )
        return

    try:
        pdf_viewer(
            str(path),
            width=700,
            height=650,
            key=f"pdf_viewer_{key}",
        )
    except TypeError:
        # Compatibility fallback for older versions of streamlit-pdf-viewer.
        pdf_viewer(str(path), width=700, height=650)
    except Exception:
        st.info("PDF preview is unavailable in this browser. Please use the download button.")


def download_all_available_files():
    st.subheader("Available source files")
    file_rows = []
    for key, name in FILES.items():
        p = BASE_DIR / name
        if p.exists():
            file_rows.append({
                "File": name,
                "Size_kB": round(p.stat().st_size / 1024, 2),
            })
    if file_rows:
        st.dataframe(pd.DataFrame(file_rows), use_container_width=True, hide_index=True)
    else:
        st.warning("No expected files found in this folder.")


def show_gene_location_table(df: pd.DataFrame, title: str, key_prefix: str):
    st.subheader(title)

    if df.empty:
        st.warning(f"No data available for {title}.")
        return

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        q = st.text_input(
            f"Search {title}",
            key=f"{key_prefix}_search",
            placeholder="Type gene name, e.g. ndhB, rpl2, trnA, rrn16S",
        )
    with col2:
        copy_filter = st.selectbox(
            "Copy status",
            ["All", "Primary/unique", "Copy"],
            key=f"{key_prefix}_copy_filter",
        )
    with col3:
        strand_filter = st.selectbox(
            "Strand",
            ["All", "+", "-", "+, -"],
            key=f"{key_prefix}_strand_filter",
        )
    with col4:
        mult_filter = st.selectbox(
            "Locations",
            ["All", "Single location", "Multiple locations"],
            key=f"{key_prefix}_multi_filter",
        )

    filtered = df.copy()

    if q:
        filtered = filtered[filtered["Gene"].astype(str).str.contains(q, case=False, na=False)]

    if copy_filter != "All":
        filtered = filtered[filtered["Copy_status"] == copy_filter]

    if strand_filter != "All":
        filtered = filtered[filtered["Strand"].astype(str) == strand_filter]

    if mult_filter == "Single location":
        filtered = filtered[filtered["Number_of_locations"] == 1]
    elif mult_filter == "Multiple locations":
        filtered = filtered[filtered["Number_of_locations"] > 1]

    display_cols = [
        "Gene",
        "Gene_type",
        "Number_of_locations",
        "Genomic_span_start",
        "Genomic_span_end",
        "Strand",
        "Location_1",
        "Location_2",
        "Location_3",
        "All_locations",
        "Copy_status",
    ]

    display_cols = [c for c in display_cols if c in filtered.columns]
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

    st.caption(
        "Genes with multiple locations represent split genes or multi-exon/multi-segment annotations. "
        "The All_locations column preserves every annotated coordinate block."
    )

    csv = filtered[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        f"Download filtered {title} CSV",
        data=csv,
        file_name=f"{key_prefix}_filtered_locations.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# Sidebar navigation
# ============================================================
page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Genome Overview",
        "Genome Map",
        "Gene Browser",
        "Gene Coordinates",
        "Codon Usage",
        "SSR Analysis",
        "Exon-Intron & Splicing",
        "mVISTA Divergence",
        "IR Junctions",
        "Phylogeny",
        "Molecular Dating",
        "Raw Files & Downloads",
    ],
)


# ============================================================
# Pages
# ============================================================
if page == "Home":
    left_col, right_col = st.columns([0.78, 1.22], gap="large")

    with left_col:
        render_title_block()
        render_home_intro_box()
        render_compact_metrics()

    with right_col:
        render_workflow_image()


elif page == "Genome Overview":
    st.title("Genome Overview")

    overview = pd.DataFrame([
        {"Feature": "Species", "Value": "Clerodendrum paniculatum"},
        {"Feature": "Genome type", "Value": "Chloroplast genome"},
        {"Feature": "Genome size", "Value": "152,278 bp"},
        {"Feature": "Total genes", "Value": "128"},
        {"Feature": "Unique genes", "Value": "107"},
        {"Feature": "Protein-coding genes", "Value": "83 total; 76 unique"},
        {"Feature": "tRNA genes", "Value": "37 total; 28 unique"},
        {"Feature": "rRNA genes", "Value": "8 total; 4 unique"},
        {"Feature": "Main analyses", "Value": "Annotation, SSR, mVISTA, IR junctions, ML phylogeny, molecular dating"},
    ])

    st.dataframe(overview, use_container_width=True, hide_index=True)

    gene_summary = pd.DataFrame([
        {"Gene class": "Protein-coding genes", "Total": 83, "Unique": 76},
        {"Gene class": "tRNA genes", "Total": 37, "Unique": 28},
        {"Gene class": "rRNA genes", "Total": 8, "Unique": 4},
        {"Gene class": "All genes", "Total": 128, "Unique": 107},
    ])

    st.subheader("Gene count summary")
    st.dataframe(gene_summary, use_container_width=True, hide_index=True)

    if px is not None:
        fig = px.bar(
            gene_summary,
            x="Gene class",
            y=["Total", "Unique"],
            barmode="group",
            title="Total and unique gene counts",
        )
        st.plotly_chart(fig, use_container_width=True)

    df_summary = load_csv_file(FILES["gene_type_summary"])
    if not df_summary.empty:
        st.subheader("Sequence type summary")
        st.dataframe(df_summary, use_container_width=True, hide_index=True)

        if px is not None:
            fig = px.bar(
                df_summary,
                x="Gene_type",
                y="Number_of_sequences",
                text="Number_of_sequences",
                title="Number of unique sequence entries by gene type",
            )
            st.plotly_chart(fig, use_container_width=True)


elif page == "Genome Map":
    st.title("Circular Chloroplast Genome Map")
    st.markdown(
        "The circular plastome map displays gene arrangement, transcription direction, functional gene categories, "
        "and the LSC, SSC, IRa, and IRb regions."
    )
    show_image("genome_map", "Circular chloroplast genome map of C. paniculatum")


elif page == "Gene Browser":
    st.title("Searchable Gene Sequence Browser")

    df = load_gene_sequences()
    if df.empty:
        st.error("Gene sequence table not found. Please keep C_paniculatum_gene_sequences_with_composition.csv in this folder.")
        st.stop()

    st.markdown(
        "Search or filter protein-coding genes, tRNAs, and rRNAs. Select a gene to display its sequence, "
        "length, GC percentage, AT percentage, and nucleotide composition."
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        gene_types = ["All"] + sorted(df["Gene_type"].dropna().unique().tolist())
        selected_type = st.selectbox("Gene type", gene_types)
    with col2:
        query = st.text_input("Search gene name", placeholder="Example: rbcL, matK, trnH, ndhB")
    with col3:
        sort_by = st.selectbox("Sort by", ["Gene", "Length_bp", "GC_percent", "AT_percent"])

    filtered = df.copy()
    if selected_type != "All":
        filtered = filtered[filtered["Gene_type"] == selected_type]
    if query:
        filtered = filtered[filtered["Gene"].astype(str).str.contains(query, case=False, na=False)]

    filtered = filtered.sort_values(sort_by, ascending=True)

    display_cols = ["Gene", "Gene_type", "Length_bp", "A_count", "T_count", "G_count", "C_count", "AT_percent", "GC_percent"]
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

    if filtered.empty:
        st.warning("No gene matched your search.")
        st.stop()

    selected_gene = st.selectbox("Select a gene to display", filtered["Gene"].tolist())
    row = filtered[filtered["Gene"] == selected_gene].iloc[0]

    st.subheader(f"Selected gene: {row['Gene']}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gene type", str(row["Gene_type"]))
    m2.metric("Length", f"{int(row['Length_bp'])} bp")
    m3.metric("GC content", f"{float(row['GC_percent']):.2f}%")
    m4.metric("AT content", f"{float(row['AT_percent']):.2f}%")

    comp_df = pd.DataFrame({
        "Base": ["A", "T", "G", "C"],
        "Count": [int(row["A_count"]), int(row["T_count"]), int(row["G_count"]), int(row["C_count"])],
    })

    if px is not None:
        fig = px.bar(comp_df, x="Base", y="Count", text="Count", title=f"Nucleotide composition of {row['Gene']}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(comp_df.set_index("Base"))

    st.markdown("### Sequence")
    st.code(wrap_sequence(row["Sequence"], 80), language="text")

    fasta_text = f">{row['Gene']} {row['Gene_type']} length={int(row['Length_bp'])}bp GC={float(row['GC_percent']):.2f}%\n{wrap_sequence(row['Sequence'], 80)}\n"
    st.download_button(
        f"Download {row['Gene']} FASTA",
        data=fasta_text,
        file_name=f"{row['Gene']}.fasta",
        mime="text/plain",
        use_container_width=True,
    )

    st.markdown("### Download full gene sequence tables")
    c1, c2, c3 = st.columns(3)
    with c1:
        show_download_button(file_path("gene_sequences"), "Download full gene sequence CSV")
    with c2:
        show_download_button(file_path("gene_stats"), "Download compact gene stats CSV")
    with c3:
        show_download_button(file_path("workbook"), "Download website workbook")


elif page == "Gene Coordinates":
    st.title("Gene Location / Coordinate Tables")

    st.markdown(
        """
        This page shows the genomic locations of annotated protein-coding genes, tRNAs, and rRNAs.
        Genes with multiple coordinate blocks represent split genes, exon-containing genes, or duplicated/multipart annotations.
        """
    )

    tables = build_gene_coordinate_tables()

    tabs = st.tabs(["All genes", "Protein-coding genes", "tRNA genes", "rRNA genes"])

    with tabs[0]:
        show_gene_location_table(tables["all"], "All annotated gene locations", "all_gene_locations")

    with tabs[1]:
        show_gene_location_table(tables["pcg"], "Protein-coding gene locations", "pcg_locations")

    with tabs[2]:
        show_gene_location_table(tables["trna"], "tRNA gene locations", "trna_locations")

    with tabs[3]:
        show_gene_location_table(tables["rrna"], "rRNA gene locations", "rrna_locations")


elif page == "Codon Usage":
    st.title("Codon Usage Bias")

    summary_df, codon_df = parse_codon_usage()

    if not summary_df.empty:
        st.subheader("Codon GC summary")
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    if not codon_df.empty:
        st.subheader("Codon usage table")
        st.dataframe(codon_df, use_container_width=True, hide_index=True)

        if px is not None:
            top = codon_df.sort_values("Number", ascending=False).head(15)
            fig = px.bar(
                top,
                x="Codon",
                y="Number",
                color="Amino_acid",
                text="Number",
                title="Top 15 most frequent codons",
            )
            st.plotly_chart(fig, use_container_width=True)

            aa = st.selectbox("View synonymous codon usage for amino acid", sorted(codon_df["Amino_acid"].unique()))
            aa_df = codon_df[codon_df["Amino_acid"] == aa]
            fig2 = px.bar(
                aa_df,
                x="Codon",
                y="Fraction",
                text="Fraction",
                title=f"Codon fraction for amino acid {aa}",
            )
            st.plotly_chart(fig2, use_container_width=True)

    show_download_button(file_path("codon"), "Download original codon usage file")


elif page == "SSR Analysis":
    st.title("Simple Sequence Repeat Analysis")

    st.markdown(
        """
        SSRs were identified using MISA with the updated repeat thresholds:
        mono-nucleotide ≥10, di-nucleotide ≥5, tri-nucleotide ≥4,
        tetra-/penta-/hexa-nucleotide ≥3. Compound SSRs were identified using
        a maximum interruption distance of 100 bp.
        """
    )

    misa = parse_misa_summary()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Updated MISA SSR summary")
        if "summary" in misa and not misa["summary"].empty:
            st.dataframe(misa["summary"], use_container_width=True, hide_index=True)

        st.subheader("SSR unit-size distribution")
        if "unit_distribution" in misa and not misa["unit_distribution"].empty:
            st.dataframe(misa["unit_distribution"], use_container_width=True, hide_index=True)

            if px is not None:
                fig = px.bar(
                    misa["unit_distribution"],
                    x="Repeat_class",
                    y="Number_of_SSRs",
                    text="Number_of_SSRs",
                    title="Distribution of SSRs by repeat unit size",
                )
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        show_image("ssr_chart", "SSR repeat type comparison among selected chloroplast genomes")

    st.markdown("---")

    tabs = st.tabs(["Identified SSR motifs", "Classified repeat types"])

    with tabs[0]:
        st.subheader("Frequency of identified SSR motifs")
        motif_df = misa.get("identified_motif_frequency", pd.DataFrame())
        if not motif_df.empty:
            st.dataframe(motif_df, use_container_width=True, hide_index=True)

            if px is not None:
                fig = px.bar(
                    motif_df.sort_values("Total", ascending=False),
                    x="Motif",
                    y="Total",
                    text="Total",
                    title="Frequency of identified SSR motifs",
                )
                st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                "Download identified SSR motif frequency CSV",
                data=motif_df.to_csv(index=False).encode("utf-8"),
                file_name="C_paniculatum_identified_SSR_motif_frequency.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with tabs[1]:
        st.subheader("Frequency of classified repeat types")
        class_df = misa.get("classified_repeat_frequency", pd.DataFrame())
        if not class_df.empty:
            st.dataframe(class_df, use_container_width=True, hide_index=True)

            if px is not None:
                fig = px.bar(
                    class_df.sort_values("Total", ascending=False),
                    x="Classified_repeat_type",
                    y="Total",
                    text="Total",
                    title="Frequency of classified SSR repeat types",
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                "Download classified repeat type frequency CSV",
                data=class_df.to_csv(index=False).encode("utf-8"),
                file_name="C_paniculatum_classified_SSR_repeat_frequency.csv",
                mime="text/csv",
                use_container_width=True,
            )

    st.markdown("### Download source/result files")
    show_download_button(file_path("misa"), "Download original MISA SSR results file")


elif page == "Exon-Intron & Splicing":
    st.title("Exon-Intron Organization and Splicing Genes")

    exon_df = parse_exon_intron_table()
    if not exon_df.empty:
        st.subheader("Lengths of introns and exons for split genes")
        st.dataframe(exon_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Could not parse exon-intron table.")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        pdf_download_and_viewer("cis_pdf", "Cis-splicing genes")
    with c2:
        pdf_download_and_viewer("trans_pdf", "Trans-splicing genes")


elif page == "mVISTA Divergence":
    st.title("mVISTA Genome Divergence Analysis")
    st.markdown(
        "The mVISTA plot compares chloroplast genomes using *C. paniculatum* as the reference. "
        "Conserved and divergent regions are displayed across coding and noncoding regions."
    )
    show_image("mvista", "mVISTA genome divergence plot")


elif page == "IR Junctions":
    st.title("IR Junction Site Analysis")
    st.markdown(
        "The IR junction analysis compares LSC/IRb/SSC/IRa boundary positions among related chloroplast genomes."
    )
    show_image("ir_junction", "IRScope / IR junction site comparison")


elif page == "Phylogeny":
    st.title("Maximum-Likelihood Phylogenetic Analysis")
    st.markdown(
        "The ML phylogeny shows the phylogenetic placement of *C. paniculatum* among selected Lamiaceae chloroplast genomes."
    )
    show_image("phylogeny", "Maximum-likelihood phylogenetic tree")


elif page == "Molecular Dating":
    st.title("Molecular Dating Analysis")
    st.markdown(
        "The dated tree summarizes divergence time estimates in million years ago (MYA) for selected lineages."
    )
    show_image("dating", "Molecular dating tree")


elif page == "Raw Files & Downloads":
    st.title("Raw Files and Downloads")
    st.markdown("Download the source files used in this web resource.")

    download_all_available_files()

    st.markdown("### Download selected files")
    for key, name in FILES.items():
        p = BASE_DIR / name
        if p.exists():
            show_download_button(p, f"Download {name}")

    st.markdown("### Preview raw annotation files")
    preview_file = st.selectbox(
        "Choose text file to preview",
        [
            "GenBank_file.txt",
            "Five_column_feature_table.txt",
            "Results of CPGview server.txt",
            "C_paniculatum_fasta_sequence.txt",
            "PCG.txt",
            "tRNA.txt",
            "rRNA.txt",
            "MISA_SSR_results.txt",
            "Codon usage bias.txt",
            "Exon_intron_distribution.txt",
        ],
    )
    st.text(read_text_file(preview_file, max_chars=15000))


# ============================================================
# Compact developer footer
# ============================================================
render_developer_footer()

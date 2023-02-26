from typing import Optional
import base64
import pathlib
import random
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import concrete_reports as cr

### Streamlit Functions

def compile_reports(
    reports_dir: str | pathlib.Path,
    company: str,
    templates_dir: Optional[pathlib.Path],
    ) ->  pd.DataFrame:
    """
    Returns a pd.DataFrame that represents the extracted data from the
    PDFs contained in the directory, 'reports_dir'.
    """
    reports_dir_path = pathlib.Path(reports_dir)
    templates_dir = pathlib.Path(templates_dir)
    report_paths = list(reports_dir_path.glob("*.pdf"))
    
    companies = {"abc_company": cr.abc_reports}
    df = pd.DataFrame()
    total_reports = len(report_paths)
    for idx, report_path in enumerate(report_paths):
        series = companies[company](report_path, templates_dir)
        if series is None: continue
        progress_value = idx / total_reports
        progress_bar.progress(progress_value, text=report_path.name)
        df = pd.concat([df, series], axis=1)
    
    df = df.T
    df = df.set_index("Date Cast")
    df = df.sort_index()
    for column_name in df.columns:
        if "Sample" in column_name or "Expected" in column_name:
            df[column_name] = df[column_name].astype(float)
    return df


def plot(concrete_df: pd.DataFrame, plot_name: str = "") -> None:
    """
    Plots the DataFrame, 'concrete_df' as a bar chart with dates on the 
    x-axis and strength on the y-axis as a stacked chart.
    """
    expected = go.Bar(name="Expected (MPa)", 
           x=concrete_df.index,
           y=concrete_df["Expected (MPa)"],
        #    width = bar_width,
           marker_color = 'rgba(255,0,0,1)',
           hovertext = concrete_df["Expected (MPa)"].map(str) + "<br>" + concrete_df["Location"],
        #    hoverinfo = "text"
          )
    
    sample_a = go.Bar(name="Sample A", 
           x=concrete_df.index, 
           y=concrete_df["Sample A (MPa)"],
        #    width = bar_width,
           marker_color = 'rgba(0,0,0, 0.3)',
           hovertext = concrete_df["Sample A (MPa)"].map(str) + " @ " + concrete_df["Sample A (Age)"].map(str) + " days",
           hoverinfo = "text"
           #width = 1
          )
    
    sample_b = go.Bar(name="Sample B", 
           x=concrete_df.index,
           y=concrete_df["Sample B (MPa)"], 
        #    width = bar_width,
           marker_color = 'rgba(0,0,0, 0.35)',
           hovertext = concrete_df["Sample B (MPa)"].map(str) + " @ " + concrete_df["Sample B (Age)"].map(str)+ " days",
           hoverinfo = "text"
          )
    
    sample_c = go.Bar(name="Sample C", 
           x=concrete_df.index,
           y=concrete_df["Sample C (MPa)"], 
        #    width = bar_width,
           marker_color = 'rgba(0, 0, 0, 0.40)',
           hovertext = concrete_df["Sample C (MPa)"].map(str) + " @ " + concrete_df["Sample C (Age)"].map(str)+ " days",
           hoverinfo = "text"
          )
    
    sample_d = go.Bar(name="Sample D", 
           x=concrete_df.index,
           y=concrete_df["Sample D (MPa)"], 
        #    width = bar_width,
           marker_color = 'rgba(0,0,0, 0.45)',
           hovertext = concrete_df["Sample D (MPa)"].map(str) + " @ " + concrete_df["Sample D (Age)"].map(str)+ " days",
           hoverinfo = "text"
          )

    
    plot_data = [expected, sample_a, sample_b, sample_c, sample_d]    
    fig = go.Figure(data=plot_data)
    
    fig.update_layout(
        barmode='overlay',
        bargroupgap = 0.3,
        height = 700,
        #width = len(concrete_df.index) * 30 if len(concrete_df.index) > 800 else 1000,
        title = f"{plot_name}",
        xaxis_tickangle=-45,
        xaxis = dict(
                title = "Date Cast",
                ticktext = concrete_df.index,
                tickvals = concrete_df.index,),
        yaxis = dict(
                title = "Concrete Strength (MPa)"
        
    ))
    return fig

###


with st.sidebar:
    st.subheader("Begin by clicking Load Data")
    st.write("This will cache 124 reports and it takes about a minute to run.")
    st.write("This processing time will only happen once.")
    load_data_button = st.button("Load Sample Data")
    progress_bar = st.empty()
    st.image("logo-black.png")
    if load_data_button:
        st.session_state['Data Loaded'] = True
        df = compile_reports('PDF_Reports', 'abc_company', 'Templates')
        st.session_state['DataFrame'] = df
    

st.header('Analyze PDF Concrete Test Reports')
sub_selection_radio = st.radio("Reports Selection", ["All reports", "28 Day (& older) Reports"])

if 'Data Loaded' not in st.session_state:
    df = pd.DataFrame()
else:
    df = st.session_state['DataFrame']

if sub_selection_radio == "28 Day (& older) Reports":
    try:
        mask = df["Sample B (MPa)"].isna()
        df = df.loc[~mask]
    except KeyError:
        pass

if 'Data Loaded' not in st.session_state:
    st.write("No data loaded. Press `Load Sample Data` first.")
else:
    st.subheader('How to read:')
    st.write("""
    * Red bars show expected strength
    * Grey bars show strength of individual cylinders as they were tested
    * All red bars should be covered in at least one layer of grey
    * If you see any red at the top of the bar, the expected strength was not achieved
    """)
    st.plotly_chart(plot(df, f'Concrete Test Reports - Local Business Center: {sub_selection_radio}'))

    st.subheader("Collected reports data")
    st.write(df)

with st.expander("Example PDF File"):
    random_button = st.button("Choose another")
    reports_path = pathlib.Path("PDF_Reports")
    file_list = [pdf_file for pdf_file in reports_path.glob("*.pdf")]
    random_file = random.choice(file_list, )
    if random_button:
        random_file = random.choice(file_list, )
    # Opening file from file path
    with open(random_file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)




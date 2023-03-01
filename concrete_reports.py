"""
A demonstration of how to create an analysis tool for PDF concrete
test reports using the basics taught in Python for Structural Engineers
"""
__version__ = "0.1.0"


import pathlib
import tabula
import pandas as pd
import json
from typing import Optional
from rich.progress import track
import plotly.graph_objects as go


# def load_template_areas(filename: list[str | pathlib.Path]) -> list[list[float]]:
#     """
#     Reads the area extents in each of the template files in filenames.
#     """
#     areas = []
#     with open(filename, 'r') as file:
#         template_data = json.load(file)
        
#     for template in template_data: 
#         areas.append([template['y1'], template['x1'], template['y2'], template['x2']])
#     return areas
        
def read_pdf_data(filename: str | pathlib.Path, template_file: str | pathlib.Path) -> list[pd.DataFrame]:
    """
    Returns multiple dataframes representing multiple area regions of table data
    extracted from the concrete test report in 'filename'.
    """
    df_list = tabula.read_pdf_with_template(
        input_path = filename,
        template_path = template_file,
        pandas_options = {"header": None},
    )
    return df_list


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
    report_paths = list(reports_dir_path.glob("*.pdf"))
    
    companies = {"abc_company": abc_reports}
    df = pd.DataFrame()
    for report_path in track(report_paths):
        series = companies[company](report_path, templates_dir)
        if series is None: continue
        df = pd.concat([df, series], axis=1)
    
    df = df.T
    # df["Date Cast"] = pd.to_datetime(df['Date Cast'], format="%Y-%m-%d")
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
           marker_color = 'rgba(255,0,0,1)',
           hovertext = concrete_df["Expected (MPa)"].map(str) + "<br>" + concrete_df["Location"],
          )
    
    sample_a = go.Bar(name="Sample A", 
           x=concrete_df.index, 
           y=concrete_df["Sample A (MPa)"],
           marker_color = 'rgba(0,0,0, 0.3)',
           hovertext = concrete_df["Sample A (MPa)"].map(str) + " @ " + concrete_df["Sample A (Age)"].map(str) + " days",
           hoverinfo = "text"
          )
    
    sample_b = go.Bar(name="Sample B", 
           x=concrete_df.index,
           y=concrete_df["Sample B (MPa)"], 
           marker_color = 'rgba(0,0,0, 0.35)',
           hovertext = concrete_df["Sample B (MPa)"].map(str) + " @ " + concrete_df["Sample B (Age)"].map(str)+ " days",
           hoverinfo = "text"
          )
    
    sample_c = go.Bar(name="Sample C", 
           x=concrete_df.index,
           y=concrete_df["Sample C (MPa)"], 
           marker_color = 'rgba(0, 0, 0, 0.40)',
           hovertext = concrete_df["Sample C (MPa)"].map(str) + " @ " + concrete_df["Sample C (Age)"].map(str)+ " days",
           hoverinfo = "text"
          )
    
    sample_d = go.Bar(name="Sample D", 
           x=concrete_df.index,
           y=concrete_df["Sample D (MPa)"], 
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
    
    fig.show()


def abc_reports(
    report: pathlib.Path,
    templates_dir: pathlib.Path
    ) -> pd.Series:
    """
    Returns a pandas series representing the data captured from the 
    conrete test report file, 'report'.
    """
    samples_df, spec_strength_df, supplier_df, cast_info_df = read_pdf_data(
        report, templates_dir /  "ABC_Company.json"
    )
    # Clean sample data
    header_first_row = any(samples_df.iloc[0].str.contains("SAMPLE").fillna(False))
    header_second_row = any(samples_df.iloc[1].str.contains("SAMPLE").fillna(False))
    header_third_row = any(samples_df.iloc[2].str.contains("SAMPLE").fillna(False))
    if header_first_row == True: 
        header_row_idx = 0
        header_row = pd.Index(samples_df.iloc[header_row_idx])
        sample_col_idx = header_row.get_loc("SAMPLE")
        try:
            age_col_idx = header_row.get_loc("AGE(DAYS)")
        except KeyError:
            age_col_idx = header_row.get_loc("AGE (DAYS)")
        strength_col_idx = header_row.get_loc("COMPRESSIVE STRENGTH (MPa)")
    elif header_second_row == True:
        header_row_idx = 1
        header_row = pd.Index(samples_df.iloc[header_row_idx])
        sample_col_idx = header_row.get_loc("SAMPLE")
        try:
            age_col_idx = header_row.get_loc("AGE(DAYS)")
        except KeyError:
            age_col_idx = header_row.get_loc("AGE (DAYS)")
        strength_col_idx = header_row.get_loc("COMPRESSIVE STRENGTH (MPa)")
    elif header_third_row == True:
        header_row_idx = 3
        header_row = pd.Index(samples_df.iloc[header_row_idx])
        sample_col_idx = header_row.get_loc("SAMPLE")
        try:
            age_col_idx = header_row.get_loc("AGE(DAYS)")
        except KeyError:
            age_col_idx = header_row.get_loc("AGE (DAYS)")
        strength_col_idx = header_row.get_loc("COMPRESSIVE STRENGTH (MPa)")

    clean_samples = samples_df.loc[header_row_idx + 1:, [sample_col_idx, age_col_idx, strength_col_idx]].reset_index(drop=True)
    clean_samples.columns = ["Sample", "Age", "Strength"]

    # Extract spec_strength
    spec_strength = spec_strength_df.iloc[:,1].item()
    spec_age = spec_strength_df.iloc[:,4].item()

    # Extract supplier
    if len(supplier_df) == 3:
        supplier_name = supplier_df.iloc[0, 1]
        mix_id = supplier_df.loc[2, 1]
    elif len(supplier_df) == 2:
        supplier_name = supplier_df.iloc[0, 1]
        mix_id = supplier_df.loc[1, 1]

    # Extract casting info

    air_content = cast_info_df.iloc[0, 1]
    if air_content == "%":
        air_content = cast_info_df.iloc[0, 0].split(" ")[-1]
    if isinstance(air_content, str):
        air_content = air_content.replace(" ","").replace("%","")
    if cast_info_df.iloc[2, 1] != cast_info_df.iloc[2, 1]:
        cast_date = cast_info_df.iloc[2, 0].split()[-1]
    else:
        cast_date = cast_info_df.iloc[2, 1]
    pour_location = cast_info_df.iloc[4,0]

    return pd.Series(data={
        "Date Cast": cast_date, 
        "Expected (MPa)": int(spec_strength), 
        "Expected (Days)": int(spec_age),
        "Supplier": supplier_name,
        "Mix ID": mix_id,
        "Sample A (MPa)": clean_samples.loc[0, "Strength"],
        "Sample A (Age)": clean_samples.loc[0, "Age"], 
        "Sample B (MPa)": clean_samples.loc[1, "Strength"],
        "Sample B (Age)": clean_samples.loc[1, "Age"], 
        "Sample C (MPa)": clean_samples.loc[2, "Strength"],
        "Sample C (Age)": clean_samples.loc[2, "Age"], 
        "Sample D (MPa)": clean_samples.loc[3, "Strength"],
        "Sample D (Age)": clean_samples.loc[3, "Age"],
        "Entrained Air, %": float(air_content),
        "Location": pour_location,
        "File": f"{report.name}"})




    

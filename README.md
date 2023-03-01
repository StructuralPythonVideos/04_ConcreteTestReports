# 04_ConcreteTestReports
This is repository contains the code featured in the StructuralPython YouTube video.

You can access the streamlit application on the web without installation here: https://structuralpython-concretereports.streamlit.app/

## Installation instructions

1. If you do not already have it, download and install miniconda: https://docs.conda.io/en/latest/miniconda.html
2. Open Anaconda Prompt (Windows) or terminal (others) and create a new conda environment: `conda create -n concrete_reports python=3.10`
3. Activate your environment with `conda activate concrete_reports`
3. Install the build tool, flit, with `pip install flit`
4. In your terminal, navigate to the directory of the cloned/extracted repository and run `flit install`
5. (Optional) Add an ipykernel for the environment so you can access it in JupyterLab: `python -m ipykernel install --user --name concrete_reports`
6. You can now run the streamlit app locally by running `streamlit run streamlit_app.py`

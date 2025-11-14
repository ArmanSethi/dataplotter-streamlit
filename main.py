import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="DataPlotter Instant Plot Generator for Multiple Datasets", layout="wide", page_icon="📊")
st.title("Data Visualizer 📊")

# Define folders to store data files and saved plots
datafolderpath = "data"
plotsfolderpath = "savedplots"
os.makedirs(datafolderpath, exist_ok=True)
os.makedirs(plotsfolderpath, exist_ok=True)

def getcsvfiles():
    return [f for f in os.listdir(datafolderpath) if f.endswith('.csv')]

# Session state for uploads and plot view
if "uploadedfile" not in st.session_state:
    st.session_state["uploadedfile"] = None
if "showstatisticalsummary" not in st.session_state:
    st.session_state["showstatisticalsummary"] = False
if "plotgenerated" not in st.session_state:
    st.session_state["plotgenerated"] = False

# Sidebar - upload & select
st.sidebar.header("Upload Dataset")
uploadedfile = st.sidebar.file_uploader("Upload a CSV file", type="csv")
if uploadedfile is not None:
    filepath = os.path.join(datafolderpath, uploadedfile.name)
    with open(filepath, 'wb') as f:
        f.write(uploadedfile.getbuffer())
    st.sidebar.success(f"Uploaded {uploadedfile.name} successfully!")

files = getcsvfiles()
st.sidebar.header("Select Dataset")
selectedfile = st.sidebar.selectbox("Choose a file", ["Select a dataset"] + files)

if selectedfile and selectedfile != "Select a dataset":
    try:
        df = pd.read_csv(os.path.join(datafolderpath, selectedfile))
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Sample Data")
            st.write(df.head())

            if st.button("Show Statistical Summary"):
                st.session_state["showstatisticalsummary"] = not st.session_state["showstatisticalsummary"]
            if st.session_state["showstatisticalsummary"]:
                st.subheader("Statistical Summary")
                numericdf = df.select_dtypes(include=["float64", "int64"])
                if not numericdf.empty:
                    st.dataframe(numericdf.describe().transpose())
                else:
                    st.warning("No numeric columns available for statistical summary.")

        with col2:
            st.subheader("Plot Options")
            columns = df.columns.tolist()
            xaxis = st.selectbox("Select the X-axis", options=[None]+columns, key="xaxis")
            yaxis = st.selectbox("Select the Y-axis", options=[None]+columns, key="yaxis")
            plottype = st.selectbox("Select Plot Type", [
                "Line Plot", "Bar Chart", "Scatter Plot", "Distribution Plot", 
                "Count Plot", "Correlation Heatmap", "Box Plot", 
                "Violin Plot", "Hexbin Plot", "Pair Plot"
            ])

            if st.button("Generate Plot"):
                st.session_state["plotgenerated"] = True

            if st.session_state["plotgenerated"]:
                st.subheader("Generated Plot")
                plt.figure(figsize=(10, 5))
                try:
                    if plottype == "Line Plot" and xaxis and yaxis:
                        plt.plot(df[xaxis], df[yaxis])
                        plt.title(f"{plottype} of {yaxis} vs {xaxis}")
                    elif plottype == "Bar Chart" and xaxis and yaxis:
                        plt.bar(df[xaxis], df[yaxis])
                        plt.title(f"{plottype} of {yaxis} by {xaxis}")
                    elif plottype == "Scatter Plot" and xaxis and yaxis:
                        plt.scatter(df[xaxis], df[yaxis])
                        plt.title(f"{plottype} of {yaxis} vs {xaxis}")
                    elif plottype == "Distribution Plot" and yaxis:
                        sns.histplot(df[yaxis], kde=True)
                        plt.title(f"{plottype} of {yaxis}")
                    elif plottype == "Count Plot" and yaxis:
                        sns.countplot(x=df[yaxis])
                        plt.title(f"{plottype} of {yaxis}")
                    elif plottype == "Correlation Heatmap":
                        sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
                        plt.title("Correlation Heatmap")
                    elif plottype == "Box Plot" and xaxis and yaxis:
                        sns.boxplot(data=df, x=xaxis, y=yaxis)
                        plt.title(f"{plottype} of {yaxis} by {xaxis}")
                    elif plottype == "Violin Plot" and xaxis and yaxis:
                        sns.violinplot(data=df, x=xaxis, y=yaxis)
                        plt.title(f"{plottype} of {yaxis} by {xaxis}")
                    elif plottype == "Hexbin Plot" and xaxis and yaxis:
                        plt.hexbin(df[xaxis], df[yaxis], gridsize=30, cmap="Blues")
                        plt.colorbar(label='Density')
                        plt.title(f"{plottype} of {yaxis} vs {xaxis}")
                    elif plottype == "Pair Plot":
                        sns.pairplot(df.select_dtypes(include=["float64", "int64"]))
                        st.pyplot()
                    else:
                        st.warning("Please select appropriate columns for the plot type.")

                    if plottype != "Pair Plot":
                        if xaxis: plt.xlabel(xaxis)
                        if yaxis: plt.ylabel(yaxis)
                        plt.grid(True)
                        st.pyplot(plt)
                        if st.button("Save Plot"):
                            savepath = os.path.join(plotsfolderpath, f"{plottype}_{selectedfile}.png")
                            plt.savefig(savepath)
                            st.success(f"Plot saved as {savepath}")
                            plt.clf()
                except Exception as e:
                    st.error(f"An error occurred while generating the plot: {e}")

    except pd.errors.EmptyDataError:
        st.error("The file is empty. Please upload a CSV file with data.")
    except pd.errors.ParserError:
        st.error("There was an error parsing the file. Please ensure it is a valid CSV format.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
else:
    st.info("Please upload a CSV file or select one from the dropdown to begin.")

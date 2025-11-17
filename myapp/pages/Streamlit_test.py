import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.title("Plot some data")

    df = pd.read_csv("Oulu.csv", sep=';', encoding="utf-8")
    st.write(df.head())  # näyttää datan
    st.write(df.columns) # näyttää sarakenimet

    fig = px.scatter(df, x="DateTime", y="Maximum temperature")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()

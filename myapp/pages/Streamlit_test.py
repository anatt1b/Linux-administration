import streamlit as st 
import pandas as pd
import plotly.expres as px

def main():
    st.title("Plot some data")
    df = pd.read_csv("Oulu.csv")
    
    ff = px.scatter(df, x="Date", y="Oulu")
    st.plotly_chart(ff, use_container_width=True)

if __name__ == "__main__":
    main()
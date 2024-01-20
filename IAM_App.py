import numpy as np
import pandas as pd
from reliability.Fitters import Fit_Weibull_2P_grouped
import streamlit as st


# FUNZIONI
def input_df(rows):
    '''
    This function modifies number of rows of the dataset to be used by the user in order to enter the failures
    and censored data.
    The number of rows is defined by the 'rows' parameter, that is defined based on the user input
    '''
    temp_df = pd.DataFrame(
        {"Period": np.arange(1, rows+1),
         "Failures": 0*rows,
         "Censored": 0*rows}
    )
    return temp_df


def editable_table(data):
    my_table = st.data_editor(
        data=data,
        use_container_width=True,
        hide_index=True,
        column_order=('Period', 'Failures', 'Censored'),
        num_rows="fixed",
        disabled=["Period"],
    )
    return my_table


def create_reliability_df(data):
    '''
    The function transforms the values contained in entered by the user in the 'DATA INPUT' section in the form required
    by the reliability library to run the Fit_Weibull_2P_grouped function
    '''
    failures_length = np.arange(1, len(data) + 1)
    censored_length = np.arange(1, len(data) + 1)

    failures = data['Failures']
    censored = data['Censored']

    failures_code = ['F'] * len(data)
    censored_code = ['C'] * len(data)

    my_df = pd.DataFrame()
    my_df['time'] = pd.concat([pd.Series(failures_length), pd.Series(censored_length)])
    my_df['quantity'] = pd.concat([pd.Series(failures), pd.Series(censored)])
    my_df['category'] = pd.concat([pd.Series(failures_code), pd.Series(censored_code)])
    return my_df


# PAGE CONFIGURATION
st.set_page_config(layout="wide",
                   page_title="Reliability calculation",
                   initial_sidebar_state="expanded"
                   )

# SIDEBAR
st.sidebar.header("Reliability calculator")
st.sidebar.markdown('''
                    This app allows you to compute the reliability value for a selected number of periods 
                    considering the available failure and censored data.
                    ''')
st.sidebar.markdown('''
                    This app uses the [reliability](https://reliability.readthedocs.io/en/latest/) library 
                    for the reliability computation. In particular, the computation is based on the Fit_Weibull_2P 
                    function available in the library. In this app, the default options are used to compute the 
                    reliability. Additional options are available reading the documentation and modifying the code.
                    
                    ''')
st.sidebar.subheader("How to use the app")
st.sidebar.markdown('''
                    1. Enter the number of periods you have data for.
                    2. Enter the failure and censored data in the table.
                    3. Select how many reliability periods you want to compute.
                    4. Click the 'Calculate reliability' button.
                    '''
                    )

# TITLE
st.title("Reliability Calculator")
st.write('''
            This simple tool to calculate reliability has been developed for the students of the Industrial Asset
            Management course of the University of Bergamo
                 ''')
st.write("---")

# DATA INPUT
st.subheader("Data input")
rows_number = st.number_input("How many time periods do you want to consider?", min_value=2)
df = input_df(rows=rows_number)
table = editable_table(data=df)
reliability_df = create_reliability_df(data=table)
st.write("---")

# CALCULATE RELIABILITY
st.subheader("Calculate reliability")
reliability_periods = st.number_input("For how many time periods do you want to calculate the reliability?",
                                      min_value=2)
times = pd.Series(np.arange(1, reliability_periods + 1))
if st.button("Calculate reliability"):
    if reliability_df['quantity'].sum() == 0:
        st.write("You should first enter the values in the table!")
    else:
        # Weibull functions
        fit = Fit_Weibull_2P_grouped(dataframe=reliability_df, show_probability_plot=False, print_results=False,
                                     method='MLE', CI_type='reliability')
        # Print the reliability values
        for time in times:
            lower, point, upper = fit.distribution.SF(CI_x=time, CI_type='reliability', CI=0.8, show_plot=False)
            if point > 0.0001:
                st.write(f'At period {time}, the reliability is:', point)
            else:
                st.write(f'From period {time} the reliability can be considered equal to 0')
                break

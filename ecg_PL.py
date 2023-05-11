import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events


# Temporal, later will accept any kind of data
def get_ecg_signal(filepath):
    ecg_data = pd.read_csv(filepath)
    ecg_data = ecg_data[9:] \
                    .rename(columns={'Name' : 'unit', 
                                    'Emil jimenez' : 'decimal'}) \
                    .reset_index()
    return (ecg_data['unit'] + '.' + ecg_data['decimal']).astype(float)

def plot_signal(signal):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(len(signal)), 
                             y= signal, 
                             line={'width':0.9, 'color':'blue'}, 
                             name='ECG signal'))
    peaks = st.session_state.get('peaks', [])
    fig.add_trace(go.Scatter(x=peaks, 
                             y= signal[peaks], 
                             mode='markers', 
                             opacity=0.5,
                             marker={
                                 'size': 12,
                                 'line': {'width':2, 'color':'red'},
                                 'color':'white',
                             }, 
                             name='Labeled peak'))
    fig.update_layout(hovermode='closest')
    return fig

def plot_signal_and_peaks(signal, peaks):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(len(signal)), 
                             y= signal, 
                             line={'width':0.9, 'color':'blue'}, 
                             name='ECG signal'))
    fig.add_trace(go.Scatter(x=peaks, 
                             y= signal[peaks], 
                             mode='markers', 
                             opacity=0.5,
                             marker={
                                 'size': 12,
                                 'line': {'width':2, 'color':'red'},
                                 'color':'white',
                             }, 
                             name='Labeled peak'))
    fig.update_layout(hovermode='closest')
    return fig

def save_peaks(peaks):
    record = st.session_state.selected_record
    st.session_state['records_df'].at[record, 'peaks'] = peaks
    st.session_state['records_df'].at[record, 'labeled'] = True
    st.session_state['records_df'].to_pickle('records_df.pkl')

def capture_click(plot):
    st.session_state['peaks'] = st.session_state.get('peaks', [])
    selected_point = plotly_events(plot, override_width=1000, click_event=True)
    if len(selected_point) != 0:
        st.session_state['peaks'].append(selected_point[0]['x'])
        st.session_state['peaks'].sort()
        st.experimental_rerun()


def peak_selection_form():
    with st.form('Peak selection', clear_on_submit=True):
        peak_idx = st.multiselect('Peak indeces', 
                st.session_state['peaks'], 
                default=st.session_state['peaks'],
                key='peak_multiselect')

        st.form_submit_button('Save', on_click=save_peaks, kwargs={'peaks':np.asarray(peak_idx)})

def clear_peaks(col):
    peaks = st.session_state.get('peaks', None)
    if peaks == None:
        with col:
            st.warning("No peaks still")
        return
    peaks.clear()

def header():
    st.radio("Mode", ['Labeling', 'Revision'], key='app_mode')
    col1, col2, col3 = st.columns([3, 2, 5])
    col2.button('Clear peaks', on_click=clear_peaks, args=[col3])
    return col1

if __name__ == '__main__':
    st.set_page_config(layout='wide')
    col1 = header()
    st.session_state['records_df'] = pd.read_pickle('records_df.pkl')
    if st.session_state.app_mode == 'Labeling':
        unlabeled = st.session_state['records_df'].loc[~st.session_state['records_df']['labeled']].index
        record = col1.selectbox('Unlabeled', unlabeled, key='selected_record')
        signal = st.session_state['records_df'].loc[record, 'ecg']
        plot = plot_signal(signal)
    elif st.session_state.app_mode == 'Revision':
        labeled = st.session_state['records_df'].loc[st.session_state['records_df']['labeled']].index
        selected = col1.selectbox('Labeled', labeled, key='selected_lbl_record')
        signal = st.session_state['records_df'].loc[selected, 'ecg']
        peaks = st.session_state['records_df'].loc[selected, 'peaks']
        plot = plot_signal_and_peaks(signal, peaks)
    capture_click(plot)
    peak_selection_form()
    


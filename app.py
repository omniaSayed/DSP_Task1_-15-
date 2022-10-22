################################## Essential imports ######################################################
from inspect import stack
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import plotly.express as px
from numpy import sin, cos, pi
from scipy.fftpack import fft, fftfreq, ifft
import random
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
################################## Page Layouts ######################################################
st.set_page_config(
    page_title="Sampling Dashboard",
    page_icon="✅",
    layout="wide",
)
################################## Page construction ######################################################
#Adding css file to webpage
with open("design.css")as f:
    st.markdown(f"<style>{f.read() }</style>",unsafe_allow_html=True)
#Add title
st.title("Sampling Studio For Biological Signals")
st.markdown(" Welcome To Our Sampling Studio ")
st.sidebar.title("Sampling Settings")
#Add elements to side bar
    #select box used to determine type pf provided signals
selected_signal = st.sidebar.selectbox('Provided Signals', ['Generate A Random Signal', 'EKG Sample Signal', 'ECG Sample Signal', 'EMG Sample Signal', 'EEG Sample Signal', 'Generate sine '])
    #slider to provide maximum frequency of signal for sampling process
def set_slider(max_freq):
        st.slider('Change Sampling Maximum Frequency ', 1,3*max_freq )
layout=st.sidebar.columns([2,1])
col1, col2 = st.columns(2)
col=st.columns([3,1])
col3=st.columns([3,1])
################################## Adding variables to session ######################################################
if 'list_of_signals' not in st.session_state:
    st.session_state['list_of_signals']=[]
    st.session_state['sum_of_signals']=np.zeros(1000)
    st.session_state['sum_of_signals_clean']=np.zeros(1000)
    st.session_state['fig_sine']=go.Figure()
################################## global variables  ######################################################
#cash using(mini memory for the front end)
@st.cache(persist=True)
################################## Function implementation  ######################################################
################################################################################################################################################
#Read and load data to be plotted function
def load_data(select, uploaded_file=None):
    if select == "EMG Sample Signal":
        column_names = ['t', 'emg']
        mvc1 = pd.read_csv('EMG.csv', sep = ',', names = column_names, skiprows= 50, skipfooter = 50)
    elif select == 'EKG Sample Signal':
        column_names = ['t', 'ekg']
        mvc1 = pd.read_csv('MVC1.txt', sep = ',', names = column_names, skiprows= 50, skipfooter = 50)
    elif select =="ECG Sample Signal":
        data = np.loadtxt('ECG.dat',unpack=True)
        mvc1 = pd.DataFrame(data)
        mvc1.columns=['ECG']
    elif select =="EEG Sample Signal":
        column_names = ['t', 'eeg']
        mvc1 = pd.read_csv('MVC1.txt', sep = ',', names = column_names, skiprows= 50, skipfooter = 50)
    elif select =="Provide A Local File Signal":
        column_names = ['time','value','frequency','amplitude','phase']
        mvc1 = pd.read_csv(uploaded_file, sep = ',', names = column_names,header=0)
    return mvc1
################################################################################################################################################
#generating a Random signal function
def generate_signal(time_domain):
    #generate random frequency
    Frequency1 = random.randint(1, 100)
    Frequency2 = random.randint(1, 100)
    randomly_generated_signal =(2*sin(2*pi*Frequency1*time_domain)) + (4*sin(2*pi*Frequency2*time_domain))
    #Adding Guassian Noise
    randomly_generated_signal += (3*np.random.randn(time_domain.size))
    print('Noise added')
    return randomly_generated_signal
################################################################################################################################################
# Noise function 
def createNoise(SNR,Signal_volt ):
    # calculate power in watto off signal 
    Signal_power=Signal_volt**2
    # calculate avarage power of signal
    Signal_avg_power=np.mean(Signal_power)
    # change signal into db
    signal_avg_db = 10 * np.log10(Signal_avg_power)
    # Calculate noise according to [2] then convert to watts
    noise_avg_db = signal_avg_db - SNR
    noise_avg_power = 10 ** (noise_avg_db / 10)
    # Generate an sample of white noise
    mean_noise = 0
    #Generate random guassian noise
    noise_volts = np.random.normal(mean_noise, np.sqrt(noise_avg_power), len(Signal_volt))
    #return noisy signal
    return noise_volts+Signal_volt
################################################################################################################################################
#function used to clear all ploted sine signals
def clear_data():
    #assign all values to zero
    st.session_state['list_of_signals']=[]
    st.session_state['sum_of_signals']=np.zeros(1000)
    st.session_state['sum_of_signals_clean']=np.zeros(1000)
    st.session_state['fig_sine']=go.Figure()
################################## Ploting functions ######################################################
################################################################################################################################################
# function used for  initialization used for ploting different sine waves
def initialize_plot(fig):
    #updating plot layout by changing color ,adding titles to plot ....
    fig.update_layout(
    autosize=False,
    width=500,
    height=500,
    title_text="Generated Sin Waves",
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),
    paper_bgcolor="white",
    font_color="black",
)
    #ploting wave using plotly
    st.plotly_chart(fig,use_container_width=True)
################################################################################################################################################
#function used to add each sine wave generated  to the same plot
def add_to_plot(fig,x,y,name):
        fig.add_trace(
        go.Scatter(x=x, y=y, name=name)
    ) 
################################################################################################################################################      
#function used to plot the addation  of sin signal generated
def plot(x,y): 
    df=pd.DataFrame(dict(x=x,y=y))
    fig=(px.line(df,x='x', y='y'))
    #update layout 
    fig.update_layout(
    autosize=False,
    width=500,
    height=500,
    title_text="Addition of Sin Waves",
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),
    paper_bgcolor="white",
    font_color="black",
)
    st.plotly_chart(fig,use_container_width=True)
################################################################################################################################################
#function used to delete signals from the plot
def delete(index_to_delete):
    #get the values that make up the signal to be deleted from list then delete it
    freq= st.session_state.list_of_signals[index_to_delete][0] #get frequency of  signal to be deleted
    amplitude=st.session_state.list_of_signals[index_to_delete][1]#get frequency of  signal to be deleted
    phase=st.session_state.list_of_signals[index_to_delete][2]#get phase of  signal to be deleted
    st.session_state.list_of_signals.pop(index_to_delete)#remove the ddesired signal parameter from session state
    #turn the tuple data of the figure into list and back to be able to remove the figure of the signal from plot
    list_fig_sine_data=list(st.session_state.fig_sine.data)
    list_fig_sine_data.remove(st.session_state.fig_sine.data[index_to_delete])
    st.session_state.fig_sine.data=tuple(list_fig_sine_data)
    #remove the signal from the summation of sine signals
    removed_signal = amplitude * sin(2 * pi * freq* time + phase)
    st.session_state.sum_of_signals-=removed_signal
    if not st.session_state.list_of_signals:
        clear_data()
#################################################################################################################################################   
def noise_sine():
    #if the value of the SNR is zero then there is no noise in the signal 
    if st.session_state.noise_key==0:
        st.session_state.sum_of_signals=st.session_state.sum_of_signals_clean
    else:
        #add noise to summation of signals
        noised_sine_sig=createNoise(st.session_state.noise_key,st.session_state.sum_of_signals_clean ) 
        st.session_state.sum_of_signals=noised_sine_sig
######################################################################################################################################################
def convert_df(df):
    df_of_signals=pd.DataFrame(st.session_state.list_of_signals,columns=['Frequency','Amplitude','Phase'])
    #df_of_signals
    df_sum_signals=pd.DataFrame({"Time": time, "Value": st.session_state.sum_of_signals})
    csv_file=pd.concat([df_sum_signals,df_of_signals],axis=1)
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return csv_file.to_csv(index=False)      
    
################################## Main implementation ###################################################### 
if selected_signal == "Generate A Random Signal":
    Fs=40
    delay_frequecny=0.0780
    N=int(Fs/delay_frequecny)
    Tw=N/Fs
    t=np.linspace(0,Tw,num=N)
    random_signal = generate_signal(t)
    fig = px.line(x=t, y=random_signal)
    st.plotly_chart(fig,use_container_width=True)

elif selected_signal == "EMG Sample Signal":
    #slider to get signal to noise ratio
    SNR= st.sidebar.slider('SNR', 0, 20,0,key='SNR')
    maximum_frequency=500
    set_slider(maximum_frequency)
    emg = load_data( selected_signal )
    if SNR==0 :
        fig = px.line(x=emg.t, y=emg.emg)
        st.plotly_chart(fig,use_container_width=True)
    else:
        emg_m=np.array(emg.emg)
        noised_signal=createNoise(SNR,emg_m)
        noise_fig=px.line(noised_signal)
        st.plotly_chart(noise_fig,use_container_width=True)

elif selected_signal == "EKG Sample Signal":
    #slider to get signal to noise ratio
    SNR= st.sidebar.slider('SNR', 0, 20,0,key='SNR')
    maximum_frequency=500
    set_slider(maximum_frequency)
    emg = load_data( selected_signal )
    fig = px.line(x=emg.t, y=emg.ekg)
    st.plotly_chart(fig,use_container_width=True)

elif selected_signal == "ECG Sample Signal":
    #slider to get signal to noise ratio
    SNR= st.sidebar.slider('SNR', 0, 20,0,key='SNR')
    ecg = load_data( selected_signal ) 
    if SNR==0 :
        fig = px.line(ecg[0:300])
        st.plotly_chart(fig,use_container_width=True)
    else:
        ecg_m=np.array(ecg[0:300])
        noised_signal=createNoise(SNR,ecg_m)
        noise_fig=px.line(noised_signal)
        noise_fig.update_traces(line_color="blue")
        st.plotly_chart(noise_fig,use_container_width=True)
        

elif selected_signal == "EEG Sample Signal":
    #slider to get signal to noise ratio
    SNR= st.sidebar.slider('SNR', 0, 20,0,key='SNR')
    maximum_frequency=500
    set_slider(maximum_frequency)
    eeg = load_data( selected_signal,use_container_width=True )
    if SNR==0 :
        fig = px.line(x=eeg.t, y=eeg.eeg)
        st.plotly_chart(fig)
    else:
        eeg_m=np.array(eeg.eeg)
        noised_signal=createNoise(SNR,eeg_m)
        noise_fig=px.line(noised_signal)
        st.plotly_chart(noise_fig,use_container_width=True)    
elif selected_signal == 'Generate sine ':
    with st.sidebar:
        #slider to get frequency for sin wave generation
        frequency = st.slider('Frequency', 0.0, 20.0, step=0.5, key='Frequency')
        #slider to get amplitude for sin wave generation
        amplitude = st.slider('Amplitude', 0, 20, 0, key='Amplitude')
        #slider to get phase for sin wave generation
        phase = st.slider('Phase', 0, 20, 0, key='Phase')
    time = np.linspace(0, 5, 1000)
    genrate_button=st.sidebar.button('Genrate Sin',key=0)
        #initialize_plot(st.session_state.fig_sine)
    if genrate_button:
        signal_parameters=[frequency,amplitude,phase]
        sine_volt = amplitude * sin(2 * pi * frequency * time + phase)
        add_to_plot(st.session_state.fig_sine,x=time,y=sine_volt,name=f"sin{frequency}hz") 
        st.session_state.list_of_signals.append(signal_parameters)
        st.session_state.sum_of_signals+=sine_volt
        st.session_state.sum_of_signals_clean=st.session_state.sum_of_signals
    with col3[0]:
        uploaded_file = st.file_uploader("Please choose a CSV or TXT file", accept_multiple_files=False,type=['csv','txt'])
    with col3[-1]:
        add_upload=st.button('Add File')
        if uploaded_file :
            if add_upload:
                data=load_data( 'Provide A Local File Signal',uploaded_file)
                amp=np.array(data.amplitude.dropna())
                freq=np.array(data.frequency.dropna())
                phase=np.array(data.phase.dropna())
                t=np.array(data.time)
                for i in range(len(data.frequency.dropna())):
                    
                    sine_volt = amp[i] * sin(2 * pi * freq[i] * t + phase[i])
                    signal_parameters=[freq[i],amp[i],phase[i]]
                    add_to_plot(st.session_state.fig_sine,x=t,y=sine_volt,name=f"sin{freq}hz")
                    st.session_state.list_of_signals.append(signal_parameters)
                st.session_state.sum_of_signals+=data.value
                st.session_state.sum_of_signals_clean=st.session_state.sum_of_signals
    if st.session_state.list_of_signals:
        option = st.sidebar.selectbox(
        'Select Values to Delete',
        st.session_state.list_of_signals,)
        selected_value=st.session_state.list_of_signals.index(option)
        with col2:
            delete_button=st.sidebar.button('delete',key=1,on_click=delete,args= (selected_value,))
    noise_sin=st.sidebar.slider('SNR sine',key="noise_key",on_change=noise_sine)  
    with col1:
        initialize_plot(st.session_state.fig_sine)
    with col2:
        plot(x=time,y=st.session_state.sum_of_signals)
    csv = convert_df(pd.DataFrame(time))
    with layout[0]:
        st.download_button(
            label="Download ",
            data=csv,
            file_name='large_df.csv',
            mime='text/csv',
        )
    with layout[-1]:
        st.button("Clear",on_click=clear_data)
        #uploaded_file =0
# elif selected_signal == 'Provide A Local File Signal':
#     time = np.linspace(0, 5, 1000)
#     uploaded_file = st.file_uploader("Please choose a CSV or TXT file", accept_multiple_files=False,type=['csv','txt'])
#     if uploaded_file:
#         data=load_data( 'Provide A Local File Signal',uploaded_file)
#         fig = px.line(x=data.time, y=data.value)
#         st.plotly_chart(fig)
#         figure=go.Figure()
#         amp=np.array(data.amplitude.dropna())
#         freq=np.array(data.frequency.dropna())
#         phase=np.array(data.phase.dropna())
#         t=np.array(data.time)
        
#         for i in range(len(data.frequency.dropna())):
#             sine_volt = amp[i] * sin(2 * pi * freq[i] * t + phase[i])
#             st.session_state.list_of_signals
#             figure.add_trace(go.Scatter(x=time,y=sine_volt))
#         st.plotly_chart(figure)
        # i=0
        # sine_volt = data.amplitude[i] * sin(2 * pi * data.frequency[i] * data.time + data.phase[i])
        # sine_volt
        # time
        # figure.add_trace(go.Scatter(x=time, y=sine_volt, name='name', mode="lines"))
        
        # st.plotly_chart(figure)
        
            


# --------------------------------------------------------------------------------------------







# SamplingRate = st.slider('sample size', 0, 200, 25)
# frequancy = 20
# time_step = np.linspace(0, 0.5, 200)
# signalWave = np.sin(2*np.pi*frequancy*time_step)
# S_rate = SamplingRate

# Time = 1/S_rate
# num_of_samp = np.arange(0, 0.5/Time)
# time_for_sampling = num_of_samp*Time
# SignalWave_for_sampling = np.sin(2*np.pi*frequancy*time_for_sampling)

#extractiong maximum frequency from a signal function
# def exract_max_frequency_of_signal(input_signal):

#sampling a signal function
# def signal_sampling(sample_rate):

#reconstruct signal from sampling functions
# def reconstruct_signal():

# #read the file provided by the user and plot the signal funtion
# def open_file():
#Sample Signals for the user to try sampling rate change on




# fig= make_subplots(rows=1, cols=2)

# fig.add_trace(
#     go.Scatter(x=time_step, y=signalWave,name='SineWave of frequency 20 Hz'),
#     row=1, col=1
# )
# fig.add_trace(
#     go.Scatter(x=time_for_sampling, y=SignalWave_for_sampling,name='Sample marks after resampling at fs=35Hz', mode='lines+markers'),
#     row=1, col=2
# )

# fig.update_xaxes(title_text='Time', row=1, col=1)
# fig.update_xaxes(title_text='Time', row=1, col=2)

# fig.update_yaxes(title_text='Amplitude', row=1, col=1)
# fig.update_yaxes(title_text='Amplitude', row=1, col=2)

# fig.update_layout(height=600, width=800)
# st.plotly_chart(fig)
# plt.subplot(2, 2, 2)
# plt.plot(time_for_sampling, SignalWave_for_sampling, 'g-', label='Reconstructed Sine Wave')
# plt.xlabel('time.', fontsize=15)
# plt.ylabel('Amplitude', fontsize=15)
# plt.legend(fontsize=10, loc='upper right')



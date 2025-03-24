import pandas as pd
import numpy as np
import streamlit as st
from io import StringIO

# Configure page
st.set_page_config(
    page_title="IPL Captaincy Analytics",
    page_icon="🏏",
    layout="wide"
)

# Custom styling
st.markdown("""
    <style>
    .metric-label { color: #2c5f2d; font-size: 0.9rem; }
    .stSlider>div>div>div>div { background: #2c5f2d !important; }
    .st-bb { background-color: white; }
    .st-at { background-color: #f5f5f5; }
    </style>
    """, unsafe_allow_html=True)

def calculate_captain_score(df, weights):
    """
    Calculate captaincy effectiveness score with error handling
    """
    try:
        # Calculate metrics with zero division handling
        df['Win_Percentage'] = np.where(df['Matches_Played'] > 0,
            (df['Matches_Won'] / df['Matches_Played']) * 100, 0)
        
        df['Close_Match_Success'] = np.where(df['Close_Matches_Played'] > 0,
            (df['Close_Matches_Won'] / df['Close_Matches_Played']) * 100, 0)
        
        df['Strategy_Success'] = np.where(df['Total_Strategies'] > 0,
            (df['Successful_Strategies'] / df['Total_Strategies']) * 100, 0)
        
        # Normalize player impact score (0-100 scale)
        df['Player_Impact'] = df['Player_Improvement_Score'].clip(0, 100)
        
        # Calculate weighted score
        df['Captaincy_Score'] = (
            (df['Win_Percentage'] * weights['win']) +
            (df['Close_Match_Success'] * weights['close']) +
            (df['Player_Impact'] * weights['player']) +
            (df['Strategy_Success'] * weights['strategy'])
        ).round(2)
        
        return df.sort_values(by='Captaincy_Score', ascending=False)
    
    except KeyError as e:
        st.error(f"Missing required column in data: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return pd.DataFrame()

def display_metrics(df):
    """Display key performance metrics"""
    cols = st.columns(4)
    metrics = {
        "🏆 Top Score": df['Captaincy_Score'].max(),
        "📊 Average Score": df['Captaincy_Score'].mean().round(2),
        "👑 Best Captain": df.iloc[0]['Captain'],
        "📈 Total Captains": len(df)
    }
    
    for (label, value), col in zip(metrics.items(), cols):
        col.metric(label, value)

def main():
    st.title("🏏 IPL Captaincy Effectiveness Analyzer")
    st.markdown("Evaluate captain performance using weighted metrics")

    # Sidebar controls
    with st.sidebar:
        st.header("Weight Configuration")
        weights = {
            'win': st.slider("Win Percentage", 0.0, 1.0, 0.4, step=0.05),
            'close': st.slider("Close Matches", 0.0, 1.0, 0.2, step=0.05),
            'player': st.slider("Player Development", 0.0, 1.0, 0.2, step=0.05),
            'strategy': st.slider("Strategy Success", 0.0, 1.0, 0.2, step=0.05)
        }
        
        st.header("Data Input")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
    # Load data
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.DataFrame({
            'Captain': [
                'Ruturaj Gaikwad', 'Axar Patel', 'Shubman Gill', 'Ajinkya Rahane',
                'Rishabh Pant', 'Hardik Pandya', 'Shreyas Iyer', 'Sanju Samson',
                'Rajat Patidar', 'Pat Cummins'
            ],
            'Matches_Played': [150, 120, 130, 200, 110, 140, 115, 160, 90, 85],
            'Matches_Won': [90, 70, 80, 110, 65, 85, 60, 95, 50, 45],
            'Close_Matches_Played': [40, 35, 38, 50, 28, 36, 30, 42, 20, 18],
            'Close_Matches_Won': [25, 18, 22, 30, 15, 20, 14, 26, 10, 9],
            'Player_Improvement_Score': [80, 75, 82, 78, 76, 79, 74, 77, 70, 72],
            'Successful_Strategies': [100, 85, 90, 110, 80, 95, 78, 105, 60, 58],
            'Total_Strategies': [130, 110, 120, 140, 100, 125, 95, 135, 75, 70]
        })

    # Process data
    if not df.empty:
        result_df = calculate_captain_score(df.copy(), weights)
        
        # Main display
        st.subheader("Performance Overview")
        display_metrics(result_df)
        
        # Interactive filters
        col1, col2 = st.columns(2)
        with col1:
            min_matches = st.slider(
                "Minimum Matches Played",
                min_value=0,
                max_value=int(df['Matches_Played'].max()),
                value=50
            )
        
        with col2:
            sort_field = st.selectbox(
                "Sort By",
                options=['Captaincy_Score', 'Win_Percentage', 
                        'Close_Match_Success', 'Player_Impact']
            )
        
        filtered_df = result_df[result_df['Matches_Played'] >= min_matches]
        filtered_df = filtered_df.sort_values(sort_field, ascending=False)
        
        # Styled dataframe
        st.dataframe(
            filtered_df.style.format({
                'Win_Percentage': '{:.1f}%',
                'Close_Match_Success': '{:.1f}%',
                'Strategy_Success': '{:.1f}%',
                'Captaincy_Score': '{:.1f}'
            }).background_gradient(subset=['Captaincy_Score'], cmap='YlGn'),
            height=500,
            use_container_width=True
        )
        
        # Visualization
        st.subheader("Score Breakdown")
        selected_captain = st.selectbox("Select Captain", result_df['Captain'])
        captain_data = result_df[result_df['Captain'] == selected_captain].iloc[0]
        
        chart_data = pd.DataFrame({
            'Metric': ['Win %', 'Close Matches', 'Player Impact', 'Strategy'],
            'Score': [
                captain_data['Win_Percentage'],
                captain_data['Close_Match_Success'],
                captain_data['Player_Impact'],
                captain_data['Strategy_Success']
            ]
        })
        
        st.bar_chart(chart_data.set_index('Metric'), use_container_width=True)

if __name__ == "__main__":
    main()
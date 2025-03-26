import streamlit as st
import pandas as pd
import plotly.express as px

# Initialize session state
if 'reset_filters' not in st.session_state:
    st.session_state.reset_filters = False

# Streamlit UI Configuration
st.set_page_config(
    page_title="Movies Rating & Genre Analysis ",
    page_icon="🎞",
    layout="wide", 
    initial_sidebar_state="expanded")

# Load cleaned dataset with caching
@st.cache_data
def load_data():
    df = pd.read_csv("n_movies.csv")
    # Convert genre to list, handling NaN values
    df['genre'] = df['genre'].apply(lambda x: str(x).split(', ') if pd.notna(x) else [])
    # Clean stars data
    df['stars'] = df['stars'].str.replace(r"[\[\]']", "", regex=True).str.split(', ')
    df['stars'] = df['stars'].apply(lambda x: [star.strip() for star in x if star.strip() not in ['', '/', 'Stars:', 'Star:', '"']])
    # Clean other columns
    df['votes'] = df['votes'].str.replace(',', '', regex=True).astype(float)
    df['year'] = df['year'].str.extract(r'(\d{4})').astype(float)
    df['duration'] = df['duration'].str.extract(r'(\d+)').astype(float)
    df['votes'].fillna(df['votes'].median(), inplace=True)
    df.dropna(subset=['rating'], inplace=True)
    return df

df = load_data()

# ==============================================================================================================================================================

# Reset filters function
def reset_filters():
    # Reset all filter values to defaults
    st.session_state.selected_genre = []
    st.session_state.selected_star = []
    st.session_state.selected_year = (int(df['year'].min()), int(df['year'].max()))
    st.session_state.selected_rating = (float(df['rating'].min()), float(df['rating'].max()))

# Safe mode calculation function
def safe_mode(series):
    try:
        mode_val = series.mode()
        return mode_val[0] if not mode_val.empty else "N/A"
    except:
        return "N/A"

# Custom styling
def style_chart(fig):
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    return fig


# Custom CSS for styling
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 5px 0;
    }
    h1, h2, h3, .stPlotlyChart h2 {
        color: #ff0000 !important;
    }
    .kpi-spacer {
        margin-bottom: 20px;
    }
    .empty-data {
        color: #ff0000;
        font-weight: bold;
    }
    .insight-box {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎬 Movies Rating & Genre Analysis")


# ==============================================================================================================================================================

# Sidebar Filters
st.sidebar.image("logo.jpg", width = 280)
with st.sidebar:
    st.header("Filters")
    
    selected_genre = st.multiselect(
        "Select Genre", 
        options=df.explode('genre')['genre'].unique(),
        key='selected_genre'
    )
    
    selected_star = st.multiselect(
        "Select Star",
        options=df.explode('stars')['stars'].unique(),
        key='selected_star'
    )
    
    selected_year = st.slider(
        "Select Year Range",
        int(df['year'].min()),
        int(df['year'].max()),
        (int(df['year'].min()), int(df['year'].max())),
        key='selected_year'
    )
    
    selected_rating = st.slider(
        "Select Rating Range",
        float(df['rating'].min()),
        float(df['rating'].max()),
        (float(df['rating'].min()), float(df['rating'].max())),
        key='selected_rating'
    )
    
    if st.button("Reset Filters", on_click=reset_filters):
        pass
    
# ==============================================================================================================================================================

# Apply filters
filtered_df = df.copy()
if selected_genre:
    filtered_df = filtered_df[filtered_df['genre'].apply(
        lambda x: any(genre in x for genre in selected_genre)
    )]
if selected_star:
    filtered_df = filtered_df[filtered_df['stars'].apply(
        lambda x: any(star in x for star in selected_star)
    )]
filtered_df = filtered_df[(filtered_df['year'] >= selected_year[0]) & (filtered_df['year'] <= selected_year[1])]
filtered_df = filtered_df[(filtered_df['rating'] >= selected_rating[0]) & (filtered_df['rating'] <= selected_rating[1])]

# KPIs with styled boxes
st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_rating = round(filtered_df['rating'].mean(), 2) if not filtered_df.empty else "N/A"
    st.markdown(f'<div class="stMetric">⭐ <b>Average Rating</b><br>{avg_rating}</div>', unsafe_allow_html=True)

with col2:
    total_movies = len(filtered_df) if not filtered_df.empty else 0
    st.markdown(f'<div class="stMetric">🎬 <b>Total Movies</b><br>{total_movies}</div>', unsafe_allow_html=True)

with col3:
    top_genre = filtered_df.explode('genre')['genre'].value_counts().idxmax() if not filtered_df.empty else "N/A"
    st.markdown(f'<div class="stMetric">🎭 <b>Most Popular Genre</b><br>{top_genre}</div>', unsafe_allow_html=True)

with col4:
    total_votes = f"{filtered_df['votes'].sum():,.0f}" if not filtered_df.empty else "0"
    st.markdown(f'<div class="stMetric">🗳️ <b>Total Votes</b><br>{total_votes}</div>', unsafe_allow_html=True)

st.markdown('<div class="kpi-spacer"></div>', unsafe_allow_html=True)

col5, col6, col7 = st.columns(3)

with col5:
    min_duration = int(filtered_df['duration'].min()) if not filtered_df.empty else "N/A"
    st.markdown(f'<div class="stMetric">⏳ <b>Shortest Movie</b><br>{min_duration} mins</div>', unsafe_allow_html=True)

with col6:
    max_duration = int(filtered_df['duration'].max()) if not filtered_df.empty else "N/A"
    st.markdown(f'<div class="stMetric">⏱️ <b>Longest Movie</b><br>{max_duration} mins</div>', unsafe_allow_html=True)

with col7:
    avg_duration = round(filtered_df['duration'].mean(), 2) if not filtered_df.empty else "N/A"
    st.markdown(f'<div class="stMetric">📏 <b>Average Duration</b><br>{avg_duration} mins</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.markdown('<div class="empty-data">⚠️ No movies match the selected filters. Please adjust your criteria.</div>', unsafe_allow_html=True)
    st.stop()

st.markdown("---")


# ==============================================================================================================================================================


# Visualization 1: Average Ratings by Certificate
st.subheader("📈 Data Insights")

cert_ratings = filtered_df.groupby('certificate')['rating'].mean().reset_index()
cert_ratings = cert_ratings.sort_values('rating', ascending=False)
fig1 = px.bar(cert_ratings, x='certificate', y='rating', color='rating',
             color_continuous_scale='Viridis', title="<b>Average Ratings by Certificate</b>")
fig1 = style_chart(fig1)
fig1.update_xaxes(tickangle=45, categoryorder='total descending')
st.plotly_chart(fig1, use_container_width=True)
with st.expander("💡 Certificate Rating Insight"):
    st.markdown("""
    - Certificates like 'R' and 'PG-13' often show higher average ratings
    - This may indicate more mature content tends to be better rated
    - Family-friendly certificates (like 'PG') typically have mid-range ratings
    """)

st.markdown("---")

# ==============================================================================================================================================================

# Visualization 2: Distribution of Ratings
fig2 = px.histogram(filtered_df, x='rating', nbins=20, title="<b>Distribution of Ratings</b>")
fig2.update_traces(marker_line_color='black', marker_line_width=1, opacity=0.85)
fig2 = style_chart(fig2)
st.plotly_chart(fig2, use_container_width=True)
with st.expander("💡 Rating Distribution Insight"):
    st.markdown("""
    - Most movies cluster around 6.0-7.5 rating range
    - Few movies get extremely high (>9) or low (<3) ratings
    - The distribution often shows a normal (bell-curve) pattern
    """)

st.markdown("---")

# ==============================================================================================================================================================

# Visualization 3: Genre Popularity
genre_counts = filtered_df.explode('genre')['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']
genre_counts = genre_counts.sort_values('count', ascending=False)
fig3 = px.pie(genre_counts, names='genre', values='count', title="<b>Genre Popularity</b>", hole=0.4)
fig3 = style_chart(fig3)
st.plotly_chart(fig3, use_container_width=True)
with st.expander("💡 Genre Popularity Insight"):
    st.markdown("""
    - Drama and Comedy are typically the most common genres
    - Genre combinations (like 'Drama, Romance') are counted separately
    - Niche genres appear as smaller slices in the pie
    """)

st.markdown("---")

# ==============================================================================================================================================================

# Visualization 4: Movies Released Per Year
year_counts = filtered_df['year'].value_counts().reset_index().sort_values('year')
year_counts.columns = ['year', 'count']
fig4 = px.line(year_counts, x='year', y='count', title="<b>Movies Released Per Year</b>")
fig4 = style_chart(fig4)
st.plotly_chart(fig4, use_container_width=True)
with st.expander("💡 Release Trends Insight"):
    st.markdown("""
    - Movie production generally increases over time
    - Dips may correspond to economic recessions or global events
    - Recent years may show incomplete data
    """)

st.markdown("---")

# ==============================================================================================================================================================

# Visualization 5: Rating Trends Over Time
avg_rating_year = filtered_df.groupby('year')['rating'].mean().reset_index()
fig5 = px.line(avg_rating_year, x='year', y='rating', title="<b>Average Rating Over Time</b>")
fig5 = style_chart(fig5)
st.plotly_chart(fig5, use_container_width=True)
with st.expander("💡 Rating Trend Insight"):
    st.markdown("""
    - Older films often have higher average ratings (survivorship bias)
    - Ratings may decline slightly in recent years as more movies are produced
    - Significant dips may indicate changes in rating standards
    """)

st.markdown("---")

# ==============================================================================================================================================================

# Visualization 6: Duration Distribution
fig6 = px.histogram(filtered_df, x='duration', nbins=20, title="<b>Movie Duration Distribution</b>")
fig6.update_traces(marker_line_color='black', marker_line_width=1, opacity=0.8)
fig6 = style_chart(fig6)
st.plotly_chart(fig6, use_container_width=True)
with st.expander("💡 Duration Insight"):
    st.markdown("""
    - Most movies fall in the 90-120 minute range
    - Very short (<60min) or very long (>180min) movies are rare
    - Different genres have characteristic duration patterns
    """)

st.markdown("---")

# ==============================================================================================================================================================

# Visualization 7: Top Rated Movies
top_movies = filtered_df.nlargest(10, 'rating').sort_values('rating', ascending=False)
fig7 = px.bar(top_movies, x='title', y='rating', color='rating',
             color_continuous_scale='Plasma', title="<b>Top 10 Highest Rated Movies</b>")
fig7 = style_chart(fig7)
fig7.update_xaxes(tickangle=45, categoryorder='total descending')
st.plotly_chart(fig7, use_container_width=True)
with st.expander("💡 Top Movies Insight"):
    st.markdown("""
    - The highest rated movies often have fewer votes.
    - Classic films frequently appear in top ratings
    - Recent blockbusters may have high ratings with many votes
    """)

st.markdown("---")

# ==============================================================================================================================================================

# Visualization 8: Votes vs Ratings
fig8 = px.scatter(filtered_df, x='votes', y='rating', title="<b>Votes vs Ratings</b>", trendline="ols")
fig8 = style_chart(fig8)
st.plotly_chart(fig8, use_container_width=True)
with st.expander("💡 Votes Insight"):
    st.markdown("""
    - Most movies have few votes with mid-range ratings
    - Highly voted movies tend to cluster around 6-8 rating
    - The trendline shows if more popular movies get better/worse ratings
    """)

st.markdown("---")

# ==============================================================================================================================================================

# Visualization 9: Certificate Distribution
cert_counts = filtered_df['certificate'].value_counts().reset_index()
cert_counts.columns = ['certificate', 'count']
cert_counts = cert_counts.sort_values('count', ascending=False)
fig9 = px.bar(cert_counts, x='certificate', y='count', color='count',
             color_continuous_scale='Viridis', title="<b>Certificate Distribution</b>")
fig9 = style_chart(fig9)
fig9.update_xaxes(tickangle=45, categoryorder='total descending')
st.plotly_chart(fig9, use_container_width=True)
with st.expander("💡 Certificate Insight"):
    st.markdown("""
    - 'TV-MA' and 'TV-14' are typically the most common certificates
    - Older certificates may appear less frequently
    - Different markets have different certificate distributions
    """)

st.markdown("---")

# ==============================================================================================================================================================

# Visualization 10: Most Voted Movies
top_voted = filtered_df.nlargest(10, 'votes').sort_values('votes', ascending=False)
fig10 = px.bar(top_voted, x='title', y='votes', color='votes',
              color_continuous_scale='Thermal', title="<b>Top 10 Most Voted Movies</b>")
fig10 = style_chart(fig10)
fig10.update_xaxes(tickangle=45, categoryorder='total descending')
st.plotly_chart(fig10, use_container_width=True)
with st.expander("💡 Popularity Insight"):
    st.markdown("""
    - These represent the most discussed/controversial movies
    - Blockbusters and franchise films dominate this list
    - High votes don't always correlate with high ratings
    """)

# ==============================================================================================================================================================

## Add footer
st.markdown(
    """
    <style>
        footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background-color: #f8f9fa;
            margin-top: 50px;
            border-top: 1px solid #ddd;
        }
        .footer-left {
            flex: 1;
            font-size: 14px;
            color: #555;
        }
        .footer-left b {
            color: #FF204E;
        }
        .footer-text {
            font-size: 14px;
            color: #777;
            margin-top: 20px;
        }
        .footer-text a {
            color: #FF204E;
            text-decoration: none;
        }
        .footer-text a:hover {
            text-decoration: underline;
        }
        .gif-container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .gif-container img {
            width: 250px;
            height: auto;
            border-radius: 8px;
        }
        .credits-container {
            text-align: center;
            margin-top: 30px;
            font-size: 18px;
            color: #333;
        }
        .credits-container b {
            font-size: 22px;
            color: #FF204E;
        }
        .contact-info {
            text-align: center;
            margin-top: 20px;
            font-size: 16px;
            color: #333;
        }
        .contact-info b {
            font-size: 18px;
            color: #007BFF;
        }
        .contact-info a {
            text-decoration: none;
            color: #007BFF;
        }
        .contact-info a:hover {
            text-decoration: underline;
        }
    </style>

    <footer>
        <div class="footer-left">
            <p><b>Project Code:</b> B41_DA_011_Data Wranglers | 
               <b>Data Source:</b> <a href="https://www.kaggle.com/datasets/narayan63/netflix-popular-movies-dataset" target="_blank">Kaggle</a>
            </p>
            <div class="footer-text">
                <p>Want to explore more? Check out our other projects or visit our <a href="https://www.kaggle.com/">Kaggle profile</a>.</p>
            </div>
        </div>
        <div class="gif-container">
            <img src="https://media.tenor.com/zDZRlH-tT1sAAAAM/despicable-me-minions.gif" />
        </div>
    </footer>

    <div class="credits-container">
        <b>✨ Dashboard Created By:</b><br>
        1. Tejas Patil <br>

    </div>

    <div class="contact-info">
        📧 For any inquiries or feedback, feel free to reach us at: 
        <b><a href="mailto:team.dashboard@example.com">team.dashboard@example.com</a></b>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("---")
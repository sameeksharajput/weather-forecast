import streamlit as st
from datetime import datetime, timedelta
import html

st.set_page_config(
    page_title="Weather Forecast",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Page styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root { --ink:#102b55; --muted:#6881a8; --blue:#4f6fff; }
html, body, [class*="css"] { font-family:'Inter','Plus Jakarta Sans',sans-serif; }
.stApp {
  background:
    linear-gradient(180deg, rgba(244,248,255,.25), rgba(247,250,255,.94)),
    url('https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=2200&q=85');
  background-size: cover; background-position: center top; background-attachment: fixed;
  color:var(--ink);
}
header[data-testid="stHeader"] { background:transparent; }
#MainMenu, footer {visibility:hidden;}
.block-container { padding: 1.2rem 1.8rem 2rem 1.8rem; max-width: 1700px; }
section[data-testid="stSidebar"] { background:rgba(255,255,255,.92); border-right:1px solid #e5edf9; }
section[data-testid="stSidebar"] > div { padding-top:1.2rem; }
.brand { font-size:27px; font-weight:800; line-height:1.1; color:#102b55; letter-spacing:-.8px; }
.brand span { color:#5275ff; }
.smallmuted {color:#6f86aa; font-size:14px; line-height:1.65;}
.navitem { padding:13px 15px; border-radius:14px; color:#5e769b; font-size:15px; margin:9px 0; }
.navactive {background:#e9edff; color:#4d6dff; font-weight:600;}
.hero-glass {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  padding: 16px 24px;
  box-shadow: 0 10px 30px rgba(32, 58, 97, 0.08);
  margin-bottom: 18px;
}
.hero-title {font-size:32px; font-weight:800; letter-spacing:-0.8px; color:#102b55; margin:0;}
.hero-sub {color:#506d98; font-size:15px; margin-top:3px;}
.glass { 
  background:rgba(255,255,255,.88); 
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border:1px solid rgba(255,255,255,.6); 
  border-radius:20px; 
  box-shadow:0 8px 24px rgba(63,102,164,.07); 
}
.current {
  background:linear-gradient(135deg,rgba(40,85,150,.85),rgba(90,140,200,.65)),
  url('https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80'); 
  background-size:cover;background-position:center;border:1px solid rgba(255,255,255,.45);
  border-radius:20px;color:white;padding:24px 24px 22px;min-height:330px;box-shadow:0 10px 28px rgba(55,98,158,.15);
}
.current-city {font-size:23px;font-weight:700;}
.current-date {font-size:14px;color:#f0f5ff;margin-top:4px;}
.big-temp {font-size:74px;line-height:1;font-weight:800;letter-spacing:-3px;}
.feels {font-size:17px;margin-top:8px;}
.metric {background:rgba(255,255,255,.16);backdrop-filter:blur(6px);border-radius:15px;padding:12px 10px;text-align:center;font-size:13px;line-height:1.5;}
.section-title {font-size:18px;font-weight:750;color:#102b55;margin:0 0 15px;}
.forecast-grid {display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:10px;}
.day {background:rgba(255,255,255,.75);border:1px solid rgba(220,230,245,.8);border-radius:16px;text-align:center;padding:16px 5px 14px;min-height:210px;}
.dayname {font-weight:700;font-size:13px;color:#172f56;}
.daydate {font-size:13px;color:#7187ab;margin-top:5px;}
.weathericon {font-size:32px;margin:20px 0 16px;}
.hitem {display:flex;align-items:center;gap:13px;padding:11px 2px;color:#7187ab;font-size:14px;}
.hitem b {margin-left:auto;color:#163766;font-size:13px;}
.tip {display:flex;align-items:center;gap:13px;padding:12px;background:rgba(245,248,255,.9);border:1px solid #edf2fb;border-radius:15px;margin:9px 0;}
.tip-icon {background:white;border-radius:50%;width:43px;height:43px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;}
.tip-title {font-size:13px;color:#385783;font-weight:600;}
.tip-sub {font-size:11px;color:#7c91b1;margin-top:4px;}
div[data-testid="stTextInput"] input {border:1px solid #dbe6f6;border-radius:28px;background:rgba(255,255,255,.95);padding:13px 18px;color:#183660;}
div[data-testid="stButton"] button {border:0;border-radius:28px;background:#4f6fff;color:white;font-weight:650;padding:0.65rem 1.25rem;min-height:45px;}
div[data-testid="stButton"] button:hover {background:#3e5ef0;color:white;border:0;}
div[data-testid="stSelectbox"] > div > div {background:rgba(255,255,255,.95);border-radius:14px;border:1px solid #dbe6f6;}
@media(max-width:1000px) {.forecast-grid{grid-template-columns:repeat(4,minmax(0,1fr));}.big-temp{font-size:58px;}}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<div style='font-size:42px;margin:8px 0 10px'>🌤️</div><div class='brand'>Weather<br><span>Forecast</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='smallmuted' style='margin-top:20px;margin-bottom:24px'>Know the weather,<br>plan your day ☀️</div>", unsafe_allow_html=True)
    st.markdown("<div class='navitem navactive'>⌂ &nbsp; Home</div><div class='navitem'>▦ &nbsp; 7-Day Forecast</div><div class='navitem'>◷ &nbsp; Hourly Forecast</div><div class='navitem'>● &nbsp; About</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:250px'></div><div style='font-size:26px;color:#9dbcf1'>⌁</div><div style='font-size:13px;color:#6684b3;font-style:italic;text-align:center'>Better weather,<br>brighter days ♥</div>", unsafe_allow_html=True)

if "city" not in st.session_state:
    st.session_state.city = "Indore"
if "search_city" not in st.session_state:
    st.session_state.search_city = "Indore"

# Dynamic Greeting based on time
current_hour = datetime.now().hour
if 5 <= current_hour < 12:
    greeting = "Good Morning!"
elif 12 <= current_hour < 17:
    greeting = "Good Afternoon!"
elif 17 <= current_hour < 21:
    greeting = "Good Evening!"
else:
    greeting = "Good Night!"

# Header Card
st.markdown(f"""
<div class="hero-glass">
  <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
    <div style="display:flex; gap:16px; align-items:center;">
      <span style="font-size:42px;">🌤️</span>
      <div>
        <div class="hero-title">{greeting}</div>
        <div class="hero-sub">Live updates and 7-day extended forecast for your selected location.</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Search & Quick Select bar
search_col, button_col, select_col = st.columns([4, 1.2, 2.2])
with search_col:
    search_value = st.text_input("City name", placeholder="📍  Type any city name...", label_visibility="collapsed", key="search_city")
with button_col:
    if st.button("⌕  Search", use_container_width=True):
        if search_value.strip():
            st.session_state.city = search_value.strip().title()
            st.rerun()
with select_col:
    city_options = ["Indore", "Bhopal", "Jabalpur", "Delhi", "Mumbai", "Pune", "Bengaluru"]
    curr_index = city_options.index(st.session_state.city) if st.session_state.city in city_options else 0
    selected_from_list = st.selectbox("Quick Select", city_options, index=curr_index, label_visibility="collapsed")
    if selected_from_list != st.session_state.city and not search_value.strip():
        st.session_state.city = selected_from_list
        st.rerun()

city = html.escape(st.session_state.city)
data = {
    "Indore": (28, 18, "Partly Cloudy", "65%", "12 km/h", "1012 hPa", "8 km", "5 (Moderate)"),
    "Bhopal": (29, 19, "Sunny", "58%", "10 km/h", "1011 hPa", "9 km", "6 (High)"),
    "Jabalpur": (27, 18, "Cloudy", "68%", "14 km/h", "1010 hPa", "7 km", "5 (Moderate)"),
    "Delhi": (31, 21, "Sunny", "42%", "9 km/h", "1008 hPa", "6 km", "6 (High)"),
    "Mumbai": (30, 25, "Partly Cloudy", "74%", "16 km/h", "1009 hPa", "7 km", "4 (Moderate)"),
    "Pune": (29, 19, "Sunny", "55%", "11 km/h", "1012 hPa", "8 km", "6 (High)"),
    "Bengaluru": (26, 19, "Light Rain", "77%", "13 km/h", "1013 hPa", "6 km", "4 (Moderate)"),
}
temp, low, condition, humidity, wind, pressure, visibility, uv = data.get(st.session_state.city, (28, 18, "Partly Cloudy", "65%", "12 km/h", "1012 hPa", "8 km", "5 (Moderate)"))
icons = ["🌤️", "☀️", "☁️", "🌧️", "☀️", "🌤️", "☁️"]
highs = [temp, temp+2, temp+1, temp-1, temp, temp+1, temp]
lows = [low, low+1, low, low-1, low-2, low-1, low]
today = datetime.now()
days = [(today + timedelta(days=i)) for i in range(7)]
day_names = [d.strftime("%a") for d in days]
day_dates = [d.strftime("%d %b") for d in days]

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
left, right = st.columns([1.02, 1.55], gap="medium")
with left:
    st.markdown(f"""
    <div class="current">
      <div style="display:flex;gap:12px;align-items:center"><span style="font-size:24px">📍</span><div><div class="current-city">{city}</div><div class="current-date">{today.strftime('%a, %d %b %Y')} &nbsp;·&nbsp; {html.escape(condition)}</div></div></div>
      <div style="display:flex;align-items:center;gap:24px;margin:30px 0 26px"><div style="font-size:72px">🌤️</div><div><div class="big-temp">{temp}°C</div><div class="feels">Feels like {temp+2}°C</div></div></div>
      <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px">
        <div class="metric"><div style="font-size:21px">💧</div>Humidity<br><b>{humidity}</b></div>
        <div class="metric"><div style="font-size:21px">≋</div>Wind<br><b>{wind}</b></div>
        <div class="metric"><div style="font-size:21px">◉</div>Pressure<br><b>{pressure}</b></div>
      </div>
    </div>
    """, unsafe_allow_html=True)
with right:
    cards = ""
    for i in range(7):
        cards += f"""<div class="day"><div class="dayname">{day_names[i]}</div><div class="daydate">{day_dates[i]}</div><div class="weathericon">{icons[i]}</div><div style="font-size:21px;font-weight:750;color:#163766">{highs[i]}°</div><div style="font-size:17px;color:#7187ab;margin-top:4px">{lows[i]}°</div></div>"""
    st.markdown(f"""
    <div class="glass" style="padding:22px 18px 18px;min-height:330px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin:0 4px 18px"><div class="section-title" style="margin:0">▦ &nbsp; 7 Day Forecast</div><div style="font-size:14px;color:#4f6fff;font-weight:650">Overview</div></div>
      <div class="forecast-grid">{cards}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
details_col, chart_col, tips_col = st.columns([1, 1.42, 1.08], gap="medium")
with details_col:
    st.markdown(f"""
    <div class="glass" style="padding:21px 20px;min-height:350px">
      <div class="section-title">Today's Details</div>
      <div class="hitem"><span>🌡️</span><span>Max Temperature</span><b>{temp}°C</b></div>
      <div class="hitem"><span>🌡️</span><span>Min Temperature</span><b>{low}°C</b></div>
      <div class="hitem"><span>💧</span><span>Humidity</span><b>{humidity}</b></div>
      <div class="hitem"><span>≋</span><span>Wind Speed</span><b>{wind}</b></div>
      <div class="hitem"><span>◉</span><span>Visibility</span><b>{visibility}</b></div>
      <div class="hitem"><span>☀️</span><span>UV Index</span><b>{uv}</b></div>
    </div>
    """, unsafe_allow_html=True)
with chart_col:
    period = st.radio("Temperature trend period", ["7 Days", "30 Days"], horizontal=True, label_visibility="collapsed", key="trend_period")
    if period == "30 Days":
        chart_high = [temp-1, temp+1, temp+2, temp, temp+3, temp+1, temp+2]
        chart_low = [low, low+1, low-1, low, low+1, low, low+1]
    else:
        chart_high = highs
        chart_low = lows
    points_hi = " ".join(f"{40+i*58},{145-(v-(temp-10))*6}" for i,v in enumerate(chart_high))
    points_lo = " ".join(f"{40+i*58},{145-(v-(temp-10))*6}" for i,v in enumerate(chart_low))
    xlabels = "".join(f"<text x='{40+i*58}' y='270' text-anchor='middle' font-size='10' fill='#7187ab'>{day_names[i]}<tspan x='{40+i*58}' dy='13'>{day_dates[i]}</tspan></text>" for i in range(7))
    grid = "".join(f"<line x1='30' y1='{40+j*45}' x2='420' y2='{40+j*45}' stroke='#edf2fa'/><text x='0' y='{44+j*45}' font-size='10' fill='#7187ab'>{40-j*10}°</text>" for j in range(5))
    circles_hi = "".join(f"<circle cx='{40+i*58}' cy='{145-(v-(temp-10))*6}' r='4' fill='#ff9f2f'/>" for i,v in enumerate(chart_high))
    circles_lo = "".join(f"<circle cx='{40+i*58}' cy='{145-(v-(temp-10))*6}' r='4' fill='#5e80ff'/>" for i,v in enumerate(chart_low))
    svg = f"<svg viewBox='0 0 440 300' width='100%' role='img'>{grid}<polyline points='{points_hi}' fill='none' stroke='#ff9f2f' stroke-width='2'/><polyline points='{points_lo}' fill='none' stroke='#5e80ff' stroke-width='2'/>{circles_hi}{circles_lo}{xlabels}</svg>"
    st.markdown(f"""
    <div class="glass" style="padding:21px 20px; min-height:350px; height:100%; box-sizing:border-box;">
      <div class="section-title">Temperature Trend</div>
      <div style="display:flex;justify-content:flex-end;gap:18px;margin:0 8px 2px;font-size:11px;color:#7187ab"><span>🟠 Max Temp</span><span>🔵 Min Temp</span></div>
      {svg}
    </div>
    """, unsafe_allow_html=True)
with tips_col:
    st.markdown("""
    <div class="glass" style="padding:21px 17px;min-height:350px">
      <div class="section-title">💡 &nbsp; Weather Tips</div>
      <div class="tip"><div class="tip-icon">☂️</div><div><div class="tip-title">Carry an umbrella</div><div class="tip-sub">Chance of light rain later this week.</div></div></div>
      <div class="tip"><div class="tip-icon">💧</div><div><div class="tip-title">Stay hydrated</div><div class="tip-sub">Keep drinking water throughout the day.</div></div></div>
      <div class="tip"><div class="tip-icon">👕</div><div><div class="tip-title">Wear light clothes</div><div class="tip-sub">Daytime temperatures are comfortable.</div></div></div>
      <div class="tip"><div class="tip-icon">☀️</div><div><div class="tip-title">UV is moderate</div><div class="tip-sub">Use sunscreen if you're outdoors.</div></div></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center;color:#8298b8;font-size:11px;padding:24px 0 10px'>Weather Forecast · Dashboard demo</div>", unsafe_allow_html=True)

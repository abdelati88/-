import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="لوحة تحكم الإنتاجية", page_icon="📈", layout="wide")

# حقن كود CSS لضبط اتجاه الصفحة للعربية RTL
st.markdown("""
<style>
    body { direction: rtl; text-align: right; }
    .stMetric { direction: rtl !important; text-align: right !important; }
    p, h1, h2, h3, h4, h5, h6 { text-align: right !important; }
    .stDataFrame { direction: rtl; }
</style>
""", unsafe_allow_html=True)

st.title("📈 لوحة تحكم إنتاجية الشركة")
st.markdown("**مواعيد العمل الرسمية:** من الأحد للخميس | 9:00 صباحاً - 5:00 مساءً (8 ساعات يومياً)")
st.markdown("---")

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours} ساعة و {minutes} دقيقة"
    elif minutes > 0:
        return f"{minutes} دقيقة و {secs} ثانية"
    else:
        return f"{secs} ثانية"

def calculate_efficiency(seconds):
    total_work_seconds = 8 * 60 * 60 
    efficiency = (seconds / total_work_seconds) * 100
    return min(efficiency, 100) 

def load_data():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('office_analytics.db')
    query = f"SELECT employee_name, desk_seconds FROM activity_logs WHERE date='{today}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = load_data()

if df.empty:
    st.info("ℹ️ مفيش بيانات متسجلة للنهاردة لسه. شغل الـ main_system.py الأول عشان يجمع داتا.")
else:
    st.subheader("📌 ملخص أداء الموظفين اليوم")
    cols = st.columns(len(df))
    
    for index, row in df.iterrows():
        emp_name = row['employee_name']
        seconds = row['desk_seconds']
        
        formatted_time = format_time(seconds)
        efficiency = calculate_efficiency(seconds)
        
        with cols[index]:
            st.metric(
                label=f"👤 {emp_name}",
                value=formatted_time,
                delta=f"{efficiency:.3f} % :الإنتاجية",
                delta_color="normal"
            )

    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    df['Efficiency (%)'] = df['desk_seconds'].apply(calculate_efficiency)
    df['وقت العمل الفعلي'] = df['desk_seconds'].apply(format_time)
    
    with col1:
        st.subheader("📊 مؤشر الإنتاجية اليومي (%)")
        st.bar_chart(df.set_index('employee_name')['Efficiency (%)'])
        
    with col2:
        st.subheader("📋 تقرير مفصل")
        display_df = df[['employee_name', 'وقت العمل الفعلي', 'Efficiency (%)']].rename(
            columns={'employee_name': 'الموظف', 'Efficiency (%)': 'النسبة'}
        )
        display_df['النسبة'] = display_df['النسبة'].apply(lambda x: f"{x:.3f} %")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")
if st.button("🔄 تحديث البيانات الان"):
    st.rerun()
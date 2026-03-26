import streamlit as st 
import pandas as pd 
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pydeck as pdk
import geopandas as gd
DSC_font= "DSC"

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
   direction: rtl;
}
.block-container {
   direction: rtl;
}
h1, h2, h3, p, div {
   text-align: right !important;
   direction: rtl !important;
}
/* التبويبات */
.stTabs [data-baseweb="tab-list"] {
   justify-content: flex-start;
   direction: rtl;
}
.stTabs [data-baseweb="tab"] {
   direction: rtl;
   text-align: right !important;
}
/* المتركس والعناصر الداخلية */
[data-testid="metric-container"] {
   direction: rtl;
   text-align: right;
}
[data-baseweb="slider"]{
   direction: ltr !important;
}
[data-baseweb="slider"] div {
   direction: ltr !important;
}
[data-baseweb="slider"] label {
   direction: ltr;
   text-align: right;
}            
</style>
""", unsafe_allow_html=True)


st.set_page_config(layout="wide")
# st.image("شعار المركز.png")
st.header("المؤشرات الاقتصادية للمملكة العربية السعودية ")
st.subheader("استعراض وتحليل مؤشرات الاقتصاد الكلي ")
## التابز
pulse, trends, relations, events, forecast = st.tabs([
    "الاقتصاد الآن",
    "الأداء الزمني للمؤشرات",
    "الارتباط والعلاقات",
    "الاحداث الاقتصادية",
    "التنبؤات المستقبلية"
])
with pulse: 
     df_dash=pd.read_excel("Dashb.xlsx", sheet_name="pulse")
     def to_billion(x): 
         return x / 1000
def growth(series):
    s=series.dropna()
    if len(s) <= 2:
        return None
    return(s.iloc[-1] / s.iloc[-2] -1) *100
def spark(df_dash, col):
    fig=px.line(df_dash.tail(10), 
                x="Year",
                y=col)
    fig.update_layout(height=100,margin=dict(l=10, r=10, t=10 , b=10), showlegend=False)
    fig.update_traces(line=dict(color="#B58500", width=3))
    fig.update_xaxes(visible=False )
    fig.update_yaxes(visible=False)
    return fig 
df_dash=df_dash.sort_values("Year")



### الصفحة الأولى
with pulse: 
    st.title(" الاقتصاد الان ")
    col1, col2, col3= st.columns(3)

    with col1: 
        value=df_dash["التضخم "].iloc[-1]
        delta=(df_dash["التضخم "].iloc[-1]-df_dash["التضخم "].iloc[-2])
        st.metric("التصخم (%)",
                f"{value:.2f}",
                f"{delta:+.2f}%",
                delta_color="inverse"
                )
        st.plotly_chart(spark(df_dash, "التضخم ") , width='content')

    with col2:
        value=df_dash["نمو الناتج المحلي الحقيقي % "].iloc[-1]
        delta=(df_dash["نمو الناتج المحلي الحقيقي % "].iloc[-1]-df_dash["نمو الناتج المحلي الحقيقي % "].iloc[-2])
        st.metric("الناتج المحلي الحقيقي (%)",
                f"{value:.2f}",
                f"{delta:+.2f}%"
                )
        st.plotly_chart(spark(df_dash, "نمو الناتج المحلي الحقيقي % ") , width='content')
    with col3:
        value=df_dash["معدل البطالة الاجمالي "].iloc[-1]
        delta=(df_dash["معدل البطالة الاجمالي "].iloc[-1]-df_dash["معدل البطالة الاجمالي "].iloc[-2])
        st.metric("معدل البطالة (%)",
                f"{value:.2f}",
                f"{delta:.2f}%",
                delta_color="inverse"
                )
        st.plotly_chart(spark(df_dash, "معدل البطالة الاجمالي ") , width='content')
        
    st.divider()
    col4, col5, col6, col7 = st.columns(4)
with col4:
        value=df_dash["عرض النقود M3 مليون "].iloc[-1]
        delta=growth(df_dash["عرض النقود M3 مليون "])
        st.metric("عرض النقود (مليار)",f"{to_billion(value):.1f}",f"{delta:+.2f}")
        st.plotly_chart(spark(df_dash, "عرض النقود M3 مليون ") , width='content')
with col5:
        value=df_dash["رصيد الحساب الجاري (مليون)"].iloc[-1]
        delta=growth(df_dash["رصيد الحساب الجاري (مليون)"])
        status="فائض" if value > 0 else "عجز"
        st.metric(f"الحساب الجاري (مليار)",f"{to_billion(value):.1f}",f"{delta:+.2f}%")
        st.plotly_chart(spark(df_dash, "رصيد الحساب الجاري (مليون)") , width='content')
with col6:
      value=df_dash["الصادرات "].iloc[-1]
      delta=growth(df_dash["الصادرات "])
      st.metric(f"الصادرات (مليار)",f"{to_billion(value):.1f}",f"{delta:+.2f}%")
      st.plotly_chart(spark(df_dash, "الصادرات ") , width='content')   
with col7:
     value=df_dash["الواردات "].iloc[-1]
     delta=growth(df_dash["الواردات "])
     st.metric(f"الواردات (مليار)",f"{to_billion(value):.1f}",f"{delta:+.2f}%")
     st.plotly_chart(spark(df_dash, "الواردات ") , width='content')
     
     st.divider()
     trade= st.columns(1)
     trade=(df_dash["صادرات السلع "]- df_dash["واردات السلع "]).dropna()
     if len(trade) > 1:
      latest=trade.iloc[-1]
      previous=trade.iloc[-2]
      delta= (latest / previous -1)*100

     st.metric(
          f"الميزان التجاري({'فائض' if latest >= 0 else 'عجز'}) (مليار)",
          f"{to_billion(latest):,.1f}",
          f"{delta:+.2f}%")


## الصفحة الثانية 
with trends: 
   real_sector , fiscal_sector , external_sector, Jop_market = st.tabs(["القطاع الحقيقي" , "القطاع النقدي" , "القطاع الخارجي", "سوق العمل "])
with real_sector:
    df_dash=pd.read_excel("Dashb.xlsx", sheet_name="Real")
    avaliable_columns=[col for col in df_dash.columns
        if col != "Year"]
    selected_columns=st.selectbox(
             "اختر المؤشر",
             avaliable_columns,
             format_func=lambda x: x.replace('_',' '))

    year_min=int(df_dash['Year'].min())
    year_max=int(df_dash['Year'].max())
    selected_year=st.slider(
         "اختر السنة",
          year_min,
          year_max,
         (year_min,year_max),
          key="year_slider_1")

    filtered_data=df_dash[(df_dash["Year"] >= selected_year[0]) & 
                         (df_dash["Year"] <= selected_year[1])]
    
    st.subheader(f"{selected_columns.replace('_' , ' ')}")
    st.line_chart(filtered_data.set_index('Year')
                  [selected_columns], color=["#B58500"])
with fiscal_sector:
    df_dash=pd.read_excel("Dashb.xlsx", sheet_name="Fiscal ")
    avaliable_columns=[col for col in df_dash.columns
                   if col != "Year"]
    selected_columns=st.selectbox(
    "اختر المؤشر",
    avaliable_columns,
    format_func=lambda x: x.replace('_',' '))

    year_min=int(df_dash['Year'].min())
    year_max=int(df_dash['Year'].max())
    selected_year=st.slider(
    "اختر السنة",
    year_min,
    year_max,
    (year_min,year_max))

    filtered_data=df_dash[(df_dash["Year"] >= selected_year[0]) & 
                         (df_dash["Year"] <= selected_year[1])]
    
    st.subheader(f"{selected_columns.replace('_' , ' ')}")
    st.line_chart(filtered_data.set_index('Year')
                  [selected_columns], color=["#B58500"])   
with Jop_market:
    df_dash=pd.read_excel("Dashb.xlsx", sheet_name="Jop")
    avaliable_columns=[col for col in df_dash.columns
                   if col != "Year"]
    selected_columns=st.selectbox(
    "اختر المؤشر",
    avaliable_columns,
    format_func=lambda x: x.replace('_',' '))

    year_min=int(df_dash['Year'].min())
    year_max=int(df_dash['Year'].max())
    selected_year=st.slider(
    "اختر السنة",
    year_min,
    year_max,
    (year_min,year_max))

    filtered_data=df_dash[(df_dash["Year"] >= selected_year[0]) & 
                         (df_dash["Year"] <= selected_year[1])]
    
    st.subheader(f"{selected_columns.replace('_' , ' ')}")
    st.bar_chart(filtered_data.set_index('Year')
                  [selected_columns],color=["#B58500"])
    st.line_chart(filtered_data.set_index('Year')
                  [selected_columns], color=["#1B365D"]) 
    regeion_un= gd.read_file("gadm41_SAU_1.shp")
    regeion_un=regeion_un.to_crs(epsg=4326)
    un_data=pd.read_excel("unempl_rate _region.xlsx")
    regeion_un=regeion_un.merge(
    un_data,
    on="NAME_1",
    how="left"
)
    regeion_un=regeion_un.to_crs(epsg=4326)
    geojson= regeion_un.to_json()
    geojson = regeion_un.__geo_interface__
    layer = pdk.Layer(
    "GeoJsonLayer",
    data=geojson,
    pickable=True,
    auto_highlight=True,
    stroked=True,
    filled=True,
    get_fill_color="""
[
  11 + (244 * properties.unemployment / 15),
  61 + (154 * properties.unemployment / 15),
  11 - (11 * properties.unemployment / 15),
  200
]
""",
    get_line_color=[80, 80, 80],
)
    view_state = pdk.ViewState(
    latitude=23.8859,
    longitude=45.0792,
    zoom=4.3
)
    deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "المنطقة : {NAME_1}\nالبطالة : {unemployment}%"},
    map_style=None
)
    
    st.markdown(
        "<h3 style='text-align:center;'>البطالة بحسب المناطق الادارية</h3>",
        unsafe_allow_html=True)
    st.pydeck_chart(deck)
with external_sector : 
     df_dash=pd.read_excel("Dashb.xlsx", sheet_name="External")
     avaliable_columns=[col for col in df_dash.columns
        if col != "Year"]
     selected_columns=st.selectbox(
             "اختر المؤشر",
             avaliable_columns,
             format_func=lambda x: x.replace('_',' '))

     year_min=int(df_dash['Year'].min())
     year_max=int(df_dash['Year'].max())
     selected_year=st.slider(
         "اختر السنة",
          year_min,
          year_max,
         (year_min,year_max),
          key="year_slider")

     filtered_data=df_dash[(df_dash["Year"] >= selected_year[0]) & 
                         (df_dash["Year"] <= selected_year[1])]
    
     st.subheader(f"{selected_columns.replace('_' , ' ')}")
     st.line_chart(filtered_data.set_index('Year')
                  [selected_columns], color=["#B58500"])


### الصفحة الثالثة 
with relations:    
    df_dash=pd.read_excel("Dashb.xlsx", sheet_name="relations")
    st.subheader("العلاقة بين المؤشرات") 
    st.write("حُدد مسبقًا الناتج المحلي الحقيقي بالمتغير المراد تفسيره (Y) ")
    Year="Year"
    Y_col="نمو الناتج المحلي الحقيقي % "
    rate_cols=["التضخم معدل %", "معدل البطالة الاجمالي ","الاستثمار معدل نمو %", "الاستهلاك النهائي معدل نمو %"]
    level_cols=["عرض النقود M3 (مليون) ", "رصيد الحساب الجاري (مليون)", "الصادرات (مليون)", "الواردات (مليون)"]
    
    def yoy_pct(s:pd.Series) ->pd.Series:
        return s.pct_change(1)*100

    x= st.selectbox("اختر المتغير X", level_cols+rate_cols)

    convert_levels=st.checkbox(" حول المتغيرات من مليون إلى نمو سنوي % في حال تم اختيار مؤشر قيمة نقدية", value=True)
    tmp=df_dash[["Year", x, Y_col]].copy().dropna().sort_values(Year)
    
    if convert_levels and x in level_cols:
            tmp[x]= yoy_pct(tmp[x])
    tmp=tmp.dropna()

    corr=tmp[x].corr(tmp[Y_col])
    st.metric("الارتباط (r)" , f"{corr:.3f}")
    if abs(corr) < 0.2:
         st.write("العلاقة ضعيفة جدًا")
    elif abs(corr) <0.4:
         st.write("العلاقة ضعيفة")
    elif abs(corr) <0.6:
         st.write("العلاقة متوسطة")
    elif abs(corr) <0.8:
         st.write("العلاقة قوية")
    else:
         st.write("العلاقة قوية جدًا")
    st.caption("ملاحظة : الارتباط لا يعني السببية")

    figR=px.scatter(tmp, x=x,y=Y_col, trendline="ols", hover_data=[Year])
    figR.update_traces(line=dict(color="#B58500", width=3))
    st.plotly_chart(figR, width='content')

    st.dataframe(tmp.tail(15), width='content')


with events: 
     df_dash=pd.read_excel("Dashb.xlsx", sheet_name="events")
     st.header("الأحداث الاقتصادية - Events")
     indicators_names=[col for col in df_dash if col != "Year"]
     events_df=pd.DataFrame({
          "Year":[2006, 2008, 2014, 2016, 2020],
          "events":[
               "أزمة سوق الاسهم السعودي", 
               "الأزمة المالية العالمية",
               "انخفاض اسعار النفط",
               "اطلاق رؤية السعودية 2030",
               "جائحة كورونا"
          ],
          "category": [
               "مالي محلي",
               "مالي عالمي",
               "نفطي",
               "سياسات",
               "صحي"
          ]})
     indicators = st.selectbox("اختر المؤشر", indicators_names)
     select_cateogary=st.multiselect(
          "نوع الحدث", 
          options=events_df["category"].unique()
        #   default=events_df["category"].unique()
        )

     filtered_events=events_df[events_df["category"].isin(select_cateogary)]
     fig_ev=px.line(df_dash, x="Year", y= indicators, markers=True)
     fig_ev.update_traces( 
          line_color="#286140",
          line_width=3,
          marker=dict(size=7, color="#6E6259"))

     for _, row in filtered_events.iterrows():
          fig_ev.add_vline(
               x=row["Year"],
               line_width=2,
               line_dash="dash",
               line_color="#286140")

          fig_ev.add_annotation(
               x=row["Year"],
               y=1,
               yref="paper",
               text=row["events"],
               showarrow=False,
               textangle=90,
               font=dict(size=12, color="#B58500"),
               xshift=-30)

          fig_ev.update_layout(
               height=550,
               xaxis_title="السنة",
               yaxis_title=indicators.replace("_", " "),
               template="plotly_white")
          
          st.plotly_chart(fig_ev,width='content' )


###  الصفحة الخامسة التنبؤات
with forecast: 
      st.header(" التنبؤات المستقبلية للناتج المحلي الاجمالي")
      df_forecast = pd.read_excel("Dashb.xlsx", sheet_name="forecast")
      year_col = "Year"
      actual_col = "الناتج المحلي الحقيقي الفعلي "
      mof_col = "توقعات وزارة المالية "
      holt_col = "توقعات نموذج هولت   "
      imf_col = "توقعات صندوق النقد الدولي "
      df_forecast = df_forecast.sort_values(year_col)
      
      last_actual_year = df_forecast[df_forecast[actual_col].notna()][year_col].max()
     
      latest_forecast_row = df_forecast[df_forecast[year_col] > last_actual_year].dropna(
     subset=[mof_col, holt_col, imf_col], how="all" )
      
      if not latest_forecast_row.empty:
       latest_row = latest_forecast_row.iloc[-1]
       latest_year = int(latest_row[year_col])
      
      
       c1, c2, c3, c4 = st.columns(4)
       with c1:
           if pd.notna(latest_row[mof_col]):
               st.metric("وزارة المالية", f"{latest_row[mof_col]:.2f}")
           else:
               st.metric("وزارة المالية", "—")
       with c2:
           if pd.notna(latest_row[holt_col]):
               st.metric("نموذج هولت", f"{latest_row[holt_col]:.2f}")
           else:
               st.metric("نموذج هولت", "—")
       with c3:
           if pd.notna(latest_row[imf_col]):
               st.metric("صندوق النقد", f"{latest_row[imf_col]:.2f}")
           else:
               st.metric("صندوق النقد", "—")
       with c4:
           vals = [latest_row[mof_col], latest_row[holt_col], latest_row[imf_col]]
           vals = [v for v in vals if pd.notna(v)]
           if vals:
               spread = max(vals) - min(vals)
               st.metric(f"فارق التوقعات ({latest_year})", f"{spread:.2f}")
           else:
               st.metric("فارق التوقعات", "—")
       st.markdown(f"**آخر سنة فعلية:** {int(last_actual_year)}")
 
      fig_f = go.Figure()
   # القيم الفعلية
      fig_f.add_trace(
             go.Scatter(
           x=df_forecast[year_col],
           y=df_forecast[actual_col],
           mode="lines+markers",
           name="الفعلي",
           line=dict(color="#286140", width=3),
           marker=dict(size=7)
       )
   )
   # وزارة المالية
      fig_f.add_trace(
       go.Scatter(
           x=df_forecast[year_col],
           y=df_forecast[mof_col],
           mode="lines+markers",
           name="وزارة المالية",
           line=dict(color="#1B365D", width=3, dash="solid"),
           marker=dict(size=7)
       )
   )
   # هولت
      fig_f.add_trace(
       go.Scatter(
           x=df_forecast[year_col],
           y=df_forecast[holt_col],
           mode="lines+markers",
           name="هولت",
           line=dict(color="#B58500", width=3, dash="solid"),
           marker=dict(size=7)
       )
   )
   # صندوق النقد
      fig_f.add_trace(
       go.Scatter(
           x=df_forecast[year_col],
           y=df_forecast[imf_col],
           mode="lines+markers",
           name="الصندوق",
           line=dict(color="#6E6259", width=3, dash="solid"),
           marker=dict(size=7)
       )
   )
   # خط يفصل الفعلي عن التوقع
      fig_f.add_vline(
       x=last_actual_year,
       line_dash="dash",
       line_color="#912F46",
       line_width=2
   )
      fig_f.add_annotation(
       x=last_actual_year,
       y=1,
       yref="paper",
       text="بداية التوقعات",
       showarrow=False,
       textangle=90,
       xshift=-30,
       font=dict(size=12, color="#912F46")
   )
      fig_f.update_layout(
       title="مقارنة التوقعات المستقبلية",
       title_x=0.5,
       xaxis_title="السنة",
       yaxis_title="المعدل",
       template="plotly_white",
       height=700
      )
      st.markdown("""
<div style="display:flex; justify-content:center; gap:40px; font-size:18px; direction:rtl;">
<span style="color:#286140;">● النمو الفعلي</span>
<span style="color:#1B365D;">● توقعات وزارة المالية </span>
<span style="color:#B58500;">● (Exponential Smoothing)توقعات نموذج هولت</span>
<span style="color:#6E6259;">● توقعات صندوق النقد الدولي</span>
</div>
""", unsafe_allow_html=True)
      
      fig_f.update_xaxes(dtick=1)
      st.plotly_chart(fig_f, use_container_width=True)
   
   # مقارنة سنة مختارة
  
      forecast_only = df_forecast[df_forecast[year_col] > last_actual_year]
      if not forecast_only.empty:
       compare_year = st.selectbox(
           "اختر سنة للمقارنة بين التوقعات",
           forecast_only[year_col].tolist()
       )
       row = forecast_only[forecast_only[year_col] == compare_year].iloc[0]
       compare_df = pd.DataFrame({
           "الجهة": ["وزارة المالية", "نموذج هولت", "صندوق النقد"],
           "القيمة": [row[mof_col], row[holt_col], row[imf_col]]
       })
       fig_bar = px.bar(
           compare_df,
           x="الجهة",
           y="القيمة",
           color="الجهة",
           text="القيمة",
           color_discrete_map={
       "وزارة المالية": "#1B365D",
       "نموذج هولت": "#B58500",
       "صندوق النقد": "#6E6259"}
       )
       fig_bar.update_traces(texttemplate="%{text:.2f}", textposition="outside")
       fig_bar.update_layout(
           title=f"مقارنة التوقعات في سنة {int(compare_year)}",
           title_x=0.5,
           xaxis_title="",
           yaxis_title="القيمة",
           template="plotly_white",
           height=550,
           showlegend=False
       )
       st.plotly_chart(fig_bar, use_container_width=True)
      with st.expander("المنهجية"):
       st.write("""
       - **وزارة المالية:** توقع رسمي منشور من الجهة الحكومية.
       - **نموذج هولت (Exponential Smoothing):** توقع إحصائي مبني على الاتجاه التاريخي للسلسلة الزمنية.
       - **صندوق النقد الدولي:** توقع خارجي من مؤسسة دولية.
       - الخط الرأسي المتقطع يوضح نقطة الانتقال من القيم الفعلية إلى القيم المتوقعة.
       """)




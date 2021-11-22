#region Importing the dependencies

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pytrends.request import TrendReq
import streamlit as st
import openpyxl
import plotly.express as px
import datetime as dt
from dateutil.relativedelta import relativedelta
from pathlib import Path
import datetime

#endregion

#region Defining Google Trends Function
#Google Trends'ten veri çekip data frame haline getireceğimiz fonksiyonu kuruyoruz.

pytrends = TrendReq(hl="en-US")
time_frames={}
def check_trends(geo,time_data):
    pytrends.build_payload(keyword,
                           timeframe=time_data,
                           geo=geo,
                          gprop="")
    data=pytrends.interest_over_time()
    return data
#endregion


#region Getting Trends
keyword_dict=dict()
keyword_file = Path(__file__).parents[0] / 'keyword ürün grupları_DEU.XLSX'
xl = pd.ExcelFile(keyword_file)

for names in xl.sheet_names:
    df=pd.read_excel(keyword_file,sheet_name=names)
    keyword_dict[names]=list(df[df.columns[0]].values)

#Türkçe ve İngilizce Kelimeleri Ekleme
turkce_ingilizce_file=Path(__file__).parents[0] / 'Kategori İsimleri.xlsx'
turkce_ingilizce_keywords=pd.read_excel(turkce_ingilizce_file)

turkce_ingilizce={}
for item in turkce_ingilizce_keywords["Ürün Grubu"].unique():
    turkce_ingilizce[item]=list(turkce_ingilizce_keywords[turkce_ingilizce_keywords["Ürün Grubu"]==item]["Kelime"].values)

for item in turkce_ingilizce.keys():
    keyword_dict[item]=turkce_ingilizce[item]

#endregion

#region Streamlit

#Logo ve başlığı oluşturuyoruz.
st.image("karaca_logo2.PNG")
st.markdown("<h1 style='text-align: center; color: black;'>Karaca Google Trends Dashboard</h1>", unsafe_allow_html=True)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
placeholder = st.empty()
placeholder.info("Soldaki menüden kriterleri seçip 'Görseli Üret' butonuna tıklayınız.")

#Sidebar
#Yandaki menü kısmını oluşturuyoruz.
st.sidebar.write("Kriterler")

ulke=st.sidebar.radio("Ülke",("Türkiye","Almanya"))
if ulke=="Türkiye":
    geo="TR"
elif ulke=="Almanya":
    geo="DE"

#Time
today = dt.datetime.today()
day = today.day
month = today.month
year = today.year

if int(day) < 10:
    day = "0" + str(int(day))
else:
    day = day

if int(month) < 10:
    month = "0" + str(int(month))
else:
    month = month
date = str(year) + "-" + str(month) + "-" + str(day)


baslangic=st.sidebar.date_input("Başlangıç Tarihi Seçiniz",min_value=datetime.date(2004,1,1))
bitis=st.sidebar.date_input("Bitiş Tarihi Seçiniz",min_value=datetime.date(2004,1,1))
time_data=str(baslangic)+" "+str(bitis)

grafik_turu=st.sidebar.radio("Kelime Grupları Aramaya Dahil Olacak Mı?",("Evet","Hayır"))

#Butona fonksiyon atıyoruz
if grafik_turu=="Evet":
    kelime_gruplari=st.sidebar.multiselect("Kelime Grubu Seçiniz",list(keyword_dict.keys()))
    tum_secili_kelimeler = []
    for kelime in range(0, len(kelime_gruplari)):
        tum_secili_kelimeler += keyword_dict[kelime_gruplari[kelime]]
    keyword_item = st.sidebar.multiselect("Kelime Seçiniz", tum_secili_kelimeler)
    ekstra_kelime=st.sidebar.text_input("Ekstra Kelimeler:",help="Virgül ile kelimeleri ayırınız.",)
    ekstra_kelime = ekstra_kelime.split(",")
    ekstra_kelime = [x.strip(' ') for x in ekstra_kelime]
    ekstra_kelime_save=pd.DataFrame(ekstra_kelime)
    ekstra_kelime_save.to_excel("ekstra.xlsx")
    tum_kelimeler=kelime_gruplari
    tum_kelimeler+=keyword_item
    tum_kelimeler+=ekstra_kelime
    ek=pd.read_excel("ekstra.xlsx")
    st.write(ek)
    try:
        tum_kelimeler.remove("")
    except:
        pass
    gorsel=st.sidebar.button("Görseli Üret")
    st.sidebar.image("datawise.png", use_column_width=True)
    if gorsel:
        try:
            if len(tum_kelimeler)>1:
                kw = dict()
                for item in tum_kelimeler:
                    keyword_sabit = tum_kelimeler[0]
                    keyword_list = []
                    keyword_list.insert(0, keyword_sabit)
                    keyword_list.insert(1, item)
                    try:
                        keyword = keyword_list
                        kw[item] = check_trends(geo=geo, time_data=time_data)[keyword]
                    except:
                        continue
                dfk = pd.DataFrame()
                df1 = kw[list(kw.keys())[0]]
                dfk = df1
                for i in range(1, len(list(kw.keys()))):
                    df2 = kw[list(kw.keys())[i]]
                    fark = df1[keyword_sabit].mean() / df2[keyword_sabit].mean()
                    df2 = df2 * fark
                    dfk = dfk.merge(df2, how="inner", left_index=True, right_index=True)
                    kw[list(kw.keys())[i]] = df2

                try:
                    dfk.drop(columns=[keyword_sabit + "_y"], inplace=True)
                except:
                    pass
                try:
                    dfk = dfk.rename(columns={keyword_sabit + "_x": keyword_sabit})
                except:
                    pass

                df4 = (dfk - dfk.min().min()) / (dfk.max().max() - dfk.min().min())
                df4 = df4 * (100 - dfk.min().min()) + dfk.min().min()
                fig, ax = plt.subplots(figsize=(16, 4))
            else:
                keyword=tum_kelimeler
                df4=check_trends(geo=geo, time_data=time_data)[keyword]
            placeholder.line_chart(data=df4, width=600, height=400)
        except:
            placeholder.error("Google aratmaları yeterli sayıda olmadığı için veriye ulaşılamadı.")

else:
    kelime_gruplari = st.sidebar.multiselect("Kelime Grubu Seçiniz", list(keyword_dict.keys()))
    tum_secili_kelimeler = []
    for kelime in range(0, len(kelime_gruplari)):
        tum_secili_kelimeler += keyword_dict[kelime_gruplari[kelime]]
    keyword_item = st.sidebar.multiselect("Kelime Seçiniz", tum_secili_kelimeler)
    ekstra_kelime = st.sidebar.text_input("Ekstra Kelimeler:", help="Virgül ile kelimeleri ayırınız.", )
    ekstra_kelime = ekstra_kelime.split(",")
    ekstra_kelime = [x.strip(' ') for x in ekstra_kelime]
    tum_kelimeler = keyword_item
    tum_kelimeler += ekstra_kelime
    try:
        tum_kelimeler.remove("")
    except:
        pass
    gorsel = st.sidebar.button("Görseli Üret")
    st.sidebar.image("datawise.png", use_column_width=True)
    if gorsel:
        try:
            if len(tum_kelimeler) > 1:
                kw = dict()
                for item in tum_kelimeler:
                    keyword_sabit = tum_kelimeler[0]
                    keyword_list = []
                    keyword_list.insert(0, keyword_sabit)
                    keyword_list.insert(1, item)
                    try:
                        keyword = keyword_list
                        kw[item] = check_trends(geo=geo, time_data=time_data)[keyword]
                    except:
                        continue
                dfk = pd.DataFrame()
                df1 = kw[list(kw.keys())[0]]
                dfk = df1
                for i in range(1, len(list(kw.keys()))):
                    df2 = kw[list(kw.keys())[i]]
                    fark = df1[keyword_sabit].mean() / df2[keyword_sabit].mean()
                    df2 = df2 * fark
                    dfk = dfk.merge(df2, how="inner", left_index=True, right_index=True)
                    kw[list(kw.keys())[i]] = df2

                try:
                    dfk.drop(columns=[keyword_sabit + "_y"], inplace=True)
                except:
                    pass
                try:
                    dfk = dfk.rename(columns={keyword_sabit + "_x": keyword_sabit})
                except:
                    pass

                df4 = (dfk - dfk.min().min()) / (dfk.max().max() - dfk.min().min())
                df4 = df4 * (100 - dfk.min().min()) + dfk.min().min()
                fig, ax = plt.subplots(figsize=(16, 4))
            else:
                keyword = tum_kelimeler
                df4 = check_trends(geo=geo, time_data=time_data)[keyword]
            placeholder.line_chart(data=df4, width=600, height=400)
        except:
            placeholder.error("Google aratmaları yeterli sayıda olmadığı için veriye ulaşılamadı.")
#endregion

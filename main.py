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
keyword_file = Path(__file__).parents[0] / 'karaca/keyword ürün grupları_DEU.xlsx'
xl = pd.ExcelFile(keyword_file)

for names in xl.sheet_names:
    df=pd.read_excel(keyword_file,sheet_name=names)
    keyword_dict[names]=list(df[df.columns[0]].values)

#endregion

#region Streamlit

#Logo ve başlığı oluşturuyoruz.
st.image("karaca_logo2.PNG")
st.markdown("<h1 style='text-align: center; color: black;'>Karaca Google Trends Dashboard</h1>", unsafe_allow_html=True)
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


time=st.sidebar.radio("Dönem",("Yıllık","Aylık","Haftalık","Günlük"))
if time=="Yıllık":
    yil_sayisi=st.sidebar.text_input("Son Kaç Yılı Görmek İstiyorsunuz?")
    if yil_sayisi=="":
        time_data="all"
    else:
        time_data_baslangic=str(year-int(yil_sayisi))+ "-" + str(month) + "-" + str(day)
        if year-int(yil_sayisi)<2004:
            st.warning('2004 yılından önce veri bulunmamaktadır.')
        else:
            time_data=time_data_baslangic+" "+date


if time=="Aylık":
    ay_sayisi=st.sidebar.text_input("Son Kaç Ayı Görmek İstiyorsunuz?")
    if ay_sayisi=="":
        time_data="all"
    else:
        today_baslangic = today - relativedelta(months=int(ay_sayisi))
        day = today_baslangic.day
        month = today_baslangic.month
        year = today_baslangic.year

        if int(day) < 10:
            day = "0" + str(int(day))
        else:
            day = day

        if int(month) < 10:
            month = "0" + str(int(month))
        else:
            month = month
        date_baslangic = str(year) + "-" + str(month) + "-" + str(day)
        time_data = date_baslangic + " " + date


if time=="Haftalık":
    hafta_sayisi=st.sidebar.text_input("Son Kaç Haftayı Görmek İstiyorsunuz?")
    if hafta_sayisi=="":
        time_data="all"
    else:
        today_baslangic = today - relativedelta(days=int(hafta_sayisi)*7)
        day = today_baslangic.day
        month = today_baslangic.month
        year = today_baslangic.year

        if int(day) < 10:
            day = "0" + str(int(day))
        else:
            day = day

        if int(month) < 10:
            month = "0" + str(int(month))
        else:
            month = month
        date_baslangic = str(year) + "-" + str(month) + "-" + str(day)
        time_data = date_baslangic + " " + date

if time=="Günlük":
    gun_sayisi=st.sidebar.text_input("Son Kaç Günü Görmek İstiyorsunuz?")
    if gun_sayisi=="":
        time_data="all"
    else:
        today_baslangic = today - relativedelta(days=int(gun_sayisi))
        day = today_baslangic.day
        month = today_baslangic.month
        year = today_baslangic.year

        if int(day) < 10:
            day = "0" + str(int(day))
        else:
            day = day

        if int(month) < 10:
            month = "0" + str(int(month))
        else:
            month = month
        date_baslangic = str(year) + "-" + str(month) + "-" + str(day)
        time_data = date_baslangic + " " + date
        print(date_baslangic)

grafik_turu=st.sidebar.radio("Ürün Grupları Aramaya Dahil Olacak Mı?",("Evet","Hayır"))

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
    tum_kelimeler=kelime_gruplari
    tum_kelimeler+=keyword_item
    tum_kelimeler+=ekstra_kelime
    try:
        tum_kelimeler.remove("")
    except:
        pass
    gorsel=st.sidebar.button("Görseli Üret")
    if gorsel:
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
    if gorsel:
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
#endregion

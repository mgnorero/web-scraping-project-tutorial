import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Recopilar y almacenar información sobre el crecimiento de la compañía cada tres meses
# Almacenar el texto scrapeado de la web en alguna variable
url =  "https://ycharts.com/companies/TSLA/revenues"
html_data = requests.get(url, time.sleep(10)).text

if "403 ERROR" in html_data:
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac 05 X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"}
    html_data = requests.get(url, headers=headers)
    time.sleep(19)
    html_data = html_data.text

soup = BeautifulSoup(html_data, "html.parser")
tables = soup.find_all("table")

#encontrar el indice de la tabla que se busca
for index, table in enumerate(tables):
    if {"Date" in str(table)}:
        table_index = index
        break
    print(table)

print(table_index)

#convertir la tabla en un data frame
tesla_df = pd.DataFrame(columns=["Date", "Revenue"])
for row in tables[table_index].find_all("tr"):
    col = row.find_all("td")
    if col != []:
        date = col[0].text
        revenue = float(col[1].text.strip().replace("B",""))
        tesla_df = pd.concat([tesla_df, pd.DataFrame([[date, revenue]], columns=["Date", "Revenue"])], ignore_index=True)

tesla_df.head()

# crear una base de datos e incluir los datos limpios en ella.
# crear la base de datos, la tabla, insertar valores, comit.

#declarar una conexion, dar nombre a la base de datos 
conn = sqlite3.connect("tesla.db")

#declarar cursor (permite ejecutar sentencias SQL dentro de la base de datos dentro de una conexion)
c = conn.cursor()

#crear la tabla
c.execute("CREATE TABLE tesla_revenue (date TEXT, revenue REAL)")
conn.commit()

#llevar data frame a la tabla
tesla_df.to_sql("tesla_revenue", conn, if_exists="replace", index=False)

#imprimir lista de los datos como pares ordenados
c.execute("SELECT * FROM tesla_revenue").fetchall()

#Graficar los datos
#Gráfico de Líneas de Ingresos de Tesla a lo Largo del Tiempo

tesla_df["Date"] = pd.to_datetime(tesla_df["Date"])

sns.lineplot(x="Date", y="Revenue", data=tesla_df)
plt.title("Tesla revenue over time")
plt.tight_layout()
plt.xticks(rotation=45)
plt.show()

#Diagrama de Dispersión con Líneas de Tendencia

# Convertir fechas a números ordinales
tesla_df["Date_ordinal"] = tesla_df["Date"].apply(lambda x: x.toordinal())

# Gráfico de dispersión con línea de tendencia
sns.lmplot(x="Date_ordinal", y="Revenue", data=tesla_df, aspect=2, height=6, line_kws={'color': 'red'}, scatter_kws={'alpha':0.5})
plt.title("Tesla Revenue Over Time with Trend Line")
plt.xlabel("Date")
plt.ylabel("Revenue")

# Convertir las etiquetas x a fechas
locs, labels = plt.xticks()
plt.xticks(locs, [pd.to_datetime(int(label)).strftime('%Y-%m-%d') for label in locs], rotation=45)

plt.tight_layout()
plt.show()

#grafico trimestral
# Agrupar por trimestre
tesla_df['Quarter'] = tesla_df['Date'].dt.to_period('Q')

# Calcular ingresos por trimestre
revenue_by_quarter = tesla_df.groupby('Quarter')['Revenue'].sum().reset_index()

# Crear gráfico de barras agrupadas
plt.figure(figsize=(10, 6))
sns.barplot(x='Quarter', y='Revenue', data=revenue_by_quarter, hue="Quarter", palette='viridis', legend=False)
plt.title('Tesla Revenue by Quarter')
plt.xlabel('Quarter')
plt.ylabel('Revenue')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
import matplotlib.pyplot as plt
import numpy
import pandas
import seaborn
seaborn.set_context('talk')

#from decouple import config
from sqlalchemy import create_engine, text
from google.colab import files
import io

import plotly
plotly.__version__
# Make sure it's 4.14.3

melb_df = pandas.read_csv(
    'https://cs.famaf.unc.edu.ar/~mteruel/datasets/diplodatos/melb_data.csv')
melb_df[:3]

"""
 Ejercicio 1 SQL: 

1. Crear una base de datos en SQLite utilizando la libreria [SQLalchemy](https://stackoverflow.com/questions/2268050/execute-sql-from-file-in-sqlalchemy).
https://docs.sqlalchemy.org/en/14/core/engines.html#sqlite

2. Ingestar los datos provistos en 'https://cs.famaf.unc.edu.ar/~mteruel/datasets/diplodatos/melb_data.csv' en una tabla y el dataset generado en clase con datos de airbnb y sus precios por codigo postal en otra.

3. Implementar consultas en SQL que respondan con la siguiente información:

    - cantidad de registros totales por ciudad.
    - cantidad de registros totales por barrio y ciudad.

4. Combinar los datasets de ambas tablas ingestadas utilizando el comando JOIN de SQL  para obtener un resultado similar a lo realizado con Pandas en clase.  
"""

# 1) Creamos la base de datos
engine = create_engine('sqlite:///melb_housing_data.sqlite3', echo=True)

# 2) Se ingresan los datos de melbourn a la base de datos
melb_df.to_sql('mlb_data', con=engine, if_exists="replace")

# Se sube el csv de los datos de aribnb
uploaded = files.upload()

file_key = 'airbnb_price_by_zipcode.csv'  # Replace for correspoing key
airbnb_df = pandas.read_csv(io.StringIO(uploaded[file_key].decode('utf-8')))

airbnb_df[:3]

#2) Se ingresan los datos de arbnb a la base de datos
airbnb_df.to_sql('airbnb_data', con=engine, if_exists="replace")

#3) Cantidad de registros totales por ciudad.
query = "SELECT CouncilArea,count(*) as Count FROM mlb_data GROUP BY CouncilArea"

df = pandas.read_sql_query(
    sql = query,
    con = engine
)

df

# Cantidad de registros totales por barrio y ciudad.
query = "SELECT CouncilArea, Suburb ,count(1) as Count FROM mlb_data GROUP BY CouncilArea, Suburb"

df = pandas.read_sql_query(
    sql = query,
    con = engine
)

df

#4) Combinar los datasets de ambas tablas ingestadas utilizando el comando JOIN de SQL para 
# Obtener un resultado similar a lo realizado con Pandas en clase.
query = """
SELECT melb_avg.PostCode postcode, melb_avg.Price melb_price, airbnb_avg.Price airbnb_day_rent_price
FROM (
    SELECT CAST(Postcode as INT) PostCode, CAST(avg(price) as INT) Price, count(1) Count_mlb 
    FROM mlb_data 
    GROUP BY Postcode) as melb_avg
    
    INNER JOIN

    (SELECT airbnb_1.zipcode, CAST(avg(airbnb_1.price) as INT) Price , count(1) Count_airbnb 
    FROM (
        SELECT CAST(zipcode as INT) zipcode, CAST(price as INT) Price 
        FROM airbnb_data) as airbnb_1
    GROUP BY airbnb_1.zipcode) as airbnb_avg

    ON melb_avg.PostCode = airbnb_avg.zipcode
"""

df = pandas.read_sql_query(
    sql = query,
    con = engine
)

df[:20]


"""
 Ejercicio 2: 

1. Seleccionar un subconjunto de columnas que les parezcan relevantes al problema de predicción del valor de la propiedad. Justificar las columnas seleccionadas y las que no lo fueron.
 - Eliminar los valores extremos que no sean relevantes para la predicción de valores de las propiedades.

2. Agregar información adicional respectiva al entorno de una propiedad a partir del [conjunto de datos de AirBnB](https://www.kaggle.com/tylerx/melbourne-airbnb-open-data?select=cleansed_listings_dec18.csv) utilizado en el práctico. 
  1. Seleccionar qué variables agregar y qué combinaciones aplicar a cada una. Por ejemplo, pueden utilizar solo la columna `price`, o aplicar múltiples transformaciones como la mediana o el mínimo.
  1. Utilizar la variable zipcode para unir los conjuntos de datos. Sólo incluir los zipcodes que tengan una cantidad mínima de registros (a elección) como para que la información agregada sea relevante.
  2. Investigar al menos otras 2 variables que puedan servir para combinar los datos, y justificar si serían adecuadas o no. Pueden asumir que cuentan con la ayuda de anotadores expertos para encontrar equivalencias entre barrios o direcciones, o que cuentan con algoritmos para encontrar las n ubicaciones más cercanas a una propiedad a partir de sus coordenadas geográficas. **NO** es necesario que realicen la implementación.

Pueden leer otras columnas del conjunto de AirBnB además de las que están en `interesting_cols`, si les parecen relevantes.
"""


#se exploran las columnas del dataset de melborn
melb_df.columns

'''1)Se eligen las siguientes columnas del dataset de melborn, para la predicción del precio
ello en razón de que son que más pueden impactar en el precio de una casa.
Quizas la ubicación, como el barrio donde se ubican, la ciudad, la región, podrían ser otros
datos que impacten en el precio, pero dado el desconocimiento que tenemos sobre la relevancia de la ubicación geográfica
ya que no conocemos cuales son, las columnas elegidas serían las más objetivas para determinar el precio.'''

colums_predict_price = ['Address','Rooms','Price','Bedroom2','Bathroom','Landsize']
melb_df.loc[:,colums_predict_price]

#se ven algunas métricas del dataset melborn
melb_df['Price'].describe().apply(lambda s: '{0:.2f}'.format(s))

seaborn.histplot(melb_df.Price.dropna())

min_price = melb_df.Price.quantile(0.05)
max_price = melb_df.Price.quantile(0.95)

melb_df_filtered = melb_df[(melb_df['Price'] > min_price) & (melb_df['Price'] < max_price)]

fig, axes = plt.subplots(nrows=2, figsize=(16, 8))
seaborn.histplot(melb_df['Price'], bins=100, ax=axes[0], color='gray')
axes[0].axvline(melb_df['Price'].mean(), color='orangered',
            linestyle='--', label='Media')
axes[0].axvline(melb_df['Price'].median(), color='indigo',
            linestyle='-.', label='Mediana')

#filtered_df = melb_df[(melb_df['Price']< 85000)]# & (melb_df['Price']> 85000)]
seaborn.histplot(melb_df_filtered['Price'], bins=100, ax=axes[1], color='gray')
axes[1].axvline(melb_df_filtered['Price'].mean(), color='orangered',
            linestyle='--', label='Media')
axes[1].axvline(melb_df_filtered['Price'].median(), color='indigo',
            linestyle='-.', label='Mediana')

axes[0].legend()
seaborn.despine()

airbnb_df_all = pandas.read_csv(
    'https://cs.famaf.unc.edu.ar/~mteruel/datasets/diplodatos/cleansed_listings_dec18.csv')

airbnb_df_all.columns

airbnb_df_all['zipcode'] = pandas.to_numeric(airbnb_df_all.zipcode, errors='coerce')

airbnb_df_all['airbnb_zipcode_counter'] = airbnb_df_all.zipcode.value_counts()

airbnb_df_all.loc[:3,['accommodates',
       'bathrooms', 'bedrooms', 'beds']]

"""2.1)Se determinan las variables a agregar y las combinaciones"""

# Pass as argument name the new name of the column, and as value a tuple where
# the first value is the original column and the second value is the operation.
relevant_cols = ['price', 'weekly_price', 'monthly_price','security_deposit','review_scores_rating','review_scores_location','zipcode']

airbnb_price_by_zipcode = airbnb_df_all[relevant_cols].groupby('zipcode')\
   .agg(airbnb_price_mean=('price', 'mean'),
        airbnb_price_median=('price', 'median'),
        airbnb_price_min=('price', 'min'),
        airbnb_price_max=('price', 'max'),
        airbnb_weekly_price_mean=('weekly_price', 'mean'),
        airbnb_monthly_price_mean=('monthly_price', 'mean'),
        airbnb_security_deposit_mean=('security_deposit', 'mean'),
        airbnb_review_scores_rating_mean=('review_scores_rating', 'mean'),
        airbnb_review_scores_location_mean=('review_scores_location', 'mean'))\
   .reset_index()

airbnb_price_by_zipcode[:3]

airbnb_df_all.zipcode.value_counts()

reg_mayor_50 = airbnb_df_all[airbnb_df_all['airbnb_zipcode_counter'] >= 25]
zipcode_reg = reg_mayor_50['zipcode']
airbnb_price_by_zipcode_filtered = airbnb_price_by_zipcode[airbnb_price_by_zipcode['zipcode'].isin(zipcode_reg)]
len(airbnb_price_by_zipcode_filtered)
#zipcode_reg[:3]

"""2.2)Se usa la variable zipcode para unir el conjunto de datos"""

merged_sales_df = melb_df_filtered.merge(
    airbnb_price_by_zipcode_filtered, how='left',
    left_on='Postcode', right_on='zipcode'
)
merged_sales_df.sample(5)

# 2.3) [PENDIENTE]

"""
 Ejercicio 3:
  
Crear y guardar un nuevo conjunto de datos con todas las transformaciones realizadas anteriormente.
"""

merged_sales_df.to_csv("melb_data_extended.csv", index=None)

files.download('melb_data_extended.csv')

"""
 Ejercicios opcionales:

1. Armar un script en python (archivo .py) [ETL](https://towardsdatascience.com/what-to-log-from-python-etl-pipelines-9e0cfe29950e) que corra los pasos de extraccion, transformacion y carga, armando una funcion para cada etapa del proceso y luego un main que corra todos los pasos requeridos.

2. Armar un DAG en Apache Airflow que corra el ETL. (https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)
"""
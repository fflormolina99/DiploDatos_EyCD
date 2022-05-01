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
query1="SELECT Postcode, COUNT(*) FROM mlb_data GROUP BY Postcode"

# Cantidad de registros totales por barrio y ciudad.
query2="SELECT Postcode, Suburb, COUNT(*) FROM mlb_data GROUP BY Postcode, Suburb"

queries = [query1, query2]

with engine.connect() as con:
    for query in queries:
      rs = con.execute(query)
      print(query)
      for row in rs:
          print(row)

      print('\n\n')

#4) Combinar los datasets de ambas tablas ingestadas utilizando el comando JOIN de SQL para 
# Obtener un resultado similar a lo realizado con Pandas en clase.
query3 = "SELECT * FROM mlb_data LEFT JOIN airbnb_data ON mlb_data.Postcode=airbnb_data.zipcode LIMIT 10"

with engine.connect() as con:
  rs = con.execute(query3)
  print(query3)
  for row in rs:
    print(row)


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

"""
 Ejercicio 3:
  
Crear y guardar un nuevo conjunto de datos con todas las transformaciones realizadas anteriormente.
"""

"""
 Ejercicios opcionales:

1. Armar un script en python (archivo .py) [ETL](https://towardsdatascience.com/what-to-log-from-python-etl-pipelines-9e0cfe29950e) que corra los pasos de extraccion, transformacion y carga, armando una funcion para cada etapa del proceso y luego un main que corra todos los pasos requeridos.

2. Armar un DAG en Apache Airflow que corra el ETL. (https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)
"""
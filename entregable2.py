import matplotlib.pyplot as plt
import numpy
import pandas

import seaborn

seaborn.set_context("talk")

# Acá deberían leer el conjunto de datos que ya tienen.
melb_df = pandas.read_csv(
    "https://cs.famaf.unc.edu.ar/~mteruel/datasets/diplodatos/melb_data.csv"
)
melb_df[:3]

"""
 Ejercicio 1: Encoding

1. Seleccionar todas las filas y columnas del conjunto de datos obtenido en la parte 1 del entregable, **excepto** `BuildingArea` y `YearBuilt`, que volveremos a imputar más adelante.

2. Aplicar una codificación One-hot encoding a cada fila, tanto para variables numéricas como categóricas. Si lo consideran necesario, pueden volver a reducir el número de categorías únicas.

Algunas opciones:
  1. Utilizar `OneHotEncoder` junto con el parámetro `categories` para las variables categóricas y luego usar `numpy.hstack` para concatenar el resultado con las variables numéricas. 
  2. `DictVectorizer` con algunos pasos de pre-proceso previo.

Recordar también que el atributo `pandas.DataFrame.values` permite acceder a la matriz de numpy subyacente a un DataFrame.
"""

# limit to categorical data using df.select_dtypes()
categorical_columns_df = melb_df.select_dtypes(include=[object])
categorical_columns_df.head(3)

categorical_columns_df.shape

# import preprocessing from sklearn
from sklearn import preprocessing

# view columns using df.columns
categorical_columns_df.columns

# reate a LabelEncoder object and fit it to each feature in categorical_columns_df
# 1. INSTANTIATE
# encode labels with value between 0 and n_classes-1.
le = preprocessing.LabelEncoder()


# 2/3. FIT AND TRANSFORM
# use df.apply() to apply le.fit_transform to all columns
categorical_columns_df_2 = categorical_columns_df.apply(le.fit_transform)
categorical_columns_df_2.head()

# create a OneHotEncoder object, and fit it to all of categorical_columns_df_2

# 1. INSTANTIATE
enc = preprocessing.OneHotEncoder()

# 2. FIT
enc.fit(categorical_columns_df_2)

# 3. Transform
onehotcategoricals = enc.transform(categorical_columns_df_2).toarray()
onehotcategoricals.shape

# as you can see, you've the same number of rows
# but now you've so many more columns due to how we changed all the categorical data into numerical data

onehotcategoricals

onhot_df = pandas.DataFrame(onehotcategoricals)
onhot_df.columns = enc.get_feature_names_out()
onhot_df

categorical_cols = []
numerical_cols = []
for col in list_col_types:
    if col[1] == "object":
        categorical_cols.append(col[0])
    elif col[0] == "BuildingArea" or col[0] == "YearBuilt":
        continue
    else:
        numerical_cols.append(col[0])
print(categorical_cols)
print(numerical_cols)

melb_df[numerical_cols].values

# melb_df_encoded = numpy.hstack((onhot_df,melb_df[numerical_cols]))
# melb_df_encoded = onhot_df+melb_df[numerical_cols]

# se concatenan ambos grupos de variables
melb_df_encoded2 = pandas.concat([onhot_df, melb_df[numerical_cols]])

# melb_df_encoded2[:3]

# melb_df_encoded

categorical_cols = ["Type"]
numerical_cols = ["Rooms"]


melb_df[categorical_cols].nunique()

# Check for nulls
melb_df[categorical_cols].isna().sum()

# melb_df_filtered = melb_df[categorical_cols] + melb_df[numerical_cols]
# melb_df_filtered.columns

# feature_cols = columns
# feature_dict = list(melb_df[feature_cols].T.to_dict().values())
# feature_dict[:2]

# from sklearn.feature_extraction import DictVectorizer
# vec = DictVectorizer()
# feature_matrix = vec.fit_transform(feature_dict)

# feature_matrix

# vec.get_feature_names()[:10]

"""
 Ejercicio 2: Imputación por KNN

En el teórico se presentó el método `IterativeImputer` para imputar valores faltantes en variables numéricas. Sin embargo, los ejemplos presentados sólo utilizaban algunas variables numéricas presentes en el conjunto de datos. En este ejercicio, utilizaremos la matriz de datos codificada para imputar datos faltantes de manera más precisa.

1. Agregue a la matriz obtenida en el punto anterior las columnas `YearBuilt` y `BuildingArea`.
2. Aplique una instancia de `IterativeImputer` con un estimador `KNeighborsRegressor` para imputar los valores de las variables. ¿Es necesario estandarizar o escalar los datos previamente?
3. Realice un gráfico mostrando la distribución de cada variable antes de ser imputada, y con ambos métodos de imputación.
"""
melb_df_encoded2["YearBuilt"] = melb_df["YearBuilt"]
melb_df_encoded2["BuildingArea"] = melb_df["BuildingArea"]

from sklearn.experimental import enable_iterative_imputer
from sklearn.neighbors import KNeighborsRegressor
from sklearn.impute import IterativeImputer

melb_data_mice = melb_df_encoded2.copy(deep=True)

mice_imputer = IterativeImputer(random_state=0, estimator=KNeighborsRegressor())
melb_data_mice[["YearBuilt", "BuildingArea"]] = mice_imputer.fit_transform(
    melb_data_mice[["YearBuilt", "BuildingArea"]]
)

melb_data_mice[:3]

"""Ejemplo de gráfico comparando las distribuciones de datos obtenidas con cada método de imputación."""

mice_year_built = melb_data_mice.YearBuilt.to_frame()
mice_year_built["Imputation"] = "KNN over YearBuilt and BuildingArea"
melb_year_build = melb_df.YearBuilt.dropna().to_frame()
melb_year_build["Imputation"] = "Original"
data = pandas.concat([mice_year_built, melb_year_build]).reset_index()
fig = plt.figure(figsize=(8, 5))
g = seaborn.kdeplot(data=data, x="YearBuilt", hue="Imputation")

"""
 Ejercicio 3: Reducción de dimensionalidad.

Utilizando la matriz obtenida en el ejercicio anterior:
1. Aplique `PCA` para obtener $n$ componentes principales de la matriz, donde `n = min(20, X.shape[0])`. ¿Es necesario estandarizar o escalar los datos?
2. Grafique la varianza capturada por los primeros $n$ componentes principales, para cada $n$.
3. En base al gráfico, seleccione las primeras $m$ columnas de la matriz transformada para agregar como nuevas características al conjunto de datos.
"""


"""
 Ejercicio 4: Composición del resultado

Transformar nuevamente el conjunto de datos procesado en un `pandas.DataFrame` y guardarlo en un archivo.

Para eso, será necesario recordar el nombre original de cada columna de la matriz, en el orden correcto. Tener en cuenta:
1. El método `OneHotEncoder.get_feature_names` o el atributo `OneHotEncoder.categories_` permiten obtener una lista con los valores de la categoría que le corresponde a cada índice de la matriz.
2. Ninguno de los métodos aplicados intercambia de lugar las columnas o las filas de la matriz.
"""


"""
 Ejercicio 5: Documentación

En un documento `.pdf` o `.md` realizar un reporte de las operaciones que realizaron para obtener el conjunto de datos final. Se debe incluir:
  1. Criterios de exclusión (o inclusión) de filas
  2. Interpretación de las columnas presentes
  2. Todas las transofrmaciones realizadas

Este documento es de uso técnico exclusivamente, y su objetivo es permitir que otres desarrolladores puedan reproducir los mismos pasos y obtener el mismo resultado. Debe ser detallado pero consiso. Por ejemplo:

```
  ## Criterios de exclusión de ejemplos
  1. Se eliminan ejemplos donde el año de construcción es previo a 1900

  ## Características seleccionadas
  ### Características categóricas
  1. Type: tipo de propiedad. 3 valores posibles
  2. ...
  Todas las características categóricas fueron codificadas con un
  método OneHotEncoding utilizando como máximo sus 30 valores más 
  frecuentes.
  
  ### Características numéricas
  1. Rooms: Cantidad de habitaciones
  2. Distance: Distancia al centro de la ciudad.
  3. airbnb_mean_price: Se agrega el precio promedio diario de 
     publicaciones de la plataforma AirBnB en el mismo código 
     postal. [Link al repositorio con datos externos].

  ### Transformaciones:
  1. Todas las características numéricas fueron estandarizadas.
  2. La columna `Suburb` fue imputada utilizando el método ...
  3. Las columnas `YearBuilt` y ... fueron imputadas utilizando el 
     algoritmo ...
  4. ...

  ### Datos aumentados
  1. Se agregan las 5 primeras columnas obtenidas a través del
     método de PCA, aplicado sobre el conjunto de datos
     totalmente procesado.
```

"""

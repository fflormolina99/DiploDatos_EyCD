# Documentación Técnica de la Exploración y Curación de Datos

## Características seleccionadas
### Características categóricas
* Suburb: región
* Address: dirección de la propiedad
* Type: Tipo de propiedad.
* Method: Método en que fue vendida/adquirida la propiedad.
* SellerG: Agente de bienes raíces
* Date: Fecha de venta
* CouncilArea: Jurisdicción en la que está circunscripta la propiedad
* Regionname: Región en que se ubica la propiedad
NOTA: Todas las características categóricas fueron codificadas con un método OneHotEncoding que aplica la clase DictVectorizer de la librería Scikit-Learn. Para ello primero se transformó todo el corpus en un diccionario

### Características numéricas
* Rooms: Número de habitaciones
* Price: Precio en dólares
* Distance: Distancia desde el centro de la ciudad
* Postcode: código postal
* Bedroom2 : Número de habitaciones (dato obtenido de diversas fuentes)
* Bathroom: Número de baños
* Car: cantidad de cocheras
* Landsize: Tamaño de la propiedad
* Lattitude y Longtitude: Ubicación geoespacial de la propiedad
* Propertycount: Número de propiedades que exiten en el suburbio donde está radicada la propiedad
* zipcode: código postal
* airbnb_price_mean: Promedio de precios publicados en Airbnb
* airbnb_price_median: Mediana de precios publicados en Airbnb
* airbnb_price_min: Precio mínimo publicado en Airbnb
* airbnb_price_max: Precio máximo publicado en Airbnb
* airbnb_weekly_price_mean: Promedio de precio semanal publicado en Airbnb
* airbnb_monthly_price_mean: Promedio de precio mensual publicado en Airbnb
* airbnb_security_deposit_mean:Promedio de precio del seguro de depósito publicado en Airbnb
* airbnb_review_scores_rating_mean: Raiting promedio publicado en Airbnb
* airbnb_review_scores_location_mean:  Puntaje promedio de la ubicación de la propiedad publicado en Airbnb.

 ## Transformaciones:
1. Todas las características numéricas fueron estandarizadas.
2. Además de la estandarización se rellenaron los valores nan (transformándolos por número)
3. La matriz esparza generada por DictVectorizer fue transformada a densa previo a proceder a la imputación.
4. Las columnas `YearBuilt` y  ‘BuildingArea',  fueron imputadas utilizando el algoritmo IterativeImputer con un estimador KNeighborsRegressor.

## Datos aumentados
1. Se agregan las 6 primeras columnas obtenidas a través del método de PCA, aplicado sobre el conjunto de datos totalmente procesado.
2. Se genera un nuevo dataset con los resultados obtenidos mediante el método de PCA


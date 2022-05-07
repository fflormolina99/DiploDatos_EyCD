import datetime
import pendulum
from airflow.decorators import dag, task
import pandas
from sqlalchemy import create_engine, text

CONN_STRING = "sqlite:///melb_housing_data.sqlite3"
MELB_URI = "https://cs.famaf.unc.edu.ar/~mteruel/datasets/diplodatos/melb_data.csv"
AIRBNB_URI = "https://cs.famaf.unc.edu.ar/~mteruel/datasets/diplodatos/cleansed_listings_dec18.csv"

@dag(
    'etl_dag',
    schedule_interval="0 0 * * *",
    start_date=pendulum.datetime(2022, 5, 1, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
)
def Etl():    
    @task
    def extract():
        # NOTA: Se consideró "extracción" a la obtención de los datos desde el repositorio remoto, para 
        # cargarlos en la base de datos SQLite local. Se usa esta base de datos para compartir la información 
        # entre las Task en lugar de usar XComs.
        #
        # Por lo tanto, en cada task los datos se van a obtener desde la BD
        engine = create_engine(CONN_STRING, echo=True)
        
        melb_df = pandas.read_csv(MELB_URI)
        melb_df.to_sql("mlb_data", con=engine, if_exists="replace")

        airbnb_df_all = pandas.read_csv(AIRBNB_URI)
        airbnb_df_all.to_sql("airbnb_data", con=engine, if_exists="replace")


    @task
    def transform():
        engine = create_engine(CONN_STRING, echo=True)
        melb_df = pandas.read_sql_table('mlb_data', engine)
        airbnb_df_all = pandas.read_sql_table('airbnb_data', engine)

        colums_predict_price = [
            "Address",
            "Rooms",
            "Price",
            "Bedroom2",
            "Bathroom",
            "Landsize",
            "Car",
        ]
        melb_df.loc[:, colums_predict_price]

        min_price = melb_df.Price.quantile(0.05)
        max_price = melb_df.Price.quantile(0.95)

        melb_df_filtered = melb_df[
            (melb_df["Price"] > min_price) & (melb_df["Price"] < max_price)
        ]

        airbnb_df_all["zipcode"] = pandas.to_numeric(airbnb_df_all.zipcode, errors="coerce")

        airbnb_df_all["airbnb_zipcode_counter"] = airbnb_df_all.zipcode.value_counts()

        airbnb_df_all.loc[:3, ["accommodates", "bathrooms", "bedrooms", "beds"]]

        relevant_cols = [
            "price",
            "weekly_price",
            "monthly_price",
            "security_deposit",
            "review_scores_rating",
            "review_scores_location",
            "zipcode",
        ]

        airbnb_price_by_zipcode = (
            airbnb_df_all[relevant_cols]
            .groupby("zipcode")
            .agg(
                airbnb_price_mean=("price", "mean"),
                airbnb_price_median=("price", "median"),
                airbnb_price_min=("price", "min"),
                airbnb_price_max=("price", "max"),
                airbnb_weekly_price_mean=("weekly_price", "mean"),
                airbnb_monthly_price_mean=("monthly_price", "mean"),
                airbnb_security_deposit_mean=("security_deposit", "mean"),
                airbnb_review_scores_rating_mean=("review_scores_rating", "mean"),
                airbnb_review_scores_location_mean=("review_scores_location", "mean"),
            )
            .reset_index()
        )

        reg_mayor_50 = airbnb_df_all[airbnb_df_all["airbnb_zipcode_counter"] >= 25]
        zipcode_reg = reg_mayor_50["zipcode"]
        airbnb_price_by_zipcode_filtered = airbnb_price_by_zipcode[
            airbnb_price_by_zipcode["zipcode"].isin(zipcode_reg)
        ]

        merged_sales_df = melb_df_filtered.merge(
            airbnb_price_by_zipcode_filtered, how="left", left_on="Postcode", right_on="zipcode"
        )
        merged_sales_df.to_sql("merged_sales_data", con=engine, if_exists="replace")


    @task
    def load():
        # En este punto, el "load" en lugar de cargar el resultado en el data warehouse, se 
        # desacrgó en un archivo csv.
        engine = create_engine(CONN_STRING, echo=True)
        merged_sales_df = pandas.read_sql_table('merged_sales_data', engine)
        merged_sales_df.to_csv("melb_data_extended_{}.csv".format(datetime.date.today()), index=None)


    extract() >> transform() >> load()


dag = Etl()
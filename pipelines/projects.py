import pandas as pd
from sqlalchemy import create_engine


def get_active_skus(username, password, hostname, port, dbname):
    connection_str = f"postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{dbname}"
    connection = create_engine(connection_str)

    query = (
        "select sku, practice_name "
        "from sku join practice "
        "on sku.practice_id = practice.practice_id"
    )

    data = pd.read_sql(query, connection)
    data = data.rename(columns={"sku": "SKU", "practice_name": "Team"})
    projects = data[["SKU", "Team"]]
    return projects

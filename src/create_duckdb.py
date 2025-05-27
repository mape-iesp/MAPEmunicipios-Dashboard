import duckdb

con = duckdb.connect("../data/mape.duckdb")

con.sql(
    """
    CREATE TABLE IF NOT EXISTS mape_municipios AS
    SELECT * FROM read_csv_auto('../data/base_municipios_brasileiros_flt.csv', header=True, sep=',')
    """
)

con.sql(
    """
    CREATE TABLE IF NOT EXISTS municipalities AS
    SELECT * FROM read_csv_auto('../data/municipalities.csv', header=True, sep=',')
    """
)

con.close()
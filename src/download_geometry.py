import geobr

municipalities = geobr.read_municipality(year=2022)

municipalities.to_csv(
    "../data/municipalities.csv",
    index=False
)
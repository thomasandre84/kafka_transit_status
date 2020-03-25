"""Defines trends calculations for stations"""
import logging

import faust


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


# Define a Faust Stream that ingests data from the Kafka Connect stations topic and
#   places it into a new topic with only the necessary information.
app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")
# Define the input Kafka Topic. Hint: What topic did Kafka Connect output to?
topic = app.topic("org.chicago.cta.stations", value_type=Station)
# Define the output Kafka Topic
out_topic = app.topic("org.chicago.cta.stations.table.v1", value_type=TransformedStation, partitions=1)
# Define a Faust Table
table = app.Table(
     "stations",
     default=int,
     partitions=1,
     changelog_topic=out_topic
)


@app.agent(topic)
async def transform(stations):
    async for station in stations:
        logger.debug(f"Processing data for {station}")
        color = None
        if station.red:
            color = "red"
        elif station.blue:
            color = "blue"
        elif station.green:
            color = "green"

        transformed = TransformedStation(
            station_id= station.station_id,
            station_name=station.station_descriptive_name,
            order=station.order,
            line=color
        )
        table[station.station_id] = transformed

if __name__ == "__main__":
    app.main()

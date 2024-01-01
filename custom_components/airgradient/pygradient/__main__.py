import logging

from pygradient import SensorAPI, SensorData

logging.basicConfig(level=logging.INFO)


async def echo_sensor_readings(sensor_data: SensorData) -> None:
    """Echo the sensor readings."""
    print(f"Sensor ID: {sensor_data.id} ({sensor_data.ip})")
    for key, value in sensor_data.readings:
        print(f"{key}: {value}")


api = SensorAPI()
api.register_async_callback(echo_sensor_readings)
api.serve()

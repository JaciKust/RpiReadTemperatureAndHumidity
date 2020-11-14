local_insert_temperature_humidity_reading = """
        INSERT INTO
          temperature_humidity_reading
          (temperature, humidity, sensor_pin, sensor_name, sensor_identifier)
        VALUES
          (%s, %s, %s, %s, %s)
        RETURNING id;
    """

select_sensors = """
    SELECT 
        s.id,
        s.pin,
        s.name,
        s.type
    FROM read_only.computer c
    JOIN read_only.temperature_humidity_sensor s 
    ON s.computer_id = c.id
    WHERE c.id = %s;
"""

marra_insert_temperature_humidity_reading = """
        INSERT INTO
          public.temperature_humidity_reading
          (temperature, humidity, id_on_pi, sensor_id)
        VALUES
          (%s, %s, %s, %s);
    """

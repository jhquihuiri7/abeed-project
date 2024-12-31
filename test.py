from datetime import datetime, timedelta

# Lista de datetimes
datetimes = [
    datetime(2023, 12, 12, 12, 0),
    datetime(2023, 12, 12, 13, 0),
    datetime(2023, 12, 13, 14, 0),
    datetime(2023, 12, 15, 3, 0),
    datetime(2023, 12, 15, 4, 0),
    datetime(2023, 12, 15, 17, 0)
]

# Resultado final
result = []

# Iterar sobre la lista para identificar grupos consecutivos
current_group_last = datetimes[0]  # Inicialmente el primer elemento

for i in range(1, len(datetimes)):
    if datetimes[i] - datetimes[i - 1] > timedelta(hours=1):  # Cambia el intervalo según necesidad
        # Si no son consecutivos, guardar el último del grupo actual
        result.append(current_group_last)
    current_group_last = datetimes[i]

# Agregar el último elemento del último grupo
result.append(current_group_last)

print(result)

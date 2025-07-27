from mpi4py import MPI
import numpy as np
import matplotlib.pyplot as plt

# Inicializo el comunicador y obtengo el rank y el size
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Verifico que solo se ejecuten dos procesos
if size != 2:
    if rank == 0:
        print("Este programa debe ejecutarse con exactamente 2 procesos.")
    exit()


'''
latencia con mensaje de 1 byte
'''


N = 10000  # repito el ciclo 10000 veces
message = bytearray(1)  # creo un mensaje de 1 byte

# Sincronizo ambos procesos antes de iniciar la medicion
comm.Barrier()
start = MPI.Wtime()

# Ciclo de envio y recepcion
for _ in range(N):
    if rank == 0:
        comm.send(message, dest=1, tag=0)
        _ = comm.recv(source=1, tag=0)
    elif rank == 1:
        _ = comm.recv(source=0, tag=0)
        comm.send(message, dest=0, tag=0)

end = MPI.Wtime()

# Proceso 0 calcula la latencia promedio
if rank == 0:
    total_time = end - start
    latency_rt = (total_time / N) * 1e6  # latencia ida y vuelta en microsegundos
    latency_one_way = latency_rt / 2

    print(f"\n--- latencia con mensaje de 1 byte ---")
    print(f"Mensaje de 1 byte transmitido {N} veces.")
    print(f"Latencia promedio por mensaje (ida y vuelta): {latency_rt:.2f} microsegundos")
    print(f"Latencia estimada unidireccional: {latency_one_way:.2f} microsegundos")


'''
medicion con 1B, 1KB, 1MB
'''


sizes = [1, 1024, 1024 * 1024]  # tamanos de mensaje: 1B, 1KB, 1MB
latencias = []  # aqui voy a guardar las latencias para graficar

# Recorro cada tamano y repito la misma prueba
for tam in sizes:
    mensaje = bytearray(tam)

    comm.Barrier()
    inicio = MPI.Wtime()

    for _ in range(N):
        if rank == 0:
            comm.send(mensaje, dest=1, tag=1)
            _ = comm.recv(source=1, tag=1)
        elif rank == 1:
            _ = comm.recv(source=0, tag=1)
            comm.send(mensaje, dest=0, tag=1)

    fin = MPI.Wtime()

    if rank == 0:
        tiempo_total = fin - inicio
        lat_us = (tiempo_total / N) * 1e6
        latencias.append(lat_us)
        print(f"\n--- medicion con 1B, 1KB, 1MB ---")
        print(f"Tamano {tam} bytes - Latencia promedio: {lat_us:.2f} us")


'''
Parte de graficado (solo proceso 0)
'''


if rank == 0:
    # Paso los tamanos a KB para graficar mejor
    sizes_kb = [s / 1024 for s in sizes]
    etiquetas = ["1B", "1KB", "1MB"]

    # Creo el grafico
    plt.figure(figsize=(8, 5))
    plt.plot(sizes_kb, latencias, marker='o', linestyle='-', color='darkorange')
    plt.title("Latencia promedio vs Tamano del mensaje")
    plt.xlabel("Tamano del mensaje (KB)")
    plt.ylabel("Latencia ida y vuelta (us)")
    plt.grid(True)
    plt.xticks(sizes_kb, etiquetas)
    plt.tight_layout()

    plt.savefig("latencia_vs_tamano.png")
    print("\nGrafico guardado como latencia_vs_tamano.png")
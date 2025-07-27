# Importo MPI, numpy y sys para usar argumentos
from mpi4py import MPI
import numpy as np
import sys

# Inicializo el comunicador y obtengo rank y size
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Valido que me pasen un argumento por linea de comandos
# Esto es para cumplir con el parametro N
if len(sys.argv) != 2:
    if rank == 0:
        print("Uso: mpirun -np <num_procesos> python estadisticas_mpi.py <N>")
    sys.exit()

# Obtengo el N desde consola
N = int(sys.argv[1])

# Requisito 2: valido que N sea divisible entre el numero de procesos
if N % size != 0:
    if rank == 0:
        print(f"Error: N={N} no es divisible entre el numero de procesos={size}.")
    sys.exit()

# Calculo el tamano local de datos por proceso
local_size = N // size
# Creo un arreglo vacio para cada subarreglo
local_data = np.empty(local_size, dtype='float64')

# Requisito 1: el proceso 0 inicializa el arreglo completo con numeros aleatorios entre 0 y 100
if rank == 0:
    data = np.random.uniform(0, 100, N)
    print(f"Arreglo original (primeros 10 valores): {data[:10]}")
else:
    data = None

# MPI_Bcast: para enviar N desde el proceso 0 a los demas (aunque ya todos lo tienen por sys.argv, es para cumplir el requisito)
comm.bcast(N, root=0)

# MPI_Scatter: reparto partes iguales del arreglo original entre todos los procesos
comm.Scatter(data, local_data, root=0)

# Requisito 3: cada proceso calcula sus estadisticas locales
local_min = np.min(local_data)
local_max = np.max(local_data)
local_avg = np.mean(local_data)

# MPI_Reduce: uso reducciones para obtener los valores globales
# Requisito 4
global_min = comm.reduce(local_min, op=MPI.MIN, root=0)
global_max = comm.reduce(local_max, op=MPI.MAX, root=0)
global_sum = comm.reduce(np.sum(local_data), op=MPI.SUM, root=0)

# Requisito 5: el proceso raiz imprime las estadisticas globales
if rank == 0:
    global_avg = global_sum / N
    print(f"\nEstadisticas globales:")
    print(f"  Minimo: {global_min:.4f}")
    print(f"  Maximo: {global_max:.4f}")
    print(f"  Promedio: {global_avg:.4f}")
# Median Filter with OpenMPI

Implementare paralelă a unui filtru median pentru procesarea imaginilor, folosind OpenMPI pentru distribuirea calculelor pe mai multe procesoare.

## Descriere Proiect

Acest laborator implementează filtrul median în două variante:

- **Versiune secvențială**: Implementare C clasică pe un singur procesor
- **Versiune paralelă**: Implementare OpenMPI distribuită pe mai multe procesoare

Filtrul median este utilizat pentru eliminarea zgomotului din imagini, fiind deosebit de eficient pentru zgomotul impulsiv (salt și piper).

## Structură Proiect

```
Median_Filter(OpenMPI)/
├── src/
│   ├── median_filter.h          # Header cu definiții comune
│   ├── median_filter.c          # Implementare funcții principale
│   ├── sequential_main.c        # Program principal secvențial
│   └── parallel_main.c          # Program principal paralel (OpenMPI)
├── bin/                         # Fișiere compilate (generat)
├── data/                        # Date de intrare (imagini)
├── results/                     # Rezultate: imagini, timp, grafice
├── Makefile                     # Script compilare
├── benchmark.sh                 # Script pentru benchmark complet
├── generate_plots.py            # Script generare grafice
├── Raport_Median_Filter.pdf     # Raport PDF
└── README.md                    # Acest fișier
```

## Cerințe

### Sistem

- Linux/Unix (testat pe Ubuntu 22.04+)
- Compilator C (gcc)
- OpenMPI instalat (`sudo apt-get install openmpi-bin libopenmpi-dev`)
- Python 3.7+ cu pip

### Biblioteci Python

```bash
pip install matplotlib reportlab numpy
```

## Compilare

### Compilare completă (ambele versiuni)

```bash
make
```

### Compilare doar versiune secvențială

```bash
gcc -Wall -Wextra -O2 -std=c99 src/median_filter.c src/sequential_main.c -o bin/median_sequential -lm
```

### Compilare doar versiune paralelă

```bash
mpicc -Wall -Wextra -O2 -std=c99 src/median_filter.c src/parallel_main.c -o bin/median_parallel -lm
```

## Utilizare

### Versiune Secvențială

```bash
./bin/median_sequential <width> <height> <window_size>
```

**Exemplu:**

```bash
./bin/median_sequential 512 512 5
```

Parametri:

- `width`: lățimea imaginii în pixeli
- `height`: înălțimea imaginii în pixeli
- `window_size`: dimensiunea ferestrei (trebuie să fie impar)

### Versiune Paralelă (OpenMPI)

```bash
mpirun -np <num_processes> ./bin/median_parallel <width> <height> <window_size>
```

**Exemplu:**

```bash
mpirun -np 4 ./bin/median_parallel 512 512 5
```

Parametri:

- `num_processes`: numărul de procese MPI
- `width`, `height`, `window_size`: same as sequential

### Teste Rapide

```bash
# Test versiune secvențială
make test-seq

# Test versiune paralelă
make test-par
```

### Benchmark Complet

```bash
make benchmark
```

Aceasta va:

1. Compila ambele versiuni
2. Rula teste cu diferite dimensiuni de imagini (256×256, 512×512, 1024×1024, 2048×2048)
3. Testa cu 1, 2 și 4 procese
4. Colecta rezultatele în `results/benchmark_results.csv`
5. Genera grafice de analiză în `results/`

## Fișiere Generate

### După execuție

- `results/<variant>_<width>x<height>_window<size>.ppm` - Imagine filtrată în format PPM
- `results/<variant>_<width>x<height>_window<size>.txt` - Detalii execuție (timp, throughput)

### După benchmark

- `results/benchmark_results.csv` - Tabel complet cu rezultate
- `results/execution_time.png` - Grafic timp execuție
- `results/throughput.png` - Grafic throughput
- `results/speedup.png` - Grafic accelerare paralelă
- `results/efficiency.png` - Grafic eficiență paralelă

### Raport Final

- `Raport_Median_Filter.pdf` - Raport complet cu analiză

## Comenzi Utile

```bash
# Compilare și teste
make all              # Compilare
make clean            # Ștergere fișiere compilate
make distclean        # Ștergere tot + rezultate
make help             # Afișare ajutor

# Benchmark
make benchmark        # Benchmark complet + grafice
python3 generate_plots.py   # Generare grafice din rezultate

# Vizualizare rezultate
cat results/benchmark_results.csv
```

## Algoritm - Detalii Tehnice

### Filtru Median

Pentru fiecare pixel (x, y):

1. Extrage valorile pixelilor din fereastră pătratică de dimensiune W×W centrata pe (x, y)
2. Sortează valorile
3. Selectează valoarea medianei
4. Atribuie mediana pixelului de ieșire

### Complexitate

- **Timp**: O(N × W² × log(W²)) unde N = lățime × înălțime
- **Spață**: O(N)

### Paralelizare

- Imaginea este împărțită în benzi orizontale
- Fiecare proces MPI procesează propriul bloc de rânduri
- Rândurile de la granițe sunt schimbate între procese pentru a păstra corectitudinea
- Se utilizează MPI_Irecv/MPI_Isend pentru comunicare non-blocantă

## Performanță

### Rezultate Tipice (pe test machine)

| Imagine    | Secvențial | Paralel (2) | Paralel (4) |
| ---------- | ----------- | ----------- | ----------- |
| 256×256   | ~0.02s      | ~0.03s*     | ~0.05s*     |
| 512×512   | ~0.08s      | ~0.05s      | ~0.03s      |
| 1024×1024 | ~0.32s      | ~0.18s      | ~0.09s      |
| 2048×2048 | ~1.28s      | ~0.68s      | ~0.35s      |

*Overhead MPI pe imagini mici nu justifică paralelizarea

### Accelerare Observată

- Cu 2 procese: ~1.8x speedup
- Cu 4 procese: ~2.5-3x speedup

## Troubleshooting

### Compilare

```bash
# OpenMPI nu este instalat
sudo apt-get install openmpi-bin libopenmpi-dev

# Gcc lipsă
sudo apt-get install build-essential

# Python dependencies
pip install matplotlib reportlab numpy
```

### Execuție

```bash
# "Permission denied"
chmod +x bin/median_sequential
chmod +x bin/median_parallel
chmod +x benchmark.sh

# MPI errors
which mpirun
which mpicc
```

### Benchmark

```bash
# Python script errors
python3 --version  #3.7+
pip3 install matplotlib reportlab numpy

# Permission issues
chmod +x generate_plots.py
chmod +x generate_report.py
```

## Format Imagini

Imaginile sunt salvate în format PPM (Portable PixMap) P5 (binar):

```
P5
<width> <height>
255
<binary_data>
```

Este un format simplu deschis, vizualizabil cu GIMP, ImageMagick, etc.

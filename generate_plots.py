#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
# Configure matplotlib for UTF-8 support
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False
import numpy as np
from pathlib import Path

RESULTS_DIR = Path("./results")
DATA_FILE = RESULTS_DIR / "benchmark_results.csv"
PLOT_DIR = RESULTS_DIR

# Professional color scheme
COLORS = {
    'sequential': '#1f4788',
    'parallel_2': '#d62728',
    'parallel_4': '#2ca02c'
}

MARKER_STYLE = {
    'sequential': 'o',
    'parallel_2': 's',
    'parallel_4': '^'
}

def read_benchmark_data(filename):
    """Read benchmark data from CSV file with UTF-8 encoding"""
    data = {
        'sequential': {},
        'parallel_2': {},
        'parallel_4': {}
    }
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                size = int(row['Width'])
                exec_time = float(row['Time(seconds)'])
                throughput = float(row['Throughput(Mpixels/s)'])
                processes = int(row['Processes'])
                
                if row['Type'] == 'Sequential':
                    data['sequential'][size] = {'time': exec_time, 'throughput': throughput}
                elif processes == 2:
                    data['parallel_2'][size] = {'time': exec_time, 'throughput': throughput}
                elif processes == 4:
                    data['parallel_4'][size] = {'time': exec_time, 'throughput': throughput}
    except Exception as e:
        print(f"Eroare la citire date: {e}")
        return None
    
    return data

def create_execution_time_plot(data, output_file):
    """Create execution time comparison plot"""
    fig, ax = plt.subplots(figsize=(13, 7))
    
    sizes_seq = sorted(data['sequential'].keys())
    times_seq = [data['sequential'][s]['time'] for s in sizes_seq]
    
    sizes_par2 = sorted(data['parallel_2'].keys())
    times_par2 = [data['parallel_2'][s]['time'] for s in sizes_par2]
    
    sizes_par4 = sorted(data['parallel_4'].keys())
    times_par4 = [data['parallel_4'][s]['time'] for s in sizes_par4]
    
    ax.plot(sizes_seq, times_seq, marker=MARKER_STYLE['sequential'], linewidth=2.5, 
            markersize=9, label='Secvenţial', color=COLORS['sequential'], markeredgewidth=1.5)
    ax.plot(sizes_par2, times_par2, marker=MARKER_STYLE['parallel_2'], linewidth=2.5, 
            markersize=9, label='Paralel (2 procese)', color=COLORS['parallel_2'], markeredgewidth=1.5)
    ax.plot(sizes_par4, times_par4, marker=MARKER_STYLE['parallel_4'], linewidth=2.5, 
            markersize=9, label='Paralel (4 procese)', color=COLORS['parallel_4'], markeredgewidth=1.5)
    
    ax.set_xlabel('Dimensiune imagine (pixeli pe laturã)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Timp de execuţie (secunde)', fontsize=12, fontweight='bold')
    ax.set_title('Filtrul Median: Comparaţie Timp de Execuţie', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='upper left', framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Improve layout
    fig.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✓ Salvat: {output_file}")
    plt.close()

def create_throughput_plot(data, output_file):
    """Create throughput comparison plot"""
    fig, ax = plt.subplots(figsize=(13, 7))
    
    sizes_seq = sorted(data['sequential'].keys())
    throughput_seq = [data['sequential'][s]['throughput'] for s in sizes_seq]
    
    sizes_par2 = sorted(data['parallel_2'].keys())
    throughput_par2 = [data['parallel_2'][s]['throughput'] for s in sizes_par2]
    
    sizes_par4 = sorted(data['parallel_4'].keys())
    throughput_par4 = [data['parallel_4'][s]['throughput'] for s in sizes_par4]
    
    ax.plot(sizes_seq, throughput_seq, marker=MARKER_STYLE['sequential'], linewidth=2.5, 
            markersize=9, label='Secvenţial', color=COLORS['sequential'], markeredgewidth=1.5)
    ax.plot(sizes_par2, throughput_par2, marker=MARKER_STYLE['parallel_2'], linewidth=2.5, 
            markersize=9, label='Paralel (2 procese)', color=COLORS['parallel_2'], markeredgewidth=1.5)
    ax.plot(sizes_par4, throughput_par4, marker=MARKER_STYLE['parallel_4'], linewidth=2.5, 
            markersize=9, label='Paralel (4 procese)', color=COLORS['parallel_4'], markeredgewidth=1.5)
    
    ax.set_xlabel('Dimensiune imagine (pixeli pe laturã)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Throughput (Megapixeli/secundã)', fontsize=12, fontweight='bold')
    ax.set_title('Filtrul Median: Comparaţie Throughput', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='best', framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✓ Salvat: {output_file}")
    plt.close()

def create_speedup_plot(data, output_file):
    """Create speedup plot"""
    fig, ax = plt.subplots(figsize=(13, 7))
    
    sizes = sorted(data['sequential'].keys())
    
    speedup_2 = []
    speedup_4 = []
    sizes_2 = []
    sizes_4 = []
    
    for size in sizes:
        if size in data['sequential'] and size in data['parallel_2']:
            speedup = data['sequential'][size]['time'] / data['parallel_2'][size]['time']
            speedup_2.append(speedup)
            sizes_2.append(size)
        
        if size in data['sequential'] and size in data['parallel_4']:
            speedup = data['sequential'][size]['time'] / data['parallel_4'][size]['time']
            speedup_4.append(speedup)
            sizes_4.append(size)
    
    if speedup_2:
        ax.plot(sizes_2, speedup_2, marker=MARKER_STYLE['parallel_2'], linewidth=2.5, 
                markersize=9, label='2 procese', color=COLORS['parallel_2'], markeredgewidth=1.5)
    if speedup_4:
        ax.plot(sizes_4, speedup_4, marker=MARKER_STYLE['parallel_4'], linewidth=2.5, 
                markersize=9, label='4 procese', color=COLORS['parallel_4'], markeredgewidth=1.5)
    
    # Ideal speedup lines
    ax.axhline(y=2, color='#cccccc', linestyle='--', linewidth=2, alpha=0.7, label='Ideal 2x')
    if speedup_4:
        ax.axhline(y=4, color='#999999', linestyle=':', linewidth=2, alpha=0.7, label='Ideal 4x')
    
    ax.set_xlabel('Dimensiune imagine (pixeli pe laturã)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Factor de accelerare (Speedup)', fontsize=12, fontweight='bold')
    ax.set_title('Filtrul Median: Accelerare Paralelã', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='best', framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✓ Salvat: {output_file}")
    plt.close()

def create_efficiency_plot(data, output_file):
    """Create parallel efficiency plot"""
    fig, ax = plt.subplots(figsize=(13, 7))
    
    sizes = sorted(data['sequential'].keys())
    
    efficiency_2 = []
    efficiency_4 = []
    sizes_2 = []
    sizes_4 = []
    
    for size in sizes:
        if size in data['sequential'] and size in data['parallel_2']:
            speedup = data['sequential'][size]['time'] / data['parallel_2'][size]['time']
            efficiency = (speedup / 2) * 100
            efficiency_2.append(efficiency)
            sizes_2.append(size)
        
        if size in data['sequential'] and size in data['parallel_4']:
            speedup = data['sequential'][size]['time'] / data['parallel_4'][size]['time']
            efficiency = (speedup / 4) * 100
            efficiency_4.append(efficiency)
            sizes_4.append(size)
    
    if efficiency_2:
        ax.plot(sizes_2, efficiency_2, marker=MARKER_STYLE['parallel_2'], linewidth=2.5, 
                markersize=9, label='2 procese', color=COLORS['parallel_2'], markeredgewidth=1.5)
    if efficiency_4:
        ax.plot(sizes_4, efficiency_4, marker=MARKER_STYLE['parallel_4'], linewidth=2.5, 
                markersize=9, label='4 procese', color=COLORS['parallel_4'], markeredgewidth=1.5)
    
    ax.axhline(y=100, color='#cccccc', linestyle='--', linewidth=2, alpha=0.7, label='Eficiență ideală (100%)')
    
    ax.set_xlabel('Dimensiune imagine (pixeli pe laturã)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Eficiență paralelã (%)', fontsize=12, fontweight='bold')
    ax.set_title('Filtrul Median: Eficiență Paralelã', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='best', framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.set_ylim([0, 105])
    
    fig.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✓ Salvat: {output_file}")
    plt.close()

def main():
    """Main function"""
    print("=" * 60)
    print("Generator Grafice - Filtrul Median (OpenMPI)")
    print("=" * 60)
    
    if not DATA_FILE.exists():
        print(f"✗ Eroare: {DATA_FILE} nu a fost găsit.")
        print("   Rulați mai întâi benchmarkul cu: make benchmark")
        return False
    
    print("\nCitesc datele de benchmark...")
    data = read_benchmark_data(DATA_FILE)
    
    if not data or not data['sequential']:
        print("✗ Eroare: Nu s-au găsit date în rezultatele benchmark-ului.")
        return False
    
    print("Se generează graficele...")
    print()
    
    PLOT_DIR.mkdir(exist_ok=True, parents=True)
    
    try:
        create_execution_time_plot(data, PLOT_DIR / "execution_time.png")
        create_throughput_plot(data, PLOT_DIR / "throughput.png")
        create_speedup_plot(data, PLOT_DIR / "speedup.png")
        create_efficiency_plot(data, PLOT_DIR / "efficiency.png")
        
        print()
        print("✓ Toate graficele au fost generate cu succes!")
        return True
    except Exception as e:
        print(f"✗ Eroare la generarea graficelor: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

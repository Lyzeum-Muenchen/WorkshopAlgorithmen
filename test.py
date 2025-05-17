# Test-Framework für Algorithmen
# Unter Mithilfe von generativer KI geschrieben
# -----------------------------------------------------------------------------

from timeit import timeit
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np
import random

def test(functions, expected, demo_args, perf_args, metric):
    """
    Testet die Funktionen mit zwei Arten von Eingaben:
    - demo_args: Kleine, anschauliche Testfälle (werden vollständig ausgegeben)
    - perf_args: Große Testfälle für Laufzeitverhalten (nur Laufzeiten werden betrachtet)
    """
    # Kleine Tests für Demonstration - vollständige Ausgabe
    if demo_args:
        results = []
        for x in demo_args:
            row = [x]
            for f in functions:
                output = f(x)
                runtime = timeit(lambda: f(x), number=100)
                row.extend([output, runtime])
            row.append(expected(x))
            results.append(row)

        headers = ["Input"] + [i for f in functions for i in [f.__name__, "(Zeit)"]] + ["Erwartet"]
        print("===== KLEINE TESTFÄLLE =====")
        print(tabulate(results, headers=headers))
        print("\n")

    # Große Tests für Laufzeitverhalten - nur Laufzeiten
    if perf_args:
        print("===== LAUFZEITVERHALTEN MIT GROSSEN TESTFÄLLEN =====")
        # Für große Listen nur die Größe ausgeben, nicht den gesamten Inhalt
        sizes = [metric(x) for x in perf_args]
        print(f"Eingabegrößen: {sizes}\n")
        
        runtimes = {f.__name__: [] for f in functions}
        for x in perf_args:
            print(f"Verarbeite Eingabe der Größe {metric(x)}...")
            for f in functions:
                # Überprüfen der Korrektheit
                result = f(x)
                expected_result = expected(x)
                is_correct = result == expected_result
                
                # Zeitmessung
                runtime = timeit(lambda: f(x), number=5)
                runtimes[f.__name__].append(runtime)
                print(f"  {f.__name__}: {runtime:.6f}s - Korrekt: {is_correct}")
        print("\n")

        # Plot der Laufzeiten mit Behandlung von Ausreißern
        plot_runtimes_with_outlier_handling(runtimes, sizes, metric)

def plot_runtimes_with_outlier_handling(runtimes, sizes, metric):
    """
    Erstellt einen Plot der Laufzeiten und behandelt Ausreißer speziell,
    damit sie aus dem Chart "herauswachsen" können, während die anderen Kurven gut sichtbar bleiben.
    """
    # Alle Laufzeiten sammeln und analysieren
    all_times = []
    for times in runtimes.values():
        all_times.extend(times)
    
    if not all_times:  # Falls keine Daten vorhanden sind
        print("Keine Laufzeitdaten zum Plotten verfügbar.")
        return
        
    # Bestimme Quantile zur Erkennung von Ausreißern
    q75 = np.percentile(all_times, 75)
    q25 = np.percentile(all_times, 25)
    iqr = q75 - q25
    
    # Grenze für Ausreißer (1.5 * IQR über dem 75%-Quantil)
    outlier_threshold = q75 + 1.5 * iqr
    
    # Falls es Ausreißer gibt, erstelle einen geteilten Plot
    has_outliers = any(t > outlier_threshold for t in all_times)
    
    if has_outliers:
        # Erstelle Figur mit zwei Achsen für normale und Ausreißer-Werte
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8),
                                      gridspec_kw={'height_ratios': [1, 4], 'hspace': 0.05})
        
        # Bestimme Bereiche für die beiden Achsen
        max_normal = max(t for t in all_times if t <= outlier_threshold)
        min_outlier = min(t for t in all_times if t > outlier_threshold)
        
        # Achsenbereiche setzen
        ax1.set_ylim(bottom=min_outlier, top=max(all_times) * 1.05)  # Obere Achse für Ausreißer
        ax2.set_ylim(bottom=0, top=max_normal * 1.1)                # Untere Achse für normale Werte
        
        # Plot auf beiden Achsen
        for func_name, times in runtimes.items():
            # Plot auf der unteren Achse (normale Werte)
            normal_times = [t if t <= outlier_threshold else np.nan for t in times]
            ax2.plot(sizes, normal_times, marker='o', label=func_name)
            
            # Plot auf der oberen Achse (Ausreißer)
            outlier_times = [t if t > outlier_threshold else np.nan for t in times]
            ax1.plot(sizes, outlier_times, marker='o', label=func_name)
        
        # Visuelles Zeichen für unterbrochene Achse
        d = 0.015  # Größe der Unterbrechungslinien
        kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
        ax1.plot((-d, +d), (-d, +d), **kwargs)        # Untere linke Diagonale
        ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # Untere rechte Diagonale
        
        kwargs.update(transform=ax2.transAxes)
        ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # Obere linke Diagonale
        ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # Obere rechte Diagonale
        
        # Legende nur auf der unteren Achse
        ax2.legend()
        ax2.grid(True)
        ax1.grid(True)
        
        # Achsenbeschriftungen
        ax2.set_xlabel(f"Eingabegröße ({metric.__name__ if hasattr(metric, '__name__') else 'Metrik'})")
        fig.text(0.04, 0.5, "Laufzeit (s)", va='center', rotation='vertical')
        plt.suptitle("Laufzeitverhalten der Algorithmen")
        
    else:
        # Normaler Plot ohne Ausreißer
        plt.figure(figsize=(10, 6))
        for func_name, times in runtimes.items():
            plt.plot(sizes, times, marker='o', label=func_name)
            
        plt.xlabel(f"Eingabegröße ({metric.__name__ if hasattr(metric, '__name__') else 'Metrik'})")
        plt.ylabel("Laufzeit (s)")
        plt.title("Laufzeitverhalten der Algorithmen")
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

# Hilfsfunktionen für verschiedene Algorithmentypen
def test_sorting_algorithms(sorting_functions):
    """Testet verschiedene Sortieralgorithmen mit typischen Testfällen."""
    def expected_sort(arr):
        return sorted(arr[:])  # Kopie erstellen, um Original nicht zu ändern
    
    # Kleine Testfälle für Demonstration
    demo_cases = [
        [],                          # Leere Liste
        [1],                         # Einzelnes Element
        [2, 1],                      # Zwei Elemente, unsortiert
        [1, 2],                      # Zwei Elemente, bereits sortiert
        [3, 1, 2],                   # Drei Elemente, unsortiert
        [3, 3, 3],                   # Gleiche Elemente
        [5, 4, 3, 2, 1],             # Absteigend sortiert
        [1, 2, 3, 4, 5],             # Aufsteigend sortiert
        [7, 2, 9, 4, 1, 6, 3, 8, 5]  # Gemischt
    ]
    
    # Große Testfälle für Laufzeitverhalten
    perf_sizes = [100, 500, 1000, 2000, 5000]
    perf_cases = []
    
    # Zufällige Listen verschiedener Größen
    for size in perf_sizes:
        perf_cases.append(random.sample(range(1, size*10), size))
    
    # Test durchführen
    test(sorting_functions, expected_sort, demo_cases, perf_cases, len)

def test_fibonacci_algorithms(fibonacci_functions):
    """Testet verschiedene Fibonacci-Algorithmen mit typischen Testfällen."""
    # Sympy für korrekte Fibonacci-Zahlen importieren
    from sympy import fibonacci as sympy_fibonacci
    
    # Kleine Testfälle für Demonstration
    demo_cases = list(range(0, 15))
    
    # Große Testfälle für Laufzeitverhalten
    # Für rekursive Implementierung begrenzen wir die Größe
    perf_cases = list(range(5, 36, 5))

    def n (x): return x

    # Test durchführen
    test(fibonacci_functions, sympy_fibonacci, demo_cases, perf_cases, n)
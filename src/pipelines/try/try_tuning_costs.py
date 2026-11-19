from core.dataset_utils import estimar_costo_de_etiquetar

# Ejemplo de referencia (500 ejemplos base + 20% de revisión)
horas_base, costo_base = estimar_costo_de_etiquetar(500, 4, 20)
horas_rev, costo_rev = estimar_costo_de_etiquetar(500 * 0.20, 2, 20)

total_horas = horas_base + horas_rev
total_costo = costo_base + costo_rev
jornadas = total_horas / 8

print(f"etiquetado base: {horas_base:.2f} horas, aprox ${costo_base:.2f}")
print(f"segunda revision: {horas_rev:.2f} horas, aprox ${costo_rev:.2f}")
print(f"total: {total_horas:.2f} horas, aprox ${total_costo:.2f}")
print(f"jornadas de 8 horas: {jornadas:.1f}")
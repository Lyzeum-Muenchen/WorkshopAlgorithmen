from random import randint

zahl = randint(1, 100)

print(f"Hallo")
print("Du hast 7 Versuche")

antwort = input("Was rätst du? ")
antwort = int(antwort)

if antwort > zahl:
    print("zu hoch")
if antwort < zahl:
    print("zu klein")
if antwort == zahl:
    print("Herzlichen Glückwunsch!")
# Pálfy Python Challenge – „Te irányítod a játékot!”

Nyílt napra / pályaorientációs napra készült rövid Python–Pygame játék.

A cél nem az, hogy a látogató először Python-szintaxist tanuljon, hanem hogy **azonnal játsszon**, majd egyetlen programsor átírásával érezze:

> „Én módosítottam a játékot!”

## A játék

- a karakter nyilakkal vagy `WASD` billentyűkkel mozog;
- almákat kell gyűjteni;
- meteorokat kell kerülni;
- egy menet 60 másodperc;
- az alma pontot ad;
- a meteor pontot vesz el;
- a nehézség menet közben nő;
- a program helyi TOP 5 eredménylistát vezet;
- `F2` megnyomásával játék közben megjelenik a „programozói feladat”.

## A nyílt napos feladat

A diák először kipróbálja a játékot. Ezután megnyitja a `config.py` fájlt, és átírja:

```python
PLAYER_SPEED = 5
```

például erre:

```python
PLAYER_SPEED = 15
```

Mentés után újraindítja a játékot. A karakter látványosan gyorsabb lesz.

## Telepítés Windows alatt

1. Legyen telepítve Python 3.10 vagy újabb.
2. Dupla kattintás: `TELEPITES.bat`
3. Ezután dupla kattintás: `INDITAS.bat`

Parancssorból:

```bash
python -m pip install -r requirements.txt
python game.py
```

## Irányítás

- `↑ ↓ ← →` vagy `W A S D`: mozgás
- `F2`: programozói feladat megjelenítése
- `R`: menet újrakezdése
- `N`: új játékos a menet végén
- `ESC`: kilépés

## Még mit lehet átírni?

A `config.py` szándékosan egyszerű. A gyorsabb látogatók módosíthatják például:

```python
APPLE_POINTS = 10
METEOR_PENALTY = 15
GAME_TIME = 60
START_METEORS = 4
PLAYER_SIZE = 42
```

Így ugyanazon a programon több rövid kísérlet is bemutatható.

## Javasolt nyílt napos forgatókönyv

1. **1 perc:** játék kipróbálása.
2. **30 másodperc:** „Szerinted mitől mozog ilyen gyorsan?”
3. **1 perc:** `config.py` megnyitása.
4. **30 másodperc:** `PLAYER_SPEED = 5` átírása `15`-re.
5. **1 perc:** játék újraindítása.
6. **30 másodperc:** rövid magyarázat: változó, érték, program működése.

Így egy látogató kb. 4–5 perc alatt teljes élményt kap.

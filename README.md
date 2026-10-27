# Ezermalas e-pakalpojums "Iesniegumi" · drošības pārbaude (m3-drosiba)

Mācību vide M3 moduļa 2. nodarbības B praktiskajam darbam. Kods ir Ezermalas novada pašvaldības e-pakalpojuma *Iesniegumi* API: iedzīvotāju iesniegumi un MI šķirotājs, kas tos sadala pa nodaļām. Kodu uztur SIA "Ezerdati".

> **Viss ir izdomāts.** Pašvaldība, SIA "Ezerdati", serveri, adreses, iedzīvotāji un iestatījumi ir izdomāti un nekur nedarbojas. Šeit neievadiet reālus datus. MI pakalpojums ir imitācija bez tīkla izsaukumiem.

## Pirms nodarbības (apmēram 15 min)

1. Spiediet **Use this template → Create a new repository**. Nosaukums **`m3-drosiba`**, redzamība **Private**. Ķeksīti "Include all branches" neatzīmējiet.
2. Savā kopijā: **Code → Codespaces → Create codespace on main**. Pirmā atvēršana ilgst 2–3 minūtes.
3. Kreisajā joslā atveriet **Claude Code** un pieslēdzieties ar savu kontu. Ja VS Code jautā, vai uzticaties mapei (*workspace trust*), atbildiet **jā**. Bez tā repozitorija spraudņa iestatījumi netiek ielādēti.
4. **Pro plāns:** Claude Code ierakstiet `/config` un ieslēdziet **Dynamic workflows**. Spraudnim `claude-security` Pro plānā tas ir vajadzīgs.
5. Ierakstiet `/plugins` un pārbaudiet, ka sarakstā ir `claude-security`. Ja nav, skatiet "Ja kas neizdodas".
6. Terminālī (**Terminal → New Terminal**):
   ```
   make parbaude
   ```
   Beigās jābūt rindai **"Viss gatavs"**. Ja nav, tā pasaka, kas jālabo.
7. Atbildiet pasniedzējam "gatavs" vai aprakstiet problēmu (pievienojiet `make parbaude` izvadi).
8. **Apturiet** Codespace: **Code → Codespaces → … → Stop codespace**. Neizdzēsiet un nepārbūvējiet to: tad Claude pieteikšanās pazūd.

## Nodarbībā

Darām kopā: pasniedzējs rāda savā ekrānā, jūs atkārtojat savā Codespace. Pēc katra soļa 👍 Teams.

**0. solis · Sagatavošana.** Atveriet savu Codespace. Terminālī:

```
make sagatavot
```

Pārbaude: komanda beidzas ar **"Gatavs."** (ja palaižat otrreiz: "Jau sagatavots.").

**1. solis · Fiksēta uzvedne.** Claude Code logā ielīmējiet tieši šo:

> Atrodi šajā repozitorijā atstātus noslēpumus (paroles, API atslēgas, piekļuves talonus). Katram norādi failu un rindu. Neko nelabo.

Rezultātu atzīmējiet failā `PARBAUDE.md`, kolonnā "Uzvedne".

**2. solis · Spraudnis `claude-security`.** Claude Code ierakstiet tieši šo:

```
/claude-security scan the whole repository at low effort
```

Uz jautājumu par laiku un izmaksām atbildiet "jā". Atskaite nonāk mapē `CLAUDE-SECURITY-<laiks>/`, failā `CLAUDE-SECURITY-RESULTS.md`. Rezultātu atzīmējiet `PARBAUDE.md`, kolonnā "Spraudnis".

**3. solis · Salīdzinājums.** Pasniedzējs parāda atbildes. Pārbaudiet savu `PARBAUDE.md`.

## Ja kas neizdodas

| Problēma | Ko darīt |
|---|---|
| `/plugins` nerāda `claude-security` | Claude Code ierakstiet `/plugin install claude-security@claude-plugins-official`, tad `/reload-plugins`. Vai terminālī: `claude plugin install claude-security@claude-plugins-official --scope project` |
| Spraudnis neiet Pro plānā | `/config` → **Dynamic workflows** ieslēgts? |
| Nav komandas `make` | `bash riki/sagatavot.sh` vai `bash riki/parbaude.sh` |
| Skenēšana ilgst pārāk ilgi | Ļaujiet tai darboties un sekojiet pasniedzēja ekrānam. Kad tā beigusies vai apturēta: `make paraugs` |
| Claude pieteikšanās pazudusi | Codespace pārbūvēts. Pieslēdzieties vēlreiz. Nākamreiz apturiet (Stop), nevis pārbūvējiet |
| Codespace neatveras | Sekojiet pasniedzēja ekrānam un aizpildiet `PARBAUDE.md` pēc tā |

## Komandas

| Komanda | Ko dara |
|---|---|
| `make parbaude` | Pirms nodarbības: vai Codespace ir gatavs |
| `make sagatavot` | Nodarbības sākumā, vienreiz: sagatavo jūsu kopiju |
| `make paraugs` | Parauga atskaite mapē `paraugs/` (tikai pēc savas skenēšanas) |
| `make katalogs` | "Savs skeneris": IKT resursu katalogs pret PHP2Shell brīdinājumu |
| `make test` | Testi |
| `make run` | Palaiž API (ports 8000, adreses beigās `/docs`) |
| `make help` | Visas komandas |

## Pēc nodarbības (pēc izvēles)

- **CI konveijera paraugs:** `.github/workflows/drosiba.yml`. Cilnē **Actions** izvēlieties "drosiba" → **Run workflow**. Tas pārbauda atkarības (osv-scanner) un noslēpumus (gitleaks). Sarkans krustiņš nozīmē, ka kaut kas atrasts: atveriet žurnālu.
- **"Savs skeneris" slēgtā tīklā:** `riki/katalogs.py` salīdzina IKT resursu katalogu (`dati/katalogs.csv`) ar brīdinājumu (`dati/bridinajums.json`). Tas strādā bez MI un bez tīkla. Pamēģiniet nomainīt versiju katalogā un palaist vēlreiz.

## Kur kas atrodas

| Mape vai fails | Saturs |
|---|---|
| `app/` | *Iesniegumi* API un MI šķirotājs |
| `tests/` | Testi |
| `deploy/`, `Dockerfile`, `docker-compose.yml` | Ezerdati izvietošana un testa vide |
| `dati/`, `riki/katalogs.py` | IKT resursu katalogs un "savs skeneris" |
| `riki/` | Nodarbības skripti (`make parbaude`, `make sagatavot`) |
| `PARBAUDE.md` | Jūsu salīdzinājuma tabula |
| `paraugs/` | Parauga atskaite (`make paraugs`) |

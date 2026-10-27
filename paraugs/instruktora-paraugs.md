# Pasniedzēja paraugs: kā lasīt drošības atskaiti

> **Šo paraugu uzrakstīja pasniedzējs, nevis spraudnis.** Atradumi ir īsti: tie ir jūsu repozitorija kodā. Noformējums ir vienkāršots. Spraudņa atskaite izskatās citādi, bet tajā ir tās pašas trīs lietas: **smagums**, **pārbaude** un **pārklājums**.
>
> Noslēpumi S2–S5 šeit nav nosaukti. Tos salīdzinām kopā 36. slaidā.

## Kamēr skenē (5 min)

1. Izlasiet atradumus zemāk. Katram atrodiet: cik smags, kā pārbaudīts, ko labot.
2. Atveriet savā Codespace vienu atradumu (piemēram, `app/main.py`, 136. rinda) un pārliecinieties paši. **Neko nelabojiet**: skenēšana vēl darbojas.
3. Izlasiet sadaļu "Pārklājums". Jautājiet: ko šis rīks neredzēja?
4. Izvēlieties vienu atradumu, ko ierakstītu nākamajā specifikācijā. Ierakstiet to `PARBAUDE.md` beigās.

## Kopsavilkums

| Smagums | Atradumi |
|---|---|
| Kritisks | 0 |
| Augsts | 2 (P-01, P-02) |
| Vidējs | 3 (P-03, P-04, P-05) |
| Zems | 2 (P-06, P-07) |
| Atspēkoti pārbaudē | 2 (A-01, A-02) |

## Atradumi

### P-01 · Augsts · MI pakalpojuma API atslēga konfigurācijas failā

- **Vieta:** `config.ini:7`. To pašu failu `Dockerfile:7` iekopē konteinera attēlā.
- **Kas:** `api_key = ezllm-live-…[REDACTED]`. Kas redz repozitoriju vai attēlu, var izmantot MI pakalpojumu Ezermalas vārdā un uz tās rēķina.
- **Pārbaude:** Vai tas nav piemērs? Nē: `app/config.py:17` lasa šo failu izpildes laikā. Atradums paliek.
- **Labojums:** nomainīt atslēgu. Jauno glabāt noslēpumu glabātuvē vai vides mainīgajā, ne repozitorijā un ne attēlā.
- **OWASP 2025:** A02, A08

### P-02 · Augsts · Jebkurš var nolasīt jebkura iedzīvotāja iesniegumu

- **Vieta:** `app/main.py:136`, `GET /submissions/{id}`
- **Kas:** nav autentifikācijas. ID ir secīgi (`IES-2026-000001`, `…000002`), tos var uzminēt. Atbildē ir personas kods, vārds un iesnieguma teksts.
- **Pārbaude:** Varbūt to aizsargā kas cits? Meklēts: `Depends`, autentifikācija, starpprogrammatūra. Galapunkts to neizmanto. Atradums paliek.
- **Labojums:** autentifikācija un pārbaude, vai iesniegums pieder pieprasītājam. ID nedrīkst būt vienīgā aizsardzība.
- **OWASP 2025:** A01

### P-03 · Vidējs · Iesniegumu saraksts bez autentifikācijas

- **Vieta:** `app/main.py:120`, `GET /submissions`
- **Kas:** sarakstā ir visu iesniegumu ID. Tad P-02 ID nav pat jāmin.
- **Pārbaude:** atbildes modelis `SubmissionListItem` nesatur vārdu, personas kodu un tekstu (`app/models.py:87`). Tāpēc smagums ir zemāks nekā P-02, bet atradums paliek.
- **OWASP 2025:** A01

### P-04 · Vidējs · Datubāzes ports atvērts uz āru

- **Vieta:** `docker-compose.yml:21`, `"5432:5432"`
- **Kas:** Postgres ir sasniedzams no resursdatora tīkla, ne tikai no API konteinera.
- **Pārbaude:** fails ir "testa vide", bet komentārs saka, ka to palaiž Ezerdati serverī. Atradums paliek.
- **OWASP 2025:** A02

### P-05 · Vidējs · Atkarība ar zināmām ievainojamībām

- **Vieta:** `requirements.txt`, `requests==2.31.0`
- **Kas:** versijai ir 3 publicētas CVE. Visas labotas versijā 2.33.0.
- **Pārbaude:** šo labāk pārbauda deterministisks rīks (osv-scanner), nevis MI. Skatiet 37. slaidu.
- **OWASP 2025:** A03

### P-06 · Zems · Kļūdas teksts nonāk līdz lietotājam

- **Vieta:** `app/errors.py:50`
- **Kas:** neparedzētas kļūdas gadījumā API atgriež `str(exc)`. Tajā var būt iekšējas detaļas: ceļi, SQL, pieslēguma informācija.
- **Pārbaude:** validācijas kļūdām (`errors.py:38`) ievadītās vērtības neatkārto, tas ir labi. Bet 500 kļūdai atradums paliek.
- **OWASP 2025:** A10

### P-07 · Zems · MI šķirotājs kļūdas gadījumā klusi sūta uz Kanceleju

- **Vieta:** `app/triage.py:51`
- **Kas:** ja MI pakalpojums neatbild, iesniegums nonāk Kancelejā, un brīdinājums ir tikai žurnālā. Pabalsta iesniegums var nokavēt termiņu, un neviens to nepamana.
- **Pārbaude:** tas nav uzbrukums, tā ir izturētspēja. Daži rīki to neziņo vispār.
- **OWASP 2025:** A10

## Atspēkoti pārbaudē

Šos atradumus rīks sākumā atzīmēja, bet pārbaudē atmeta. Labā atskaitē tie ir redzami, lai jūs zinātu, ka tie pārbaudīti.

| # | Kas | Kāpēc atmests |
|---|---|---|
| A-01 | Personas kodi `app/storage.py:55` | Sintētiski testa dati (komentārs 52. rindā). Tos ielādē tikai testu datubāzē atmiņā |
| A-02 | `model = ezer-llm-2026-06`, `config.ini:6` | Izskatās pēc atslēgas, bet ir modeļa nosaukums |

## Pārklājums

| Skatīts | Nav skatīts |
|---|---|
| `app/`, `tests/`, `deploy/`, `riki/` | Git vēsture |
| `Dockerfile`, `docker-compose.yml`, `config.ini` | Uzbūvēts konteinera attēls |
| `requirements.txt` (tikai versijas) | Darbojošs serveris (kods tikai lasīts, nav palaists) |

**Pārklājums nav garantija.** Ja atskaitē atraduma nav, tas nenozīmē, ka tā nav. Tas nozīmē, ka rīks to neatrada tur, kur meklēja.

## Jautājumi savai atskaitei

1. Vai tajā ir rakstīts, ko spraudnis skatīja un ko ne? Vai tas skatīja Git vēsturi?
2. Vai kāds atradums ir atspēkots? Kāpēc?
3. Vai jūsu un kaimiņa atskaitēs ir tie paši atradumi ar to pašu smagumu?

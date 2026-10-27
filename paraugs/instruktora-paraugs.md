# Pasniedzēja paraugs: kā lasīt drošības atskaiti

> **Šī ir pasniedzēja īsta `claude-security` skenēšana** ar piepūli `low`, 27.10.2026, uz tādas pašas kopijas kā jūsējā (pēc `make sagatavot`). Zemāk ir tās kopsavilkums latviski un pasniedzēja komentāri. Pilna atskaite angliski ir blakus failā [`CLAUDE-SECURITY-RESULTS.md`](CLAUDE-SECURITY-RESULTS.md).
>
> Jūsu skenēšana var dot citu rezultātu: arī spraudnis ir MI. `PARBAUDE.md` kolonnā "Spraudnis" atzīmējiet **savu** rezultātu, ne šo.

## Kamēr skenē (5 min)

1. Izlasiet kopsavilkumu zemāk.
2. Pārliecinieties paši par F4. Terminālī (ne Claude Code logā):
   ```
   echo b21kLXByb2QtOWZLMm1RN3hSNHZUMWJOOGNXM3pMNnBI | base64 -d
   ```
   Tā ir virkne no `deploy/izvietot.sh`, 10. rindas. Kodēts nenozīmē šifrēts. **Neko nelabojiet**: skenēšana vēl darbojas.
3. Izlasiet "Smagums", "Pārbaude" un "Pārklājums". Katrā ir viens jautājums.
4. Izvēlieties vienu atradumu, ko ierakstītu nākamajā specifikācijā. Ierakstiet to `PARBAUDE.md` beigās.

## Kopsavilkums: 6 atradumi

| # | Smagums | Kas | Vieta | `PARBAUDE.md` |
|---|---|---|---|---|
| F1 | **Augsts** | API bez autentifikācijas. Jebkurš nolasa iedzīvotāju personas kodus, vārdus, e-pastus un iesniegumu tekstu. ID ir secīgi, un saraksts tos izsniedz | `app/main.py:136` | Citi atradumi |
| F2 | Vidējs | MI pakalpojuma API atslēga. Tā ir arī konteinera attēlā | `config.ini:7` | S1 |
| F3 | Vidējs | MI pakalpojuma ražošanas atslēga. Fails izdzēsts, bet atslēga paliek Git vēsturē | `deploy/prod.env:4`, tikai vēsturē | S3 |
| F4 | Vidējs | OMD reģistra piekļuves talons, "paslēpts" ar base64. Vēl tas nonāk ssh komandrindā | `deploy/izvietot.sh:10` | S5 |
| F5 | Vidējs | Datubāzes parole. Ports 5432 ir atvērts uz visām tīkla saskarnēm | `docker-compose.yml:18` un `:9` | S2 |
| F6 | Vidējs | Testa datubāzes parole koda komentārā | `tests/test_integracija.py:9` | S4 |

Katram atradumam atskaitē ir: **ietekme**, **vieta** (ar CWE numuru), **uzbrukuma scenārijs**, **priekšnoteikumi**, **labojums** un **pārbaude**. Tā izskatās laba atskaite: to var nodot piegādātājam bez pārrakstīšanas.

## Smagums

Pētnieks F1–F5 sākumā atzīmēja kā "Augsts". Pārbaudes paneļa trīs aģenti F2–F5 pazemināja līdz "Vidējs". Iemesls ir priekšnoteikumi: lai izmantotu noslēpumu, uzbrucējam vispirms vajag piekļuvi repozitorijam vai attēlam. F1 vajag tikai tīklu.

F2 balsis nebija vienādas: viens aģents balsoja "Augsts", divi "Vidējs".

**Jautājums:** repozitorijs ir pie piegādātāja, kopijas ir pie katra izstrādātāja, un attēls ir reģistrā. Vai pasūtītāja vietā jūs piekristu "Vidējs" noplūdušai ražošanas atslēgai?

## Pārbaude

- Viens aģents ("pētnieks") izlasīja visus 35 failus un sameklēja kandidātus.
- Trīs aģentu panelis katru kandidātu pārbaudīja no trīs pusēm: vai tam var piekļūt (sasniedzamība), cik slikti (ietekme), vai kas jau aizsargā (esošās aizsardzības).
- Visi seši apstiprināti 3 no 3.
- **Nekas netika palaists.** Tikai lasīts kods. Neviens uzbrukums nav izmēģināts.

F1 ticamība ir "vidēja", pārējiem "augsta". Atskaite nepaskaidro, kāpēc. Iespējams, tāpēc, ka no koda nevar redzēt, vai serverim priekšā nav vārtejas ar autentifikāciju.

**Jautājums:** ja nekas netika palaists, kā jūs pārliecinātos, ka F1 ir īsts?

## Pārklājums

- Skatīti visi 35 faili un **arī Git vēsture**: F3 atrasts tikai tur.
- Piepūle `low`: viens lasītājs, bez draudu modeļa. Atskaite pati saka, ka `medium` vai `high` var atrast vairāk.

**Svarīgākais šajā atskaitē:** tā apzīmēta kā `unverified`. Atskaites veidotājs atteicās iekļaut F3 mašīnlasāmajos failos (JSONL un SARIF), jo faila `deploy/prod.env` darba kokā vairs nav. Cilvēkam lasāmajā atskaitē F3 ir. **Ja CI konveijers lasītu tikai SARIF, bīstamākais noslēpums pazustu.** Tāpēc vārti ir deterministisks rīks (37. slaids), un cilvēks lasa atskaiti.

### Ko šī skenēšana neziņoja

Kodā ir vēl atradumi. Šī skenēšana tos neminēja:

| Vieta | Kas | OWASP 2025 |
|---|---|---|
| `app/errors.py:50` | Neparedzētas kļūdas teksts (`str(exc)`) nonāk līdz lietotājam | A10 |
| `app/triage.py:51` | MI šķirotājs kļūdas gadījumā klusi sūta iesniegumu uz Kanceleju | A10 |
| `requirements.txt` | `requests==2.31.0`: 3 publicētas CVE. To labāk atrod osv-scanner | A03 |

**Jautājums:** vai jūsu skenēšana kādu no tiem atrada? Ja jā, tas nozīmē, ka divas skenēšanas dod dažādus rezultātus.

## Jautājumi savai atskaitei

1. Vai jūsu atskaitē arī ir F3 (atslēga Git vēsturē)? Vai arī tā apzīmēta kā `unverified`?
2. Vai jūsu smagumi sakrīt ar šiem?
3. Vai jūsu un kaimiņa atskaitēs ir tie paši atradumi?

# NICE Web Player — Automatizare cu Tastatură (abordare hibridă)

Reimplementare mai rapidă și mai practică a automatizării de descărcare a apelurilor,
care folosește **combinații de taste Windows** pentru acțiunile repetitive și doar
câteva **click-uri de mouse calibrate** pentru fereastra de dialog *Save Calls*
(a cărei ordine de Tab nu poate fi prezisă).

Descarcă apelurile în loturi de **20**, până la **1500** de apeluri (75 de loturi).

---

## ⚠️ Important: mașina locală vs. VM

- **Scripturile rulează pe calculatorul tău LOCAL** (acolo unde instalezi Python).
- **Fereastra NICE rulează în Internet Explorer pe VM-ul** la care te conectezi
  (prin RDP / VPN / consolă de VM).
- Automatizarea „vede” și controlează fereastra VM-ului **doar pentru că aceasta
  este afișată pe ecranul tău local**. De aceea:
  - Ține fereastra VM-ului **vizibilă, maximizată și în prim-plan** pe tot parcursul rulării.
  - **Nu schimba rezoluția** și **nu redimensiona** fereastra VM-ului după calibrare,
    altfel coordonatele calibrate nu mai corespund.
  - Apelurile se salvează în folderul **Location** ales în dialog — adică **pe VM**,
    nu pe calculatorul local (calea de tip `C:\Users\...\Downloads` se referă la VM).

---

## De ce „hibrid”?

| Acțiune | Cum se realizează |
| --- | --- |
| Selectarea a 20 de apeluri | **Tastatură** — click pe primul rând, apoi `Shift + Down` ×19 |
| Trecerea la următoarele 20 | **Tastatură** — `Down` o dată, apoi `Shift + Down` ×19 (derulează automat) |
| Deschiderea meniului click-dreapta | **Tastatură** — `Shift + F10` |
| Alegerea „Save Calls” (al 4-lea element) | **Tastatură** — `Down` ×4 + `Enter` |
| Setarea câmpului Location | **Mouse** (calibrat) + tastare |
| Alegerea „WAV - Voice only” | **Mouse** (calibrat) |
| Apăsarea „Save” | **Mouse** (calibrat) |
| Așteptare ~32s, apoi „Close” | pauză temporizată + `Enter` (sau click „Close” calibrat) |

---

## Conținutul folderului

| Fișier | Rol |
| --- | --- |
| `kb_core.py` | Funcțiile comune (taste, click-uri calibrate, pașii workflow-ului) |
| `kb_config.json` | Configurația (coordonate, întârzieri, timeout-uri, taste) |
| `kb_calibrate.py` | Unealta de **calibrare** (se rulează o singură dată) |
| `kb_download_one_call.py` | Descarcă **UN singur apel** (test rapid) |
| `kb_download_batch_20.py` | Descarcă **un lot de 20** de apeluri |
| `kb_download_all_1500.py` | Descarcă **toate loturile până la 1500** (cu reluare) |
| `requirements.txt` | Dependențele Python |

---

## Instalare (pe calculatorul LOCAL, Windows)

Deschide **Command Prompt** sau **PowerShell** în acest folder:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Pasul 1 — Calibrare (o singură dată)

Deschide fereastra NICE pe VM (vizibilă pe ecranul local), apoi rulează:

```bat
python kb_calibrate.py
```

Treci cu mouse-ul peste fiecare element și apasă **ENTER** pentru a-l înregistra:

1. `first_row` — primul rând de apel din grilă
2. `location_field` — câmpul „Location” din dialogul Save Calls
3. `wav_radio` — butonul radio **WAV - Voice only**
4. `save_button` — butonul **Save**
5. `close_button` — butonul **Close** din dialogul *Done* *(opțional — dacă îl
   sari, scriptul apasă `Enter` pentru a închide)*

> Pentru a calibra elementele din dialog, deschide-l o dată manual:
> selectează un rând → `Shift+F10` (sau click-dreapta) → **Save Calls**.

Coordonatele se salvează automat în `kb_config.json`.

---

## Pasul 2 — Test cu un singur apel

```bat
python kb_download_one_call.py
```

Verifică dacă se selectează un rând, dacă dialogul se completează corect
(Location + WAV) și dacă se închide. Dacă VM-ul este lent, mărește valorile din
secțiunea `delays` din `kb_config.json`.

---

## Pasul 3 — Test cu un lot de 20

```bat
python kb_download_batch_20.py
```

Asigură-te că grila este derulată **la început** (primul rând vizibil).

---

## Pasul 4 — Descărcarea completă (1500 de apeluri)

```bat
python kb_download_all_1500.py
```

- Derulează grila **la început** înainte de start (sau alege *resume*).
- Progresul se salvează în `kb_session.json` după fiecare lot, deci o
  întrerupere (cădere VPN/VM) poate fi reluată de la lotul următor.

---

## 🛑 Oprire de urgență (fail-safe)

**Împinge brusc cursorul mouse-ului în oricare colț al ecranului** — se declanșează
fail-safe-ul PyAutoGUI și execuția se oprește instant.

---

## Reglaje (`kb_config.json`)

- **`batch.rows_per_batch`** / **`batch.total_calls`** — dimensiunea lotului și ținta totală.
- **`download.location_path`** — lasă gol pentru `~/Downloads`, sau pune o cale
  explicită **de pe VM** (ex.: `C:\\Users\\NumeleTau\\Downloads`).
- **`keys.save_calls_menu_index`** — câte apăsări `Down` până la „Save Calls” (implicit 4).
- **`timeouts.save_complete_wait`** — secunde de așteptare ca un lot să termine salvarea (implicit 32).
- **`delays.*`** — mărește valorile dacă VM-ul/rețeaua sunt lente.
- **`coords.*`** — scrise de calibrator; pot fi editate și manual.

---

## Depanare rapidă

- **Nu selectează 20 de rânduri** → click-ul `first_row` nu nimerește grila;
  recalibrează `first_row` și asigură-te că grila are focus.
- **Meniul „Save Calls” nu se deschide** → unele VM-uri nu transmit `Shift+F10`;
  mărește `delays.context_menu_load` sau ajustează `keys.save_calls_menu_index`.
- **Câmpurile din dialog sunt greșite** → recalibrează `location_field`, `wav_radio`,
  `save_button` (fereastra VM-ului nu trebuie redimensionată după calibrare).
- **Se închide prea devreme/târziu** → ajustează `timeouts.save_complete_wait`.

# Meross Boiler Sync

Szobánkénti hőigény alapján vezérli a Meross kazán termosztátot.

## Mit ír és mit olvas a plugin?

**Kazán termosztát (írás):** csak két dolgot állít, semmi mást:
- `hvac_mode`: bekapcsol (heat) ha valamelyik szoba hőt kér, kikapcsol (off) ha egy sem
- célhőmérséklet: fűtéskor a beállított érték (alap 35 °C, "Kazán célhőmérséklet fűtéskor").
  Ettől a kazán termosztát saját (rossz helyen lévő) hőmérője nem számít: a cél mindig
  magasabb, mint amit mér, tehát a ki/be döntést a plugin hozza, nem a termosztát.
  FIGYELEM: ha ezt 0-ra állítod ("nem módosít"), a termosztát saját mérése is beleszól.

**Kazán termosztát (olvasás):** csak a ki/be állapotát és a megengedett módokat/maximumot.
A termosztát saját hőmérsékletét a plugin SOHA nem használja.

**Szelepek (olvasás):** a célhőmérsékletüket és a saját mérésüket (current_temperature).

**Szelepek (írás):** KIZÁRÓLAG két esetben:
- az "Automata szelep szabályzás" kapcsoló bekapcsolásakor: a szelep célhőmérsékletét ideiglenesen a
  szelep maximumára emeli, majd visszaállítja (6–34 °C között, lásd lent);
- a "Szelep kalibráció" funkció bekapcsolásakor (2.11-től, alapból KI): a szelep *Calibration*
  (kalibráció) szám-entitását állítja, hogy a szelep mérése a szoba hőmérőjét kövesse (2.12-től szobánként
  beállítható eltolással: a szoba hőmérőjénél alapból 1,0 °C-kal hidegebbet, lásd *TRV eltolás*).

A többi kapcsoló és beállítás a szelepekbe nem ír. A kazán termosztátba a kalibráció SOHA nem ír.

Az emelt szelepeket a plugin az integráció **letiltásakor** (2.11.1-től) és **törlésekor** visszaállítja az
eredeti célhőmérsékletükre. A kazán termosztátot letiltáskor és törléskor nem kapcsolja ki, az az utolsó állapotában
marad (lásd *Felügyelet nélküli működés*).

**Szoba hőmérő / páramérő / kinti hőmérő:** csak olvasás.

## Szobánkénti beállítások

| Beállítás | Mire jó |
|---|---|
| Szoba hőmérséklet szenzor | A hőigényt ez alapján számolja a szelep saját (radiátor melletti) mérése helyett. |
| Automata szelep szabályzás | Ha a szobában hideg van, kinyitja a szelepet (célhőmérséklet-emeléssel), a cél közelében visszaengedi. |
| Szelep emelés küszöb / várakozás / visszaengedés | Mennyire legyen hideg, meddig várjon, és mikor engedje vissza a szelepet. Üresen az Alapbeállítások értéke érvényes. |
| Kazán hőigény a szelep állapotához kötve | A szoba csak akkor kér hőt a kazántól, ha a szelep a SAJÁT mérése szerint nyitva van (vagy a plugin éppen kinyitotta). Csak a döntést befolyásolja, nem ír sehova. |
| Szoba páratartalom szenzor | Magas páratartalomnál (60% fölött) enyhén megemeli a szoba célhőmérsékletét. |
| Szelepek automata kalibrációja (2.11-től) | Csak akkor számít, ha a Funkciókban be van kapcsolva a *Szelep kalibráció*. Szobánként kikapcsolható; alapból be van kapcsolva. A szoba hőmérő a referencia, enélkül nincs kalibráció. |
| TRV eltolás (2.12-től) | A kalibráció a szelep mérését a szoba hőmérőjénél ennyivel **hidegebbre** állítja, hogy a szelep a cél alatti szobában teljesen nyisson, ne csak részben. Alap 1,0 °C; 0 (ki) vagy 1,0–3,0 °C. Csak a *Szelepek automata kalibrációja* mellett számít, lásd *TRV eltolás* a Szelep kalibráció fejezetben. |

## Nyári mód
Aktív, ha a dátum a nyári időszakon belül van ÉS a kinti 24 órás átlag a küszöb fölött van.
Ilyenkor nincs hőigény, a kazán termosztát kikapcsol.

## Diagnosztika
Minden szobához és a nyári módhoz tartozik egy binary szenzor. Az attribútumai (magyar
névvel) megmutatják, mit lát és mit döntött a plugin: aktuális hőmérséklet és forrása,
cél, eltérés, a szelep becsült állapota, az érvényes küszöbök stb.

A kártyákhoz (2.7-től) a szoba szenzor még ezeket is kiadja:

| Attribútum | Jelentés |
|---|---|
| `temperature_trend` | a szoba hőmérsékletének változása °C/órában (az utolsó ~30 percből, legalább 10 perc mérés után; 0,1-re kerekítve, és csak ≥ 0,2 változásnál frissül) |
| `valve_boost_starts_at` | mikor kezdi a plugin a szelepemelést (ha a szoba "vár") |
| `valve_boost_rest_until` | meddig tart a pihenő a szelepemelés után |
| `valve_boost_max_until` | mikor éri el a szelepemelés a maximális időt |
| `window_open_pending_until` | mikor számít nyitottnak az ablak (a késleltetés lejártakor) |

Az időpontok ISO 8601 (UTC) formátumúak, és csak akkor vannak kitöltve, ha az adott állapot éppen tart. Mind az
öt attribútum ki van zárva a HA előzményeiből (recorder), így a percenként változó trend és a visszaszámlálók
nem növelik az adatbázist; az állapotgépben és a kártyákon viszont látszanak.

Szelep szabályzás próbaüzem (Alapbeállítások): csak naplóz `[PRÓBAÜZEM]` előtaggal, a
szelepekbe nem ír. A naplózáshoz:

```yaml
logger:
  logs:
    custom_components.meross_boiler_sync: info
```

## Biztonsági funkciók (Alapbeállítások, külön ki/be kapcsolhatók)

**Elavult szenzor figyelése** (alap: be, 6 óra)
Az elemes szenzorok gyakran nem lesznek "elérhetetlenek", amikor kimerül az elem: a HA az utolsó
értéket mutatja tovább. Ha egy szenzor a megadott ideje nem jelentett, a plugin elérhetetlenként kezeli:
a szoba a szelepek saját mérésére vált, az automata szelep szabályzás leáll (a szelep visszaáll), és
a Beállítások -> Javítások alatt értesítés jelenik meg. Ugyanez igaz a kinti szenzorra is: elavult
kinti szenzornál nincs nyári mód, a fűtés engedélyezett marad.
Az időt állítsd a szenzor szokásos jelentési idejének legalább a kétszeresére (különben hamis riasztás).
Az értesítés magától eltűnik, amint a szenzor újra jelent.

**Szelep emelés időtartamának korlátozása** (alap: be, 3 óra, utána 60 perc pihenő)
Ha az emelés a megadott ideig tart és a szoba még mindig nem érte el a célt (nyitott ablak, rossz helyre
tett szenzor, beragadt érték), a szelep visszakapja az eredeti célhőmérsékletét, és a pihenő idejéig nem
emel újra. Ha a szoba eléri a célját, a pihenő nullázódik. Újraindítás után az idő az eredeti kezdettől
számít.

**Szelep célhőmérséklet határa: 6–34 °C (2.10.2-től, mindig él)**
A Meross vezérlő a tartományon kívüli célhőmérsékletet elutasítja, a folyamatos újrapróbálás pedig
tele tudja szemetelni a HA naplóját, és a vezérlőt is lefagyaszthatja. Ezért a plugin a szelepnek **soha nem küld 6 °C alatti
vagy 34 °C feletti célt** (ha a szelep saját `min_temp` / `max_temp` értéke szűkebb, akkor az számít):
- A szelepemelés ("ráfűtés") a szelep `max_temp` értékére emel, de legfeljebb 34 °C-ra.
- A visszaállítás az eredeti célt a 6–34 °C tartományba igazítva küldi vissza (egy 5 °C-os eredeti cél így 6 °C lesz).
- Ha a szelep elutasít egy parancsot, a plugin **nem próbálkozik percenként**: 2, 5, 15, 30, majd 60 percenként
  újra, és csak az első hibát naplózza figyelmeztetésként. Egy `valve_command_failed` esemény (és Napló-bejegyzés) is megy ki,
  hibasorozatonként egyszer. Az első sikeres parancs után minden visszaáll a megszokott működésre.
- A kártya a határon (34 °C felett / 6 °C alatt) **nem küld parancsot**, csak egyszer jelez ("Nem állítható 34° fölé."),
  lásd a Lovelace kártya fejezetben.

A szoba szenzorán az új attribútumok: `temperature_sensor_stale`, `valve_boost_resting`
(kinti szenzor: `outdoor_sensor_stale`), 2.11.1-től `temperature_sensor_unreliable` (a képtelen vagy ugráló
értéket adó szoba hőmérő jelzése, lásd *Felügyelet nélküli működés*).

## Események, kazán ciklusok és védelem (2.8-tól)

Az **Alapbeállítások -> Funkciók** lépésben minden külön ki/be kapcsolható.

| Kapcsoló | Alap | Mit csinál |
|---|---|---|
| Események és naplóbejegyzések | be | A plugin `meross_boiler_sync_event` eseményeket küld, és a HA **Napló** (Logbook) oldalán olvasható szöveggel is megjelennek. |
| Kazán ciklusok figyelése | be | Számolja a kazán indításait (a ki/be váltásokat 24 órára visszamenőleg megőrzi, újraindítás után is). |
| Kazán védelem (minimum be / ki idő) | **ki** | A kazánt nem kapcsolja ki / vissza a megadott minimum idő letelte előtt. Késleltetheti a fűtést, ezért alapból ki van kapcsolva. |

**Események.** Az esemény neve `meross_boiler_sync_event`, a `type` mező mondja meg, mi történt; szobához
kötött eseménynél van `room` (név) és `entity_id` (a szoba hőigény szenzora) is. Indulás alatt nem küld eseményt.

| `type` | Mikor | További mezők |
|---|---|---|
| `boost_started` | a szelepemelés elindult | `deviation`, `current_temperature`, `target_temperature`, `dry_run` |
| `boost_ended` | a szelepemelés véget ért | `reason` (`target_reached`, `max_time`, `window`, `summer`, `sensor`, `manual`, `disabled`, `other`), `duration_minutes`, `dry_run` |
| `window_paused` | az ablak a késleltetésnél tovább nyitva, a szoba szünetel | `open_minutes` |
| `window_resumed` | az ablak bezárva, a fűtés folytatódik | `open_minutes` |
| `sensor_stale` / `sensor_recovered` | egy szenzor elavult / újra frissül | `sensor`, `age_minutes`, kinti szenzornál `outdoor: true` |
| `sensor_unreliable` / `sensor_reliable` | a szoba hőmérő képtelen vagy ugráló értéket ad / újra megbízhatónak látszik (2.11.1) | `sensor`, `reason` (`range` / `jump`), `value` (a gyanús mérés °C-ban; `null`, ha nem szám) |
| `short_cycling` | a kazán gyakran kapcsolgat | `starts_last_hour`, `avg_on_minutes` |
| `manual_boost_started` | elindult a "Fűts most" (2.9) | `minutes`, `offset` |
| `manual_boost_ended` | véget ért a "Fűts most" (2.9) | `reason` (`expired`, `cancelled`, `target_reached`, `window`, `summer`, `sensor`, `disabled`), `duration_minutes` |
| `preheat_started` | elindult az előfűtés (2.9) | `target_temperature`, `ready_by` (óra:perc, helyi idő), `minutes_to_ready`, `heating_rate`, `source` (`schedule` / `service`) |
| `preheat_unreachable` | az előfűtés már nem érheti el időben a célt (2.9; futásonként egyszer) | `target_temperature`, `ready_by`, `minutes_needed`, `minutes_available` |
| `valve_command_failed` | a szelep elutasított egy parancsot (2.10.2; hibasorozatonként egyszer, utána egyre ritkábban próbálkozik) | `valve` (a szelep entitás azonosítója) |
| `valve_calibrated` | a szelep kalibrációja módosult / visszaállt, vagy próbaüzemi javaslat (2.11) | `valve`, `from_offset`, `to_offset`, `difference` (a szoba hőmérője és a szelep mérése közti különbség, °C), `target_difference` (a kívánt különbség: a szoba TRV eltolása, 2.12), `dry_run`, `reason` (`auto` / `revert`) |
| `valve_calibration_suspended` | a szelep kalibrációja 7 napra felfüggesztve (2.11) | `valve`, `days`, `reason` (`ineffective` / `rejected` / `revert_failed`) |

Példa automatizáció (értesítés, ha egy szenzor elavul):

```yaml
trigger:
  - platform: event
    event_type: meross_boiler_sync_event
    event_data:
      type: sensor_stale
action:
  - service: notify.mobile_app_telefon
    data:
      message: "{{ trigger.event.data.room or 'Kinti szenzor' }}: elavult szenzor"
```

**Kazán ciklusok.** Két entitás (a figyelés kikapcsolásakor mindkettő eltűnik):
- `sensor` **Kazán indítások (24 óra)**: az indítások száma az elmúlt 24 órában. Attribútumok: `starts_last_hour`,
  `avg_on_minutes`, `avg_off_minutes` (az utolsó 2 óra lezárt ciklusaiból), `last_start`, `last_stop`, `cycles`
  (az elmúlt 12 óra be/ki szakaszai, a kártyák ebből rajzolnak; a recorder nem menti).
- `binary_sensor` **Gyakori kapcsolgatás** (`problem`): bekapcsol, ha a kazán óránként legalább a megadott
  számszor indult (alap: 5), vagy az utolsó 2 óra átlagos bekapcsolt ideje (legalább 3 ciklusból) a megadott
  perc alatt van (alap: 4; 0 = nem figyeli). Attribútumai: `starts_last_hour`, `avg_on_minutes`,
  `max_starts_per_hour`, `min_avg_on_minutes`.

**Kazán védelem.** Bekapcsolva a kazán legalább a megadott ideig bekapcsolva (alap: 5 perc) illetve
kikapcsolva (alap: 5 perc) marad, akkor is, ha a szobák hőigénye közben változik. A számolás a megfigyelt
váltásoktól indul, így újraindítás után és külső kapcsolásnál is érvényes. Az Alapbeállítások "Minimális
kapcsolási idő" értéke ettől függetlenül továbbra is érvényes (a kettő közül a hosszabb számít).

## Fűts most és Előfűtés (2.9-től)

Mindkettő az **Alapbeállítások -> Funkciók** lépésben kapcsolható. A **Fűts most** alapból **be**, az
**Előfűtés** alapból **ki** van kapcsolva, hogy a meglévő beállításod ugyanúgy működjön, mint eddig.

| Beállítás | Alap | Mit csinál |
|---|---|---|
| Fűts most (megemelt cél) | be | Engedélyezi a "Fűts most" gombot és szolgáltatást. |
| Fűts most: alap időtartam | 60 perc (5–480) | Meddig tartson, ha nem adsz meg mást. |
| Fűts most: a cél emelése | +2,0 °C (0,5–5) | Ennyivel emeli a szoba célját. |
| Fűts most: véget ér, ha a szoba eléri a megemelt célt | **ki** | Be: a Fűts most a cél elérésekor leáll (`reason: target_reached`). Ki: a teljes időtartamig tartja a megemelt célt. |
| Előfűtés (menetrend és szolgáltatás) | **ki** | Engedélyezi az előfűtést (heti menetrend és `preheat` szolgáltatás). |
| Előfűtés: legkorábbi indulás | 240 perc | Ennél korábban nem kezd előfűteni a kész időpont előtt. |
| Előfűtés: a cél tartása | 30 perc | A kész időpont után ennyi ideig tartja a célt. |
| Előfűtés: alap felfűtési sebesség | 1,0 °C/ó | Ezzel számol, amíg a szoba saját sebességét meg nem tanulta. |

**Fűts most.** A szoba *tényleges célját* ideiglenesen megemeli: az alap cél (a szelep célja és a páratartalom
miatti emelés) + a beállított emelés, legfeljebb 30 °C-ig (vagy az alap célig, ha az magasabb). A szoba
hőigénye, az eltérés (`deviation`) és a "hőt kér" szenzor ehhez a megemelt célhoz igazodik. Ha a szobában
be van kapcsolva az **Automata szelep szabályzás** (és a szoba hőmérő szenzorról dolgozik), és a szoba a
megemelt céltól legalább a szelep emelés küszöbével hidegebb, a szelepet nem várakoztatja a szokásos késleltetéssel,
hanem azonnal kinyitja. A Fűts most önmagában nem ír a szelepekbe: a szelep célhőmérsékletét csak ez az
automata szelep szabályzás emeli ideiglenesen, a szokásos módon.
A Fűts most **nem indítható** nyári módban, nyitott ablaknál (a késleltetés letelte után), elavult hőmérőnél
és ha a szobában nincs elérhető szelep, a szolgáltatás ilyenkor érthető hibaüzenetet ad. **Véget ér**, ha
letelt az idő (`expired`), lemondtad (`cancelled`), kinyílt az ablak (`window`), nyári mód lett (`summer`),
elavult a hőmérő (`sensor`), a cél elérésekor (ha ezt bekapcsoltad: `target_reached`), vagy kikapcsoltad a
funkciót (`disabled`). Újraindítás után is folytatódik a hátralévő idővel.

**Előfűtés.** A szoba legyen egy megadott időpontra a megadott hőmérsékleten. Kétféleképp adhatod meg:
- **heti menetrend** szobánként: Beállítások -> **Előfűtés menetrend (szobánként)** -> szoba -> új sor:
  napok (H–V), "ekkorra legyen kész" időpont, célhőmérséklet. Több sor is lehet (pl. hétköznap 06:30 →
  22 °C, hétvégén 08:00 → 22 °C).
- **egyszeri kérés** a `meross_boiler_sync.preheat` szolgáltatással (automatizációból is).

Az indulás ideje: *kész időpont − szükséges idő*, ahol a szükséges idő = (cél − mostani hőmérséklet) ÷
felfűtési sebesség × 1,15 (15 % biztonság), legfeljebb a beállított legkorábbi indulás. Az előfűtés alatt a
szoba tényleges célja a kért hőmérséklet (ha az magasabb a mostaninál), ezután a "kész" időponttól a beállított
ideig tartja; ha egyszer elindult, a kész időpont és a tartás végéig megmarad, akkor is, ha a szoba közben már
felmelegedett. Nyitott ablaknál, elavult hőmérőnél és nyári módban nem fűt előre (a terv megmarad). Ha már nem érheti el időben a célt, egyszer
`preheat_unreachable` esemény megy ki.

**Tanult felfűtési sebesség.** A plugin méri, hogy a szoba mennyit melegszik óránként, miközben fűt (a kazán be
van kapcsolva, a szobának hőigénye van, a hőmérő szenzor friss, az ablak zárva). Az átlagot szobánként
megtartja (újraindítás után is). Legalább kb. 20 mérési pont után használja, addig az alap sebességgel számol.
A tanult sebesség a **Fűtési statisztika** kártyán is látszik (`show_rates`).

**Szolgáltatások** (a célpont egy szoba "fűtési igény" szenzora):

| Szolgáltatás | Mezők | Mit csinál |
|---|---|---|
| `meross_boiler_sync.boost_now` | `minutes` (5–480), `offset` (0,5–5 °C) | "Fűts most": megemeli a szoba célját. A mezők nélkül a Funkciók alap értékei érvényesek. |
| `meross_boiler_sync.cancel_boost_now` | – | Idő előtt befejezi a Fűts most-ot. |
| `meross_boiler_sync.preheat` | `ready_by` (időpont: a következő ilyen óra:perc, vagy dátum és idő), `target_temperature` (5–30 °C), `hold_minutes` (0–480) | Egyszeri előfűtés. |
| `meross_boiler_sync.cancel_preheat` | – | Törli az egyszeri kérést, és kihagyja a most futó vagy következő menetrendi előfűtést. |

Példa: ha a telefonod hazafelé jelzi, hogy 30 percre vagy, melegítsd elő a nappalit:

```yaml
service: meross_boiler_sync.preheat
target:
  entity_id: binary_sensor.nappali_futesi_igeny
data:
  ready_by: "{{ (now() + timedelta(minutes=45)).strftime('%H:%M:%S') }}"
  target_temperature: 22
```

**Új attribútumok a szoba szenzorán:** `manual_boost_available`, `manual_boost_active`, `manual_boost_until`,
`manual_boost_offset`, `manual_boost_default_minutes`, `manual_boost_default_offset`, `preheat_available`,
`preheat_status` (`scheduled` / `heating` / `ready` / `unreachable`), `preheat_start_at`, `preheat_ready_by`,
`preheat_target`, `preheat_source` (`schedule` / `service`), `heating_rate` (°C/óra), `heating_rate_learned`.
Az időket tartalmazó attribútumokat a recorder nem menti.

## Becsült gázfogyasztás az Energia fülhöz (2.10-től)

A **Beállítások → Funkciók** menüben bekapcsolható a *Gázbecslés (az Energia fülhöz)* (alapból ki van kapcsolva).
Bekapcsolva létrejön egy új entitás:

- `sensor` **Becsült gázfogyasztás** (`device_class: gas`, m³, `state_class: total_increasing`): a kazán bekapcsolt
  idejének és a megadott gázfogyasztásnak (m³/óra, alap: 1,6) a szorzataként folyamatosan növekvő számláló.
  Attribútumai: `m3_per_hour` (a használt fogyasztás) és `boiler_on` (a kazán állapota az utolsó kiértékeléskor).

**Beállítás az Energia fülön:** Beállítások → Irányítópultok → Energia, a Gáz résznél nyisd meg a
*Gázfogyasztás konfigurálása* ablakot, és a *Gázfogyasztás* mezőben (Statisztika kiválasztása) válaszd ki a
**Becsült gázfogyasztás** szenzort. A költséghez ugyanitt a *Fix ár használata* pontnál add meg a gáz egy
köbméterre jutó árát (az Energia fül ezzel számolja a forintot).
Ha van valódi gázóra szenzorod is, **csak az egyiket** add hozzá, különben duplán számolódik a fogyasztás.

**Hogyan számol?**
- A kazán (az integráció által vezérelt termosztát) bekapcsolt másodperceit összegzi, és az akkor érvényes m³/órával
  szorozza. A kiértékelés percenként fut, a kazán be- és kikapcsolását a váltás valódi idejéhez igazítja.
- A számláló újraindítás után is megmarad. Amíg a Home Assistant nem fut (vagy a kazán elérhetetlen, vagy egy
  kiértékelés 10 percnél hosszabb ideig kimaradt), azt az időt **nem** számolja, hogy ne legyen túlbecslés.
  Legfeljebb ~5 percnyi számlálás veszhet el, ha a rendszer váratlanul áll le.
- A m³/óra módosítása csak a további fogyasztásra hat, a már felhalmozott érték nem íródik át.
- Ha a funkciót kikapcsolod, az entitás eltűnik (a halmozott érték megmarad, és újra bekapcsolva folytatódik).

**Becslés, nem mérés.** A kazán működés közben modulál, és előfordulhat, hogy a használati melegvizet is fűti, ezért a
szenzor csak közelítő érték. A pontosításhoz hasonlítsd össze a szenzort a gázóra állásával (néhány napon át), és
igazítsd a *Gázbecslés: gázfogyasztás bekapcsolt kazánnál* értéket úgy, hogy a kettő egyezzen. A Fűtési statisztika
kártya költségbecslése (`show_cost`) ettől független, a saját `gas_m3_per_hour` értékével számol.

## Szelep kalibráció (2.11-től, kísérleti)

A szelep a radiátor mellett méri a hőmérsékletet, ezért a szoba valódi hőmérsékletétől eltérhet. A szelep a
**saját mérése** alapján nyit és zár, így egy téves méréssel a szoba túl hideg vagy túl meleg marad. A funkció a
szoba hőmérőjét veszi referenciának, és a szelep *Calibration* (kalibráció) szám-entitását úgy állítja, hogy a
szelep mérése a szoba hőmérőjét kövesse. (2.12-től ez szobánként eltolható: a szelep a szoba hőmérőjénél szándékosan
hidegebbet mér, hogy teljesen nyisson, lásd *TRV eltolás* lent.) **Csak a radiátor szelepekre vonatkozik, a kazán
termosztátot nem érinti.**

**Bekapcsolás:** Beállítások → Funkciók → *Szelep kalibráció (automata, kísérleti)* (alapból KI). Szobánként
kikapcsolható a szoba szerkesztésénél (*Szelepek automata kalibrációja*, alapból be). A szobához meg kell adni a
*Szoba hőmérséklet szenzor*t, mert az a referencia (enélkül a szoba szelepei `waiting` / `no_reference` állapotban maradnak).

**Először kapcsold be a *Próbaüzem*et** (*Szelep kalibráció: próbaüzem*): ilyenkor a plugin semmit nem ír a
szelepekbe, csak a naplóba (`[PRÓBAÜZEM]`) és egy eseménybe írja, mire állítaná a kalibrációt. A szoba
szenzorának `valve_calibration` attribútumában a `proposed_offset` mutatja a javasolt értéket. Ha a javaslatok
ésszerűek, kapcsold ki a próbaüzemet. Fontos: a funkció tartós beállítást ír a szelep memóriájába, ezért
kísérletinek számít, és valódi Meross eszközön még nem volt kipróbálva (lásd *Feltételezések* lent).

### TRV eltolás (2.12-től)

A szelep saját szabályzása **arányos**: minél kisebb a hiány a célhoz képest, annál kevésbé nyit. Néhány tized fokos
hiánynál a szelep a saját firmware-e szerint a nyitásnak csak a töredékét adja (becslés szerint kb. 20–30%-át),
ami nem biztos, hogy elég a szoba felfűtéséhez. Ilyenkor a rendszer "küzd": a szoba hőt kér, a kazán megy, de a
radiátor alig melegszik. Ezen a pontos kalibráció önmagában nem segít, hiszen a szelep a pontos mérés mellett is csak
részben nyit.

Erre való a szobánkénti **TRV eltolás** (a szoba szerkesztésénél; alap **1,0 °C**, 0 vagy 1,0–3,0 °C, 0,5-ös
lépésekkel). A kalibráció a szelep mérését nem a szoba hőmérőjére, hanem annál az eltolásnyival **hidegebb** értékre
állítja (a szoba hőmérője mínusz az eltolás). Így a szelep a céljánál hidegebb szobában legalább az eltolásnyi hiányt
lát, és ez a saját szabályzása szerint teljesen kinyitja. A szoba célja (a szelepen beállított érték) nem változik, és a
plugin ehhez **nem ír célhőmérsékletet** a szelepbe: csak a már meglévő kalibrációs szám-entitást állítja.

Példa: a cél 21 °C, a szoba hőmérője 20,5 °C, a szelep mérése pontosan egyezik vele. Eltolás nélkül a szelep 0,5 °C
hiányt lát. 1,0 °C eltolással a mérése 19,5 °C-ra áll, tehát 1,5 °C hiányt lát, és teljesen nyit.

**A kompromisszum, amire figyelj:**
- A szelep a saját szabályzása szerint akkor zár vissza, amikor a szoba hőmérője a célnál az eltolásnyival
  magasabb. A szoba hőigénye ettől függetlenül a cél elérésekor megszűnik (a hőigényt a szoba hőmérője adja, nem a
  szelep), a kazán tehát miatta nem megy tovább. De **ha a kazán más szobáknak fűt, ez a szoba legfeljebb az
  eltolásnyival a cél fölé melegedhet**, mert a szelepe még nyitva van. Ha ez zavar, csökkentsd az eltolást.
- Ha a szoba hőmérője kiesik (elavult vagy gyanús értéket ad), a plugin a szelepek saját mérésére vált. Az eltolással
  ez az eltolásnyival hidegebbet mutat, ezért erre az időre a szoba szintén legfeljebb az eltolásnyival melegedhet a
  cél fölé. A plugin és a szelep ilyenkor ugyanazt látják, a hiba korlátos.
- Ha a Home Assistant leáll, a szelepben tartósan csak az eltolásnyi kalibráció marad, ami legfeljebb ennyivel
  emeli a szoba hőmérsékletét. Ez más, mint az *Automata szelep szabályzás*, ahol a szelep a maximumra (akár 34 °C-ra)
  emelt célon maradhat. Az eltolás tehát a biztonságosabb, korlátos mód arra, hogy a szelep rendesen kinyisson.
- Ajánlott érték **1,0–1,5 °C**. Az 1,0 °C-nál kisebb, de nem nulla érték nem engedélyezett: a kalibráció ±0,8 °C-os
  tűréssel dolgozik (hogy ne írjon feleslegesen a szelepbe), és az ennél kisebb eltolás nem érvényesülne megbízhatóan.
  A tűrés miatt a ténylegesen beállt különbség (`difference`) az eltolástól (`target_difference`) legfeljebb ±0,8
  °C-kal térhet el: ha a szelep eleve hidegebbet mér a kelleténél, a plugin nem melegíti vissza, ha pedig csak kicsit
  melegebbet, nem hajtja tovább. Az első beállításkor a lépésköz (0,5 °C) miatt a különbség az eltolás ±0,25 °C-án belül áll be.
- A **0** a 2.11 viselkedése: a szelep mérése a szoba hőmérőjét követi.
- Az eltolás csak olyan szobában számít, ahol van *Szoba hőmérséklet szenzor*, be van kapcsolva a *Szelep
  kalibráció*, és a szoba részt vesz benne. Az eltolás módosítása után a szelep a következő csendes időben (legalább 90
  perc fűtés nélkül) áll át az új célra. A kalibráció minden korlátja és védelme (2 óra két módosítás között, napi
  4, hatásellenőrzés, visszaállítás, felfüggesztés, újraindítás-állóság) változatlanul érvényes.
- Az eltolást 0-ra állítva a szelep a következő csendes időben újra a szoba hőmérőjét követi. A *Szelepek automata
  kalibrációja* kikapcsolásakor viszont a szelep az utolsó értéken marad (lásd *Kikapcsolás és visszaállítás*).
- Fontos: a **frissítés után** (2.12) az eltolás alapból 1,0 °C, ezért ha a kalibráció már be volt kapcsolva, a szelepek
  a következő csendes időben 1,0 °C-kal hidegebbre állnak a szoba hőmérőjénél. Ha nem ezt szeretnéd, állítsd az
  eltolást 0-ra a szoba szerkesztésénél. Próbaüzemben ez csak javaslatként jelenik meg.

**Melyik entitást állítja?** A szelep eszközén keresi a kalibráció szám-entitást. A Meross LAN esetén ez a
*Calibration* (`translation_key: calibration_temperature`; a hubos szelepeknél ±5 °C, 0,5 °C lépésköz). Más
integrációnál a nevében "hőmérséklet" és "kalibráció/offset" szavakat tartalmazó szám-entitást próbálja
(például Zigbee2MQTT `local_temperature_calibration`), de ez nem tesztelt. A tartományt és a lépésközt a
szám-entitás adja; ha az entitás nincs vagy le van tiltva (`no_entity` / `disabled`), a plugin semmit nem módosít.
Letiltott entitásnál engedélyezd a szelep eszközoldalán (a *Calibration* számot), és pár perc múlva újra keresi.

**Mikor mér? (csendes idő)** Fűtés közben a forró radiátor melegebbnek mutatja a szelepet, és egy ilyenkor végzett
"korrekció" a kihűlt radiátornál rossz irányba tolná a szelepet. Ezért a plugin csak akkor mér, ha a radiátor már
kihűlt: a kazán, **vagy** az adott szelep legalább **90 perce** nem fűt. Mérés közben ezeknek is teljesülniük kell:
- a szoba hőmérője friss, nem gyanús (lásd *Felügyelet nélküli működés*), 5–40 °C közötti, és legfeljebb 0,6 °C/óra sebességgel változik;
- nincs nyitott (vagy nyitásra váró) ablak, és nincs szelepemelés;
- a szelep saját mérése 5–40 °C közötti;
- a Meross LAN *Tracked sensor* (külső hőmérő követése) választója nincs bekapcsolva. Ha be van kapcsolva, a
  Meross LAN maga állítja a kalibrációt, ehhez a plugin nem nyúl (`tracker` állapot).

A plugin 150 másodpercenként mintát vesz (a hub kb. 3 percenként jelent), legalább 6 stabil mintát gyűjt (kb. 13
perc), és a döntés a minták **mediánján** alapul. Instabil mérésnél (a minták 0,8 °C-nál jobban szórnak, vagy a
szoba hőmérője 0,6 °C-nál jobban ingadozik) nem dönt, hanem tovább mér.

**Mikor módosít?** (Az "eltérés" itt a szelep mérése és a **cél** között van: a cél a szoba hőmérője mínusz a *TRV
eltolás*, eltolás nélkül maga a szoba hőmérője.)
- 0,8 °C-nál kisebb eltérésnél nem csinál semmit (`ok`, 6 óra múlva újra ellenőrzi).
- 3 °C-nál nagyobb eltérésnél sem (`implausible`): ekkora különbség rossz helyre tett szenzorra vagy huzatra utal,
  nem kalibrációs hibára.
- Különben az új érték = a mostani kalibráció + az eltérés, a lépésközre kerekítve, a szám-entitás határain
  belül, és az **eredeti** (a plugin első módosítása előtti) értéktől legfeljebb ±4 °C-ra.
- Korlátok: szelepenként legalább 2 óra két módosítás között, naponta legfeljebb 4, és két szelep módosítása
  között legalább 5 perc (a Meross hubot nem terheli).

**Hogyan ellenőrzi a módosítást?**
1. 60 másodperc múlva megnézi, hogy a szám-entitás megtartotta-e az új értéket. (A Meross LAN a forráskódja szerint
   azonnal "optimistán" az újat mutatja, és ha az eszköz elutasítja, csendben visszaáll, a hívás pedig nem ad
   hibát. Ezért nem a hívás sikeréből, hanem az entitás állapotából ítéli meg.) Ha visszaállt, az sikertelen kísérlet.
2. 10 percet vár, hogy a hub új mérést jelentsen, majd a következő csendes időben új mérést végez.
3. A módosítás akkor hatásos, ha a kért változtatás legalább fele megjelenik a szelep mérésében. (Az 1 °C-nál
   kisebb módosítás hatása a mérési zajtól nem különböztethető meg, azt nem ítéli meg.)
4. Ha nem hatásos (a szelep nem veszi figyelembe, vagy éppen rossz irányba hat), visszaállítja az előző értéket
   (legfeljebb 3 próbával), és sikertelennek számolja. **Két egymás utáni sikertelen módosítás után a szelepet 7
   napra felfüggeszti** (`suspended`), és a Beállítások → Javítások alatt értesítés jelenik meg. A 7 nap lejárta után
   még egyszer próbát tesz; ha az is sikertelen, újra felfüggeszti.
5. Ha közben te állítod át kézzel a kalibrációt, a plugin észreveszi (`external`), eldobja a félbehagyott műveletet,
   és nem írja felül a te értékedet.

**Kikapcsolás és visszaállítás:** a funkció kikapcsolása **nem** állítja vissza a már módosított kalibrációkat
(a szelepek az utolsó beállított értéken maradnak). Az eredeti értéket a szoba szenzorának `valve_calibration`
attribútuma (`original_offset`) és a Napló ("a szelep kalibrációja módosítva: … +0 → +1.5 °C") mutatja; visszaállítani
kézzel lehet a szelep *Calibration* számán. Ha kikapcsolod, miközben egy módosítás ellenőrzése vagy visszaállítása
folyamatban van, a művelet megáll, és a szelep az aktuális értéken marad.

**Események.** A `meross_boiler_sync_event` esemény két új `type` értéke: `valve_calibrated` (megerősített módosítás,
visszaállítás vagy próbaüzemi javaslat) és `valve_calibration_suspended` (a szelep felfüggesztődött). A mezőiket az
*Események, kazán ciklusok és védelem* fejezet táblázata sorolja fel; a HA Napló oldalán is olvasható szöveggel
jelennek meg.

**Attribútumok** a szoba szenzorán: `calibration_enabled`, `calibration_dry_run`, `calibration_room` (részt vesz-e a
szoba), `trv_offset` (a szoba TRV eltolása, °C) és `valve_calibration`: szelepenként egy elem `valve`, `status`,
`reason`, `offset` (mostani kalibráció), `original_offset`, `difference` (a szoba hőmérője és a szelep mérése közti
különbség, °C; pozitív, ha a szelep hidegebbet mér), `target_difference` (a kívánt különbség, vagyis a szoba TRV
eltolása), `samples`, `last_adjusted`, `proposed_offset` (próbaüzemben) és `suspended_until` mezőkkel. Beállított
eltolásnál a rendben lévő szelepnél a `difference` az eltolás közelében van. A recorder nem menti.

| `status` | Jelentése |
|---|---|
| `off` | a szobában ki van kapcsolva |
| `waiting` | vár; a `reason` mondja meg, mire: `not_quiet` (a radiátor még nem hűlt ki), `settling` (módosítás utáni várakozás), `window` (nyitott ablak), `boost` (szelepemelés), `trend` (a szoba hőmérséklete gyorsan változik), `no_reference` / `stale` / `unreliable` (nincs, elavult, vagy képtelen / ugráló értéket ad a szoba hőmérője), `no_reading` (a szelep mérése hiányzik), `interval` / `daily_limit` / `spacing` (időkorlát), `backoff` (a szelep elutasított egy parancsot), `hold` (HA indulás / leállás), `dry_run`, `external` (kézzel állítottad át), `reverting` / `reverted` (visszaállítás), `unsent` (a parancs el sem ment) |
| `sampling` | mintát gyűjt (`samples` darab van meg; `reason`: `samples` vagy `unstable`) |
| `verifying` | az utolsó módosítás hatását ellenőrzi |
| `ok` | a szelep mérése a küszöbön belül van a céltól, vagyis a szoba hőmérője mínusz az eltolás értéktől (`reason: recheck`: 6 óra múlva újra ellenőrzi) |
| `proposed` | próbaüzem: a `proposed_offset` lenne az új érték |
| `suspended` | felfüggesztve (`suspended_until`-ig) |
| `failed` | az utolsó módosítás nem sikerült (a szelep elutasította) |
| `tracker` | a Meross LAN követi a külső hőmérőt, a plugin nem nyúl hozzá |
| `no_entity` | nincs (vagy le van tiltva / nem hihető) kalibráció szám-entitás |
| `unavailable` | a szelep vagy a szám-entitás nem elérhető |
| `implausible` | a szelep mérése és a cél eltérése 3 °C-nál nagyobb: nem korrigál |
| `limit` | az eltérést a ±4 °C-os (vagy a szám-entitás tartománya, lépésköze szerinti) határ miatt nem lehet tovább korrigálni |
| `error` | váratlan hiba (naplózva); a fűtést nem érinti |

**Feltételezések és korlátok:**
- A Meross LAN a szelep `current_temperature` értékében már benne adja a kalibrációt. A plugin ebből indul ki: ha
  közben megváltozik a kalibráció, a régi mintákat eldobja, és újakat gyűjt.
- A plugin °C-ban számol (metrikus Home Assistant rendszer), mint a többi funkciója is; a kalibráció szám-entitása
  fokban, eltolásként értendő.
- A *TRV eltolás* azon alapul, hogy a szelep a saját (kalibrált) mérését és a beállított célt veti össze, és minél
  nagyobb a hiány, annál jobban nyit. A kb. 20–30%-os nyitás kis hiánynál becslés, nem mért adat; a pontos
  szabályzási görbe nem ismert, és szelepenként más lehet. Az eltolás hatását ezért a valódi szelepen érdemes megfigyelni
  (a radiátor melegedése, a szoba hőmérője), és ha kell, 1,5 °C-ra emelni.
- A hubos szelepek kb. 3 percenként jelentenek, ezért lassú a visszacsatolás: egy módosítás igazolása legalább
  kb. 25 percet vesz igénybe, és a plugin ezt tudatosan megvárja.
- A funkciót szimulált Home Assistant környezetben és szimulált szelepekkel teszteltem (hibás, elutasító, hatástalan
  és ellentétes irányba ható eszközök, újraindítás és összeomlás a módosítás közben is), **valódi Meross
  eszközön még nem**. Ezért kísérleti: használd először próbaüzemben, és kövesd a naplót.

## Újraindítás- és összeomlás-állóság (2.11-től)

Ha a Home Assistant újraindul, leáll, összeomlik, vagy a pluginot kézzel újratöltöd (Beállítások → Eszközök és
szolgáltatások → Meross Boiler Sync → Újratöltés, vagy beállítás módosításakor), a plugin nem állíthat el
semmit, és nem maradhat rossz érték sem a szelepben, sem a saját adataiban. A 2.11 ezt az összes tárolt adatra
átnézte, és több helyen javított:

| Adat | Mi történik újraindításkor |
|---|---|
| **Indulás / leállás** | A HA indulásakor a plugin olvas és számol, de **90 másodpercig nem ír** a szelepekbe és a kazánba (az entitások még töltődnek, a hiányos adatból hozott döntés feleslegesen kikapcsolhatná a kazánt). Leálláskor sem ír. Futó HA-ban (újratöltés) nincs várakozás. |
| **Tiszta leállítás / újratöltés** | A plugin megvárja a futó kiértékelést, az állapotot **azonnal menti**, a régi vezérlő pedig leállítottnak számít (nem értékel, nem ír), így nem lehet két vezérlő egyszerre. |
| **Szelepemelés** | A szelep eredeti célhőmérsékletét a plugin a parancs elküldése **előtt** menti. Ha a HA a kettő között áll le, az újraindulás tudja az eredeti célt, és vissza tudja állítani (különben a megemelt érték a szelep "saját" céljának látszana, és ott maradna). Az emelés kezdete és a pihenő is megmarad: a maximális emelési idő nem nullázódik. |
| **Szelep kalibráció** | A módosítás szándéka a parancs előtt a lemezre kerül; újraindítás után a plugin a szám-entitás tényleges állapotából dönti el, megtörtént-e. Az időközök (2 óra, napi 4), a hibaszámláló és a 7 napos felfüggesztés is megmarad. A mintagyűjtés és a csendes idő mérése újraindul (a hűlést újra meg kell figyelni), ezért újraindítás után legalább 90 perc telik el az első új mérésig. |
| **Kazán ciklus napló** | Ha a leállás alatt a kazán állapota nem volt ismert, a ciklus vége "ismeretlen" jelölést kap, a plugin nem találja ki. |
| **Kazán minimális váltási ideje** | Az utolsó ismert váltás ideje a ciklus-naplóból pótolható, így a kazán újraindítás után sem kapcsol vissza azonnal, ha nemrég váltott. |
| **Nyári mód** | Az állapota megmarad, így újraindítás után a plugin nem "téli módban" indul. |
| **Hőigény hiszterézis** | Csak a memóriában él, ezért indulás után az első 10 percben, ha a kazán fűt, a céltól elmaradó szoba tovább kér hőt, mintha az előző körben is kért volna. A kazán így nem kapcsol ki idő előtt. |
| **Gázbecslés** | A számláló megmarad, a kimaradt idő nincs benne (lásd fent). |
| **Betöltött adatok** | A tárolt adatot a plugin ellenőrzi: a sérült vagy értelmetlen értéket (rossz típus, jövőbeli időpont, lehetetlen hőmérséklet) eldobja, nem fogadja el, és nem hibázik tőle. A mentés másolatot ment, így a mentés közbeni változás nem torzítja. |
| **Váratlan leállás** | A ritkán fontos adatok mentése késleltetett (néhány másodperctől 10 percig), ezek legfeljebb ennyit veszíthetnek áramszünetnél vagy összeomlásnál. A kritikus rekordok (szelepemelés kezdete, kalibráció módosítása és visszaállítása) azonnal mentve vannak. |

## Felügyelet nélküli működés (2.11.1-től)

A cél: a fűtés akkor se csináljon butaságot, ha egy szenzor elromlik, egy eszköz kiesik vagy a plugin leáll, és ha
mégis baj van, szóljon. Ez a fejezet leírja, mit véd a plugin, mit **nem**, és hogyan érdemes beállítani, ha nem
akarod felügyelni. Mindez szimulált környezetben tesztelt, valódi Meross eszközön még nem.

### A szoba hőmérő hihetőségi ellenőrzése (mindig él)

Egy hibás szenzor (kimerülő elem, zárlat, hibaérték) hideget vagy meleget hazudna: a kazán feleslegesen járna, a
szelep feleslegesen nyitna. Ezért a plugin nem hisz el minden mérést. A szoba hőmérője **gyanús**, ha:

| Szempont | Példa |
|---|---|
| a mért érték **1 °C alatt vagy 45 °C felett** van, vagy nem szám (`nan`, `inf`) | `85`, `-127`, `0`, `nan` (tipikus hibaértékek) |
| a mérés az utolsó **20 percben** összesen **6 °C-nál többet** ugrál fel-le (az 1 °C-nál kisebb lépés mérési zaj, az nem számít; a ritkán jelentő szenzor lépései sem, ha 20 percnél messzebb vannak egymástól) | `21 → 2 → 21`, vagy folyamatosan `18 ↔ 24` |

Gyanús érték után **30 percig** (az utolsó gyanús lépéstől számítva) a plugin nem használja a szenzort:
- a szoba a **szelepek saját mérésére** vált, mint elérhetetlen szenzornál (`temperature_source: valve`), a fűtés
  tovább működik;
- az **automata szelep szabályzás leáll**, a szelep visszakapja az eredeti célhőmérsékletét; a *Fűts most* leáll és
  nem indítható, az előfűtés nem fűt előre; a szelep kalibráció vár (`waiting` / `unreliable`);
- a szoba szenzorán a `temperature_sensor_unreliable` attribútum `true`;
- a Beállítások → Javítások alatt értesítés jelenik meg, és `sensor_unreliable` esemény megy ki (a Naplóban is);
- ha a szenzor közben elérhetetlenné válik, a jelzés megmarad: csak egy újabb hihető mérés oldja fel (a 30 perc
  lejárta után). Ekkor jön a `sensor_reliable` esemény, és az értesítés eltűnik.

**Amit nem fog meg:** ha a szenzor hihető, de tartósan rossz értéken ragad (például lefagy 17 °C-on, miközben a szoba
meleg). Ez ellen a *Kazán hőigény a szelep állapotához kötve* kapcsoló véd: a szoba csak akkor kér hőt a kazántól, ha
a szelep a SAJÁT mérése szerint is nyitva van. (Ha az automata szelep szabályzás is be van kapcsolva, a szelepemelés
alatt a szoba a szelep állapotától függetlenül hőt kér, legfeljebb a beállított maximális emelési ideig.)

Újraindítás után a figyelő előzménye üres: a képtelen értéket az első kiértékelés is kiszűri, az ugrálást pedig
néhány jelentés után ismeri fel újra.

### További hibaértékek (mindig élnek)

- **Szelepek saját mérése:** az 1 °C alatti vagy 45 °C feletti érték nem számít bele a szoba hőmérsékletébe.
- **Páratartalom:** a 0–100 % tartományon kívüli érték nem emeli a célhőmérsékletet.
- **Kinti hőmérő:** a −60…+60 °C tartományon kívüli érték nem kerül a mintákba (óránként egyszer figyelmeztet a
  naplóban), nehogy tévesen nyári módot kapcsoljon.

### Letiltás és törlés

Ha az integrációt **letiltod** (Beállítások → Eszközök és szolgáltatások → Meross Boiler Sync → Letiltás), a plugin
előbb visszaállítja az emelt szelepeket az eredeti célhőmérsékletükre; korábban a szelep az emelt, maximális célon
maradt volna, mert senki nem állítaná vissza. **Törléskor** ez már korábban is így volt. Ha egy szelep éppen nem
elérhető, azt a plugin nem tudja visszaállítani (letiltásnál a rekordja megmarad, és újra engedélyezéskor
visszaállítódik). Az újratöltés (beállítás módosítása) nem állít vissza: az új példány onnan folytatja.

A **kazán termosztátot** a plugin letiltáskor és törléskor nem kapcsolja ki: abban az állapotban marad, amiben volt.
Ha éppen fűtött, tovább fűt (a beállított célhőmérsékleten), amíg te ki nem kapcsolod, ezért letiltás vagy törlés előtt
kapcsold ki a kazánt, ha nem kell fűtenie.

### Mi történik, ha…?

| Eset | A plugin viselkedése | Teendőd |
|---|---|---|
| A szoba hőmérő nem elérhető (`unavailable`) | A szoba a szelepek saját mérésére vált, a fűtés tovább működik. Az automata szelep szabályzás leáll (a szelep visszakapja az eredeti célt), a kalibráció vár. | Rövid kiesésnél semmi. Tartósnál nézd meg a szenzort. |
| A szoba hőmérő elavult (alap: 6 órája nem jelentett) | Mint fent, és Javítások-értesítés, `sensor_stale` esemény. | Elem cseréje, kapcsolat ellenőrzése. |
| A szoba hőmérő képtelen vagy ugráló értéket ad | Mint fent, 30 percre; Javítások-értesítés, `sensor_unreliable` esemény. | A szenzor ellenőrzése, cseréje. |
| A szoba hőmérő hihető, de rossz értéken ragad | **Nem észleli.** A *szelep állapotához kötés* korlátozza a kazánt; a szelepemelés legfeljebb a beállított maximális ideig tart (alap: 3 óra), utána pihenő. | Kapcsold be a szelep állapotához kötést. |
| A kinti hőmérő nem elérhető, elavult vagy képtelen értéket ad | A plugin a kinti hőmérő utolsó 24 órányi hihető mintájából számol; elavult szenzornál, vagy ha nincs minta, nincs nyári mód, a fűtés engedélyezett marad. A képtelen érték nem kerül a mintákba. | – |
| Egy szelep nem elérhető | A szoba a többi szelepből számol. Ha a szoba összes szelepe kiesett, a szoba nem kér hőt. | – |
| **Az összes** szelep nem elérhető (például a Meross hub kiesett) | A plugin **nem nyúl a kazánhoz**: az az utolsó állapotában marad (ha fűtött, tovább fűt). A szelepek a saját beállított céljukat tartják. | Tartós kiesésnél kapcsold ki a kazánt, és nézd meg a hubot. |
| A szelep elutasít egy parancsot | Nem próbálkozik percenként: 2, 5, 15, 30, majd 60 percenként. Az első hibáról figyelmeztetés és `valve_command_failed` esemény. | A szelep, a hub ellenőrzése. |
| A kazán termosztát nem elérhető | A plugin nem tud kapcsolni, percenként újra próbálja; visszatérése után a pillanatnyi igényt követi. | – |
| A HA újraindul | A mentett állapotból folytatja (szelepemelés eredeti célja, nyári mód, pihenő, kalibráció). 90 másodpercig nem ír. Részletek: *Újraindítás- és összeomlás-állóság*. | – |
| A plugin újratöltése (beállítás módosítása) | Az új példány onnan folytatja; nem állít vissza és nem emel újra feleslegesen. | – |
| Az integráció letiltása | Az emelt szelepek visszakapják az eredeti célt. A kazán az utolsó állapotában marad. | Kapcsold ki a kazánt, ha nem kell fűtenie. |
| Az integráció törlése | Mint letiltásnál, és a plugin tárolt adatai törlődnek. | Ugyanaz. |
| **A HA vagy a hálózat tartósan leáll** (áramszünet, router, összeomlás) | **Semmilyen szoftver nem tud beavatkozni.** A szelepek és a kazán az utolsó állapotukban maradnak: ha egy szelep fel volt emelve, az emelt célon marad (a Meross szelepnek nincs lejárati időzítője), ha a kazán fűtött, tovább fűt. | Ezért ajánlott az automata szelep szabályzást kikapcsolva hagyni, és a HA-tól független védelmet használni (lásd lent). |
| A kazán gyakran kapcsolgat | `short_cycling` jelzés és esemény; a *Kazán védelem* (ha be van kapcsolva) a minimum be / ki idővel véd. | A beállítások és a szelepek ellenőrzése. |

### Ajánlott beállítás, ha magára akarod hagyni

1. **Automata szelep szabályzás: KI** (a szoba szerkesztésénél, szobánként). Ez az egyetlen funkció, ami a szelepet a
   maximumra állítja, és ha a Home Assistant közben tartósan leáll, a szelep az emelt célon marad. A plugin legfeljebb
   3 órát emel, de ehhez futnia kell. Ha mégis bekapcsolod, csökkentsd a *Szelep emelés max. időtartamát*.
2. **Kazán hőigény a szelep állapotához kötve: BE** minden szobánál. A szoba csak akkor kér hőt, ha a szelep a saját
   mérése szerint is nyitva van, így a kazán nem jár akkor, amikor a radiátor már hideg.
3. **Szelep kalibráció: BE** (Funkciók), előbb *próbaüzemben*. Az okot kezeli: a szelep és a szoba mérése közti
   eltérést, ami miatt a szelep korábban zár, mint ahogy a szoba eléri a célt. A **TRV eltolás** (alap 1,0 °C,
   szobánként) pedig azt, hogy a szelep kis hiánynál csak részben nyit: ez a korlátos, biztonságosabb alternatívája
   az 1. pontban említett maximumra emelésnek.
4. **Szoba hőmérő minden szobában**, és ablakérzékelő ott, ahol van. Az **Elavult szenzor figyelése** maradjon
   bekapcsolva, az idő legyen a szenzor szokásos jelentési idejének legalább a kétszerese.
5. **Események BE** (alap) és egy értesítés-automatizmus (lásd lent), hogy a problémáról telefonon értesülj.
6. **Kazán védelem (minimum be / ki idő): BE**, ha a kazánod hajlamos a gyakori kapcsolgatásra.
7. **A HA-tól független védelem:** ha a kazán termosztátnak vagy a kazánnak van saját időzítője, ütemezése vagy
   biztonsági korlátja, használd. Ha a HA leáll, a plugin nem tud beavatkozni.

### Értesítések a fontos eseményekről

```yaml
alias: Fűtés – figyelmeztetések
mode: queued
trigger:
  - platform: event
    event_type: meross_boiler_sync_event
condition:
  - condition: template
    value_template: >
      {% set d = trigger.event.data %}
      {{ d.type in ['sensor_stale', 'sensor_unreliable', 'valve_command_failed',
                    'valve_calibration_suspended', 'short_cycling']
         or (d.type == 'boost_ended' and d.reason == 'max_time') }}
action:
  - service: notify.mobile_app_telefon   # a saját értesítő szolgáltatásod
    data:
      title: "Fűtés"
      message: >
        {% set t = {
          'sensor_stale': 'elavult szenzor',
          'sensor_unreliable': 'a szoba hőmérő nem megbízható, a szelepek mérésére váltottam',
          'valve_command_failed': 'a szelep nem fogadta el a parancsot',
          'valve_calibration_suspended': 'a szelep kalibrációja felfüggesztve',
          'short_cycling': 'a kazán gyakran kapcsolgat',
          'boost_ended': 'a szelepemelés elérte a maximális időt, a szoba nem melegedett fel'
        } %}
        {{ trigger.event.data.room or 'Fűtés' }}: {{ t[trigger.event.data.type] }}
```

## Ablakérzékelő (szobánként)

A szoba beállításainál megadhatsz egy vagy több ablak-/ajtóérzékelőt (`binary_sensor`). Ha az ablak
a **késleltetésnél** tovább nyitva van, a szoba nem kér hőt a kazántól, és a szelep emelés leáll (a szelep
visszakapja az eredeti célját). Becsukáskor a fűtés újraindul. A rövid szellőztetés (a késleltetésnél
rövidebb) nem változtat semmit.

A késleltetés (alap: 5 perc, 0 = azonnal) az Alapbeállításokban adható meg, és szobánként felülírható.
Elérhetetlen ablakérzékelő zártnak számít (nem blokkolja a fűtést). A plugin az ablaknál a szelepet nem zárja,
csak a hőigényt szünetelteti.

## Lovelace kártya

**Felvétel (a kártya nem kerül fel magától semmilyen irányítópultra):**
Irányítópult szerkesztése -> Kártya hozzáadása -> keresd: **Meross Boiler Sync** -> a vizuális szerkesztőben
állítsd be. YAML-ban: `type: custom:meross-boiler-sync-card`.

Az integráció a kártya fájlját magától felveszi az irányítópult **erőforrásai** közé (Beállítások ->
Irányítópultok -> három pont -> Erőforrások), és minden frissítésnél a verziószámát is frissíti, így a
böngésző nem a régit tölti be. Emiatt jelenik meg a "Kártya hozzáadása" listában. Magától semmilyen kártyát
nem tesz fel egyetlen irányítópultra sem.
Telepítés / frissítés után: indítsd újra a HA-t, majd a böngészőben egyszer Ctrl+F5.

Ha korábban kézzel felvetted az erőforrást (`/meross_boiler_sync_static/meross-boiler-sync-card.js`), azt hagyd
békén: az integráció ugyanazt az elemet frissíti, nem csinál mellé másodikat.

Kikapcsolható (Alapbeállítások -> "Lovelace kártya betöltése"): ilyenkor az integráció nem nyúl az
erőforrásokhoz, és te veszed fel kézzel: URL `/meross_boiler_sync_static/meross-boiler-sync-card.js`,
típus: *JavaScript modul*. **YAML módú irányítópultnál** (`resource_mode: yaml`) szintén kézzel kell felvenni:

```yaml
lovelace:
  resources:
    - url: /meross_boiler_sync_static/meross-boiler-sync-card.js
      type: module
```

*Miért erőforrás, és nem a korábbi "extra modul"?* A Home Assistant újabb frontendjében az extra modulként
betöltött kártya versenyhelyzetbe kerül a felület indulásával, és néha "Konfigurációs hiba / Custom element
doesn't exist" üzenet jelenik meg (a töltőikon forog, majd hiba). Az erőforrásként felvett kártya a felület
elindulása után fut le, ezért megbízható.

**Kártyák (2.8-tól kilenc van)**, mind a "Kártya hozzáadása" listában, vizuális szerkesztővel:

| Kártya | `type` | Mire jó |
|---|---|---|
| Meross Boiler Sync | `custom:meross-boiler-sync-card` | szobánkénti csempék (üveg, radiátor, minimál, színátmenetes, lista) |
| Meross Boiler Sync · Áttekintő | `custom:meross-boiler-sync-overview-card` | a kazán, a kinti hőmérséklet, a nyári mód és a szobák egy helyen |
| Meross Boiler Sync · Idővonal | `custom:meross-boiler-sync-timeline-card` | mikor fűtött a kazán és melyik szoba (6 ó / 12 ó / 24 ó / 7 nap) |
| Meross Boiler Sync · Chip-sor | `custom:meross-boiler-sync-chips-card` | egysoros, kompakt állapotjelző (irányítópult tetejére) |
| Meross Boiler Sync · Miért fűt? | `custom:meross-boiler-sync-why-card` | egy mondatban: miért fűt (vagy áll) a kazán, szobánként a hiánnyal és becsléssel |
| Meross Boiler Sync · Figyelmeztetések | `custom:meross-boiler-sync-alerts-card` | csak a bajokat mutatja, ha nincs baj, elrejtőzik |
| Meross Boiler Sync · Szoba részletes | `custom:meross-boiler-sync-room-card` | egy szoba nagy nézete: csempe, 6 / 12 / 24 órás görbe a céllal, szelepek |
| Meross Boiler Sync · Heti hőtérkép | `custom:meross-boiler-sync-heatmap-card` | óránként hány percet fűtött a kazán (vagy egy szoba) az elmúlt 7 / 14 napban |
| Meross Boiler Sync · Fűtési statisztika | `custom:meross-boiler-sync-stats-card` | napi fűtési idő a kinti átlaggal, szobák rangsora, opcionális költségbecslés |

**Dizájnok** (`design`, a csempe kártyán): `glass` (üveg, gyűrűs mérő), `radiator` (radiátor-rajz a bordák
színével, − / + gombbal és profilválasztóval, mint az üveg), `minimal` (kompakt sorok), `gradient`
(színátmenetes csempék), `list` (lista sávval), `heat` (2.8: hőtérkép-csempe: a csempe háttere a szoba
hőmérsékletét mutatja a `heat_min`–`heat_max` skálán; az elavult szenzorú szoba elszürkül).

**Beállítások** (mind a vizuális szerkesztőben is):

| Kulcs | Jelentés | Alap |
|---|---|---|
| `design` | dizájn | `glass` |
| `title` | cím | – |
| `rooms` | megjelenítendő szobák (szenzor azonosítók, sorrend szerint); üres = mind | mind |
| `columns` | oszlopok száma, 0 = automatikus | 0 |
| `size` | az egész tartalom mérete, 70–160 % (100 = alap; az üveg csempe alapból ~250 px széles) | 100 |
| `tap_action` | koppintásra: `valve` (a szelep termosztátja), `sensor` (a hőigény szenzor), `none` | `valve` |
| `show_controls` | − / + gombok a célhőmérséklet módosításához (csak `glass`) | `true` |
| `step` | a gombok lépésköze (°C), 0 = a szelep saját lépésköze | 0 |
| `show_presets` | profil (preset) választó: auto, sleep, comfort… (csak `glass`) | `true` |
| `glow` | ragyogás a csempe körül az aktuális állapot színével (`glass`, `minimal`, `gradient`) | `true` |
| `glow_level` | a ragyogás erőssége, 1–5 | 3 |
| `glow_states` | mely állapotoknál ragyogjon: `idle`, `demand`, `boost`, `waiting`, `rest`, `stale`, `window`, `off` | `off` kivételével mind |
| `animation` | animált dizájn: láng (hőt kér), pulzáló piros alj (elavult szenzor), kék "szél" (ablak nyitva), finom lélegzés a többinél (`glass`); a `radiator`-on a lángot a radiátor fölött felszálló hőhullámok helyettesítik (hőt kér: 3, szelepemelés: 5) | `false` |
| `temp_gradient` | a gyűrű színe a hőmérséklet-skálát követi (hideg kék -> zöld -> sárga -> narancs) az állapotszín helyett (csak `glass`) | `false` |
| `show_trend` | hőmérséklet-trend a csempén: nyíl és °C/óra (a szoba `temperature_trend` attribútumából) | `true` |
| `show_eta` | ha a szoba melegszik és a cél alatt van: becsült idő a cél eléréséig ("kb. 1 ó 35 p"); 6 óránál hosszabb becslést nem mutat | `true` |
| `show_countdown` | visszaszámláló gyűrű az állapotcímke helyén: szelepemelés indulása, pihenő vége, maximális idő, ablak-késleltetés | `true` |
| `smooth` | sima átmenet: a gyűrű, a szám és a sávok az új értékre úsznak, nem ugranak | `true` |
| `show_quick` | gyorsgomb sor a kártya tetején: egy koppintással az összes megjelenített szoba profilja (csak a *minden* szelep által ismert profilok) | `false` |
| `quick_presets` | mely profilok legyenek a gyorsgomb sorban (sorrend szerint); üres = mind | mind |
| `show_header`, `show_boiler`, `show_demand`, `show_summer` | fejléc és elemei | `true` |
| `show_current`, `show_target`, `show_humidity`, `show_deviation`, `show_status`, `show_flags` | szobánkénti elemek | `true` |
| `gauge_min`, `gauge_max` | a gyűrű / sáv skálája (°C) | 15 / 28 |
| `decimals` | tizedesjegyek | 1 |
| `radius`, `opacity`, `blur` | lekerekítés (px), háttér átlátszatlansága (%), elmosás (px) | dizájntól függ |
| `color_idle`, `color_demand`, `color_boost`, `color_waiting`, `color_rest`, `color_stale`, `color_window`, `color_off`, `color_summer` | állapotszínek: `[r, g, b]` vagy `#rrggbb` | beépített |

**Vezérlés a kártyáról (üveg dizájn):** a − / + gomb a szoba szelepének (több szelepnél mindegyiknek)
célhőmérsékletét állítja, a gyors egymás utáni koppintásokat összevonja és egyszer küldi el. **A cél 6 és 34 °C között állítható** (2.10.2-től; ha a szelep saját határa szűkebb, az számít). A határon a gomb
halvány, de kattintható: parancs nélkül, egyetlen rövid üzenetet ("Nem állítható 34° fölé." / "…6° alá.") ad, akárhányszor
nyomják; ugyanez igaz a gyűrű húzására és a részletek lapjára. Ha a szoba minden szelepén már az új érték a cél (pl. + majd −
a gyors koppintásokon belül), felesleges parancs sem megy ki. Ha a szelep mégis elutasít egy parancsot, a kártya egyszer jelez
("A szelep nem fogadta el az értéket."), és nem próbálkozik újra. Ha a plugin
éppen "ráfűt" a szelepre (automata szelepvezérlés), a gombok a *te* eredeti célodat módosítják: a plugin ezt új
beállításnak veszi, és a szoba felmelegedése után erre állítja vissza a szelepet. A profil gomb a szelep
`preset_modes` listáját mutatja, a választás a szoba összes szelepére érvényes. A lista utolsó eleme a **Fűtés ki** (2.10.1-től): a szoba szelepeit kikapcsolja
(`climate.set_hvac_mode: off`), ezt jelzi a szoba "Szelep ki" állapota is. Bármelyik profil kiválasztása újra
bekapcsolja őket (előbb `heat`, ennek hiányában `auto` módba, aztán beállítja a profilt). Csak akkor jelenik meg,
ha a szelep `hvac_modes` listájában szerepel az `off`; az integráció ilyenkor a szobát nem fűti, és megszakítja a
szelepemelést. A gyorsgomb sor ezt nem tartalmazza. Az animáció és a ragyogás a
rendszer "csökkentett mozgás" beállítását is tiszteletben tartja (az animáció ilyenkor nem fut).
A méretezés a böngésző `zoom` tulajdonságát használja (minden modern böngészőben működik; Firefox 126 előtt a
`size` nem hat).

A régi `tap_more_info: false` beállítás továbbra is működik (`tap_action: none`-nak számít).

A `look` kulcs (2.8) **minden kártyán** működik (`glass` / `eink` / `neon`), a vizuális szerkesztőben az "Értékek és megjelenés" szakaszban.

**Hatások és kényelmi funkciók**: mindegyik külön ki/be kapcsolható (a vizuális szerkesztő "Hatások" és
"Vezérlés" szakaszában). Alapból be van kapcsolva a trend, a becslés, a visszaszámláló és a sima átmenet;
alapból ki a hőmérséklet-színes gyűrű, az animáció, a hangulat és a gyorsgomb sor. A gyorsgomb sor a
kiválasztott profilt azonnal jelzi (a HA visszaigazolásáig), kis visszajelzést mutat ("Takarékos · 6 szoba"),
és ha a szobák profilja eltér, "vegyes" jelzést ad. A visszaszámláló gyűrű másodpercenként frissül, a trend
és a becslés csak akkor jelenik meg, ha a szoba szenzora már legalább 10 perce ad mérést.

### Új csempe-funkciók (2.8-tól, mind külön kapcsolható)

A vizuális szerkesztő **Új funkciók** szakaszában. Alapból minden ki van kapcsolva, kivéve a hosszú nyomás lapot,
tehát a meglévő kártyád ugyanúgy néz ki és működik, mint eddig.

| Kulcs | Jelentés | Alap |
|---|---|---|
| `show_sparkline` | minigrafikon a csempén (`glass`, `radiator`, `gradient`, `list`): a szoba hőmérséklete az elmúlt `sparkline_hours` órában. Bekapcsolva a kártya előzményt kér a HA-tól (5 percenként frissül), kikapcsolva nem kér semmit | `false` |
| `sparkline_hours` | a minigrafikon időtartama: `6`, `12`, `24` | 24 |
| `drag_target` | a célhőmérséklet a gyűrű körül **húzással** állítható (lépésköz-igazítással; elengedéskor egyetlen szolgáltatás-hívás megy a szelepre) | `false` |
| `hold_action` | **hosszú nyomás** (0,6 s) a csempén: `sheet` (részletes lap: görbe, − / + gombok, profilok, szelepek), `more-info`, `none` | `sheet` |
| `look` | megjelenés: `glass` (alap), `eink` (e-ink: papírszín, vastag keret, az állapotot minta is jelzi, nem csak szín), `neon` | `glass` |
| `night_mode`, `night_from`, `night_to`, `night_dim` | éjszakai mód: a megadott időszakban (alap 22:00–06:00; éjfélen átnyúlhat) a kártya elsötétül (`night_dim` %, alap 70), az animációk leállnak | `false` |
| `heat_min`, `heat_max` | a `heat` dizájn hőmérséklet-skálája (°C) | 17 / 25 |

A hosszú nyomás utáni elengedés nem nyit `more-info`-t; ha közben elmozdítod az ujjad (görgetés), a hosszú
nyomás megszakad. A lap Esc-re, a sötét háttérre koppintva, lehúzva vagy a × gombbal zárható.

### Fűts most és előfűtés a kártyákon (2.9-től, mind külön kapcsolható)

A funkciókat az integrációban is be kell kapcsolni (lásd fent); ha ki vannak kapcsolva, a kártyán nem jelenik
meg semmi.

| Kulcs | Hol | Jelentés | Alap |
|---|---|---|---|
| `show_boost` | csempe (üveg és radiátor dizájn), lap, Szoba kártya | **Fűts most** gomb (láng). Koppintásra felugró kérdezi: "Mennyi ideig fűtsön?" (30 p / 1 ó / 1 ó 30 p / 2 ó, az alapérték kiemelve). Közben a címke helyén **visszaszámláló** ("Fűtés most 47 p") áll lemondás (×) gombbal, a gyűrűn szaggatott jelölő és "+2,0°" címke mutatja a megemelt célt. Ha a szoba nem fűthető (nyitott ablak, elavult hőmérő, nyári mód, kikapcsolt szoba), a gomb halvány, és koppintásra megmondja az okot. | csempe: `false`, Szoba: `true` |
| `show_preheat` | csempe (üveg és radiátor), lap, Szoba kártya | **Előfűtés jelzés**: "Előfűtés 05:10" (ha 6 órán belül indul), az indulás előtti utolsó 10 percben visszaszámláló, fűtés közben "Előfűt · Kész 06:30 · 21,0°", elérve "Kész · tartja", ha nem érhető el időben, piros figyelmeztetés. A lapon és a Szoba kártyán teljes doboz: indulás, kész időpont, cél, tanult sebesség és **Kihagyás** (egyszeri kérésnél **Mégse**) gomb. | csempe: `false`, Szoba: `true` |
| `alert_preheat` | Figyelmeztetések | figyelmeztetés, ha az előfűtés már nem érheti el időben a célt | `true` |
| `show_rates` | Statisztika | szobánként a tanult melegedési sebesség (°C/ó), sávokkal; a még nem tanult szoba halványan az alapértéket mutatja | `false` |

A **Miért fűt?** kártya jegyzetei külön beállítás nélkül mutatják a futó Fűts most-ot és az előfűtés állapotát.
Az előfűtés és a Fűts most a többi tervezet (minimal, gradient, list, heat) csempéin nem jelenik meg, de a hosszú
nyomás lapon igen. A kigyúlt láng gomb a lemondás gombja is, ha a visszaszámláló ki van kapcsolva.

### Miért fűt? kártya

```yaml
type: custom:meross-boiler-sync-why-card
```

Egy mondat a tetején ("A kazán fűt: Dolgozó és Hálószoba hidegebb a célnál"), alatta szobánként a hiány, a
trend és a becsült idő, majd jegyzetek (nyitott ablak, elavult szenzor, várakozó szelepemelés). Eseteket
különböztet meg: fűt / még fut (nincs hőigény, de a kazán még be van kapcsolva) / vár (hőigény van, a kazán
még nem indult el) / áll / nyári mód.

| Kulcs | Jelentés | Alap |
|---|---|---|
| `show_list` | a szobák listája a mondat alatt | `true` |
| `max_rows` | a lista legfeljebb ennyi sort mutat, a többit "további N szoba" | 5 |
| `show_notes` | jegyzetek: ablak, elavult szenzor, várakozó / aktív szelepemelés | `true` |
| `compact` | csak a mondat (nincs lista, nincs jegyzet) | `false` |
| `show_countdown` | visszaszámláló a jegyzetekben | `true` |
| (nincs külön kulcs) | a futó "Fűts most" és az előfűtés jegyzete (2.9) a `show_notes`-szal együtt jelenik meg | |
| `title`, `rooms`, `size`, `tap_action`, `decimals`, `look`, `color_*` | mint a csempe kártyán | |

### Figyelmeztetések kártya

```yaml
type: custom:meross-boiler-sync-alerts-card
```

Csak a bajokat mutatja, súlyosság szerint rendezve: elavult szenzor, elérhetetlen szelep vagy kazán, tovább
nyitva felejtett ablak, a szelepemelés elérte a maximális időt, gyakori kazán-kapcsolgatás. **Ha nincs baj, a
kártya elrejtőzik** (az irányítópult szerkesztő módjában ilyenkor is látszik). Elrejtőzéskor a HA 
`card-visibility-changed` eseményt kap, így szekcióban, rácsban sem marad üres hely.

| Kulcs | Jelentés | Alap |
|---|---|---|
| `alert_stale`, `alert_unavailable`, `alert_window`, `alert_max_boost`, `alert_cycling`, `alert_preheat` | a figyelmeztetés-típusok külön kapcsolhatók (`alert_preheat`: az előfűtés nem éri el időben a célt, 2.9) | `true` |
| `window_minutes` | ennyi perc után számít "tovább nyitva felejtettnek" az ablak | 20 |
| `show_when_ok` | ha nincs baj, zöld "minden rendben" sáv a rejtőzés helyett | `false` |
| `compact` | egy sáv a legsúlyosabb bajjal és "+N további" jelzéssel; koppintásra kinyílik | `false` |
| `show_cycles` | a kazán ciklusainak sávja (a Kazán indítások szenzorból) | `false` |
| `title`, `rooms`, `size`, `tap_action`, `look`, `color_*` | mint a csempe kártyán | |

### Szoba részletes kártya

```yaml
type: custom:meross-boiler-sync-room-card
room: binary_sensor.dolgozo_futesi_igeny
hours: 24
```

Egy szoba nagy nézete: bal oldalon a csempe (gyűrű, − / + gombok, profilok), mellette a szoba hőmérsékletének
görbéje a céllal, a hőt kérő és a szelepemelés sávjaival, az ablak nyitva és az elavult szenzor jelzésével;
alatta a szelepek külön sorban. Az előzményt a HA `recorder`-éből kéri (5 percenként frissül).

| Kulcs | Jelentés | Alap |
|---|---|---|
| `room` | a szoba hőigény szenzora (a vizuális szerkesztőben legördülő) | – |
| `hours` | a görbe időtartama: `6`, `12`, `24` | 24 |
| `show_chart`, `show_valves`, `show_controls`, `show_presets` | a blokkok külön kapcsolhatók (grafikon nélkül nincs előzmény-lekérés) | `true` |
| `show_boost`, `show_preheat` | a **Fűts most** gomb és az előfűtés doboza a diagram alatti sorban (2.9) | `true` |
| `show_trend`, `show_eta`, `show_countdown`, `smooth`, `step`, `gauge_min`, `gauge_max` | mint a csempe kártyán | |
| `title`, `size`, `tap_action`, `decimals`, `look`, `color_*` | mint a csempe kártyán | |

### Heti hőtérkép kártya

```yaml
type: custom:meross-boiler-sync-heatmap-card
days: 14
entity: boiler
```

Napok × 24 óra rács: egy cella színe az adott órában a fűtéssel töltött percek számát mutatja (0–60). A mai nap
még nem elteltelt órái üresek. Egy cellára koppintva / ráállva felugró részlet jelenik meg ("37 perc fűtés").
Alatta összegzés: napi átlag, csúcsóra, leghosszabb fűtés. A fejlécben választósáv: kazán vagy egy-egy szoba.
Könnyített előzmény-lekérdezést használ (csak ki/be állapotok).

| Kulcs | Jelentés | Alap |
|---|---|---|
| `entity` | a kezdeti nézet: `boiler` vagy egy szoba hőigény szenzora | `boiler` |
| `days` | `7` vagy `14` | 7 |
| `show_selector` | a kazán / szobák választósáv | `true` |
| `show_summary` | az összegzés a térkép alatt | `true` |
| `title`, `rooms`, `size`, `look`, `color_*` | mint a csempe kártyán | |

Ha a kazán termosztátnak nincs előzménye, a kazán nézet a szobák uniójából számol.

### Fűtési statisztika kártya

```yaml
type: custom:meross-boiler-sync-stats-card
days: 7
show_cost: true
gas_price: 120
```

Naponta egy oszlop a kazán fűtési idejével, mellette a kinti napi átlag vonala (a nyári mód szenzorban megadott
kinti szenzorból). Mutatók: összes fűtési idő, napi átlag, kinti átlag. Alatta a szobák rangsora (kinek
mennyit kért a fűtés). Előzmény: `recorder`.

| Kulcs | Jelentés | Alap |
|---|---|---|
| `days` | `7`, `14`, `30` | 7 |
| `show_outdoor` | kinti átlag vonal és mutató | `true` |
| `show_rooms` | szobák rangsora | `true` |
| `show_cost` | **költségbecslés** (fűtési idő × gázfogyasztás × ár) | `false` |
| `gas_m3_per_hour` | a kazán gázfogyasztása óránként (m³), a kazán adatlapján található | 1.6 |
| `gas_price` | a gáz ára m³-enként; ha 0, csak a gázfogyasztást (m³) mutatja | 0 |
| `currency` | pénznem felirata | `Ft` |
| `show_rates` | szobánként a tanult melegedési sebesség (°C/óra), 2.9 | `false` |
| `show_cycles` | a kazán indításainak blokkja (a Kazán indítások szenzorból) | `false` |
| `title`, `rooms`, `size`, `look`, `color_*` | mint a csempe kártyán | |

A költség **becslés**: a kazán bekapcsolt idejéből számol, nem mért gázfogyasztásból. A kazán valós
(modulált) teljesítménye ennél kisebb lehet.

### Áttekintő kártya

```yaml
type: custom:meross-boiler-sync-overview-card
title: Fűtés
ambience: true
show_quick: true
quick_presets: [auto, eco, comfort]
```

Három blokk (kazán, kinti hőmérséklet a küszöbbel és a 24 órás átlaggal, nyári mód) és alatta a szobák egy
"csőrendszeren": ha a kazán fűt, a hőt kérő szobák felé folyamatos animáció fut.

| Kulcs | Jelentés | Alap |
|---|---|---|
| `title`, `rooms`, `size`, `tap_action`, `decimals`, `radius`, `opacity`, `blur`, `color_*` | mint a csempe kártyán | |
| `show_boiler`, `show_outdoor`, `show_summer`, `show_rooms` | a blokkok külön kapcsolhatók | `true` |
| `flow_animation` | a kazánból a szobák felé futó hőáramlás-animáció | `true` |
| `ambience` | hangulat a háttérben: hóesés (kint ≤ 1 °C), napsugár (nyári mód aktív) | `false` |
| `smooth` | sima átmenetek | `true` |
| `show_quick`, `quick_presets` | gyorsgomb sor (mint a csempe kártyán) | `false` |

### Idővonal kártya

```yaml
type: custom:meross-boiler-sync-timeline-card
hours: 24
```

Sávokat rajzol a HA előzményeiből (`recorder`; a szoba szenzorok és a kazán termosztát múltja): a kazán sora
és szobánként egy sor, a sor végén a fűtési idő. A sávok: hőt kért, szelep kinyitva, ablak nyitva, elavult
szenzor. A jobb szél mindig az élő állapotot mutatja. 6 / 12 / 24 órás nézetben az állapot-attribútumok is
bekerülnek (szelepemelés, ablak, elavult szenzor); a **7 napos nézet könnyített lekérdezést használ, ezért
csak a "hőt kért" és a kazán sávjait mutatja**. A kártya 5 percenként, illetve állapotváltáskor frissít.
Ha a `recorder` ki van kapcsolva vagy az előzmények törölve vannak, üres állapotot mutat.

| Kulcs | Jelentés | Alap |
|---|---|---|
| `title`, `rooms`, `size`, `tap_action`, `radius`, `opacity`, `blur`, `color_*` | mint a csempe kártyán | |
| `hours` | az időtartam: `6`, `12`, `24`, `168` (7 nap) | `24` |
| `show_range` | az időtartam-választó gombok | `true` |
| `show_boiler_row` | a kazán sora (ha nincs a kazánnak előzménye, a szobák uniójából számol) | `true` |
| `show_total` | a kazán összes fűtési ideje a fejlécben | `true` |
| `show_legend` | jelmagyarázat | `true` |
| `intro_animation` | a sávok betöltéskor "kifutnak" | `true` |

### Chip-sor kártya

```yaml
type: custom:meross-boiler-sync-chips-card
style: chip_target
```

| Kulcs | Jelentés | Alap |
|---|---|---|
| `style` | `chip` (állapotikon + hőmérséklet), `chip_target` (+ célhőmérséklet), `dot` (színes pont + érték) | `chip` |
| `show_summary` | összegző chip: kazán állapota és a hőt kérő szobák száma | `true` |
| `rooms`, `size`, `tap_action`, `decimals`, `radius`, `opacity`, `blur`, `color_*` | mint a csempe kártyán | |

A kártya a szobákat az integráció szenzoraiból ismeri fel, a kazánt a nyári mód szenzor `boiler_entity`
attribútumából. A színek, a háttér és a betűk a HA témádhoz igazodnak.

Példa:

```yaml
type: custom:meross-boiler-sync-card
design: gradient
title: Fűtés
columns: 4
gauge_min: 16
gauge_max: 26
color_demand: [255, 120, 0]
```

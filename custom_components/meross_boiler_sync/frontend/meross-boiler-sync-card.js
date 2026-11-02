/*!
 * Meross Boiler Sync – Lovelace kártyák / Lovelace cards
 * Verzió / version: 2.8.0
 *
 * Felvétel: Irányítópult szerkesztése → Kártya hozzáadása → "Meross Boiler Sync".
 * Add: Edit dashboard → Add card → "Meross Boiler Sync".
 *
 * Kártyák / cards:
 *   type: custom:meross-boiler-sync-card            (csempék / tiles: glass, radiator, minimal, gradient, list)
 *   type: custom:meross-boiler-sync-overview-card   (áttekintő / overview)
 *   type: custom:meross-boiler-sync-timeline-card   (fűtési idővonal / heating timeline)
 *   type: custom:meross-boiler-sync-chips-card      (chip-sor / chip row)
 *   type: custom:meross-boiler-sync-why-card        (miért fűt a kazán / why is the boiler heating)
 *   type: custom:meross-boiler-sync-room-card       (szoba részletes / room detail)
 *   type: custom:meross-boiler-sync-heatmap-card    (heti hőtérkép / weekly heat map)
 *   type: custom:meross-boiler-sync-stats-card      (fűtési statisztika / heating statistics)
 *   type: custom:meross-boiler-sync-alerts-card     (figyelmeztetések / alerts)
 */
(() => {
  "use strict";
  const TAG = "meross-boiler-sync-card";
  const EDITOR_TAG = "meross-boiler-sync-card-editor";
  const OVERVIEW_TAG = "meross-boiler-sync-overview-card";
  const TIMELINE_TAG = "meross-boiler-sync-timeline-card";
  const CHIPS_TAG = "meross-boiler-sync-chips-card";
  const WHY_TAG = "meross-boiler-sync-why-card";
  const ROOM_TAG = "meross-boiler-sync-room-card";
  const HEATMAP_TAG = "meross-boiler-sync-heatmap-card";
  const STATS_TAG = "meross-boiler-sync-stats-card";
  const ALERTS_TAG = "meross-boiler-sync-alerts-card";
  if (customElements.get(TAG)) return;

  /* ===================================================================
   *  Fordítások (hu / en)
   * =================================================================== */
  const STR = {
    en: {
      st_idle: "Not calling", st_demand: "Calling for heat", st_boost: "Valve forced open",
      st_waiting: "Waiting", st_rest: "Resting", st_stale: "Stale sensor",
      st_window: "Window open", st_windowpend: "Window opening…", st_off: "Valve off",
      target: "Target", boiler: "Boiler", on: "On", off: "Off", calling: "Calling",
      rooms_word: "rooms", outdoor: "Outdoor", avg24: "24 h avg", summer: "Summer mode",
      active: "Active", inactive: "Inactive", valve_control: "Automatic valve control",
      link: "Boiler demand tied to valve", dry: "Dry run", no_data: "No data",
      no_rooms: "No rooms found. Add rooms in the Meross Boiler Sync integration (Configure).",
      description: "Rooms, heat demand and summer mode of the Meross Boiler Sync integration.",
      // szerkesztő
      sec_general: "General", sec_show: "What to show", sec_values: "Values and look", sec_colors: "Colors",
      design: "Design", d_glass: "Glass – ring gauge", d_radiator: "Radiator – glowing fins", d_minimal: "Minimal – compact rows",
      d_gradient: "Gradient tiles", d_list: "List – table with bar",
      title: "Title (optional)", rooms: "Rooms to show",
      h_rooms: "Leave empty to show all rooms. The order is the order you pick them in.",
      columns: "Columns", h_columns: "0 = automatic (fits the card width)",
      show_header: "Show header", show_boiler: "Boiler state", show_demand: "Number of rooms calling for heat",
      show_summer: "Summer mode and outdoor temperature", show_current: "Current temperature",
      show_target: "Target temperature", show_humidity: "Humidity", show_deviation: "Deviation from target",
      show_status: "Status chip", show_flags: "Flags (valve control, link, dry run)",
      gauge_min: "Gauge minimum (°C)", gauge_max: "Gauge maximum (°C)", decimals: "Decimals",
      radius: "Corner radius (px)", opacity: "Background opacity (%)", blur: "Background blur (px)",
      h_gauge: "The ring / bar scale", reset_colors: "Reset colors",
      color_idle: "Color: not calling", color_demand: "Color: calling for heat", color_boost: "Color: valve forced open",
      color_waiting: "Color: waiting", color_rest: "Color: resting", color_stale: "Color: stale sensor",
      color_window: "Color: window open", color_off: "Color: valve off", color_summer: "Color: summer mode",
      editor_no_rooms: "No Meross Boiler Sync rooms found yet – the room list will fill in once they exist.",
      // v2.6
      increase: "Raise target temperature", decrease: "Lower target temperature", preset_word: "Profile",
      size: "Card size (%)", h_size: "Scales the whole card content (100 = default).",
      tap_action: "Action on tap", ta_valve: "Open the valve thermostat", ta_sensor: "Open the heat demand sensor", ta_none: "Nothing",
      sec_controls: "Controls on the card", show_controls: "− / + buttons (glass and radiator designs)",
      step: "Step (°C)", h_step: "0 = automatic (the valve's own step)",
      show_presets: "Profile (preset) selector (glass and radiator designs)",
      sec_effects: "Effects", glow: "Glow around the card", glow_level: "Glow strength (1–5)",
      glow_states: "Glow in these states", h_glow_states: "Pick the states where the glow is shown.",
      animation: "Animations (flames, heat waves, wind, alarm)", h_animation: "Glass and radiator designs. Turns itself off when the system asks for reduced motion.",
      p_auto: "Auto", p_sleep: "Sleep", p_comfort: "Comfort", p_eco: "Eco", p_away: "Away", p_home: "Home",
      p_manual: "Manual", p_boost: "Boost", p_none: "None",
      // v2.7 – hatások
      temp_gradient: "Temperature-coloured ring (glass)", h_temp_gradient: "The ring runs from blue (cold) through green and yellow to orange (warm).",
      show_trend: "Temperature trend", h_show_trend: "Shows whether the room is warming or cooling. Needs about 10 minutes of data after a restart.",
      show_eta: "Estimated time to reach the target", show_countdown: "Countdown rings",
      h_show_countdown: "Timers for waiting, boost, rest and the window delay.",
      smooth: "Smooth transitions", h_smooth: "The ring slides and the number rolls to the new value. Off when the system asks for reduced motion.",
      trend_flat: "steady", per_h: "°/h", eta_word: "about", unit_h: "h", unit_min: "min",
      cd_start: "Waiting", cd_max: "Boost", cd_rest: "Rest", cd_win: "Window",
      // gyorsgombok
      show_quick: "Quick preset bar (all rooms at once)", quick_presets: "Quick preset buttons",
      h_quick_presets: "Empty = every preset that all valves support.",
      quick_all: "All rooms", quick_mixed: "mixed", quick_applied: "rooms updated",
      // áttekintő
      card_overview: "Meross Boiler Sync · Overview", desc_overview: "Boiler, outdoor temperature, summer mode and a pipe diagram of the rooms.",
      sec_blocks: "Blocks", show_outdoor: "Outdoor temperature", show_rooms: "Rooms (pipe diagram)",
      flow_animation: "Heat-flow animation", h_flow_animation: "Dashed lines flow from the boiler to the rooms that call for heat.",
      ambience: "Seasonal ambience (snow / sun)", h_ambience: "Snow near freezing, a soft sun in summer mode.",
      rooms_calling: "rooms calling for heat", no_demand: "No heat demand", threshold_word: "threshold", period_word: "period",
      // idővonal
      card_timeline: "Meross Boiler Sync · Timeline", desc_timeline: "A bar per room: when it called for heat, when the valve was forced open, window and sensor problems.",
      tl_default: "Heating timeline", tl_total: "Boiler total", hours: "Time range",
      hr_6: "6 h", hr_12: "12 h", hr_24: "24 h", hr_168: "7 days",
      show_range: "Time range buttons", show_total: "Boiler total", show_boiler_row: "Boiler row",
      show_legend: "Legend", intro_animation: "Loading animation",
      lg_demand: "calling for heat", lg_boost: "valve forced open", lg_window: "window open", lg_stale: "stale sensor",
      tl_loading: "Loading…", tl_empty: "No history available. Is the recorder enabled for these sensors?",
      tl_week_note: "In the 7-day view only the heat demand is shown.", now: "now",
      // chip-sor
      card_chips: "Meross Boiler Sync · Chip row", desc_chips: "A compact row of chips with the temperature of each room.",
      style: "Style", s_chip: "Chip", s_chip_target: "Chip + target", s_dot: "Dot",
      show_summary: "Boiler summary chip", sum_on: "On", sum_off: "Off",
    },
    hu: {
      st_idle: "Nem kér hőt", st_demand: "Hőt kér", st_boost: "Szelep kinyitva",
      st_waiting: "Vár", st_rest: "Pihenő", st_stale: "Elavult szenzor",
      st_window: "Ablak nyitva", st_windowpend: "Ablak nyílik…", st_off: "Szelep ki",
      target: "Cél", boiler: "Kazán", on: "Be", off: "Ki", calling: "Hőt kér",
      rooms_word: "szoba", outdoor: "Kint", avg24: "24 órás átlag", summer: "Nyári mód",
      active: "Aktív", inactive: "Nem aktív", valve_control: "Automata szelepvezérlés",
      link: "Kazán hőigény a szelephez kötve", dry: "Próbaüzem", no_data: "Nincs adat",
      no_rooms: "Nem találok szobát. Adj hozzá szobákat a Meross Boiler Sync integrációban (Konfigurálás).",
      description: "A Meross Boiler Sync integráció szobái, hőigénye és nyári módja.",
      sec_general: "Általános", sec_show: "Mit mutasson", sec_values: "Értékek és megjelenés", sec_colors: "Színek",
      design: "Dizájn", d_glass: "Üveg – gyűrűs mérő", d_radiator: "Radiátor – izzó bordák", d_minimal: "Minimál – kompakt sorok",
      d_gradient: "Színátmenetes csempék", d_list: "Lista – táblázat sávval",
      title: "Cím (opcionális)", rooms: "Megjelenítendő szobák",
      h_rooms: "Üresen hagyva az összes szoba megjelenik. A sorrend a kiválasztás sorrendje.",
      columns: "Oszlopok száma", h_columns: "0 = automatikus (a kártya szélességéhez igazodik)",
      show_header: "Fejléc megjelenítése", show_boiler: "Kazán állapota", show_demand: "Hőt kérő szobák száma",
      show_summer: "Nyári mód és kinti hőmérséklet", show_current: "Aktuális hőmérséklet",
      show_target: "Célhőmérséklet", show_humidity: "Páratartalom", show_deviation: "Eltérés a céltól",
      show_status: "Állapotcímke", show_flags: "Jelzők (szelepvezérlés, kötés, próbaüzem)",
      gauge_min: "Mérő alsó értéke (°C)", gauge_max: "Mérő felső értéke (°C)", decimals: "Tizedesjegyek",
      radius: "Sarkok lekerekítése (px)", opacity: "Háttér átlátszatlansága (%)", blur: "Háttér elmosása (px)",
      h_gauge: "A gyűrű / sáv skálája", reset_colors: "Színek visszaállítása",
      color_idle: "Szín: nem kér hőt", color_demand: "Szín: hőt kér", color_boost: "Szín: szelep kinyitva",
      color_waiting: "Szín: vár", color_rest: "Szín: pihenő", color_stale: "Szín: elavult szenzor",
      color_window: "Szín: ablak nyitva", color_off: "Szín: szelep ki", color_summer: "Szín: nyári mód",
      editor_no_rooms: "Még nincs Meross Boiler Sync szoba – a szobalista akkor töltődik fel, ha lesznek.",
      // v2.6
      increase: "Célhőmérséklet növelése", decrease: "Célhőmérséklet csökkentése", preset_word: "Profil",
      size: "Kártya mérete (%)", h_size: "Az egész kártya tartalmát skálázza (100 = alap).",
      tap_action: "Koppintás művelete", ta_valve: "A szelep termosztátjának megnyitása", ta_sensor: "A hőigény szenzor megnyitása", ta_none: "Semmi",
      sec_controls: "Vezérlés a kártyán", show_controls: "− / + gombok (üveg és radiátor dizájn)",
      step: "Lépésköz (°C)", h_step: "0 = automatikus (a szelep saját lépésköze)",
      show_presets: "Profil (preset) választó (üveg és radiátor dizájn)",
      sec_effects: "Hatások", glow: "Ragyogás a kártya körül", glow_level: "Ragyogás erőssége (1–5)",
      glow_states: "Mely állapotoknál ragyogjon", h_glow_states: "Jelöld ki azokat az állapotokat, ahol a ragyogás látszik.",
      animation: "Animációk (láng, hőhullám, szél, riasztás)", h_animation: "Üveg és radiátor dizájnnál. Magától kikapcsol, ha a rendszer csökkentett mozgást kér.",
      p_auto: "Auto", p_sleep: "Alvás", p_comfort: "Komfort", p_eco: "Takarékos", p_away: "Távol", p_home: "Itthon",
      p_manual: "Kézi", p_boost: "Boost", p_none: "Nincs",
      // v2.7 – hatások
      temp_gradient: "Hőmérséklet-színes gyűrű (üveg)", h_temp_gradient: "A gyűrű kéktől (hideg) zölden és sárgán át narancsig (meleg) színeződik.",
      show_trend: "Hőmérséklet trend", h_show_trend: "Megmutatja, hogy a szoba melegszik vagy hűl. Újraindítás után kb. 10 perc adat kell hozzá.",
      show_eta: "Becsült idő a cél eléréséig", show_countdown: "Visszaszámláló gyűrűk",
      h_show_countdown: "A várakozás, az emelés, a pihenő és az ablak-késleltetés időzítői.",
      smooth: "Sima átmenetek", h_smooth: "A gyűrű odacsúszik, a szám odagördül az új értékre. Csökkentett mozgásnál magától kikapcsol.",
      trend_flat: "stabil", per_h: "°/ó", eta_word: "kb.", unit_h: "ó", unit_min: "p",
      cd_start: "Vár", cd_max: "Emel", cd_rest: "Pihenő", cd_win: "Ablak",
      // gyorsgombok
      show_quick: "Gyorsgombok (minden szobára egyszerre)", quick_presets: "Gyorsgomb profilok",
      h_quick_presets: "Üresen: minden profil, amit az összes szelep ismer.",
      quick_all: "Mindenhol", quick_mixed: "vegyes", quick_applied: "szobára alkalmazva",
      // áttekintő
      card_overview: "Meross Boiler Sync · Áttekintő", desc_overview: "Kazán, kinti hőmérséklet, nyári mód és a szobák egy csővezeték-rajzon.",
      sec_blocks: "Blokkok", show_outdoor: "Kinti hőmérséklet", show_rooms: "Szobák (csővezeték)",
      flow_animation: "Hőáramlás animáció", h_flow_animation: "Szaggatott vonal áramlik a kazántól a hőt kérő szobákhoz.",
      ambience: "Évszakhangulat (hó / nap)", h_ambience: "Fagypont körül hóesés, nyári módban finom nap.",
      rooms_calling: "szoba kér hőt", no_demand: "Nincs hőigény", threshold_word: "küszöb", period_word: "időszak",
      // idővonal
      card_timeline: "Meross Boiler Sync · Idővonal", desc_timeline: "Szobánként egy sáv: mikor kért hőt, mikor emelt a szelep, ablak- és szenzorhibák.",
      tl_default: "Fűtési idővonal", tl_total: "Kazán összesen", hours: "Időtartam",
      hr_6: "6 ó", hr_12: "12 ó", hr_24: "24 ó", hr_168: "7 nap",
      show_range: "Időtartam gombok", show_total: "Kazán összesen", show_boiler_row: "Kazán sor",
      show_legend: "Jelmagyarázat", intro_animation: "Betöltési animáció",
      lg_demand: "hőt kért", lg_boost: "szelep kinyitva", lg_window: "ablak nyitva", lg_stale: "elavult szenzor",
      tl_loading: "Betöltés…", tl_empty: "Nincs előzmény. Be van kapcsolva a recorder ezekhez a szenzorokhoz?",
      tl_week_note: "A 7 napos nézetben csak a hőigény látszik.", now: "most",
      // chip-sor
      card_chips: "Meross Boiler Sync · Chip-sor", desc_chips: "Kompakt sor chipekkel: szobánként a hőmérséklet.",
      style: "Stílus", s_chip: "Chip", s_chip_target: "Chip + cél", s_dot: "Pont",
      show_summary: "Kazán összesítő chip", sum_on: "Be", sum_off: "Ki",
    },
  };
  const langOf = (hass) => {
    const l = ((hass && (hass.locale && hass.locale.language || hass.language)) || navigator.language || "en").toLowerCase();
    return l;
  };
  const T = (hass, key) => {
    const l = langOf(hass).startsWith("hu") ? "hu" : "en";
    return (STR[l] && STR[l][key]) || STR.en[key] || key;
  };

  /* ===================================================================
   *  Fordítások (2.8): új kártyák és funkciók
   * =================================================================== */
  Object.assign(STR.hu, {
    ago_now: "most", ago_min: "{n} perce", ago_h: "{n} órája", ago_d: "{n} napja",
    // kazán ciklusok
    cyc_title: "Kazán ciklusok (utolsó 6 óra)", cyc_starts_h: "Indítások az utolsó órában", cyc_per_h: "/ óra", cyc_limit: "határ:",
    cyc_avg_on: "Átlag bekapcsolva", cyc_min: "alsó határ:", cyc_avg_off: "Átlag kikapcsolva", cyc_24h: "Elmúlt 24 óra", cyc_starts: "indítás",
    // miért fűt
    card_why: "Meross Boiler Sync · Miért fűt?", desc_why: "Egy mondatban megmondja, miért fűt (vagy miért áll) a kazán, szobánként a hiánnyal és becsléssel.",
    why_heat_a: "A kazán <b>fűt</b>, mert a ", why_join: ", a ", why_join_last: " és a ", why_heat_b1: " hideg.", why_heat_bn: " hideg.", why_more: "további",
    why_wait: "A szobák hőt kérnek, a kazán még <b>vár</b> (minimális kapcsolási idő).",
    why_cool: "A kazán még <b>fut</b>, de már nincs hőigény: hamarosan leáll.",
    why_idle: "A kazán <b>áll</b>: minden szoba eléri a célhőmérsékletet.",
    why_summer_avg: "A kazán <b>nyári módban</b> áll: kint a 24 órás átlag <b>{avg}°</b>, a küszöb {thr}°.", why_summer: "A kazán <b>nyári módban</b> áll.",
    why_reached: "cél elérve", why_from_target: "a céltól",
    why_n_window: "az ablak nyitva, ezért nem kér hőt", why_n_windowpend: "az ablak nyitva, {t} múlva a szoba szünetel",
    why_n_stale: "elavult szenzor, a szelep saját mérését használja", why_n_waiting: "a szelepemelés {t} múlva indul",
    why_n_rest: "pihenő, még {t} amíg újra emelhet", why_n_boost: "a szelep ki van nyitva, legfeljebb még {t}",
    why_n_period: "Nyári időszak: {from} – {to} · a szobák hőt kérhetnek, de a kazán nem indul",
    show_list: "Szobák listája", show_notes: "Jegyzetek (ablak, elavult szenzor, várakozás)", compact: "Kompakt (csak a mondat)", max_rows: "Legfeljebb ennyi sor",
    // figyelmeztetések
    card_alerts: "Meross Boiler Sync · Figyelmeztetések", desc_alerts: "Csak a bajokat mutatja: elavult szenzor, nyitva felejtett ablak, elérhetetlen szelep, gyakori kapcsolgatás. Ha nincs baj, elrejtőzik.",
    al_boiler_unavail: "Kazán: nem elérhető", al_boiler_unavail_s: "A kazán termosztát nem válaszol, a fűtés nem vezérelhető",
    al_cycling: "Kazán: gyakori kapcsolgatás", al_cycling_sub: "{n} indítás az elmúlt órában (átlag {m} perc bekapcsolva)", al_cycling_sub1: "{n} indítás az elmúlt órában",
    al_valve_unavail: "{room}: a szelep nem elérhető", al_valve_unavail_s: "Nem érkezik adat a szelepről",
    al_stale: "{room}: elavult szenzor", al_stale_sub: "A hőmérséklet {ago} nem frissült, a szelep saját mérése számít", al_stale_sub0: "A hőmérséklet régóta nem frissült, a szelep saját mérése számít",
    al_maxboost: "{room}: elérte a maximális szelepemelést", al_maxboost_sub: "A szelep visszaáll, {m} percig nem emel újra", al_maxboost_sub0: "A szelep visszaáll, pihenő következik",
    al_window: "{room}: az ablak nyitva", al_window_sub: "A fűtés szünetel; {ago} nyitva van", al_window_sub0: "A fűtés szünetel",
    al_ok: "Minden rendben · {n} szoba, a kazán normálisan fut", al_empty_preview: "Nincs figyelmeztetés: a kártya ilyenkor elrejti magát.", al_more: "további",
    window_minutes: "Ablak figyelmeztetés ennyi perc után", show_when_ok: "„Minden rendben” chip, ha nincs baj",
    alert_stale: "Elavult szenzor", alert_unavailable: "Elérhetetlen szelep / kazán", alert_window: "Nyitva felejtett ablak", alert_max_boost: "Maximális szelepemelés", alert_cycling: "Gyakori kapcsolgatás",
    show_cycles: "Kazán ciklusok blokk",
    // szoba részletes
    card_room: "Meross Boiler Sync · Szoba részletes", desc_room: "Egy szoba nagy nézete: gyűrű és vezérlők, 24 órás görbe a céllal, a szelepek külön sorban.",
    rc_chart: "Hőmérséklet és fűtés", rc_valves: "Szelepek ({n})", rc_missing: "A kiválasztott szoba nem található.",
    lg_cur: "szoba hőmérséklete", lg_target: "cél", room: "Szoba", show_chart: "Grafikon", show_valves: "Szelepek listája",
    // hőtérkép
    card_heatmap: "Meross Boiler Sync · Heti hőtérkép", desc_heatmap: "Óránként hány percet fűtött a kazán (vagy egy szoba) az elmúlt napokban.",
    hm_title_boiler: "Fűtés az elmúlt {n} napban", hm_title_room: "{room} – fűtés az elmúlt {n} napban", days_n: "{n} nap", days: "Időtartam (nap)",
    hm_less: "kevesebb", hm_more: "több (óránként 60 p)", hm_avg: "Átlag {v} / nap", hm_peak: "Csúcs: {v} óra", hm_longest: "Leghosszabb: {d} ({v})",
    hm_tip: "{m} perc fűtés", hm_tip0: "nem fűtött", and_word: "és", show_selector: "Szoba-választó sáv", show_summary: "Összegzés a hőtérkép alatt", entity: "Kezdő nézet",
    // statisztika
    card_stats: "Meross Boiler Sync · Fűtési statisztika", desc_stats: "A kazán fűtési ideje naponta a kinti átlaggal, a szobák rangsora, opcionális költségbecslés.",
    stt_title: "Fűtési statisztika", stt_total: "Kazán összesen", stt_avg: "Átlag naponta", stt_outdoor: "Kinti átlag",
    stt_cost: "Becsült gázköltség", stt_gas: "Becsült gázfogyasztás", stt_cost_note: "{m3} m³/ó · {price} {cur}/m³ (becslés)", stt_gas_note: "{m3} m³/ó (becslés)",
    stt_daily: "Naponta", stt_daily_out: "Naponta, a kinti átlaggal", stt_rank: "Ki kéri a legtöbb hőt?",
    stt_lg_boiler: "kazán fűtési ideje", stt_lg_out: "kinti napi átlag",
    show_outdoor_stat: "Kinti átlag a grafikonon", show_rooms_stat: "Szobák rangsora", show_cost: "Költségbecslés",
    gas_m3_per_hour: "Gázfogyasztás fűtés közben (m³/óra)", gas_price: "Gáz ára (egy m³)", currency: "Pénznem",
    // csempe funkciók
    d_heat: "Hőtérkép – a háttér a hőmérséklet", close: "Bezárás", sh_details: "Részletek",
    sec_features: "Új funkciók (mind kapcsolható)",
    show_sparkline: "Minigrafikon (sparkline) a csempén", sparkline_hours: "A minigrafikon időtartama (óra)",
    drag_target: "Célhőmérséklet húzása a gyűrűn", hold_action: "Hosszú nyomás", ha_none: "Semmi", ha_sheet: "Részletek lapja", ha_more_info: "Eszköz részletei",
    look: "Megjelenés", lk_glass: "Üveg (alap)", lk_eink: "E-ink – mintázat színek helyett", lk_neon: "Neon",
    night_mode: "Éjszakai mód", night_from: "Éjszakai mód kezdete (ÓÓ:PP)", night_to: "Éjszakai mód vége (ÓÓ:PP)", night_dim: "Éjszakai fényerő (%)",
    heat_min: "Hőtérkép skála alja (°C)", heat_max: "Hőtérkép skála teteje (°C)",
    h_show_sparkline: "A csempén a szoba hőmérsékletének görbéje, a céllal és a fűtés idejével. Üveg, radiátor és lista dizájnban. Az előzményekből dolgozik.",
    h_drag_target: "A jelölőt húzva állítod a célt (a szelep lépésközéhez ragad). A − / + gomb megmarad. Üveg dizájnban.",
    h_hold_action: "Egy csempét 0,6 másodpercig nyomva a kiválasztott művelet indul. A rövid koppintás a „Koppintás művelete” szerint működik.",
    h_look: "E-ink: papírszín és mintázatok színek helyett (e-papíros falitabletre, színtévesztőknek). Neon: fekete alap, izzó körvonal.",
    h_night_mode: "Az éjszakai időszakban a kártya elhalványodik, az animációk megállnak (a böngésző idejét használja).",
    h_heat: "A „Hőtérkép” dizájn háttérszíne ebben a tartományban fut hidegkéktől a meleg narancsig.",
    sec_cost: "Költségbecslés", sec_alerts: "Mire figyelmeztessen",
    h_show_when_ok: "Ha nincs baj, alapból a kártya teljesen eltűnik; bekapcsolva egy zöld „Minden rendben” chipet mutat.",
    h_window_minutes: "Ennyi perc nyitva tartás után számít „nyitva felejtett” ablaknak.",
    h_show_cost: "Becslés, nem mérés: a fűtési időt szorozza az órás fogyasztással és az árral. Alapból ki van kapcsolva.",
    h_gas: "A kazán gázfogyasztása működés közben (a típustáblán vagy a számlán megtalálod).", h_gas_price: "Egy köbméter gáz ára, a megadott pénznemben.",
  });
  Object.assign(STR.en, {
    ago_now: "just now", ago_min: "{n} min ago", ago_h: "{n} h ago", ago_d: "{n} d ago",
    cyc_title: "Boiler cycles (last 6 h)", cyc_starts_h: "Starts in the last hour", cyc_per_h: "/ h", cyc_limit: "limit:",
    cyc_avg_on: "Avg. on-time", cyc_min: "min:", cyc_avg_off: "Avg. off-time", cyc_24h: "Last 24 h", cyc_starts: "starts",
    card_why: "Meross Boiler Sync · Why heating?", desc_why: "One sentence on why the boiler is heating (or idle), with the shortfall and an estimate per room.",
    why_heat_a: "The boiler is <b>heating</b> because ", why_join: ", ", why_join_last: " and ", why_heat_b1: " is below target.", why_heat_bn: " are below target.", why_more: "more",
    why_wait: "Rooms are calling for heat, the boiler is still <b>waiting</b> (minimum switching time).",
    why_cool: "The boiler is still <b>running</b> but nothing calls for heat: it will stop soon.",
    why_idle: "The boiler is <b>off</b>: every room reaches its target.",
    why_summer_avg: "The boiler is off in <b>summer mode</b>: the outdoor 24 h average is <b>{avg}°</b>, the threshold {thr}°.", why_summer: "The boiler is off in <b>summer mode</b>.",
    why_reached: "target reached", why_from_target: "from target",
    why_n_window: "window open, so it does not call for heat", why_n_windowpend: "window open, the room pauses in {t}",
    why_n_stale: "stale sensor, using the valve's own reading", why_n_waiting: "valve boost starts in {t}",
    why_n_rest: "resting, {t} until it may boost again", why_n_boost: "valve forced open, at most {t} more",
    why_n_period: "Summer period: {from} – {to} · rooms may call for heat but the boiler stays off",
    show_list: "Room list", show_notes: "Notes (window, stale sensor, waiting)", compact: "Compact (sentence only)", max_rows: "Maximum rows",
    card_alerts: "Meross Boiler Sync · Alerts", desc_alerts: "Shows only problems: stale sensor, forgotten open window, unreachable valve, short cycling. Hides itself when all is well.",
    al_boiler_unavail: "Boiler: unavailable", al_boiler_unavail_s: "The boiler thermostat does not respond, heating cannot be controlled",
    al_cycling: "Boiler: short cycling", al_cycling_sub: "{n} starts in the last hour (avg. {m} min on)", al_cycling_sub1: "{n} starts in the last hour",
    al_valve_unavail: "{room}: valve unavailable", al_valve_unavail_s: "No data from the valve",
    al_stale: "{room}: stale sensor", al_stale_sub: "Not updated {ago}; the valve's own reading is used", al_stale_sub0: "No recent update; the valve's own reading is used",
    al_maxboost: "{room}: reached the maximum valve boost time", al_maxboost_sub: "The valve is released, no boost for {m} min", al_maxboost_sub0: "The valve is released, a rest period follows",
    al_window: "{room}: window open", al_window_sub: "Heating is paused; open since {ago}", al_window_sub0: "Heating is paused",
    al_ok: "All good · {n} rooms, the boiler runs normally", al_empty_preview: "No alerts: the card hides itself when there is nothing to show.", al_more: "more",
    window_minutes: "Window alert after this many minutes", show_when_ok: "\"All good\" chip when nothing is wrong",
    alert_stale: "Stale sensor", alert_unavailable: "Unreachable valve / boiler", alert_window: "Forgotten open window", alert_max_boost: "Maximum valve boost", alert_cycling: "Short cycling",
    show_cycles: "Boiler cycles block",
    card_room: "Meross Boiler Sync · Room detail", desc_room: "One room in large view: ring and controls, a 24 h curve with the target, valves in their own rows.",
    rc_chart: "Temperature and heating", rc_valves: "Valves ({n})", rc_missing: "The selected room was not found.",
    lg_cur: "room temperature", lg_target: "target", room: "Room", show_chart: "Chart", show_valves: "Valve list",
    card_heatmap: "Meross Boiler Sync · Weekly heat map", desc_heatmap: "How many minutes per hour the boiler (or a room) was heating over the last days.",
    hm_title_boiler: "Heating over the last {n} days", hm_title_room: "{room} – heating over the last {n} days", days_n: "{n} days", days: "Time range (days)",
    hm_less: "less", hm_more: "more (60 min per hour)", hm_avg: "Average {v} / day", hm_peak: "Peak: {v} h", hm_longest: "Longest: {d} ({v})",
    hm_tip: "{m} min heating", hm_tip0: "no heating", and_word: "and", show_selector: "Room selector bar", show_summary: "Summary under the map", entity: "Initial view",
    card_stats: "Meross Boiler Sync · Heating statistics", desc_stats: "Daily boiler run time with the outdoor average, a room ranking, optional cost estimate.",
    stt_title: "Heating statistics", stt_total: "Boiler total", stt_avg: "Average per day", stt_outdoor: "Outdoor average",
    stt_cost: "Estimated gas cost", stt_gas: "Estimated gas use", stt_cost_note: "{m3} m³/h · {price} {cur}/m³ (estimate)", stt_gas_note: "{m3} m³/h (estimate)",
    stt_daily: "Per day", stt_daily_out: "Per day, with the outdoor average", stt_rank: "Who calls for the most heat?",
    stt_lg_boiler: "boiler run time", stt_lg_out: "outdoor daily average",
    show_outdoor_stat: "Outdoor average on the chart", show_rooms_stat: "Room ranking", show_cost: "Cost estimate",
    gas_m3_per_hour: "Gas use while heating (m³/h)", gas_price: "Gas price (per m³)", currency: "Currency",
    d_heat: "Heat – the background is the temperature", close: "Close", sh_details: "Details",
    sec_features: "New features (each can be switched)",
    show_sparkline: "Mini chart (sparkline) on the tile", sparkline_hours: "Mini chart time range (hours)",
    drag_target: "Drag the target on the ring", hold_action: "Long press", ha_none: "Nothing", ha_sheet: "Details sheet", ha_more_info: "Entity details",
    look: "Look", lk_glass: "Glass (default)", lk_eink: "E-ink – patterns instead of colors", lk_neon: "Neon",
    night_mode: "Night mode", night_from: "Night mode starts (HH:MM)", night_to: "Night mode ends (HH:MM)", night_dim: "Night brightness (%)",
    heat_min: "Heat map scale bottom (°C)", heat_max: "Heat map scale top (°C)",
    h_show_sparkline: "A curve of the room temperature on the tile, with the target and the heating time. Glass, radiator and list designs. Uses the history.",
    h_drag_target: "Drag the marker to set the target (it snaps to the valve step). The − / + buttons stay. Glass design.",
    h_hold_action: "Pressing a tile for 0.6 seconds starts the chosen action. A short tap follows \"Action on tap\".",
    h_look: "E-ink: paper color and patterns instead of colors (for e-paper wall tablets, colour-blind users). Neon: black base, glowing outline.",
    h_night_mode: "During the night period the card dims and animations stop (uses the browser's clock).",
    h_heat: "The \"Heat map\" design's background runs through this range from cold blue to warm orange.",
    sec_cost: "Cost estimate", sec_alerts: "What to warn about",
    h_show_when_ok: "When nothing is wrong the card hides itself completely; when on, it shows a green \"All good\" chip instead.",
    h_window_minutes: "A window counts as \"forgotten open\" after being open this many minutes.",
    h_show_cost: "An estimate, not a measurement: the run time multiplied by the hourly consumption and the price. Off by default.",
    h_gas: "The boiler's gas consumption while running (see the type plate or your bill).", h_gas_price: "The price of one cubic metre of gas, in the currency below.",
  });
  /* ===================================================================
   *  Alapértékek, dizájn előbeállítások, színek
   * =================================================================== */
  const DESIGNS = ["glass", "radiator", "minimal", "gradient", "list", "heat"];
  const LOOKS = ["glass", "eink", "neon"];
  const HOLD_ACTIONS = ["none", "sheet", "more-info"];
  const DEFAULTS = {
    design: "glass", title: "", rooms: [], columns: 0, size: 100, tap_action: "valve",
    show_controls: true, step: 0, show_presets: true, show_quick: false,
    glow: true, glow_level: 3, animation: false,
    temp_gradient: false, show_trend: true, show_eta: true, show_countdown: true, smooth: true,
    show_header: true, show_boiler: true, show_demand: true, show_summer: true,
    show_current: true, show_target: true, show_humidity: true, show_deviation: true,
    show_status: true, show_flags: true,
    gauge_min: 15, gauge_max: 28, decimals: 1,
    // 2.8: új funkciók (mind kapcsolható; alapból ki, kivéve a hosszú nyomás lapot)
    show_sparkline: false, sparkline_hours: 24, drag_target: false, hold_action: "sheet",
    look: "glass", night_mode: false, night_from: "22:00", night_to: "06:00", night_dim: 70,
    heat_min: 17, heat_max: 25,
  };
  const WHY_DEFAULTS = {
    title: "", rooms: [], size: 100, tap_action: "valve", decimals: 1,
    show_list: true, show_notes: true, compact: false, max_rows: 5, show_countdown: true,
  };
  const ROOM_DEFAULTS = {
    title: "", room: "", size: 100, tap_action: "valve", decimals: 1, hours: 24, step: 0,
    show_chart: true, show_valves: true, show_controls: true, show_presets: true, show_trend: true, show_eta: true,
    show_countdown: true, smooth: true, gauge_min: 15, gauge_max: 28,
  };
  const HEATMAP_DEFAULTS = {
    title: "", entity: "boiler", rooms: [], size: 100, days: 7, show_selector: true, show_summary: true,
  };
  const STATS_DEFAULTS = {
    title: "", rooms: [], size: 100, days: 7, show_outdoor: true, show_rooms: true, show_cost: false,
    gas_m3_per_hour: 1.6, gas_price: 0, currency: "Ft", show_rates: false, show_cycles: false,
  };
  const ALERTS_DEFAULTS = {
    title: "", rooms: [], size: 100, tap_action: "valve", window_minutes: 20, show_when_ok: false, compact: false,
    alert_stale: true, alert_unavailable: true, alert_window: true, alert_max_boost: true, alert_cycling: true,
    show_cycles: false,
  };
  const OVERVIEW_DEFAULTS = {
    title: "", rooms: [], size: 100, tap_action: "valve", decimals: 1,
    show_boiler: true, show_outdoor: true, show_summer: true, show_rooms: true,
    flow_animation: true, ambience: false, smooth: true, show_quick: false,
  };
  const TIMELINE_DEFAULTS = {
    title: "", rooms: [], size: 100, tap_action: "valve", hours: 24,
    show_boiler_row: true, show_total: true, show_range: true, show_legend: true, intro_animation: true,
  };
  const CHIPS_DEFAULTS = {
    rooms: [], size: 100, tap_action: "valve", decimals: 1, style: "chip", show_summary: true,
  };
  const PRESET = {
    glass: { radius: 22, opacity: 55, blur: 14 },
    radiator: { radius: 22, opacity: 55, blur: 14 },
    minimal: { radius: 16, opacity: 40, blur: 0 },
    gradient: { radius: 24, opacity: 100, blur: 0 },
    heat: { radius: 26, opacity: 100, blur: 0 },
    list: { radius: 14, opacity: 45, blur: 8 },
    wide: { radius: 22, opacity: 55, blur: 14 },
  };
  const COLOR_KEYS = ["idle", "demand", "boost", "waiting", "rest", "stale", "window", "off", "summer"];
  const DEFAULT_COLORS = {
    idle: [102, 187, 106], demand: [255, 152, 0], boost: [255, 87, 34], waiting: [255, 202, 40],
    rest: [100, 181, 246], stale: [239, 83, 80], window: [79, 195, 247], off: [130, 140, 150],
    summer: [255, 213, 79],
  };
  const GLOW_STATES = ["idle", "demand", "boost", "waiting", "rest", "stale", "window", "off"];
  const GLOW_DEFAULT = GLOW_STATES.filter((k) => k !== "off");
  const FX = {
    demand: '<div class="fx flame"><i></i><i></i><i></i></div>',
    boost: '<div class="fx flame hot"><i></i><i></i><i></i></div>',
    stale: '<div class="fx alarm"></div>',
    window: '<div class="fx wind"><i></i><i></i><i></i><i></i></div>',
    windowpend: '<div class="fx soft"></div>',
    waiting: '<div class="fx"></div>', rest: '<div class="fx"></div>', idle: '<div class="fx soft"></div>',
  };
  // a radiátor dizájnon a lángot a hőhullámok helyettesítik, csak ezek a rétegek kellenek
  const FX_RADIATOR = { stale: FX.stale, window: FX.window };
  const TEMP_GRADIENT = [[0, "#4fc3f7"], [0.38, "#66bb6a"], [0.68, "#ffca28"], [1, "#ff7043"]];
  const TREND_FLAT = 0.15;       // °C/óra: ennél kisebb változás = "stabil"
  const ETA_MAX_MIN = 360;       // ennél hosszabb becslést nem mutatunk
  const HISTORY_RANGES = [6, 12, 24, 168];
  const HOLD_MS = 600;           // ennyi ideig kell nyomni egy csempét a részletek lapjához

  /** Becslés (perc), mikorra éri el a szoba a célt a mostani trenddel; null, ha nincs értelme. */
  function etaMinutes(r) {
    const t = r.trend, tgt = r.effTarget != null ? r.effTarget : r.target;
    if (t == null || t < TREND_FLAT || !r.below || r.cur == null || tgt == null || tgt <= r.cur) return null;
    const min = ((tgt - r.cur) / t) * 60;
    return min >= 1 && min <= ETA_MAX_MIN ? (min > 10 ? Math.round(min / 5) * 5 : min) : null;
  }

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const pad2 = (n) => String(n).padStart(2, "0");

  /** Szín CSS-ként. Tömb [r,g,b] / "#rrggbb" / bármilyen CSS szín (alpha: color-mix). */
  function cssColor(value, alpha) {
    const a = alpha == null ? 1 : alpha;
    let rgb = null;
    if (Array.isArray(value) && value.length >= 3) rgb = value.slice(0, 3).map((n) => clamp(Math.round(Number(n) || 0), 0, 255));
    else if (typeof value === "string" && /^#[0-9a-f]{6}$/i.test(value.trim())) {
      const h = value.trim().slice(1);
      rgb = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
    }
    if (rgb) return a >= 1 ? `rgb(${rgb[0]},${rgb[1]},${rgb[2]})` : `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${a})`;
    if (typeof value === "string" && value) return a >= 1 ? value : `color-mix(in srgb, ${value} ${Math.round(a * 100)}%, transparent)`;
    return "transparent";
  }

  /* ===================================================================
   *  Ikonok (saját, vonalas SVG – nem függ a HA ikonkészletétől)
   * =================================================================== */
  const ICONS = {
    radiator: '<rect x="4" y="5" width="3" height="14" rx="1.5"/><rect x="10.5" y="5" width="3" height="14" rx="1.5"/><rect x="17" y="5" width="3" height="14" rx="1.5"/>',
    drop: '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    flame: '<path d="M12 3c.5 3-3 4.5-3 8.5a4 4 0 0 0 8 0c0-2-1-3-2-4.5-.5 1.5-1.5 2-2.5 1.5C13 6.5 12.5 5 12 3z"/>',
    window: '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M12 3v18M5 12h14"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9L7 7M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
    valve: '<circle cx="12" cy="12" r="9"/><path d="M12 16V8M8.5 11.5L12 8l3.5 3.5"/>',
    link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    alert: '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.1"/>',
    power: '<path d="M12 3v9"/><path d="M6.3 6.8a8 8 0 1 0 11.4 0"/>',
    thermo: '<path d="M10 14.5V5a2 2 0 0 1 4 0v9.5a4 4 0 1 1-4 0z"/>',
    flask: '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4A2 2 0 0 0 19 18l-5-9V3"/>',
    pause: '<path d="M9 5v14M15 5v14"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    minus: '<path d="M6 12h12"/>',
    plus: '<path d="M12 6v12M6 12h12"/>',
    chev: '<path d="M6 9l6 6 6-6"/>',
    moon: '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    sofa: '<path d="M5 11V8a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v3M3 13a2 2 0 0 1 4 0v2h10v-2a2 2 0 0 1 4 0v5H3z"/>',
    leaf: '<path d="M5 19c0-8 5-13 14-14 0 9-5 14-13 14M5 19l7-7"/>',
    auto: '<circle cx="12" cy="12" r="9"/><path d="M8.5 16l3.5-8 3.5 8M9.8 13.5h4.4"/>',
    tune: '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
    home: '<path d="M4 11l8-7 8 7v9H4z"/><path d="M10 20v-6h4v6"/>',
    away: '<path d="M5 20V4h8v16M13 12h6M16 9l3 3-3 3"/>',
    check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    up: '<path d="M4 17l6-6 4 4 6-8M15 7h5v5"/>',
    down: '<path d="M4 7l6 6 4-4 6 8M15 17h5v-5"/>',
    flat: '<path d="M4 12h15M14 7l5 5-5 5"/>',
    cal: '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>',
    cycle: '<path d="M20 12a8 8 0 1 1-2.4-5.7M20 4v5h-5"/>',
    close: '<path d="M6 6l12 12M18 6L6 18"/>',
    bolt: '<path d="M13 3L5 13h6l-1 8 8-10h-6z"/>',
  };
  const PRESET_ICON = { auto: "auto", sleep: "moon", comfort: "sofa", eco: "leaf", away: "away", home: "home", manual: "tune", boost: "flame" };
  const ic = (name, cls) => `<svg class="ic ${cls || ""}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ""}</svg>`;
  const STATUS_ICON = {
    idle: "thermo", demand: "flame", boost: "valve", waiting: "clock", rest: "pause",
    stale: "alert", window: "window", windowpend: "window", off: "power",
  };

  /* ===================================================================
   *  Adatgyűjtés a HA állapotokból
   * =================================================================== */
  const isRoom = (s) => !!(s && s.entity_id && s.entity_id.startsWith("binary_sensor.") && s.attributes &&
    "room_below_target" in s.attributes && "valves" in s.attributes);
  const isSummer = (s) => !!(s && s.entity_id && s.entity_id.startsWith("binary_sensor.") && s.attributes &&
    "in_summer_period" in s.attributes);

  const isStarts = (s) => !!(s && s.entity_id && s.entity_id.startsWith("sensor.") && s.attributes &&
    "starts_last_hour" in s.attributes && "cycles" in s.attributes);
  const isCycling = (s) => !!(s && s.entity_id && s.entity_id.startsWith("binary_sensor.") && s.attributes &&
    "max_starts_per_hour" in s.attributes);

  function statusOf(a, on) {
    if (a.temperature_sensor_stale) return "stale";
    if (a.window_open) return "window";
    if (a.window_open_pending) return "windowpend";
    if (a.valve_boosted) return "boost";
    if (a.valve_boost_resting) return "rest";
    if (a.valve_boost_waiting) return "waiting";
    if (on) return "demand";
    if (a.valve_active === false) return "off";
    return "idle";
  }

  const num = (v) => (v == null || v === "" || isNaN(Number(v)) ? null : Number(v));
  const toMs = (v) => { if (!v) return null; const t = Date.parse(v); return isNaN(t) ? null : t; };

  function collect(hass, cfg) {
    const states = (hass && hass.states) || {};
    let list;
    if (cfg.rooms && cfg.rooms.length) list = cfg.rooms.map((id) => states[id]).filter(isRoom);
    else {
      const lang = langOf(hass);
      list = Object.values(states).filter(isRoom).sort((x, y) =>
        String(x.attributes.room_name || x.attributes.friendly_name).localeCompare(String(y.attributes.room_name || y.attributes.friendly_name), lang));
    }
    const summer = Object.values(states).find(isSummer) || null;
    const boilerId = (summer && summer.attributes.boiler_entity) || cfg.boiler || null;
    const rooms = list.map((s) => {
      const a = s.attributes;
      const on = s.state === "on";
      // minden szelep (a preset és a gyorsgombok miatt) + a "vezérlő" szelep: az első elérhető
      const vs = (Array.isArray(a.valves) ? a.valves : []).map((id) => states[id]).filter(Boolean);
      const mkValve = (v) => ({
        id: v.entity_id, state: v.state, name: v.attributes.friendly_name || v.entity_id, cur: num(v.attributes.current_temperature),
        preset: v.attributes.preset_mode == null ? null : String(v.attributes.preset_mode),
        presets: Array.isArray(v.attributes.preset_modes) ? v.attributes.preset_modes.map(String) : [],
        min: num(v.attributes.min_temp), max: num(v.attributes.max_temp), step: num(v.attributes.target_temp_step), target: num(v.attributes.temperature),
        ok: v.state !== "unavailable" && v.state !== "unknown" && v.state !== "off",
      });
      const valves = vs.map(mkValve);
      const valve = valves.find((x) => x.state !== "unavailable" && x.state !== "unknown") || valves[0] || null;
      return {
        id: s.entity_id, on, a, valve, valves,
        valveIds: vs.map((x) => x.entity_id),
        tempSensor: a.temperature_sensor || null,
        windowSensors: Array.isArray(a.window_sensors) ? a.window_sensors : [],
        humBoost: num(a.humidity_boost),
        name: a.room_name || a.friendly_name || s.entity_id,
        status: statusOf(a, on),
        cur: num(a.current_temperature),
        target: num(a.target_temperature),
        effTarget: num(a.effective_target),
        hum: num(a.humidity),
        dev: num(a.deviation),
        trend: num(a.temperature_trend),
        below: !!a.room_below_target,
        delayMin: num(a.boost_delay_minutes),
        times: {
          start: toMs(a.valve_boost_starts_at), rest: toMs(a.valve_boost_rest_until),
          max: toMs(a.valve_boost_max_until), win: toMs(a.window_open_pending_until),
        },
      };
    });
    const all = Object.values(states);
    return {
      rooms, summer, boiler: boilerId ? states[boilerId] || null : null, boilerId,
      starts: all.find(isStarts) || null, cycling: all.find(isCycling) || null,
    };
  }

  const boilerOn = (b) => !!b && b.state !== "off" && b.state !== "unavailable" && b.state !== "unknown";

  /** A visszaszámláló: melyik időpontig tart az aktuális állapot (ha a szenzor kiadta). */
  function countdownOf(r, now) {
    const t = r.times;
    let kind = null, end = null, total = null;
    if (r.status === "windowpend" && t.win) { kind = "win"; end = t.win; }
    else if (r.status === "waiting" && t.start) { kind = "start"; end = t.start; if (r.delayMin) total = r.delayMin * 60000; }
    else if (r.status === "rest" && t.rest) { kind = "rest"; end = t.rest; }
    else if (r.status === "boost" && t.max) { kind = "max"; end = t.max; }
    if (!kind || end <= now) return null;
    return { kind, end, total };
  }

  /** 7:12 (10 perc alatt) · 41 p · 2 ó 15 p */
  function fmtRemain(ms, hass) {
    const s = Math.max(0, Math.ceil(ms / 1000));
    const h_ = T(hass, "unit_h"), m_ = T(hass, "unit_min");
    if (s < 600) return `${Math.floor(s / 60)}:${pad2(s % 60)}`;
    if (s < 3600) return `${Math.ceil(s / 60)} ${m_}`;
    let h = Math.floor(s / 3600), m = Math.ceil((s % 3600) / 60);
    if (m === 60) { h += 1; m = 0; }
    return `${h} ${h_} ${pad2(m)} ${m_}`;
  }

  /** Percek -> "35 p" / "1 ó 20 p" */
  function fmtMinutes(min, hass) {
    const h_ = T(hass, "unit_h"), m_ = T(hass, "unit_min");
    const m = Math.round(min);
    if (m < 60) return `${m} ${m_}`;
    const h = Math.floor(m / 60), r = m % 60;
    return r ? `${h} ${h_} ${pad2(r)} ${m_}` : `${h} ${h_}`;
  }

  /** Színátmenet a hőmérséklet-skálán (hideg kék -> meleg narancs). */
  function gradientStops() {
    return TEMP_GRADIENT.map(([o, c]) => `<stop offset="${o}" stop-color="${c}"/>`).join("");
  }

  /** A hőmérséklet-skála színe (0..1) [r,g,b]-ként. */
  function tempRgb(f) {
    const hex = (h_) => [1, 3, 5].map((i) => parseInt(h_.slice(i, i + 2), 16));
    const x = clamp(f, 0, 1);
    for (let i = 1; i < TEMP_GRADIENT.length; i++) {
      if (x <= TEMP_GRADIENT[i][0]) {
        const [a, ca] = TEMP_GRADIENT[i - 1], [b, cb] = TEMP_GRADIENT[i], k = (x - a) / (b - a), c0 = hex(ca), c1 = hex(cb);
        return c0.map((v, j) => Math.round(v + (c1[j] - v) * k));
      }
    }
    return hex(TEMP_GRADIENT[TEMP_GRADIENT.length - 1][1]);
  }
  const mixRgb = (c, d, k) => c.map((v, i) => Math.round(v + (d[i] - v) * k));

  /* ===================================================================
   *  Rajzolás-segédek
   * =================================================================== */
  function arcPath(cx, cy, r, f) {
    const a0 = (135 * Math.PI) / 180;
    const sweep = 270 * clamp(f, 0, 1);
    const a1 = ((135 + sweep) * Math.PI) / 180;
    const x0 = cx + r * Math.cos(a0), y0 = cy + r * Math.sin(a0);
    const x1 = cx + r * Math.cos(a1), y1 = cy + r * Math.sin(a1);
    return `M ${x0.toFixed(2)} ${y0.toFixed(2)} A ${r} ${r} 0 ${sweep > 180 ? 1 : 0} 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`;
  }
  function pointOn(cx, cy, r, f) {
    const ang = ((135 + 270 * clamp(f, 0, 1)) * Math.PI) / 180;
    return [cx + r * Math.cos(ang), cy + r * Math.sin(ang)];
  }

  /* ===================================================================
   *  Közös stílus (minden kártya ugyanezt tölti be a saját shadow DOM-jába)
   * =================================================================== */
  const CSS = `
    :host { display:block; }
    * { box-sizing:border-box; }
    .root {
      --r: var(--mbs-radius, 22px);
      --op: var(--mbs-opacity, 55%);
      --blur: var(--mbs-blur, 14px);
      --surface: color-mix(in srgb, var(--card-background-color, #1c1c1e) var(--op), transparent);
      --border: color-mix(in srgb, var(--primary-text-color, #fff) 12%, transparent);
      --muted: var(--secondary-text-color, #9aa0a6);
      --text: var(--primary-text-color, #f2f2f2);
      --track: color-mix(in srgb, var(--primary-text-color, #fff) 14%, transparent);
      --c: var(--c-idle);
      color: var(--text);
      font-family: var(--ha-font-family-body, var(--paper-font-body1_-_font-family, inherit));
    }
    .ic { width:1.1em; height:1.1em; flex:none; }
    .hd { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin:0 0 12px; }
    .ttl { font-size:1.15rem; font-weight:600; margin-right:auto; padding-left:4px; }
    .pill { display:inline-flex; align-items:center; gap:7px; padding:7px 13px; border-radius:999px; font-size:.82rem;
      background:var(--surface); border:1px solid var(--border); backdrop-filter:blur(var(--blur)); -webkit-backdrop-filter:blur(var(--blur)); }
    .pill .ic { color:var(--c, var(--muted)); }
    .pill b { font-weight:600; }
    .pill small { color:var(--muted); font-size:.95em; }
    [data-entity] { cursor:pointer; }
    .grid { display:grid; gap:12px; grid-template-columns:repeat(var(--cols), minmax(0,1fr)); }
    .t { position:relative; border-radius:var(--r); background:var(--surface); border:1px solid var(--border);
      backdrop-filter:blur(var(--blur)); -webkit-backdrop-filter:blur(var(--blur)); overflow:hidden; }
    .t::before { content:""; position:absolute; left:0; right:0; top:0; height:3px; background:var(--c); opacity:.9; }
    .chip { display:inline-flex; align-items:center; gap:5px; padding:3px 10px; border-radius:999px; font-size:.72rem; font-weight:600;
      color:var(--c); background:color-mix(in srgb, var(--c) 16%, transparent); border:1px solid color-mix(in srgb, var(--c) 35%, transparent); white-space:nowrap; }
    .chip .ic { width:.95em; height:.95em; }
    .fl { display:flex; gap:7px; color:var(--muted); }
    .fl .ic { width:.95em; height:.95em; }
    .dev { font-weight:600; color:var(--c); }
    .msg { padding:18px; border-radius:var(--r); border:1px dashed var(--border); color:var(--muted); text-align:center; }
    ${COLOR_KEYS.map((k) => `[data-st="${k}"] { --c: var(--c-${k}); }`).join("\n")}
    [data-st="windowpend"] { --c: var(--c-window); }

    /* ---------- méretezés (zoom: az egész tartalmat arányosan skálázza) ---------- */
    .zm { zoom:var(--sz, 1); }

    /* ---------- ragyogás (glow) 1-5: az aktuális állapot színével ---------- */
    .gl1 { box-shadow:0 0 .6em 0 color-mix(in srgb, var(--c) 24%, transparent); }
    .gl2 { box-shadow:0 0 1em .05em color-mix(in srgb, var(--c) 34%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--c) 22%, transparent); }
    .gl3 { box-shadow:0 0 1.6em .15em color-mix(in srgb, var(--c) 46%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--c) 34%, transparent); }
    .gl4 { box-shadow:0 0 2.2em .3em color-mix(in srgb, var(--c) 58%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--c) 46%, transparent); }
    .gl5 { box-shadow:0 0 3em .5em color-mix(in srgb, var(--c) 72%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--c) 60%, transparent), inset 0 0 1.6em color-mix(in srgb, var(--c) 14%, transparent); }

    /* ---------- glass ---------- */
    .glass { font-size:16px; text-align:center; }
    .glass .in { position:relative; z-index:2; padding:1em .9em .9em; display:flex; flex-direction:column; align-items:center; gap:.5em; }
    .glass::before { z-index:3; }
    .glass .nm { font-size:1.06em; font-weight:500; letter-spacing:.01em; max-width:100%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .ring { position:relative; width:12.3em; height:12.3em; margin-bottom:.85em; flex:none; }
    .ring svg { width:100%; height:100%; display:block; }
    .ring .mid { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; padding-bottom:1.2em; }
    .big { font-size:3.2em; font-weight:400; line-height:1; display:flex; align-items:flex-start; font-variant-numeric:tabular-nums; }
    .big .dc { font-size:.42em; margin-top:.55em; color:var(--muted); }
    .big .un { font-size:.27em; margin:.65em 0 0 .25em; color:var(--muted); }
    .ctl { position:absolute; left:0; right:0; bottom:-.95em; display:flex; align-items:center; justify-content:space-between; padding:0 .45em; }
    .tg { font-size:.82em; color:var(--muted); text-align:center; line-height:1.25; min-width:4em; }
    .tg b { display:block; color:var(--text); font-size:1.15em; font-weight:500; font-variant-numeric:tabular-nums; }
    .pm { width:2.55em; height:2.55em; border-radius:50%; border:1px solid var(--border); padding:0; margin:0; cursor:pointer; font:inherit;
      background:color-mix(in srgb, var(--text) 7%, transparent); color:var(--text); display:grid; place-items:center;
      -webkit-tap-highlight-color:transparent; transition:background .15s, transform .1s; }
    .pm .ic { width:1.15em; height:1.15em; }
    .pm:hover:not(:disabled) { background:color-mix(in srgb, var(--text) 14%, transparent); }
    .pm:active:not(:disabled) { transform:scale(.93); }
    .pm:disabled { opacity:.35; cursor:default; }
    .glass .info { display:flex; gap:1em; align-items:center; justify-content:center; font-size:.88em; min-height:1.4em; }
    .hum { color:var(--c-rest-text, #64b5f6); display:inline-flex; gap:.3em; align-items:center; }
    .glass .foot { position:relative; display:flex; gap:.5em; align-items:center; justify-content:center; flex-wrap:wrap; margin-top:.1em; }
    .glass .chip { font-size:.74em; padding:.28em .75em; }
    .pre { display:inline-flex; align-items:center; gap:.4em; padding:.3em .65em; border-radius:99px; font:inherit; font-size:.76em; font-weight:500;
      color:var(--text); background:color-mix(in srgb, var(--text) 7%, transparent); border:1px solid var(--border); cursor:pointer; white-space:nowrap;
      -webkit-tap-highlight-color:transparent; }
    .pre:hover { background:color-mix(in srgb, var(--text) 14%, transparent); }
    .pre .ic { width:1em; height:1em; }
    .pre .chev { width:.8em; height:.8em; opacity:.7; }
    .menu { position:absolute; right:-.2em; bottom:calc(100% + .5em); min-width:9.5em; max-height:15em; overflow:auto; padding:.35em; border-radius:1em; z-index:6;
      background:color-mix(in srgb, var(--card-background-color, #1c1c1e) 97%, transparent); border:1px solid var(--border);
      box-shadow:0 10px 30px rgba(0,0,0,.45); text-align:left; }
    .mi { display:flex; align-items:center; gap:.6em; width:100%; padding:.5em .65em; border-radius:.7em; font:inherit; font-size:.82em; border:0;
      background:transparent; color:var(--text); cursor:pointer; text-align:left; }
    .mi:hover { background:color-mix(in srgb, var(--text) 9%, transparent); }
    .mi.on { background:color-mix(in srgb, var(--c) 18%, transparent); color:var(--c); font-weight:600; }
    .mi .ic { width:1.15em; height:1.15em; }
    .mi .ck { margin-left:auto; }

    /* ---------- trend és becslés ---------- */
    .trend { display:flex; align-items:center; justify-content:center; gap:.45em; font-size:.8em; color:var(--muted); margin-top:-.1em; }
    .trend .ic { width:1.1em; height:1.1em; }
    .trend b { font-weight:600; color:var(--text); font-variant-numeric:tabular-nums; }
    .trend.up { color:var(--c); }
    .trend.down { color:var(--c-rest); }

    /* ---------- visszaszámláló gyűrű (a címke helyén) ---------- */
    .cd { display:inline-flex; align-items:center; gap:.55em; padding:.34em .9em .34em .4em; border-radius:999px; font-size:.8em;
      background:color-mix(in srgb, var(--c) 12%, transparent); border:1px solid color-mix(in srgb, var(--c) 34%, transparent); color:var(--text); white-space:nowrap; }
    .cd .cdr { width:1.9em; height:1.9em; flex:none; transform:rotate(-90deg); }
    .cd .bg { fill:none; stroke:color-mix(in srgb, var(--c) 22%, transparent); stroke-width:3; }
    .cd .fg { fill:none; stroke:var(--c); stroke-width:3; stroke-linecap:round; stroke-dasharray:100; transition:stroke-dashoffset 1s linear; }
    .cd b { color:var(--c); font-weight:600; font-variant-numeric:tabular-nums; }
    .cd .cdl { color:var(--muted); }

    /* ---------- animált réteg (üveg és radiátor, kikapcsolható) ---------- */
    .fx { position:absolute; inset:0; z-index:1; pointer-events:none; overflow:hidden; border-radius:inherit; }
    .fx::before { content:""; position:absolute; left:-20%; right:-20%; bottom:-25%; height:60%;
      background:radial-gradient(ellipse 55% 55% at 50% 60%, color-mix(in srgb, var(--c) 62%, transparent), transparent 100%);
      opacity:.35; animation:mbs-breathe 4s ease-in-out infinite; }
    @keyframes mbs-breathe { 0%,100% { opacity:.25; transform:scale(1); } 50% { opacity:.75; transform:scale(1.08); } }
    .fx.soft::before { opacity:.2; animation-name:mbs-breathe-soft; }
    @keyframes mbs-breathe-soft { 0%,100% { opacity:.1; transform:scale(1); } 50% { opacity:.42; transform:scale(1.05); } }
    .fx.flame i { position:absolute; bottom:-18%; width:34%; height:46%; border-radius:50% 50% 45% 45% / 72% 72% 28% 28%;
      background:radial-gradient(ellipse at 50% 100%, color-mix(in srgb, var(--c) 82%, transparent) 0%, color-mix(in srgb, var(--c) 38%, transparent) 46%, transparent 74%);
      filter:blur(8px); transform-origin:50% 100%; opacity:.7; animation:mbs-lick 2s ease-in-out infinite; }
    .fx.flame i:nth-child(1) { left:-4%; animation-duration:2s; animation-delay:-.4s; }
    .fx.flame i:nth-child(2) { left:33%; height:56%; animation-duration:1s; animation-delay:-.2s; }
    .fx.flame i:nth-child(3) { left:70%; animation-duration:2s; animation-delay:-1.1s; }
    @keyframes mbs-lick { 0%,100% { transform:scale(.9,.8) skewX(0); } 25% { transform:scale(1.05,1.1) skewX(-4deg); }
      50% { transform:scale(.95,.95) skewX(3deg); } 75% { transform:scale(1.08,1.2) skewX(-2deg); } }
    .fx.flame.hot i { height:62%; opacity:.95; }
    .fx.flame.hot i:nth-child(2) { height:74%; animation-duration:.5s; }
    .fx.flame.hot i:nth-child(1), .fx.flame.hot i:nth-child(3) { animation-duration:1s; }
    .fx.alarm::before { animation:mbs-alarm 2s ease-in-out infinite; }
    .fx.alarm::after { content:""; position:absolute; left:8%; right:8%; bottom:0; height:2px; border-radius:2px; background:var(--c);
      box-shadow:0 0 14px 2px var(--c); animation:mbs-alarm 2s ease-in-out infinite; }
    @keyframes mbs-alarm { 0%,100% { opacity:.12; } 50% { opacity:.9; } }
    .fx.wind i { position:absolute; left:0; width:60%; height:2px; border-radius:2px; opacity:0;
      background:linear-gradient(90deg, transparent, color-mix(in srgb, var(--c) 75%, transparent), transparent);
      filter:blur(.6px); animation:mbs-gust 4s linear infinite; }
    .fx.wind i:nth-child(1) { top:54%; animation-duration:4s; animation-delay:-.5s; }
    .fx.wind i:nth-child(2) { top:63%; width:45%; animation-duration:2s; animation-delay:-1.2s; }
    .fx.wind i:nth-child(3) { top:72%; width:72%; animation-duration:4s; animation-delay:-2.6s; }
    .fx.wind i:nth-child(4) { top:80%; width:40%; animation-duration:2s; animation-delay:-.3s; }
    @keyframes mbs-gust { 0% { transform:translateX(-70%); opacity:0; } 15% { opacity:.6; } 80% { opacity:.5; } 100% { transform:translateX(240%); opacity:0; } }

    /* ---------- radiator ---------- */
    .rd .rad { position:relative; width:11.6em; height:8.4em; margin:.1em 0 .15em; }
    .rd .rad svg { width:100%; height:100%; display:block; overflow:visible; }
    .rd .fin { fill:var(--c); opacity:.2; transition:opacity .6s; }
    .rd .pipe { fill:var(--c); opacity:.35; }
    .rd[data-st="idle"] .fin { opacity:.28; }
    .rd[data-st="waiting"] .fin, .rd[data-st="rest"] .fin { opacity:.3; }
    .rd[data-st="window"] .fin, .rd[data-st="windowpend"] .fin { opacity:.45; }
    .rd[data-st="demand"] .fin { opacity:.78; filter:drop-shadow(0 0 4px var(--c)); }
    .rd[data-st="boost"] .fin { opacity:.95; filter:drop-shadow(0 0 7px var(--c)); }
    .rd[data-st="off"] .fin { opacity:.1; }
    .rd.anim[data-st="boost"] .fin { animation:mbs-finb 2s ease-in-out infinite; }
    .rd.anim[data-st="stale"] .fin { animation:mbs-finalarm 2s ease-in-out infinite; }
    .rd[data-st="stale"] .fin { opacity:.5; }
    @keyframes mbs-finb { 0%,100% { opacity:.8; } 50% { opacity:1; } }
    @keyframes mbs-finalarm { 0%,100% { opacity:.18; } 50% { opacity:.7; } }
    .rd .wv { fill:none; stroke:var(--c); stroke-width:2; stroke-linecap:round; opacity:0; }
    .rd.anim[data-st="demand"] .wv, .rd.anim[data-st="boost"] .wv { animation:mbs-rise 2s ease-in infinite; }
    .rd.anim[data-st="boost"] .wv { animation-duration:1s; stroke-width:2.5; }
    .rd .wv:nth-of-type(2) { animation-delay:-.7s !important; } .rd .wv:nth-of-type(3) { animation-delay:-1.3s !important; }
    .rd .wv:nth-of-type(4) { animation-delay:-.35s !important; } .rd .wv:nth-of-type(5) { animation-delay:-1.65s !important; }
    @keyframes mbs-rise { 0% { transform:translateY(8px); opacity:0; } 25% { opacity:.75; } 100% { transform:translateY(-22px); opacity:0; } }
    .rd .num { display:flex; align-items:center; justify-content:space-between; width:100%; padding:0 .15em; }
    .rd .num .big { font-size:2.6em; }
    .rd .num .big .dc { font-size:.45em; margin-top:.4em; }
    .rd .num .big .un { font-size:.3em; margin-top:.5em; }
    .rd .num .pm { width:2.3em; height:2.3em; }
    .rd .tg2 { font-size:.8em; color:var(--muted); margin-top:-.55em; }
    .rd .tg2 b { color:var(--text); font-weight:500; font-variant-numeric:tabular-nums; }

    /* ---------- gyorsgombok ---------- */
    .qbar { display:flex; align-items:center; flex-wrap:wrap; gap:8px 12px; margin:0 0 12px; padding-left:4px; position:relative; z-index:2; }
    .qbar .ql { font-size:.8rem; color:var(--muted); }
    .qseg { display:inline-flex; flex-wrap:wrap; gap:2px; padding:3px; border-radius:999px; background:color-mix(in srgb, var(--text) 7%, transparent); border:1px solid var(--border); }
    .qseg button { display:inline-flex; align-items:center; gap:7px; padding:7px 14px; border-radius:999px; border:0; background:transparent; color:var(--muted);
      font:inherit; font-size:.84rem; cursor:pointer; -webkit-tap-highlight-color:transparent; }
    .qseg button:hover { color:var(--text); }
    .qseg button .ic { width:15px; height:15px; }
    .qseg button.on { background:color-mix(in srgb, var(--text) 15%, transparent); color:var(--text); font-weight:600; }
    .qmix { font-size:.76rem; color:var(--muted); padding:3px 10px; border-radius:999px; border:1px dashed var(--border); }
    .toast { display:inline-flex; align-items:center; gap:8px; padding:6px 12px; border-radius:999px; font-size:.8rem;
      background:color-mix(in srgb, var(--card-background-color, #1c1c1e) 96%, transparent); border:1px solid var(--border); animation:mbs-toast .25s ease-out both; }
    .toast .ic { color:var(--c-idle); }
    @keyframes mbs-toast { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:none; } }

    /* ---------- minimal ---------- */
    .minimal { display:flex; align-items:center; gap:12px; padding:11px 14px; }
    .minimal .ib { width:42px; height:42px; border-radius:50%; display:grid; place-items:center; flex:none;
      color:var(--c); background:color-mix(in srgb, var(--c) 18%, transparent); }
    .minimal .ib .ic { width:22px; height:22px; }
    .minimal .tx { min-width:0; flex:1; }
    .minimal .nm { font-weight:600; font-size:.95rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .minimal .sb { font-size:.8rem; color:var(--muted); margin-top:2px; display:flex; flex-wrap:wrap; align-items:center; gap:2px 10px; }
    .minimal .sb > * { white-space:nowrap; }
    .minimal .sb b { color:var(--text); font-weight:600; }

    /* ---------- gradient ---------- */
    .gradient { padding:14px 16px 16px; display:flex; flex-direction:column; gap:6px; border:0;
      background:linear-gradient(155deg, color-mix(in srgb, var(--c) 42%, var(--card-background-color, #1c1c1e)) 0%,
        color-mix(in srgb, var(--c) 10%, var(--card-background-color, #1c1c1e)) 100%); }
    .gradient::before { display:none; }
    .gradient .top { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:6px 8px; }
    .gradient .nm { font-weight:600; font-size:1rem; min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .gradient .chip { background:color-mix(in srgb, #000 22%, transparent); color:var(--text); border-color:transparent; }
    .gradient .bg { font-size:2.6rem; font-weight:300; line-height:1.05; }
    .gradient .bg small { font-size:1rem; color:color-mix(in srgb, var(--text) 70%, transparent); margin-left:4px; }
    .gradient .sb { font-size:.82rem; color:color-mix(in srgb, var(--text) 78%, transparent); display:flex; gap:12px; flex-wrap:wrap; }
    .bar { position:relative; height:6px; border-radius:99px; background:color-mix(in srgb, var(--text) 16%, transparent); margin-top:6px; }
    .bar i { position:absolute; left:0; top:0; bottom:0; border-radius:99px; background:var(--c); }
    .bar b { position:absolute; top:-3px; width:3px; height:12px; border-radius:2px; background:var(--text); transform:translateX(-50%); }

    /* ---------- list ---------- */
    .tbl { border-radius:var(--r); background:var(--surface); border:1px solid var(--border); overflow:hidden;
      backdrop-filter:blur(var(--blur)); -webkit-backdrop-filter:blur(var(--blur)); }
    .rw { display:grid; grid-template-columns:minmax(110px,1.1fr) 84px 92px minmax(90px,2fr) 118px 215px; gap:12px; align-items:center;
      padding:10px 16px; border-top:1px solid var(--border); position:relative; }
    .rw:first-child { border-top:0; }
    .rw::before { content:""; position:absolute; left:0; top:0; bottom:0; width:3px; background:var(--c); }
    .rw .nm { font-weight:600; font-size:.93rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .rw .v { font-size:1.05rem; font-variant-numeric:tabular-nums; text-align:right; white-space:nowrap; }
    .rw .v small { color:var(--muted); font-size:.75em; }
    .rw .bar { margin:0; }
    @media (max-width:560px) { .rw { grid-template-columns:1fr auto auto; } .rw .bar, .rw .hum, .rw .fl { display:none; } }

    /* ---------- áttekintő kártya ---------- */
    .t.ov::before, .t.tl::before { display:none; }
    .ov { position:relative; container-type:inline-size; padding:22px 24px 20px; --c:var(--c-off); }
    .ov .ottl { position:relative; z-index:2; font-size:1.1rem; font-weight:600; margin:0 0 14px; }
    .ov .top { position:relative; z-index:2; display:flex; align-items:stretch; }
    .ov .blk { flex:1 1 0; min-width:0; padding:0 22px; border-left:1px solid var(--border); display:flex; flex-direction:column; gap:3px; justify-content:center; }
    .ov .blk:first-child { padding-left:0; border-left:0; flex-direction:row; align-items:center; gap:16px; flex-grow:1.1; }
    .ov .blk:last-child { padding-right:0; }
    .ov .lbl { font-size:.78rem; color:var(--muted); letter-spacing:.02em; }
    .ov .val { font-size:1.9rem; font-weight:400; line-height:1.1; font-variant-numeric:tabular-nums; }
    .ov .val small { font-size:.9rem; color:var(--muted); margin-left:3px; }
    .ov .sub { font-size:.82rem; color:var(--muted); }
    .ov .sub b { color:var(--text); font-weight:600; font-variant-numeric:tabular-nums; }
    .boiler { position:relative; width:64px; height:64px; flex:none; border-radius:50%; display:grid; place-items:center; color:var(--c); }
    .boiler svg.rg { position:absolute; inset:0; width:100%; height:100%; }
    .boiler .ic { width:28px; height:28px; position:relative; }
    .boiler.fxon::after { content:""; position:absolute; inset:-6px; border-radius:50%; border:2px solid var(--c); opacity:0; animation:mbs-ping 2s ease-out infinite; }
    @keyframes mbs-ping { 0% { transform:scale(.85); opacity:.55; } 100% { transform:scale(1.25); opacity:0; } }
    .boiler.fxon .ic { animation:mbs-flick 1s ease-in-out infinite; transform-origin:50% 90%; }
    @keyframes mbs-flick { 0%,100% { transform:scale(1) rotate(0); } 30% { transform:scale(1.08,1.14) rotate(-3deg); } 60% { transform:scale(.97,1.04) rotate(2deg); } }
    .scale { position:relative; height:4px; border-radius:99px; background:var(--track); margin:9px 0 3px; }
    .scale i { position:absolute; left:0; top:0; bottom:0; border-radius:99px; background:var(--c-rest); }
    .scale u { position:absolute; top:-4px; width:2px; height:12px; background:var(--c-summer); border-radius:2px; text-decoration:none; }
    .flow { position:relative; z-index:2; display:flex; align-items:flex-start; gap:12px; margin-top:26px; }
    .src { width:34px; height:34px; margin-top:-16px; border-radius:50%; display:grid; place-items:center; flex:none; color:var(--c);
      background:color-mix(in srgb, var(--c) 16%, transparent); border:1px solid color-mix(in srgb, var(--c) 36%, transparent); }
    .src .ic { width:16px; height:16px; }
    .rail { flex:1; display:flex; flex-wrap:wrap; gap:10px; min-width:0; }
    .node { position:relative; flex:1 1 104px; min-width:0; padding-top:24px; }
    .node::before { content:""; position:absolute; top:0; left:-5px; right:-5px; height:2px; background:color-mix(in srgb, var(--text) 13%, transparent); }
    .node::after { content:""; position:absolute; top:0; left:50%; width:2px; height:24px; margin-left:-1px; background:color-mix(in srgb, var(--text) 13%, transparent); }
    .node.hot::before, .node.hot::after { background:var(--c); }
    .rail.flowing .node.hot::before { background:repeating-linear-gradient(90deg, var(--c) 0 8px, transparent 8px 16px); background-size:16px 2px; animation:mbs-flowx 1s linear infinite; }
    .rail.flowing .node.hot::after { background:repeating-linear-gradient(180deg, var(--c) 0 8px, transparent 8px 16px); background-size:2px 16px; animation:mbs-flowy 1s linear infinite; }
    @keyframes mbs-flowx { to { background-position:16px 0; } } @keyframes mbs-flowy { to { background-position:0 16px; } }
    .nchip { display:flex; align-items:center; gap:9px; padding:9px 11px; border-radius:16px; min-width:0;
      background:color-mix(in srgb, var(--text) 5%, transparent); border:1px solid var(--border); }
    .node.hot .nchip { border-color:color-mix(in srgb, var(--c) 45%, transparent); background:color-mix(in srgb, var(--c) 10%, transparent); }
    .nchip .dot { width:9px; height:9px; border-radius:50%; background:var(--c); flex:none; }
    .nchip .tx { min-width:0; line-height:1.2; }
    .nchip .n { font-size:.76rem; color:var(--muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .nchip .v { font-size:1rem; font-weight:500; font-variant-numeric:tabular-nums; }
    .ov .qbar { margin:18px 0 0; padding-left:0; }
    .amb { position:absolute; inset:0; z-index:1; pointer-events:none; overflow:hidden; border-radius:inherit; }
    .amb.sun::before { content:""; position:absolute; right:-90px; top:-90px; width:240px; height:240px; border-radius:50%;
      background:radial-gradient(circle, color-mix(in srgb, var(--c-summer) 42%, transparent) 0%, color-mix(in srgb, var(--c-summer) 12%, transparent) 42%, transparent 70%);
      animation:mbs-sunb 4s ease-in-out infinite; }
    .amb.sun::after { content:""; position:absolute; right:-130px; top:-130px; width:320px; height:320px; border-radius:50%; opacity:.12;
      background:repeating-conic-gradient(from 0deg, var(--c-summer) 0 4deg, transparent 4deg 18deg);
      -webkit-mask:radial-gradient(circle, transparent 28%, #000 36%, transparent 70%); mask:radial-gradient(circle, transparent 28%, #000 36%, transparent 70%);
      animation:mbs-spin 80s linear infinite; }
    @keyframes mbs-sunb { 0%,100% { opacity:.7; transform:scale(1); } 50% { opacity:1; transform:scale(1.08); } } @keyframes mbs-spin { to { transform:rotate(360deg); } }
    .amb.snow i { position:absolute; top:-10px; left:var(--l); width:var(--s); height:var(--s); border-radius:50%; background:#fff; opacity:0;
      animation:mbs-fall var(--d) linear infinite; animation-delay:var(--o); }
    @keyframes mbs-fall { 0% { transform:translate(0,0); opacity:0; } 10% { opacity:.65; } 50% { transform:translate(12px, 120px); } 90% { opacity:.5; } 100% { transform:translate(-6px, 250px); opacity:0; } }
    .amb.snow::after { content:""; position:absolute; left:0; right:0; bottom:0; height:46px; background:linear-gradient(0deg, rgba(180,215,255,.12), transparent); }
    @container (max-width: 560px) {
      .ov { padding:18px 16px 16px; }
      .ov .top { flex-direction:column; gap:14px; }
      .ov .blk { padding:0; border-left:0; }
      .ov .blk + .blk { border-top:1px solid var(--border); padding-top:12px; }
    }

    /* ---------- idővonal kártya ---------- */
    .tl { position:relative; padding:20px 24px 18px; }
    .tl .thd { display:flex; align-items:center; flex-wrap:wrap; gap:8px 12px; margin-bottom:16px; }
    .tl .tt { font-size:1.02rem; font-weight:600; margin-right:auto; }
    .tl .total { font-size:.82rem; color:var(--muted); } .tl .total b { color:var(--text); font-weight:600; }
    .seg { display:inline-flex; padding:3px; border-radius:999px; background:color-mix(in srgb, var(--text) 7%, transparent); border:1px solid var(--border); }
    .seg button { padding:4px 12px; border-radius:999px; font:inherit; font-size:.78rem; color:var(--muted); background:transparent; border:0; cursor:pointer; -webkit-tap-highlight-color:transparent; }
    .seg button:hover { color:var(--text); }
    .seg button.on { background:color-mix(in srgb, var(--text) 14%, transparent); color:var(--text); font-weight:600; }
    .tlbody { position:relative; }
    .tlrow { display:grid; grid-template-columns:104px 1fr 74px; gap:14px; align-items:center; padding:7px 0; }
    .tlrow .rn { font-size:.88rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .tlrow .du { font-size:.8rem; color:var(--muted); text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
    .track { position:relative; height:12px; border-radius:99px; background:color-mix(in srgb, var(--text) 7%, transparent); overflow:hidden; }
    .track i { position:absolute; top:0; bottom:0; min-width:4px; background:var(--k); border-radius:99px; transform-origin:0 50%; }
    .tlfx.intro .track i { animation:mbs-grow 1.2s cubic-bezier(.2,.7,.2,1) both; }
    .tlfx .track i.live { animation:mbs-livep 2s ease-in-out infinite; }
    .tlfx.intro .track i.live { animation:mbs-grow 1.2s cubic-bezier(.2,.7,.2,1) both, mbs-livep 2s ease-in-out 1.2s infinite; }
    @keyframes mbs-grow { from { transform:scaleX(0); opacity:0; } to { transform:scaleX(1); opacity:1; } }
    @keyframes mbs-livep { 0%,100% { filter:brightness(1); } 50% { filter:brightness(1.45); } }
    .tlrow.boilerrow .rn { font-weight:600; } .tlrow.boilerrow .track { height:14px; }
    .tlrow.boilerrow { border-bottom:1px solid var(--border); padding-bottom:12px; margin-bottom:5px; }
    .tlgrid { position:absolute; left:118px; right:88px; top:0; bottom:0; pointer-events:none; }
    .tlgrid span { position:absolute; top:0; bottom:0; width:1px; background:color-mix(in srgb, var(--text) 7%, transparent); }
    .tlgrid .nowline { width:2px; border-radius:2px; background:var(--text); opacity:.55; top:-2px; bottom:-2px; }
    .axis { display:grid; grid-template-columns:104px 1fr 74px; gap:14px; margin-top:8px; }
    .ticks { position:relative; height:18px; font-size:.72rem; color:var(--muted); }
    .ticks span { position:absolute; transform:translateX(-50%); white-space:nowrap; }
    .ticks span.now { right:0; left:auto; transform:none; color:var(--text); font-weight:600; }
    .legend { display:flex; flex-wrap:wrap; gap:6px 16px; margin-top:12px; font-size:.76rem; color:var(--muted); }
    .legend span::before { content:""; display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--k); margin-right:6px; }
    .tlnote { margin-top:8px; font-size:.74rem; color:var(--muted); }
    @container (max-width: 480px) {
      .tl { padding:16px 14px 14px; }
      .tlrow, .axis { grid-template-columns:70px 1fr 58px; gap:8px; }
      .tlgrid { left:78px; right:66px; }
    }

    /* ---------- chip-sor ---------- */
    .cps { display:flex; flex-wrap:wrap; gap:8px; }
    .cp { display:inline-flex; align-items:center; gap:9px; padding:7px 14px 7px 8px; border-radius:999px; border:1px solid var(--border);
      background:var(--surface); backdrop-filter:blur(var(--blur)); -webkit-backdrop-filter:blur(var(--blur)); font-size:.88rem; }
    .cp .ri { width:24px; height:24px; border-radius:50%; display:grid; place-items:center; flex:none; color:var(--c); background:color-mix(in srgb, var(--c) 18%, transparent); }
    .cp .ri .ic { width:14px; height:14px; }
    .cp .pn { color:var(--muted); } .cp .pv { font-weight:600; font-variant-numeric:tabular-nums; }
    .cp .pt { color:var(--muted); font-size:.8em; display:inline-flex; align-items:center; gap:2px; font-variant-numeric:tabular-nums; }
    .cp .pt .ic { width:.9em; height:.9em; }
    .cp.hot { border-color:color-mix(in srgb, var(--c) 50%, transparent); background:color-mix(in srgb, var(--c) 10%, var(--surface)); box-shadow:0 0 14px color-mix(in srgb, var(--c) 28%, transparent); }
    .cp.sum .pv { color:var(--c-demand); }
    .cp.sum.off .pv { color:var(--muted); }
    .dts { display:flex; flex-wrap:wrap; gap:14px 18px; padding-left:4px; }
    .dtc { display:inline-flex; align-items:center; gap:7px; font-size:.86rem; }
    .dtc i { width:8px; height:8px; border-radius:50%; background:var(--c); box-shadow:0 0 0 3px color-mix(in srgb, var(--c) 22%, transparent); }
    .dtc.hot i { animation:mbs-pulse 2s ease-in-out infinite; }
    @keyframes mbs-pulse { 0%,100% { box-shadow:0 0 0 3px color-mix(in srgb, var(--c) 22%, transparent); } 50% { box-shadow:0 0 0 7px color-mix(in srgb, var(--c) 8%, transparent); } }
    .dtc span { color:var(--muted); } .dtc b { font-weight:600; font-variant-numeric:tabular-nums; }

    /* csökkentett mozgás: nincs animáció és átmenet (a pszeudo-elemekre is vonatkozik) */
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation:none !important; transition:none !important; } }
  `;

  /* ===================================================================
   *  2.8: az új kártyák és funkciók stílusa
   * =================================================================== */
  const CSS3 = `
    .t.pn { padding:1.25em 1.5em 1.15em; font-size:16px; }
    .pn .hd2 { display:flex; align-items:center; gap:12px; margin-bottom:14px; flex-wrap:wrap; }
    .pn .hd2 .ttl { font-size:1.02rem; font-weight:600; margin-right:auto; padding-left:0; }
    .sm { font-size:.78rem; color:var(--muted); }
    .sm b { color:var(--text); font-weight:600; }
    .dot6 { display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--c); margin-right:6px; }
    .btnx { display:inline-flex; align-items:center; gap:7px; padding:7px 14px; border-radius:99px; border:1px solid var(--border); background:color-mix(in srgb,var(--text) 7%,transparent); color:var(--text); font:inherit; font-size:.84rem; cursor:pointer; -webkit-tap-highlight-color:transparent; }
    .btnx .ic { width:15px; height:15px; }
    .btnx:hover:not(:disabled) { background:color-mix(in srgb,var(--text) 14%,transparent); }
    .btnx:disabled { opacity:.4; cursor:default; }
    .btnx.hot { color:var(--c-demand); border-color:color-mix(in srgb,var(--c-demand) 45%,transparent); background:color-mix(in srgb,var(--c-demand) 12%,transparent); }

    /* ---------- Miért fűt? ---------- */
    .why .top { display:flex; gap:18px; align-items:center; }
    .why .orb { position:relative; width:58px; height:58px; flex:none; border-radius:50%; display:grid; place-items:center; color:var(--c);
      background:color-mix(in srgb,var(--c) 14%,transparent); border:1px solid color-mix(in srgb,var(--c) 40%,transparent); }
    .why .orb .ic { width:27px; height:27px; }
    .why .orb.on::after { content:""; position:absolute; inset:-6px; border-radius:50%; border:2px solid var(--c); opacity:0; animation:mbs-ping 2s ease-out infinite; }
    .why .lbl { font-size:.78rem; color:var(--muted); margin-bottom:2px; }
    .why .sent { font-size:1.08rem; line-height:1.75; }
    .why .rcp { display:inline-flex; align-items:center; gap:6px; padding:1px 11px 1px 9px; border-radius:99px; font-size:.88em; font-weight:500; vertical-align:1px; margin:0 1px;
      background:color-mix(in srgb,var(--c) 13%,transparent); border:1px solid color-mix(in srgb,var(--c) 36%,transparent); white-space:nowrap; }
    .why .rcp i { width:7px; height:7px; border-radius:50%; background:var(--c); }
    .why .rcp b { color:var(--c); font-weight:600; font-variant-numeric:tabular-nums; }
    .why .list { margin-top:16px; }
    .why .li { display:grid; grid-template-columns:minmax(70px,.9fr) 1.4fr auto; gap:14px; align-items:center; padding:8px 0; font-size:.86rem; border-top:1px solid color-mix(in srgb,var(--text) 8%,transparent); }
    .why .li .nmx { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .why .li .db { position:relative; height:8px; border-radius:99px; background:var(--track); overflow:hidden; }
    .why .li .db i { position:absolute; left:0; top:0; bottom:0; border-radius:99px; background:var(--c); }
    .why .li .rt { color:var(--muted); text-align:right; font-variant-numeric:tabular-nums; }
    .why .li .rt b { color:var(--text); font-weight:600; }
    .why .notes { margin-top:12px; display:flex; flex-direction:column; gap:7px; }
    .why .nt { display:flex; align-items:center; gap:9px; font-size:.84rem; color:var(--muted); }
    .why .nt .ic { width:16px; height:16px; color:var(--c); }
    .why .nt b { color:var(--text); font-weight:600; font-variant-numeric:tabular-nums; }
    .why.compact { padding:.9em 1.1em; }
    .why.compact .top { gap:12px; } .why.compact .orb { width:40px; height:40px; } .why.compact .orb .ic { width:19px; height:19px; }
    .why.compact .sent { font-size:.96rem; line-height:1.65; }
    @media (max-width:420px) { .why .li { grid-template-columns:1fr auto; } .why .li .db { display:none; } }

    /* ---------- grafikon (szoba részletes) ---------- */
    .chart { display:block; width:100%; height:auto; overflow:visible; }
    .chart text { fill:var(--muted); font-size:10.5px; font-family:inherit; }
    .chart .gl { stroke:color-mix(in srgb,var(--text) 9%,transparent); stroke-width:1; }
    .chart .ln { fill:none; stroke:var(--c); stroke-width:2.4; stroke-linecap:round; stroke-linejoin:round; }
    .chart .tg { fill:none; stroke:color-mix(in srgb,var(--text) 55%,transparent); stroke-width:1.5; stroke-dasharray:4 4; }
    .chart .nw { fill:var(--text); stroke:var(--surface); stroke-width:2; }
    .chart .nl { stroke:color-mix(in srgb,var(--text) 40%,transparent); stroke-width:1; stroke-dasharray:2 3; }
    .chart .lane { fill:color-mix(in srgb,var(--text) 7%,transparent); }
    .chart .intro { animation:mbs-draw 1.1s ease-out both; }
    @keyframes mbs-draw { from { stroke-dasharray:100; stroke-dashoffset:100; } to { stroke-dasharray:100; stroke-dashoffset:0; } }
    .lgd { display:flex; gap:6px 16px; font-size:.74rem; color:var(--muted); margin-top:6px; flex-wrap:wrap; }
    .lgd .dash { display:inline-block; width:12px; border-top:2px dashed var(--muted); vertical-align:3px; margin-right:6px; }

    /* ---------- Szoba részletes ---------- */
    .rc .body { display:grid; grid-template-columns:minmax(210px,250px) 1fr; gap:26px; align-items:start; }
    .rc .left .t.glass { background:none; border:0; box-shadow:none; backdrop-filter:none; -webkit-backdrop-filter:none; overflow:visible; }
    .rc .left .t.glass::before { display:none; }
    .rc .left .t.glass .in { padding:.2em 0 0; }
    .rc .left .t.glass .nm { display:none; }
    .rc .vl { margin-top:14px; display:grid; gap:2px; }
    .rc .vr { display:grid; grid-template-columns:20px 1fr auto auto; gap:10px; align-items:center; padding:8px 0; font-size:.84rem; border-top:1px solid color-mix(in srgb,var(--text) 8%,transparent); }
    .rc .vr .ic { width:17px; height:17px; color:var(--c); }
    .rc .vr .a { color:var(--muted); font-variant-numeric:tabular-nums; } .rc .vr .a b { color:var(--text); font-weight:600; }
    .rc .vr .pr { font-size:.76rem; padding:2px 10px; border-radius:99px; border:1px solid var(--border); background:color-mix(in srgb,var(--text) 6%,transparent); display:inline-flex; gap:6px; align-items:center; }
    .rc .vr .pr .ic { width:13px; height:13px; color:var(--muted); }
    .rc .vr .vn { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .rc .hd2 .ttl { cursor:default; } .rc .hchips { align-items:center; }
    .rc.solo .body { grid-template-columns:1fr; } .rc.solo .left { max-width:260px; margin:0 auto; }
    .rc .actions { display:flex; gap:8px; flex-wrap:wrap; margin-top:14px; align-items:center; }
    .rc .hchips { display:flex; gap:6px; flex-wrap:wrap; }
    @media (max-width:560px) { .rc .body { grid-template-columns:1fr; } }

    /* ---------- Heti hőtérkép ---------- */
    .hm .sel { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:14px; }
    .hm .sel button { padding:5px 13px; border-radius:99px; font:inherit; font-size:.78rem; color:var(--muted); border:1px solid var(--border); background:color-mix(in srgb,var(--text) 5%,transparent); cursor:pointer; }
    .hm .sel button:hover { color:var(--text); }
    .hm .sel button.on { color:var(--text); font-weight:600; background:color-mix(in srgb,var(--text) 14%,transparent); }
    .hm .hgrid { position:relative; display:grid; grid-template-columns:var(--dnw,34px) repeat(24,minmax(0,1fr)); gap:3px; align-items:center; }
    .hm .dn { font-size:.74rem; color:var(--muted); text-align:right; padding-right:6px; }
    .hm .hn { font-size:.66rem; color:var(--muted); text-align:left; height:16px; white-space:nowrap; }
    .hm .cell { aspect-ratio:1; border-radius:5px; background:color-mix(in srgb,var(--c-demand) calc(var(--v) * 90% + 4%), color-mix(in srgb,var(--text) 6%,transparent)); position:relative; cursor:default; }
    .hm .cell.z { background:color-mix(in srgb,var(--text) 6%,transparent); }
    .hm .cell.hi { outline:2px solid var(--text); outline-offset:1px; z-index:3; }
    .hm .cell.now { box-shadow:inset 0 0 0 1.5px color-mix(in srgb,var(--text) 55%,transparent); }
    .hm .tip { position:absolute; z-index:5; left:50%; bottom:calc(100% + 8px); transform:translateX(-50%); padding:6px 10px; border-radius:10px; font-size:.76rem; white-space:nowrap; text-align:left;
      background:color-mix(in srgb,var(--card-background-color,#1c1c1e) 96%,transparent); border:1px solid var(--border); box-shadow:0 8px 24px rgba(0,0,0,.35); pointer-events:none; color:var(--text); }
    .hm .tip.l { left:0; transform:none; } .hm .tip.r { left:auto; right:0; transform:none; }
    .hm .cell.fu { background:transparent; border:1px dashed color-mix(in srgb,var(--text) 12%,transparent); }
    .hm .dn small { display:block; font-size:.62rem; opacity:.7; line-height:1; margin-top:1px; }
    .hm .lg { display:flex; align-items:center; gap:10px; margin-top:14px; font-size:.74rem; color:var(--muted); }
    .hm .lg i { display:block; width:150px; height:8px; border-radius:99px; background:linear-gradient(90deg,color-mix(in srgb,var(--text) 6%,transparent),color-mix(in srgb,var(--c-demand) 94%,transparent)); }
    .hm .sum { display:flex; gap:8px 22px; flex-wrap:wrap; margin-top:12px; font-size:.8rem; color:var(--muted); }
    .hm .sum b { color:var(--text); font-weight:600; }

    /* ---------- Statisztika ---------- */
    .stt .kp { display:flex; gap:10px; flex-wrap:wrap; }
    .stt .k { padding:10px 14px; border-radius:16px; border:1px solid var(--border); background:color-mix(in srgb,var(--text) 5%,transparent); min-width:120px; flex:1 1 120px; }
    .stt .k .l { font-size:.72rem; color:var(--muted); } .stt .k .v { font-size:1.25rem; font-weight:500; margin-top:2px; font-variant-numeric:tabular-nums; }
    .stt .k .v small { font-size:.72rem; color:var(--muted); margin-left:3px; }
    .stt .k.cost .v { color:var(--c-summer); } .stt .k .e { font-size:.66rem; color:var(--muted); margin-top:1px; }
    .stt .two { display:grid; grid-template-columns:1.5fr 1fr; gap:26px; margin-top:18px; align-items:start; }
    .stt h4 { margin:0 0 8px; font-size:.82rem; font-weight:600; color:var(--text); }
    .stt .rk { display:grid; grid-template-columns:minmax(56px,.75fr) 1fr 6.2em; gap:10px; align-items:center; padding:5px 0; font-size:.82rem; }
    .stt .rk .db { height:9px; border-radius:99px; background:var(--track); position:relative; overflow:hidden; }
    .stt .rk .db i { position:absolute; inset:0 auto 0 0; border-radius:99px; background:var(--c-demand); }
    .stt .rk .vv { color:var(--muted); text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
    .stt .lgd span::before { content:""; display:inline-block; width:9px; height:9px; margin-right:6px; border-radius:3px; background:var(--k); vertical-align:-1px; }
    .stt .sub2 { margin-top:16px; }
    .stt .two.one { grid-template-columns:1fr; }
    @media (max-width:560px) { .stt .two { grid-template-columns:1fr; } }

    /* ---------- Kazán ciklusok ---------- */
    .cyc { margin-top:16px; }
    .cyc .pulses { position:relative; height:34px; border-radius:12px; background:color-mix(in srgb,var(--text) 5%,transparent); overflow:hidden; }
    .cyc .pulses i { position:absolute; top:6px; bottom:6px; border-radius:6px; background:var(--c-demand); min-width:3px; }
    .cyc .pulses i.sh { background:var(--c-stale); }
    .cyc .pax { display:flex; justify-content:space-between; font-size:.68rem; color:var(--muted); margin-top:4px; }
    .cyc .cks { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
    .cyc .ck { padding:8px 12px; border-radius:14px; border:1px solid var(--border); background:color-mix(in srgb,var(--text) 5%,transparent); font-size:.8rem; }
    .cyc .ck .l { font-size:.68rem; color:var(--muted); }
    .cyc .ck .v { font-size:1.05rem; font-variant-numeric:tabular-nums; }
    .cyc .ck.bad { border-color:color-mix(in srgb,var(--c-stale) 45%,transparent); background:color-mix(in srgb,var(--c-stale) 9%,transparent); }
    .cyc .ck.bad .v { color:var(--c-stale); }

    /* ---------- Figyelmeztetések ---------- */
    .al { padding:.9em 1.25em; }
    .al .ar { display:grid; grid-template-columns:36px 1fr auto; gap:14px; align-items:center; padding:10px 0; border-top:1px solid color-mix(in srgb,var(--text) 8%,transparent); }
    .al .ar:first-child { border-top:0; }
    .al .ai { width:36px; height:36px; border-radius:50%; display:grid; place-items:center; color:var(--c); background:color-mix(in srgb,var(--c) 15%,transparent); border:1px solid color-mix(in srgb,var(--c) 38%,transparent); flex:none; }
    .al .ai .ic { width:18px; height:18px; }
    .al .at { font-size:.92rem; font-weight:500; } .al .as { font-size:.78rem; color:var(--muted); margin-top:1px; }
    .al .ag { font-size:.76rem; color:var(--muted); text-align:right; white-space:nowrap; }
    .al.ok { display:inline-flex; align-items:center; gap:10px; padding:.55em 1em .55em .6em; border-radius:99px; width:auto; }
    .al.ok .ai { width:28px; height:28px; } .al.ok .ai .ic { width:15px; height:15px; }
    .al.abr { display:flex; align-items:center; gap:12px; padding:.6em .85em; border-radius:18px; cursor:pointer; }
    .al.abr .ai { width:30px; height:30px; } .al.abr .ai .ic { width:16px; height:16px; }
    .al.abr .at { font-size:.88rem; flex:1; }
    .al.abr .bdg { font-size:.76rem; padding:2px 10px; border-radius:99px; background:color-mix(in srgb,var(--c) 16%,transparent); color:var(--c); font-weight:600; }
    .al.abr .chev { width:1em; height:1em; color:var(--muted); transition:transform .2s; }
    .al.abr.open .chev { transform:rotate(180deg); }
    .al .more { margin-top:8px; border-top:1px solid color-mix(in srgb,var(--text) 8%,transparent); }
    .al .more .ar:first-child { border-top:0; }
    .al.empty { text-align:center; color:var(--muted); font-size:.84rem; border-style:dashed; background:none; }
    .alwrap { display:flex; flex-direction:column; gap:10px; }

    /* ---------- sparkline (csempe / sor) ---------- */
    .sp { display:block; width:100%; height:auto; overflow:visible; }
    .sp .l { fill:none; stroke:var(--c); stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }
    .sp .t { fill:none; stroke:color-mix(in srgb,var(--text) 45%,transparent); stroke-width:1; stroke-dasharray:3 3; }
    .sp .hb { fill:var(--c-demand); opacity:.85; }
    .sp .n { fill:var(--text); }
    .spw { width:100%; padding:0 .1em; }
    .spw .spc { display:flex; justify-content:space-between; font-size:.66rem; color:var(--muted); margin-top:1px; }
    .rw .rsp { display:block; min-width:0; }
    .rw .rsp .sp { max-height:34px; }

    /* ---------- húzható gyűrű ---------- */
    .knob { position:absolute; width:44px; height:44px; margin:-22px 0 0 -22px; border-radius:50%; cursor:grab; touch-action:none; z-index:4; -webkit-tap-highlight-color:transparent; }
    .t.dragging .knob { cursor:grabbing; }
    .ring .bubble { position:absolute; z-index:6; padding:5px 11px; border-radius:99px; font-size:.95rem; font-weight:600; font-variant-numeric:tabular-nums; pointer-events:none;
      background:var(--text); color:var(--card-background-color,#15171a); box-shadow:0 6px 18px rgba(0,0,0,.45); transform:translate(-50%,-190%); white-space:nowrap; }
    .ring .bubble::after { content:""; position:absolute; left:50%; bottom:-5px; margin-left:-5px; border:5px solid transparent; border-top-color:var(--text); border-bottom:0; }

    /* ---------- hosszú nyomás: gyűrű és lap ---------- */
    .holdring { position:fixed; z-index:50; width:64px; height:64px; margin:-32px 0 0 -32px; pointer-events:none; opacity:0; animation:mbs-holdfade .6s linear forwards; transform:rotate(-90deg); }
    .holdring circle { fill:none; stroke:var(--c-demand); stroke-width:3.5; stroke-linecap:round; stroke-dasharray:100; stroke-dashoffset:100; animation:mbs-hold .6s linear forwards; }
    @keyframes mbs-hold { to { stroke-dashoffset:0; } }
    @keyframes mbs-holdfade { 0%,22% { opacity:0; } 30%,100% { opacity:1; } }
    .t[data-room], .rw[data-room] { -webkit-touch-callout:none; }
    .sheetroot { position:fixed; inset:0; z-index:9999; pointer-events:none; font-size:16px; }
    .sh-wrap { position:fixed; inset:0; display:flex; align-items:flex-end; justify-content:center; pointer-events:none; }
    .sh-wrap.open { pointer-events:auto; }
    .sh-dim { position:absolute; inset:0; background:rgba(5,6,8,.62); backdrop-filter:blur(3px); -webkit-backdrop-filter:blur(3px); opacity:0; transition:opacity .25s; }
    .sh-wrap.open .sh-dim { opacity:1; }
    .sheet { position:relative; width:min(100%,560px); max-height:90vh; overflow:auto; border-radius:26px 26px 0 0; padding:0 20px calc(22px + env(safe-area-inset-bottom,0px));
      background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.02)), var(--card-background-color,#1c1f24); border:1px solid var(--border); border-bottom:0;
      box-shadow:0 -10px 40px rgba(0,0,0,.5); transform:translateY(105%); transition:transform .3s cubic-bezier(.2,.8,.2,1); color:var(--text); }
    .sh-wrap.open .sheet { transform:none; }
    .sheet .grab { padding:10px 0 12px; display:grid; place-items:center; cursor:grab; touch-action:none; }
    .sheet .grab i { display:block; width:42px; height:5px; border-radius:99px; background:color-mix(in srgb,var(--text) 28%,transparent); }
    .sheet .sh { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
    .sheet .sh .n { font-size:1.12rem; font-weight:600; margin-right:auto; }
    .sheet .xb { display:grid; place-items:center; width:34px; height:34px; border-radius:50%; border:1px solid var(--border); background:color-mix(in srgb,var(--text) 7%,transparent); color:var(--text); cursor:pointer; padding:0; }
    .sheet .xb .ic { width:16px; height:16px; }
    .sheet .big2 { display:flex; align-items:baseline; gap:14px; margin:2px 0 8px; flex-wrap:wrap; }
    .sheet .big2 .bv { font-size:2.6rem; }
    .sheet .big2 .trend { margin:0; justify-content:flex-start; }
    .sheet .ctrl { display:flex; align-items:center; gap:10px; margin:12px 0 4px; }
    .sheet .ctrl .pm { width:2.4em; height:2.4em; }
    .sheet .ctrl .tv { font-size:1.2rem; font-weight:500; min-width:80px; text-align:center; font-variant-numeric:tabular-nums; }
    .sheet .pchips { display:flex; gap:6px; flex-wrap:wrap; margin:10px 0 2px; }
    .sheet .pchips button { display:inline-flex; align-items:center; gap:6px; padding:6px 12px; border-radius:99px; font:inherit; font-size:.78rem; color:var(--muted); border:1px solid var(--border); background:color-mix(in srgb,var(--text) 5%,transparent); cursor:pointer; }
    .sheet .pchips button.on { color:var(--text); font-weight:600; background:color-mix(in srgb,var(--text) 15%,transparent); }
    .sheet .pchips .ic { width:14px; height:14px; }
    .sheet .vl { margin-top:8px; }
    .sheet .vr { display:grid; grid-template-columns:20px 1fr auto; gap:10px; align-items:center; padding:8px 0; font-size:.82rem; border-top:1px solid color-mix(in srgb,var(--text) 8%,transparent); }
    .sheet .vr .ic { width:16px; height:16px; color:var(--c); } .sheet .vr .a { color:var(--muted); font-variant-numeric:tabular-nums; } .sheet .vr .a b { color:var(--text); font-weight:600; }
    .sheet .chip { font-size:.74rem; }

    /* ---------- hőtérkép dizájn ---------- */
    .t.heat { position:relative; min-height:10.6em; padding:1em 1.15em .9em; color:var(--fg,#fff); display:flex; flex-direction:column; font-size:16px; border:0;
      background:linear-gradient(155deg,var(--b1),var(--b2)); box-shadow:0 10px 30px color-mix(in srgb,var(--b1) 28%,transparent); backdrop-filter:none; -webkit-backdrop-filter:none; }
    .t.heat::before { display:none; }
    .t.heat::after { content:""; position:absolute; inset:0; background:radial-gradient(180px 120px at 100% 0%,rgba(255,255,255,.22),transparent 70%); pointer-events:none; }
    .t.heat .tp { display:flex; justify-content:space-between; align-items:center; font-weight:500; font-size:1rem; gap:8px; }
    .t.heat .tp .nm { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-weight:500; font-size:1em; }
    .t.heat .tp .ic { width:1.2em; height:1.2em; opacity:.9; }
    .t.heat .bg { margin-top:auto; font-size:3rem; line-height:1; font-weight:400; display:flex; align-items:flex-start; font-variant-numeric:tabular-nums; padding-top:.3em; }
    .t.heat .bg .dc { font-size:.46em; margin-top:.42em; color:inherit; opacity:.8; }
    .t.heat .bg .un { font-size:.34em; margin:.5em 0 0 .25em; color:inherit; opacity:.8; }
    .t.heat .rw2 { display:flex; justify-content:space-between; font-size:.8rem; margin-top:6px; opacity:.9; font-variant-numeric:tabular-nums; gap:8px; }
    .t.heat .tb { height:4px; border-radius:99px; background:rgba(255,255,255,.28); margin-top:8px; overflow:hidden; }
    .t.heat .tb i { display:block; height:100%; background:rgba(255,255,255,.92); border-radius:99px; }
    .t.heat.dis { filter:saturate(.35) brightness(.78); }

    /* ---------- éjszakai mód ---------- */
    .root.nt .t, .root.nt .rw, .root.nt .sheet { filter:brightness(calc(1 - (1 - var(--nd,.7)) * var(--k,0))) saturate(calc(1 - .28 * var(--k,0))); }
    .root.nt .fx { opacity:calc(1 - var(--k,0)); }
    .root.night .fx, .root.night .t.heat::after { display:none; }
    .root.night *, .root.night *::before, .root.night *::after { animation:none !important; }
    .root.night .t[class*="gl"] { box-shadow:0 0 .5em 0 color-mix(in srgb,var(--c) 18%,transparent), inset 0 0 0 1px color-mix(in srgb,var(--c) 22%,transparent); }

    /* ---------- e-ink: papír, éles vonalak, színek helyett mintázat ---------- */
    .root.look-eink { --text:#111; --muted:#555; --border:#111; --track:#d8d4c8; --surface:#f3f0e6; --card-background-color:#f3f0e6; --primary-text-color:#111; --secondary-text-color:#555; color:#111; }
    .root.look-eink [data-st] { --c:#111; }
    .root.look-eink .t, .root.look-eink .rw, .root.look-eink .pill, .root.look-eink .cp { background:#f3f0e6 !important; border:2px solid #111 !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important; border-radius:14px !important; box-shadow:none !important; }
    .root.look-eink .t::before, .root.look-eink .t::after, .root.look-eink .rw::before { display:none !important; }
    .root.look-eink .fx { display:none !important; }
    .root.look-eink .big, .root.look-eink .nm { color:#111; }
    .root.look-eink .big .dc, .root.look-eink .big .un { color:#555; }
    .root.look-eink .pm, .root.look-eink .pre { background:#fff; border:2px solid #111; color:#111; }
    .root.look-eink .chip { background:#fff; color:#111; border:2px solid #111; }
    .root.look-eink .hum, .root.look-eink .dev, .root.look-eink .trend.up, .root.look-eink .trend.down { color:#111; }
    .root.look-eink .ring svg path[data-role="arc"] { stroke:#111; }
    .root.look-eink .sp .l { stroke:#111; } .root.look-eink .sp .hb { fill:#111; }
    .root.look-eink .t.heat { color:#111; background:#f3f0e6 !important; }
    .root.look-eink .pat { display:inline-block; width:1.15em; height:1.15em; border:2px solid #111; border-radius:4px; flex:none; background:var(--pt); }
    .root.look-eink .stripe { height:14px; border-bottom:2px solid #111; background:var(--pt); }
    .root.look-eink .glass .in { padding-top:.7em; }
    .root:not(.look-eink) .pat, .root:not(.look-eink) .stripe { display:none; }
    .root.look-eink [data-st="demand"] { --pt:repeating-linear-gradient(45deg,#111 0 2px,transparent 2px 6px); }
    .root.look-eink [data-st="boost"] { --pt:repeating-linear-gradient(45deg,#111 0 2px,transparent 2px 5px),repeating-linear-gradient(-45deg,#111 0 2px,transparent 2px 5px); }
    .root.look-eink [data-st="waiting"] { --pt:radial-gradient(#111 1.5px,transparent 1.8px) 0 0/6px 6px; }
    .root.look-eink [data-st="rest"] { --pt:repeating-linear-gradient(0deg,#111 0 2px,transparent 2px 6px); }
    .root.look-eink [data-st="stale"] { --pt:repeating-linear-gradient(90deg,#111 0 3px,transparent 3px 5px); }
    .root.look-eink [data-st="window"], .root.look-eink [data-st="windowpend"] { --pt:radial-gradient(circle at 50% 50%,#111 42%,transparent 46%); }
    .root.look-eink [data-st="idle"], .root.look-eink [data-st="off"] { --pt:transparent; }

    /* ---------- neon: fekete alap, izzó körvonal és gyűrű ---------- */
    .root.look-neon { --surface:#05070d; --card-background-color:#05070d; --border:rgba(255,255,255,.18); }
    .root.look-neon .t, .root.look-neon .rw, .root.look-neon .pill { background:#05070d !important; border:1px solid color-mix(in srgb,var(--c) 75%,transparent) !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important; border-radius:18px !important;
      box-shadow:0 0 0 1px color-mix(in srgb,var(--c) 22%,transparent), 0 0 22px color-mix(in srgb,var(--c) 38%,transparent), inset 0 0 26px color-mix(in srgb,var(--c) 10%,transparent) !important; }
    .root.look-neon .t::before, .root.look-neon .t::after, .root.look-neon .rw::before { display:none !important; }
    .root.look-neon .big { font-weight:300; text-shadow:0 0 14px color-mix(in srgb,var(--c) 75%,transparent), 0 0 3px color-mix(in srgb,var(--c) 90%,transparent); color:#fff; }
    .root.look-neon .chip, .root.look-neon .pre, .root.look-neon .pm { background:transparent; border-color:color-mix(in srgb,var(--c) 70%,transparent); color:var(--c); box-shadow:0 0 10px color-mix(in srgb,var(--c) 30%,transparent); }
    .root.look-neon .pm { color:#fff; }
    .root.look-neon .glass .nm { letter-spacing:.14em; text-transform:uppercase; font-size:.86em; color:color-mix(in srgb,var(--c) 85%,#fff); text-shadow:0 0 8px color-mix(in srgb,var(--c) 60%,transparent); }
    .root.look-neon .ring svg { overflow:visible; }
    .root.look-neon .ring svg path[data-role="arc"] { filter:drop-shadow(0 0 5px var(--c)) drop-shadow(0 0 10px var(--c)); }
    .root.look-neon .t.heat { color:var(--fg,#fff); }
  `;
  /* ===================================================================
   *  Közös ős: minden kártya ebből épül (shadow DOM, koppintás, gyorsgombok,
   *  sima átmenetek, visszaszámlálók)
   * =================================================================== */
  class MbsBase extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" });
      this._sig = null;
      this._open = null;          // melyik szoba profil-listája van nyitva
      this._pending = {};         // szoba -> {value, timer, sent, expire}: a + / − gombok még nem érvényesült értéke
      this._pendingPreset = {};   // szoba -> {value, expire}
      this._pendingQuick = null;  // {value, expire}: a gyorsgomb még nem érvényesült profilja
      this._toast = null;         // {text, timer}
      this._shown = {};           // kulcs -> a képernyőn most látható (animált) értékek
      this._raf = {};
      this._cdMax = {};           // visszaszámláló: a látott legnagyobb hátralévő idő (a gyűrű arányához)
      this._tick = null;
      this._onDoc = (ev) => {
        if (this._open == null) return;
        if (ev.type === "keydown" && ev.key !== "Escape") return;
        if (ev.type === "click") {
          const path = typeof ev.composedPath === "function" ? ev.composedPath() : [];
          if (path.some((n) => n && n.classList && (n.classList.contains("menu") || n.classList.contains("pre")))) return;
        }
        this._open = null;
        this._sig = null;
        this._render();
      };
    }

    connectedCallback() {
      document.addEventListener("click", this._onDoc, true);
      document.addEventListener("keydown", this._onDoc, true);
      if (this._config && this._hass) { this._sig = null; this._render(); }
    }

    disconnectedCallback() {
      document.removeEventListener("click", this._onDoc, true);
      document.removeEventListener("keydown", this._onDoc, true);
      Object.values(this._pending).forEach((p) => { clearTimeout(p.timer); clearTimeout(p.expire); });
      Object.values(this._pendingPreset).forEach((p) => clearTimeout(p.expire));
      if (this._pendingQuick) clearTimeout(this._pendingQuick.expire);
      if (this._toast) clearTimeout(this._toast.timer);
      Object.values(this._raf).forEach((id) => cancelAnimationFrame(id));
      this._pending = {};
      this._pendingPreset = {};
      this._pendingQuick = null;
      this._toast = null;
      this._raf = {};
      this._stopTick();
      if (this._nightTimer) { clearInterval(this._nightTimer); this._nightTimer = null; }
    }

    set hass(hass) {
      this._hass = hass;
      this._render();
    }

    getGridOptions() { return { columns: 12, min_columns: 3 }; }

    /* ---------- megjelenési változók ---------- */
    _presetOf() { return PRESET[this._config.design] || PRESET.wide; }

    _vars(cfg) {
      const p = this._presetOf();
      const n = (v, d) => (v == null || v === "" || isNaN(Number(v)) ? d : Number(v));
      const colors = COLOR_KEYS.map((k) => `--c-${k}:${cssColor(cfg["color_" + k] != null ? cfg["color_" + k] : DEFAULT_COLORS[k])}`).join(";");
      const cols = Math.round(n(cfg.columns, 0));
      const grid = cols > 0 ? `--cols:${cols}` : `--cols:auto-fill`;
      return `--mbs-radius:${n(cfg.radius, p.radius)}px;--mbs-opacity:${n(cfg.opacity, p.opacity)}%;--mbs-blur:${n(cfg.blur, p.blur)}px;${colors};${grid}`;
    }

    _unit() {
      const u = this._hass && this._hass.config && this._hass.config.unit_system && this._hass.config.unit_system.temperature;
      return u || "°C";
    }

    _num(v, d) {
      if (v == null || isNaN(v)) return "–";
      const lang = langOf(this._hass);
      return Number(v).toLocaleString(lang, { minimumFractionDigits: d, maximumFractionDigits: d });
    }

    /** A nagy számjegyek: egész rész + kisebb tizedes rész + egység. */
    _bigInner(v, d) {
      const s = this._num(v, d), sep = s.search(/[.,]/);
      const ip = sep < 0 ? s : s.slice(0, sep), dp = sep < 0 ? "" : s.slice(sep);
      return `${esc(ip)}${dp ? `<span class="dc">${esc(dp)}</span>` : ""}<span class="un">${esc(this._unit())}</span>`;
    }

    _reduced() {
      try { return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches); } catch (e) { return false; }
    }

    /* ---------- koppintás ---------- */
    _tapAction() { return this._config.tap_action; }
    _tapOn() { return this._tapAction() !== "none"; }
    _tapEntity(r) {
      const a = this._tapAction();
      if (a === "none") return null;
      if (a === "valve" && r.valve) return r.valve.id;
      return r.id;
    }
    _tapAttr(r) {
      const e = this._tapEntity(r);
      return e ? `data-entity="${esc(e)}"` : "";
    }

    _callService(domain, service, data) {
      const h = this._hass;
      if (!h || typeof h.callService !== "function") return Promise.resolve();
      try { return Promise.resolve(h.callService(domain, service, data)); } catch (e) { return Promise.reject(e); }
    }

    _redraw() { this._sig = null; this._render(); }

    _room(id) { return this._data && this._data.rooms.find((x) => x.id === id); }

    _presetLabelFor(valveId, p) {
      const h = this._hass;
      try {
        if (h && typeof h.formatEntityAttributeValue === "function" && h.states[valveId]) {
          const t = h.formatEntityAttributeValue(h.states[valveId], "preset_mode", p);
          if (t && String(t) !== String(p)) return String(t);
        }
      } catch (e) { /* tartalék lent */ }
      const k = "p_" + String(p).toLowerCase();
      if (STR.en[k]) return T(h, k);
      const txt = String(p).replace(/[_-]+/g, " ");
      return txt.charAt(0).toUpperCase() + txt.slice(1);
    }

    /* ---------- célhőmérséklet és profil (egy szoba) ---------- */
    _bounds(r) {
      const v = r.valve, c = this._config;
      const lo = v && v.min != null ? v.min : 5, hi = v && v.max != null ? v.max : 35;
      const step = Number(c.step) > 0 ? Number(c.step) : (v && v.step > 0 ? v.step : 0.5);
      return { lo, hi, step };
    }

    /** + / −: a kijelzett érték azonnal változik, a hívás a gyors koppintások után egyszer megy el. */
    _adjust(id, dir) {
      const r = this._room(id);
      if (!r || !r.valve || !r.valve.ok) return;
      const { lo, hi, step } = this._bounds(r);
      const pend = this._pending[id];
      const base = pend ? pend.value : r.target;
      if (base == null) return;
      let v = dir > 0 ? Math.floor(base / step + 1e-9) * step + step : Math.ceil(base / step - 1e-9) * step - step;
      this._queueTarget(id, Math.round(clamp(v, lo, hi) * 100) / 100);
    }

    /** Új célhőmérséklet várakozó (optimista) értékként; a hívás a gyors módosítások után egyszer megy el. */
    _queueTarget(id, v) {
      const pend = this._pending[id];
      if (pend) { clearTimeout(pend.timer); clearTimeout(pend.expire); }
      this._pending[id] = { value: v, sent: false, timer: setTimeout(() => this._commit(id), 700), expire: null };
      this._redraw();
    }

    _commit(id) {
      const p = this._pending[id], r = this._room(id);
      if (!p) return;
      if (!r || !r.valveIds.length) { delete this._pending[id]; this._redraw(); return; }
      p.sent = true;
      p.expire = setTimeout(() => { if (this._pending[id] === p) { delete this._pending[id]; this._redraw(); } }, 8000);
      this._callService("climate", "set_temperature", { entity_id: r.valveIds, temperature: p.value })
        .catch(() => { if (this._pending[id] === p) { clearTimeout(p.expire); delete this._pending[id]; this._redraw(); } });
    }

    _setPreset(id, preset) {
      const r = this._room(id);
      this._open = null;
      if (!r || !r.valveIds.length) { this._redraw(); return; }
      const old = this._pendingPreset[id];
      if (old) clearTimeout(old.expire);
      const p = { value: preset, expire: null };
      p.expire = setTimeout(() => { if (this._pendingPreset[id] === p) { delete this._pendingPreset[id]; this._redraw(); } }, 8000);
      this._pendingPreset[id] = p;
      this._redraw();
      this._callService("climate", "set_preset_mode", { entity_id: r.valveIds, preset_mode: preset })
        .catch(() => { if (this._pendingPreset[id] === p) { clearTimeout(p.expire); delete this._pendingPreset[id]; this._redraw(); } });
    }

    /* ---------- gyorsgombok: minden megjelenített szoba profilja egyszerre ---------- */
    _quickInfo(rooms) {
      const valves = [];
      rooms.forEach((r) => r.valves.forEach((v) => { if (v.ok && v.presets.length) valves.push(v); }));
      if (!valves.length) return null;
      // csak azok a profilok, amelyeket MINDEN szelep ismer
      let common = valves[0].presets.filter((p) => valves.every((v) => v.presets.includes(p)));
      const sel = this._config.quick_presets;
      if (Array.isArray(sel) && sel.length) common = sel.map(String).filter((p) => common.includes(p));
      if (!common.length) return null;
      const same = valves.every((v) => v.preset === valves[0].preset);
      return { valves, common, current: same ? valves[0].preset : null };
    }

    _quickHtml(rooms) {
      if (!this._config.show_quick) return "";
      const info = this._quickInfo(rooms);
      if (!info) return "";
      const h = this._hass, pend = this._pendingQuick;
      const cur = pend ? pend.value : info.current;
      const btns = info.common.map((p) =>
        `<button type="button" class="${p === cur ? "on" : ""}" data-act="quick" data-preset="${esc(p)}" aria-pressed="${p === cur}">${ic(PRESET_ICON[p] || "tune")}<span>${esc(this._presetLabelFor(info.valves[0].id, p))}</span></button>`).join("");
      const mixed = !pend && info.current == null ? `<span class="qmix">${esc(T(h, "quick_mixed"))}</span>` : "";
      const toast = this._toast ? `<span class="toast" role="status">${ic("check")}${esc(this._toast.text)}</span>` : "";
      return `<div class="qbar"><span class="ql">${esc(T(h, "quick_all"))}</span><div class="qseg" role="group">${btns}</div>${mixed}${toast}</div>`;
    }

    _quickSet(preset) {
      const rooms = this._data ? this._data.rooms : [];
      const ids = [];
      let n = 0;
      rooms.forEach((r) => {
        let hit = false;
        r.valves.forEach((v) => { if (v.ok && v.presets.includes(preset)) { ids.push(v.id); hit = true; } });
        if (hit) n++;
      });
      if (!ids.length) return;
      if (this._pendingQuick) clearTimeout(this._pendingQuick.expire);
      const p = { value: preset, expire: null };
      p.expire = setTimeout(() => { if (this._pendingQuick === p) { this._pendingQuick = null; this._redraw(); } }, 8000);
      this._pendingQuick = p;
      if (this._toast) clearTimeout(this._toast.timer);
      const toast = { text: `${this._presetLabelFor(ids[0], preset)} · ${n} ${T(this._hass, "quick_applied")}`, timer: null };
      toast.timer = setTimeout(() => { if (this._toast === toast) { this._toast = null; this._redraw(); } }, 3000);
      this._toast = toast;
      this._open = null;
      this._redraw();
      this._callService("climate", "set_preset_mode", { entity_id: ids, preset_mode: preset })
        .catch(() => {
          if (this._pendingQuick === p) { clearTimeout(p.expire); this._pendingQuick = null; }
          if (this._toast === toast) { clearTimeout(toast.timer); this._toast = null; }
          this._redraw();
        });
    }

    _act(ds) {
      if (ds.act === "inc") this._adjust(ds.room, 1);
      else if (ds.act === "dec") this._adjust(ds.room, -1);
      else if (ds.act === "menu") { this._open = this._open === ds.room ? null : ds.room; this._redraw(); }
      else if (ds.act === "preset") this._setPreset(ds.room, ds.preset);
      else if (ds.act === "quick") this._quickSet(ds.preset);
    }

    /** A hass-ból érkező értékek utolérték a várakozó (optimista) értékeket: eldobjuk őket. */
    _settle(rooms) {
      rooms.forEach((r) => {
        const p = this._pending[r.id];
        if (p && p.sent && r.target != null && Math.abs(r.target - p.value) < 0.05) {
          clearTimeout(p.expire);
          delete this._pending[r.id];
        }
        const q = this._pendingPreset[r.id];
        if (q && r.valve && r.valve.preset === q.value) {
          clearTimeout(q.expire);
          delete this._pendingPreset[r.id];
        }
      });
      const pq = this._pendingQuick;
      if (pq) {
        const mine = [];
        rooms.forEach((r) => r.valves.forEach((v) => { if (v.ok && v.presets.includes(pq.value)) mine.push(v); }));
        if (!mine.length || mine.every((v) => v.preset === pq.value)) { clearTimeout(pq.expire); this._pendingQuick = null; }
      }
    }

    /* ---------- sima átmenetek ---------- */
    /** A kulcshoz tartozó értékek (számok) átúsznak a régiről az újra; apply(értékek) rajzolja őket. */
    _tween(key, to, apply) {
      const prev = this._shown[key];
      if (this._raf[key]) { cancelAnimationFrame(this._raf[key]); delete this._raf[key]; }
      const keys = Object.keys(to);
      const finite = (o) => o && keys.every((k) => typeof o[k] === "number" && isFinite(o[k]));
      const same = prev && keys.every((k) => prev[k] === to[k] || (typeof prev[k] === "number" && typeof to[k] === "number" && Math.abs(prev[k] - to[k]) < 1e-6));
      if (!prev || same || !this._config.smooth || this._reduced() || !finite(prev) || !finite(to)) {
        this._shown[key] = { ...to };
        return;
      }
      const from = { ...prev }, t0 = performance.now(), dur = 600;
      apply(from); // a frissen felépített DOM még az új értéket mutatná: onnan indulunk, ahol a szem tartott
      const step = (now) => {
        const p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 3);
        const cur = {};
        keys.forEach((k) => { cur[k] = from[k] + (to[k] - from[k]) * e; });
        if (p >= 1) { this._shown[key] = { ...to }; apply(to); delete this._raf[key]; return; }
        this._shown[key] = cur;
        apply(cur);
        this._raf[key] = requestAnimationFrame(step);
      };
      this._shown[key] = from;
      this._raf[key] = requestAnimationFrame(step);
    }

    /* ---------- visszaszámláló ---------- */
    _cdHtml(r) {
      if (!this._config.show_countdown) return "";
      const now = Date.now(), cd = countdownOf(r, now);
      if (!cd) return "";
      const remain = cd.end - now;
      const key = `${r.id}|${cd.kind}|${cd.end}`;
      let total = cd.total && cd.total >= remain ? cd.total : 0;
      if (!total) total = Math.max(this._cdMax[key] || 0, remain);
      this._cdMax[key] = total;
      const off = (1 - clamp(remain / total, 0, 1)) * 100;
      return `<span class="cd" data-cd="${cd.end}" data-total="${total}"><svg class="cdr" viewBox="0 0 24 24" aria-hidden="true"><circle class="bg" cx="12" cy="12" r="9"/><circle class="fg" pathLength="100" cx="12" cy="12" r="9" style="stroke-dashoffset:${off.toFixed(2)}"/></svg><span class="cdl">${esc(T(this._hass, "cd_" + cd.kind))}</span><b class="cdt">${esc(fmtRemain(remain, this._hass))}</b></span>`;
    }

    _startTick() {
      if (!this.shadowRoot.querySelector("[data-cd]")) { this._stopTick(); return; }
      if (this._tick) return;
      this._tick = setInterval(() => this._tickCd(), 1000);
    }

    _stopTick() {
      if (this._tick) { clearInterval(this._tick); this._tick = null; }
    }

    _tickCd() {
      const now = Date.now();
      this.shadowRoot.querySelectorAll("[data-cd]").forEach((el) => {
        const end = Number(el.dataset.cd), total = Number(el.dataset.total) || 1;
        const remain = Math.max(0, end - now);
        const t = el.querySelector(".cdt");
        if (t) t.textContent = fmtRemain(remain, this._hass);
        const fg = el.querySelector(".fg");
        if (fg) fg.style.strokeDashoffset = ((1 - clamp(remain / total, 0, 1)) * 100).toFixed(2);
      });
    }

    /* ---------- eseménykötés ---------- */
    _wire() {
      const root = this.shadowRoot;
      root.querySelectorAll("[data-entity]").forEach((el) => {
        el.addEventListener("click", (ev) => {
          if (this._holdFired) { this._holdFired = false; ev.stopPropagation(); return; }
          if (ev.target && ev.target.closest && ev.target.closest("[data-act]")) return;
          this.dispatchEvent(new CustomEvent("hass-more-info", { bubbles: true, composed: true, detail: { entityId: el.getAttribute("data-entity") } }));
        });
      });
      root.querySelectorAll("[data-act]").forEach((el) => {
        el.addEventListener("click", (ev) => {
          ev.stopPropagation();
          this._act(el.dataset);
        });
      });
    }

    /* ---------- kirajzolás ---------- */
    /** Az újrarajzolás aláírása: ha nem változik, a DOM-hoz nem nyúlunk. */
    _sigData(data) {
      return [data.rooms.map((r) => [r.id, r.on, r.a, r.valve, r.valves, r.valveIds]),
        data.summer && [data.summer.state, data.summer.attributes], data.boiler && data.boiler.state];
    }

    /** A gyökér osztályai: megjelenés (look) és éjszakai mód. */
    _rootCls() {
      const look = this._config.look;
      return look === "eink" || look === "neon" ? ` look-${look}` : "";
    }

    /** Éjszakai mód: 0..1 közötti érték (a ki- és belépés két percig tart, nem villan). */
    _nightK() {
      const c = this._config;
      if (!c.night_mode) return 0;
      const mm = (t, d) => { const m = /^(\d{1,2}):(\d{2})/.exec(String(t || "")); return m ? Number(m[1]) * 60 + Number(m[2]) : d; };
      const from = mm(c.night_from, 1320), to = mm(c.night_to, 360), d = new Date(), now = d.getHours() * 60 + d.getMinutes() + d.getSeconds() / 60;
      const since = (t) => ((now - t) % 1440 + 1440) % 1440;
      const inside = from === to ? false : from < to ? now >= from && now < to : now >= from || now < to;
      if (inside) return clamp(since(from) / 2, 0, 1);
      const out = since(to);
      return out < 2 && from !== to ? 1 - out / 2 : 0;
    }

    _applyNight() {
      const root = this.shadowRoot && this.shadowRoot.querySelector(".root");
      if (!root) return;
      const on = !!this._config.night_mode, k = on ? this._nightK() : 0;
      root.classList.toggle("nt", on);
      root.classList.toggle("night", on && k >= 0.5);
      root.style.setProperty("--k", k.toFixed(3));
      root.style.setProperty("--nd", String(clamp(Number(this._config.night_dim) || 70, 30, 100) / 100));
      if (on && !this._nightTimer) this._nightTimer = setInterval(() => this._applyNight(), 20000);
      if (!on && this._nightTimer) { clearInterval(this._nightTimer); this._nightTimer = null; }
    }

    _render() {
      if (!this._config || !this._hass) return;
      if (this._dragging) { this._dragDirty = true; return; }
      const cfg = this._config;
      const data = collect(this._hass, cfg);
      this._data = data;
      this._settle(data.rooms);
      const ui = [this._open, Object.keys(this._pending).map((k) => [k, this._pending[k].value]),
        Object.keys(this._pendingPreset).map((k) => [k, this._pendingPreset[k].value]),
        this._pendingQuick && this._pendingQuick.value, this._toast && this._toast.text];
      const sig = JSON.stringify([cfg, this._sigData(data), langOf(this._hass), ui]);
      if (sig === this._sig) return;
      this._sig = sig;
      const sz = clamp(Number(cfg.size) || 100, 70, 160) / 100;
      this._gn = 0;
      this.shadowRoot.innerHTML = `<style>${CSS}${CSS3}</style><div class="root${this._rootCls()}" style="${this._vars(cfg)};--sz:${sz}">${this._build(data)}</div>`;
      this._applyNight();
      this._wire();
      this._after(data);
      this._startTick();
    }

    _after() { /* a leszármazottak felülírhatják */ }

    /** Szobánkénti elemek közös részei */
    _hum(r) {
      if (!this._config.show_humidity || r.hum == null) return "";
      return `<span class="hum">${ic("drop")}${this._num(r.hum, 0)}%</span>`;
    }
  }

  /* ===================================================================
   *  Új kártyák (2.8): Miért fűt a kazán? és Figyelmeztetések
   * =================================================================== */
  const F = (hass, key, vars) => T(hass, key).replace(/\{(\w+)\}/g, (m, k) => (vars && vars[k] != null ? vars[k] : m));

  /** "47 perce" / "2 órája" / "most" a megadott időponttól számítva. */
  function fmtAgo(hass, ms) {
    const min = Math.max(0, Math.round((Date.now() - ms) / 60000));
    if (min < 1) return T(hass, "ago_now");
    if (min < 60) return F(hass, "ago_min", { n: min });
    if (min < 2880) return F(hass, "ago_h", { n: Math.floor(min / 60) });
    return F(hass, "ago_d", { n: Math.floor(min / 1440) });
  }

  /** Ki / be kapcsolható visszaszámláló egy szövegen belül (a közös másodperces léptető frissíti). */
  function cdInline(hass, end, live) {
    const remain = Math.max(0, end - Date.now());
    const txt = esc(fmtRemain(remain, hass));
    return live ? `<span data-cd="${end}" data-total="1"><b class="cdt">${txt}</b></span>` : `<b>${txt}</b>`;
  }

  /** A kazán ciklusai: indítások, átlagos be/ki idő, utolsó 6 óra sávban (Statisztika, Figyelmeztetések). */
  function cyclesHtml(h, data, nf) {
    const s = data.starts;
    if (!s) return "";
    const a = s.attributes, ca = data.cycling ? data.cycling.attributes : {};
    const now = Date.now(), span = 6 * 3600000, from = now - span;
    const minOn = num(ca.min_avg_on_minutes), maxStarts = num(ca.max_starts_per_hour);
    const list = (Array.isArray(a.cycles) ? a.cycles : []).map((x) => [Number(x[0]) * 1000, x[1] == null ? now : Number(x[1]) * 1000])
      .filter((x) => x[1] >= from);
    const pulses = list.map(([on, off]) => {
      const s0 = Math.max(on, from), short = minOn != null && off !== now && (off - on) / 60000 < minOn;
      return `<i class="${short ? "sh" : ""}" style="left:${(((s0 - from) / span) * 100).toFixed(2)}%;width:${Math.max(0.9, ((off - s0) / span) * 100).toFixed(2)}%"></i>`;
    }).join("");
    const n1 = num(a.starts_last_hour), on = num(a.avg_on_minutes), off = num(a.avg_off_minutes);
    const bad1 = maxStarts != null && n1 != null && n1 >= maxStarts, bad2 = minOn != null && on != null && on < minOn;
    const chk = (cls, label, val, unit, lim) => `<div class="ck ${cls}"><div class="l">${esc(label)}${lim ? ` <small>(${esc(lim)})</small>` : ""}</div><div class="v">${val}<small> ${esc(unit)}</small></div></div>`;
    const m_ = T(h, "unit_min");
    return `<div class="cyc"><h4 style="margin:0 0 8px;font-size:.82rem;font-weight:600">${esc(T(h, "cyc_title"))}</h4>
      <div class="pulses">${pulses}</div><div class="pax"><span>${esc(F(h, "ago_h", { n: 6 }))}</span><span>${esc(F(h, "ago_h", { n: 4 }))}</span><span>${esc(F(h, "ago_h", { n: 2 }))}</span><span>${esc(T(h, "now"))}</span></div>
      <div class="cks">
        ${chk(bad1 ? "bad" : "", T(h, "cyc_starts_h"), n1 == null ? "–" : n1, T(h, "cyc_per_h"), maxStarts != null ? `${T(h, "cyc_limit")} ${maxStarts}` : "")}
        ${chk(bad2 ? "bad" : "", T(h, "cyc_avg_on"), on == null ? "–" : nf(on, 0), m_, minOn != null ? `${T(h, "cyc_min")} ${minOn}` : "")}
        ${chk("", T(h, "cyc_avg_off"), off == null ? "–" : nf(off, 0), m_, "")}
        ${chk("", T(h, "cyc_24h"), s.state === "unknown" || s.state === "unavailable" ? "–" : esc(s.state), T(h, "cyc_starts"), "")}
      </div></div>`;
  }

  /** "Elrejti magát": a kártya, ha nincs mit mutatnia, a Lovelace-ben is eltűnik (szerkesztőben látszik). */
  function inEditor(el) {
    let n = el;
    for (let i = 0; i < 20 && n; i++) {
      const tn = String(n.tagName || "").toUpperCase();
      if (tn.includes("CARD-PREVIEW") || tn.includes("EDIT-CARD") || tn === "HUI-CARD-OPTIONS" || tn === "HUI-CARD-PICKER") return true;
      n = n.parentNode && n.parentNode.host ? n.parentNode.host : n.parentNode;
    }
    return false;
  }

  /* ---------- Miért fűt a kazán? ---------- */
  class MerossBoilerSyncWhyCard extends MbsBase {
    static getConfigElement() { return document.createElement(WHY_TAG + "-editor"); }
    static getStubConfig() { return {}; }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...WHY_DEFAULTS, ...config };
      if (!["valve", "sensor", "none"].includes(c.tap_action)) c.tap_action = "valve";
      c.max_rows = clamp(Math.round(Number(c.max_rows) || 5), 1, 12);
      this._config = c;
      this._sig = null;
      this._render();
    }

    getCardSize() { return this._config && this._config.compact ? 2 : 5; }

    _kind(data) {
      if (data.summer && data.summer.state === "on") return "summer";
      const calling = data.rooms.some((r) => r.on), bOn = boilerOn(data.boiler);
      if (calling) return bOn || !data.boiler ? "heat" : "wait";
      return bOn ? "cool" : "idle";
    }

    _chip(r) {
      const n = this._num(r.dev, 1);
      return `<span class="rcp" data-st="${r.status}" ${this._tapAttr(r)}><i></i>${esc(r.name)} <b>${r.dev != null && r.dev > 0.05 ? "−" + n + "°" : "✓"}</b></span>`;
    }

    _sentence(kind, data) {
      const h = this._hass, sm = data.summer;
      if (kind === "summer") {
        const a = sm.attributes, avg = num(a.outdoor_average_24h), thr = num(a.threshold);
        return avg != null && thr != null
          ? F(h, "why_summer_avg", { avg: this._num(avg, 1), thr: this._num(thr, 0) }) : T(h, "why_summer");
      }
      if (kind === "wait") return T(h, "why_wait");
      if (kind === "cool") return T(h, "why_cool");
      if (kind === "idle") return T(h, "why_idle");
      const calling = data.rooms.filter((r) => r.on).sort((x, y) => (y.dev || 0) - (x.dev || 0));
      const shown = calling.slice(0, 3), rest = calling.length - shown.length;
      const chips = shown.map((r) => this._chip(r));
      let txt = chips.slice(0, -1).join(T(h, "why_join"));
      txt = chips.length > 1 ? txt + T(h, "why_join_last") + chips[chips.length - 1] : chips[0];
      if (rest > 0) txt += ` <span class="sm">+${rest} ${esc(T(h, "why_more"))}</span>`;
      return T(h, "why_heat_a") + txt + T(h, calling.length > 1 ? "why_heat_bn" : "why_heat_b1");
    }

    _rows(kind, data) {
      const c = this._config, h = this._hass;
      let rows = [];
      if (kind === "heat" || kind === "wait") rows = data.rooms.filter((r) => r.on).sort((x, y) => (y.dev || 0) - (x.dev || 0));
      else if (kind === "idle" || kind === "cool") rows = data.rooms.filter((r) => r.cur != null && r.target != null && (r.status === "idle" || r.status === "demand"));
      if (!rows.length) return "";
      const html = rows.slice(0, c.max_rows).map((r) => {
        const calling = r.on && r.dev != null && r.dev > 0.05;
        let right;
        if (calling) {
          const bits = [`<b>−${this._num(r.dev, 1)}°</b>`];
          if (r.trend != null) {
            const k = Math.abs(r.trend) < TREND_FLAT ? 0 : r.trend;
            bits.push(k ? `${k > 0 ? "+" : "−"}${this._num(Math.abs(k), 1)}${esc(T(h, "per_h"))}` : esc(T(h, "trend_flat")));
          }
          const eta = etaMinutes(r);
          if (eta != null) bits.push(`${esc(T(h, "eta_word"))} ${esc(fmtMinutes(eta, h))}`);
          right = bits.join(" · ");
        } else right = `<b>✓ ${esc(T(h, "why_reached"))}</b>`;
        const w = calling ? Math.min(100, (r.dev / 3) * 100) : 100;
        return `<div class="li" data-st="${calling ? r.status : "idle"}" ${this._tapAttr(r)}><span class="nmx">${esc(r.name)}</span><span class="db"><i style="width:${w.toFixed(1)}%"></i></span><span class="rt">${right}</span></div>`;
      }).join("");
      return `<div class="list">${html}</div>`;
    }

    _notes(kind, data) {
      const h = this._hass, live = this._config.show_countdown, out = [];
      const add = (icon, color, body) => out.push(`<div class="nt" style="--c:${color}">${ic(icon)}<span>${body}</span></div>`);
      if (kind === "summer" && data.summer) {
        const a = data.summer.attributes;
        if (a.period_start && a.period_end) add("cal", "var(--c-summer)", F(h, "why_n_period", { from: `<b>${esc(fmtMonthDay(a.period_start))}</b>`, to: `<b>${esc(fmtMonthDay(a.period_end))}</b>` }));
        return out.join("");
      }
      data.rooms.forEach((r) => {
        const nm = `<b>${esc(r.name)}</b>`, now = Date.now(), tt = r.times;
        if (r.status === "window") add("window", "var(--c-window)", `${nm}: ${esc(T(h, "why_n_window"))}${r.dev != null && r.dev > 0.05 ? ` (−${this._num(r.dev, 1)}° ${esc(T(h, "why_from_target"))})` : ""}`);
        else if (r.status === "windowpend" && tt.win) add("window", "var(--c-window)", `${nm}: ${F(h, "why_n_windowpend", { t: cdInline(h, tt.win, live) })}`);
        else if (r.status === "stale") add("alert", "var(--c-stale)", `${nm}: ${esc(T(h, "why_n_stale"))}`);
        else if (r.status === "waiting" && tt.start) add("clock", "var(--c-waiting)", `${nm}: ${F(h, "why_n_waiting", { t: cdInline(h, tt.start, live) })}`);
        else if (r.status === "rest" && tt.rest) add("pause", "var(--c-rest)", `${nm}: ${F(h, "why_n_rest", { t: cdInline(h, tt.rest, live) })}`);
        else if (r.status === "boost" && tt.max) add("valve", "var(--c-boost)", `${nm}: ${F(h, "why_n_boost", { t: esc(fmtRemain(Math.max(0, tt.max - now), h)) })}`);
      });
      return out.slice(0, 6).join("");
    }

    _build(data) {
      const c = this._config, h = this._hass;
      if (!data.rooms.length && !data.boiler) return `<div class="msg">${esc(T(h, "no_rooms"))}</div>`;
      const kind = this._kind(data);
      const col = { heat: "var(--c-demand)", wait: "var(--c-waiting)", cool: "var(--c-demand)", idle: "var(--c-off)", summer: "var(--c-summer)" }[kind];
      const icon = { heat: "flame", wait: "clock", cool: "flame", idle: "power", summer: "sun" }[kind];
      const on = kind === "heat";
      const title = c.title ? esc(c.title) : esc(T(h, "boiler"));
      const body = c.compact ? "" : (c.show_list ? this._rows(kind, data) : "") + (c.show_notes ? `<div class="notes">${this._notes(kind, data)}</div>` : "");
      return `<div class="zm"><div class="t pn why${c.compact ? " compact" : ""}" style="--c:${col}">
        <div class="top"><div class="orb${on ? " on" : ""}" ${this._tapOn() && data.boilerId ? `data-entity="${esc(data.boilerId)}"` : ""}>${ic(icon)}</div>
        <div><div class="lbl">${title}</div><div class="sent">${this._sentence(kind, data)}</div></div></div>${body}</div></div>`;
    }
  }

  /* ---------- Figyelmeztetések ---------- */
  class MerossBoilerSyncAlertsCard extends MbsBase {
    static getConfigElement() { return document.createElement(ALERTS_TAG + "-editor"); }
    static getStubConfig() { return {}; }

    constructor() {
      super();
      this._expanded = false;
      this._hidden = null;
    }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...ALERTS_DEFAULTS, ...config };
      if (!["valve", "sensor", "none"].includes(c.tap_action)) c.tap_action = "valve";
      c.window_minutes = Math.max(0, Number(c.window_minutes) || 0);
      this._config = c;
      this._sig = null;
      this._render();
    }

    getCardSize() { return 2 + (this._alertCount || 0); }

    _sigData(data) {
      return [super._sigData(data), data.cycling && [data.cycling.state, data.cycling.attributes], data.starts && data.starts.state,
        this._expanded, inEditor(this), Math.floor(Date.now() / 60000)];
    }

    _act(ds) {
      if (ds.act === "toggle") { this._expanded = !this._expanded; this._redraw(); return; }
      super._act(ds);
    }

    /** A hibák listája, súlyosság szerint rendezve. */
    _alerts(data) {
      const c = this._config, h = this._hass, now = Date.now(), states = (h && h.states) || {}, out = [];
      const since = (id) => { const s = states[id]; const t = s && Date.parse(s.last_changed || s.last_updated || ""); return t && !isNaN(t) ? t : null; };
      const add = (sev, icon, color, title, sub, ts, entity) => out.push({ sev, icon, color, title, sub, ago: ts ? fmtAgo(h, ts) : "", entity });
      if (c.alert_unavailable && data.boiler && (data.boiler.state === "unavailable" || data.boiler.state === "unknown")) {
        add(0, "power", "var(--c-stale)", T(h, "al_boiler_unavail"), T(h, "al_boiler_unavail_s"), since(data.boilerId), data.boilerId);
      }
      if (c.alert_cycling && data.cycling && data.cycling.state === "on") {
        const a = data.cycling.attributes, avg = num(a.avg_on_minutes);
        add(1, "cycle", "var(--c-waiting)", T(h, "al_cycling"),
          F(h, avg != null ? "al_cycling_sub" : "al_cycling_sub1", { n: num(a.starts_last_hour), m: avg == null ? "" : this._num(avg, 0) }), since(data.cycling.entity_id), data.cycling.entity_id);
      }
      data.rooms.forEach((r) => {
        const entity = this._tapEntity(r);
        if (c.alert_unavailable && r.valves.length && r.valves.every((v) => v.state === "unavailable" || v.state === "unknown")) {
          add(0, "power", "var(--c-stale)", F(h, "al_valve_unavail", { room: r.name }), T(h, "al_valve_unavail_s"), since(r.id), entity);
          return;
        }
        if (c.alert_stale && r.status === "stale") {
          const st = r.tempSensor ? states[r.tempSensor] : null, t = st ? Date.parse(st.last_reported || st.last_updated || "") : NaN;
          add(2, "alert", "var(--c-stale)", F(h, "al_stale", { room: r.name }),
            !isNaN(t) ? F(h, "al_stale_sub", { ago: fmtAgo(h, t) }) : T(h, "al_stale_sub0"), !isNaN(t) ? t : since(r.id), entity);
        }
        if (c.alert_max_boost && r.status === "rest") {
          const mins = r.times.rest ? Math.max(1, Math.ceil((r.times.rest - now) / 60000)) : null;
          add(3, "flame", "var(--c-boost)", F(h, "al_maxboost", { room: r.name }), mins ? F(h, "al_maxboost_sub", { m: mins }) : T(h, "al_maxboost_sub0"), null, entity);
        }
        if (c.alert_window && (r.status === "window" || r.status === "windowpend")) {
          const opened = r.windowSensors.map((id) => (states[id] && states[id].state === "on" ? since(id) : null)).filter(Boolean);
          const t0 = opened.length ? Math.min(...opened) : null, mins = t0 ? Math.round((now - t0) / 60000) : null;
          if (r.status === "window" && (mins == null || mins >= c.window_minutes)) {
            add(4, "window", "var(--c-window)", F(h, "al_window", { room: r.name }), mins != null ? F(h, "al_window_sub", { ago: fmtAgo(h, t0) }) : T(h, "al_window_sub0"), t0, entity);
          }
        }
      });
      return out.sort((x, y) => x.sev - y.sev);
    }

    _row(a) {
      return `<div class="ar" style="--c:${a.color}" ${a.entity && this._tapOn() ? `data-entity="${esc(a.entity)}"` : ""}><div class="ai">${ic(a.icon)}</div>
        <div><div class="at">${esc(a.title)}</div><div class="as">${esc(a.sub)}</div></div><div class="ag">${esc(a.ago)}</div></div>`;
    }

    _setHidden(hide) {
      if (this._hidden === hide) return;
      this._hidden = hide;
      this.style.display = hide ? "none" : "";
      this.dispatchEvent(new CustomEvent("card-visibility-changed", { bubbles: true, composed: true, detail: { value: !hide } }));
    }

    _build(data) {
      const c = this._config, h = this._hass;
      const list = this._alerts(data);
      this._alertCount = list.length;
      const editing = inEditor(this);
      if (!list.length) {
        if (c.show_when_ok) {
          this._setHidden(false);
          const n = data.rooms.length;
          return `<div class="zm"><div class="t pn al ok" style="--c:var(--c-idle)"><div class="ai">${ic("check")}</div><span style="font-size:.88rem">${esc(F(h, "al_ok", { n }))}</span></div>${c.show_cycles ? `<div class="t pn al" style="margin-top:10px">${cyclesHtml(h, data, (v, d) => this._num(v, d))}</div>` : ""}</div>`;
        }
        if (!editing) { this._setHidden(true); return ""; }
        this._setHidden(false);
        return `<div class="zm"><div class="t pn al empty">${esc(T(h, "al_empty_preview"))}</div></div>`;
      }
      this._setHidden(false);
      let inner;
      if (c.compact) {
        const first = list[0], more = list.length - 1;
        const open = this._expanded && more > 0;
        inner = `<div class="alwrap"><div class="t pn al abr${open ? " open" : ""}" style="--c:${first.color}" ${more > 0 ? 'data-act="toggle"' : ""}>
          <div class="ai">${ic(first.icon)}</div><div class="at">${esc(first.title)}</div>${more > 0 ? `<span class="bdg">+${more} ${esc(T(h, "al_more"))}</span>${ic("chev", "chev")}` : ""}</div>
          ${open ? `<div class="t pn al">${list.slice(1).map((a) => this._row(a)).join("")}</div>` : ""}</div>`;
      } else {
        inner = `<div class="t pn al">${c.title ? `<div class="hd2"><div class="ttl">${esc(c.title)}</div></div>` : ""}${list.map((a) => this._row(a)).join("")}</div>`;
      }
      const cyc = c.show_cycles ? `<div class="t pn al" style="margin-top:10px">${cyclesHtml(h, data, (v, d) => this._num(v, d))}</div>` : "";
      return `<div class="zm">${inner}${cyc}</div>`;
    }
  }
  /* ===================================================================
   *  Előzmény-segédek (2.8): grafikonok, szakaszok, közös lekérő
   * =================================================================== */
  const DAY_MS = 86400000;
  let chartSeq = 0;

  const isRunState = (r) => !["off", "unavailable", "unknown", "undefined", "none"].includes(r.s);
  const isOnState = (r) => r.s === "on";

  /** A feltételnek megfelelő egymást követő szakaszok [kezdet, vég] az [from, to] tartományban. */
  function stateSegments(rows, from, to, pred) {
    const out = [];
    rows.forEach((r, i) => {
      if (!pred(r)) return;
      const s = Math.max(r.t, from), e = Math.min(i + 1 < rows.length ? rows[i + 1].t : to, to);
      if (e <= s) return;
      const last = out[out.length - 1];
      if (last && s <= last[1] + 1) last[1] = Math.max(last[1], e); else out.push([s, e]);
    });
    return out;
  }

  /** Az entitás előzmény-sorai + a legutóbbi (élő) állapot, hogy a jobb szél mindig a mostanit mutassa. */
  function rowsOf(hass, hist, id, keepAttrs) {
    const rows = parseRows(hist && hist.data ? hist.data[(keepAttrs ? "f:" : "") + id] : null, keepAttrs);
    const st = hass && hass.states && hass.states[id];
    if (st) {
      const lu = Date.parse(st.last_updated || st.last_changed || "");
      const last = rows[rows.length - 1];
      if (!isNaN(lu) && (!last || lu > last.t + 1000)) rows.push({ t: lu, s: String(st.state), a: keepAttrs ? st.attributes || {} : {} });
    }
    return rows;
  }

  /** Egy szakaszlista és egy időablak metszete (ms). */
  function overlapMs(segs, from, to) {
    let sum = 0;
    segs.forEach(([s, e]) => { const a = Math.max(s, from), b = Math.min(e, to); if (b > a) sum += b - a; });
    return sum;
  }

  function mergeSegments(lists) {
    const all = [].concat(...lists).sort((a, b) => a[0] - b[0]);
    const out = [];
    all.forEach(([s, e]) => {
      const last = out[out.length - 1];
      if (last && s <= last[1] + 1) last[1] = Math.max(last[1], e); else out.push([s, e]);
    });
    return out;
  }

  /** A helyi naptár szerinti nap eleje (ms), `back` nappal ezelőtt. */
  function dayStart(now, back) {
    const d = new Date(now);
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() - back);
    return d.getTime();
  }

  const capital = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);
  const weekdayOf = (hass, ts, style) => capital(new Date(ts).toLocaleDateString(langOf(hass), { weekday: style || "short" }));
  const hourLabel = (n) => pad2(n) + ":00";

  /** Időtengely-jelölők: óránként / 2 óránként / 6 óránként, a jobb szélen hagyunk helyet a "most" feliratnak. */
  function timeTicks(from, to, hours, lang) {
    const stepH = hours <= 6 ? 1 : hours <= 12 ? 2 : 6;
    const d = new Date(from);
    d.setMinutes(0, 0, 0);
    let guard = 0;
    while ((d.getTime() < from || d.getHours() % stepH !== 0) && guard++ < 60) d.setHours(d.getHours() + 1);
    const out = [];
    guard = 0;
    while (d.getTime() < to && guard++ < 60) {
      const pos = (d.getTime() - from) / (to - from);
      if (pos <= 0.88) out.push({ t: d.getTime(), label: d.toLocaleTimeString(lang, { hour: "2-digit", minute: "2-digit" }) });
      d.setHours(d.getHours() + stepH);
    }
    return out;
  }

  /** Közös előzmény-lekérő: a leszármazott megmondja, mit kér (_hRequest), az eredmény a this._hist.data-ban lesz. */
  const withHistory = (Base) => class extends Base {
    constructor() {
      super();
      this._hist = null;
      this._hkey = null;
      this._hat = 0;
      this._hloading = false;
      this._herr = false;
      this._hver = 0;
      this._hfresh = false;
    }

    _hReset() {
      this._hist = null;
      this._hkey = null;
      this._hat = 0;
      this._hloading = false;
      this._herr = false;
      this._data = null;
    }

    set hass(hass) {
      this._hass = hass;
      this._hMaybe();
      this._render();
    }

    /** {key, hours, groups: [{ids, full}]} vagy null (a régi {key, ids, hours, full} alak is jó) */
    _hRequest() { return null; }

    _hMaybe() {
      if (!this._config || !this._hass || typeof this._hass.callWS !== "function") return;
      const data = this._data || collect(this._hass, this._config);
      const req = this._hRequest(data);
      if (!req) return;
      if (!req.groups) req.groups = [{ ids: req.ids || [], full: !!req.full }];
      if (!req.groups.some((g) => g.ids.length)) return;
      const now = Date.now();
      if (this._hkey !== req.key || (!this._hloading && now - this._hat > 300000)) this._hFetch(req);
    }

    async _hFetch(req) {
      const keyChanged = this._hkey !== req.key;
      if (keyChanged) { this._hist = null; this._herr = false; }
      this._hloading = true;
      this._hkey = req.key;
      this._hat = Date.now();
      const end = Date.now(), start = end - req.hours * 3600000;
      try {
        const results = await Promise.all(req.groups.filter((g) => g.ids.length).map((g) => this._hass.callWS({
          type: "history/history_during_period", start_time: new Date(start).toISOString(), end_time: new Date(end).toISOString(),
          entity_ids: g.ids, include_start_time_state: true, significant_changes_only: false,
          minimal_response: !g.full, no_attributes: !g.full,
        }).then((res) => ({ full: g.full, res: res || {} }))));
        if (this._hkey !== req.key) return;
        const data = {};
        results.forEach(({ full, res }) => Object.keys(res).forEach((id) => { data[(full ? "f:" : "") + id] = res[id]; }));
        this._hist = { key: req.key, start, end, data };
        this._herr = false;
        if (keyChanged) this._hfresh = true;
      } catch (err) {
        if (this._hkey !== req.key) return;
        this._hist = null;
        this._herr = true;
      } finally {
        if (this._hkey === req.key) {
          this._hloading = false;
          this._hver++;
          this._sig = null;
          this._render();
        }
      }
    }

    _hMsg() {
      return `<div class="msg">${esc(T(this._hass, this._herr ? "tl_empty" : "tl_loading"))}</div>`;
    }
  };

  /** A grafikon: szoba hőmérséklete, cél (szaggatott), alatta sávok (hőt kért / szelep / ablak / elavult). */
  function roomChartHtml(h, r, rows, from, to, hours, intro) {
    const lang = langOf(h);
    const pts = [], tg = [];
    rows.forEach((x) => {
      const t = Math.min(Math.max(x.t, from), to);
      const cur = num(x.a.current_temperature), target = num(x.a.target_temperature);
      if (cur != null) pts.push([t, cur]);
      if (target != null && (!tg.length || tg[tg.length - 1][1] !== target)) tg.push([t, target]);
    });
    if (r.cur != null && (!pts.length || pts[pts.length - 1][0] < to)) pts.push([to, r.cur]);
    if (!pts.length) return `<div class="msg">${esc(T(h, "tl_empty"))}</div>`;
    if (pts.length === 1) pts.unshift([from, pts[0][1]]);
    const segs = segmentsOf(rows, from, to);
    const lanes = ["demand", "boost", "window"].concat(segs.stale.length ? ["stale"] : []);
    const W = 560, padL = 30, padR = 10, padT = 10, plotH = 150, laneH = 7, laneG = 4, laneY = padT + plotH + 12;
    const lanesH = lanes.length * laneH + (lanes.length - 1) * laneG, H = laneY + lanesH + 22;
    const vals = pts.map((p) => p[1]).concat(tg.map((p) => p[1]));
    let lo = Math.floor(Math.min(...vals) - 0.3), hi = Math.ceil(Math.max(...vals) + 0.3);
    if (hi - lo < 3) { lo = Math.floor((lo + hi) / 2 - 1.5); hi = lo + 3; }
    const step = hi - lo > 8 ? 2 : 1, span = to - from;
    const X = (t) => padL + ((t - from) / span) * (W - padL - padR), Y = (v) => padT + ((hi - v) / (hi - lo)) * plotH;
    const id = "rc" + (++chartSeq), f1 = (n) => n.toFixed(1);
    let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img"><defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--c);stop-opacity:.34"/><stop offset="1" style="stop-color:var(--c);stop-opacity:0"/></linearGradient></defs>`;
    for (let v = lo; v <= hi; v += step) s += `<line class="gl" x1="${padL}" x2="${W - padR}" y1="${f1(Y(v))}" y2="${f1(Y(v))}"/><text x="${padL - 6}" y="${f1(Y(v) + 3.5)}" text-anchor="end">${v}°</text>`;
    timeTicks(from, to, hours, lang).forEach((k) => {
      s += `<line class="gl" x1="${f1(X(k.t))}" x2="${f1(X(k.t))}" y1="${padT}" y2="${padT + plotH}" style="stroke-dasharray:2 4"/><text x="${f1(X(k.t))}" y="${H - 4}" text-anchor="middle">${esc(k.label)}</text>`;
    });
    s += `<text x="${W - padR}" y="${H - 4}" text-anchor="end" style="fill:var(--text);font-weight:600">${esc(T(h, "now"))}</text>`;
    const line = pts.map((p, i) => `${i ? "L" : "M"}${f1(X(p[0]))} ${f1(Y(p[1]))}`).join(" ");
    const last = pts[pts.length - 1], first = pts[0];
    s += `<path d="${line} L${f1(X(last[0]))} ${padT + plotH} L${f1(X(first[0]))} ${padT + plotH} Z" fill="url(#${id})"/>`;
    if (tg.length) {
      let d = `M${f1(X(tg[0][0]))} ${f1(Y(tg[0][1]))}`;
      tg.slice(1).forEach((p, i) => { d += ` L${f1(X(p[0]))} ${f1(Y(tg[i][1]))} L${f1(X(p[0]))} ${f1(Y(p[1]))}`; });
      d += ` L${f1(X(to))} ${f1(Y(tg[tg.length - 1][1]))}`;
      s += `<path class="tg" d="${d}"/>`;
    }
    s += `<path class="ln${intro ? " intro" : ""}" pathLength="100" d="${line}"/>`;
    s += `<line class="nl" x1="${f1(X(to))}" x2="${f1(X(to))}" y1="${padT}" y2="${padT + plotH}"/><circle class="nw" cx="${f1(X(last[0]))}" cy="${f1(Y(last[1]))}" r="4.5"/>`;
    lanes.forEach((k, i) => {
      const y = laneY + i * (laneH + laneG);
      s += `<rect class="lane" x="${padL}" y="${y}" width="${W - padL - padR}" height="${laneH}" rx="3.5"/>`;
      segs[k].forEach(([a, b]) => {
        const x0 = X(Math.max(a, from)), x1 = X(Math.min(b, to));
        if (x1 - x0 > 0.4) s += `<rect x="${f1(x0)}" y="${y}" width="${f1(Math.max(2, x1 - x0))}" height="${laneH}" rx="3.5" style="fill:var(--c-${k})"/>`;
      });
    });
    const legend = [["", "lg_cur", true], ["dash", "lg_target", false]].concat(lanes.map((k) => [k, "lg_" + k, false]))
      .map(([k, t, line_]) => {
        if (k === "dash") return `<span><span class="dash"></span>${esc(T(h, t))}</span>`;
        if (line_) return `<span><span class="dot6" style="--c:var(--text);opacity:.6"></span>${esc(T(h, t))}</span>`;
        return `<span><span class="dot6" style="--c:var(--c-${k})"></span>${esc(T(h, t))}</span>`;
      }).join("");
    return `${s}</svg><div class="lgd">${legend}</div>`;
  }

  /** A szoba csempéjéhez a minigrafikon adata: a hőmérséklet-szenzor előzménye, ennek híján a szoba entitás attribútuma. */
  function sparkData(h, hist, r) {
    const hasSensor = !!(r.tempSensor && hist && hist.data && hist.data[r.tempSensor] != null);
    if (hasSensor) return { trows: rowsOf(h, hist, r.tempSensor, false), drows: rowsOf(h, hist, r.id, false), attr: false };
    const rows = rowsOf(h, hist, r.id, true);
    return { trows: rows, drows: rows, attr: true };
  }

  /** Mini grafikon a csempére / sorba: görbe, cél (szaggatott), alul a fűtés ideje. */
  function sparkHtml(h, r, sd, from, to) {
    let pts = [];
    sd.trows.forEach((x) => {
      const v = sd.attr ? num(x.a.current_temperature) : parseFloat(x.s);
      if (v != null && !isNaN(v)) pts.push([Math.min(Math.max(x.t, from), to), v]);
    });
    if (pts.length > 240) { const k = Math.ceil(pts.length / 240); pts = pts.filter((p, i) => i % k === 0 || i === pts.length - 1); }
    if (r.cur != null && (!pts.length || pts[pts.length - 1][0] < to)) pts.push([to, r.cur]);
    if (pts.length < 2) return "";
    const W = 210, H = 44, span = to - from, tg = r.target;
    const vals = pts.map((p) => p[1]).concat(tg != null ? [tg] : []);
    let lo = Math.min(...vals) - 0.25, hi = Math.max(...vals) + 0.25;
    if (hi - lo < 1.5) { const m = (hi + lo) / 2; lo = m - 0.75; hi = m + 0.75; }
    const X = (t) => ((t - from) / span) * W, Y = (v) => 3 + ((hi - v) / (hi - lo)) * (H - 11), f1 = (n) => n.toFixed(1);
    const id = "sp" + (++chartSeq), line = pts.map((p, i) => `${i ? "L" : "M"}${f1(X(p[0]))} ${f1(Y(p[1]))}`).join(" "), last = pts[pts.length - 1];
    let s = `<svg class="sp" viewBox="0 0 ${W} ${H}" aria-hidden="true"><defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--c);stop-opacity:.3"/><stop offset="1" style="stop-color:var(--c);stop-opacity:0"/></linearGradient></defs>`;
    s += `<path d="${line} L${f1(X(last[0]))} ${H - 5} L${f1(X(pts[0][0]))} ${H - 5} Z" fill="url(#${id})"/>`;
    if (tg != null) s += `<line class="t" x1="0" x2="${W}" y1="${f1(Y(tg))}" y2="${f1(Y(tg))}"/>`;
    s += `<path class="l" d="${line}"/><circle class="n" cx="${f1(X(last[0]))}" cy="${f1(Y(last[1]))}" r="2.6"/>`;
    stateSegments(sd.drows, from, to, isOnState).forEach(([a, b]) => { s += `<rect class="hb" x="${f1(X(a))}" y="${H - 3}" width="${f1(Math.max(2, X(b) - X(a)))}" height="3" rx="1.5"/>`; });
    return s + "</svg>";
  }
  /* ===================================================================
   *  Csempe kártya: glass, radiator, minimal, gradient, list
   * =================================================================== */
  class MerossBoilerSyncCard extends withHistory(MbsBase) {
    static getConfigElement() { return document.createElement(EDITOR_TAG); }
    static getStubConfig() { return { design: "glass" }; }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...DEFAULTS, ...config };
      if (!DESIGNS.includes(c.design)) c.design = "glass";
      // régi (2.5) beállítás: tap_more_info: false  ->  tap_action: none
      if (config.tap_action === undefined && config.tap_more_info === false) c.tap_action = "none";
      if (!["valve", "sensor", "none"].includes(c.tap_action)) c.tap_action = "valve";
      if (!LOOKS.includes(c.look)) c.look = "glass";
      if (!HOLD_ACTIONS.includes(c.hold_action)) c.hold_action = "sheet";
      c.sparkline_hours = [6, 12, 24].includes(Number(c.sparkline_hours)) ? Number(c.sparkline_hours) : 24;
      this._config = c;
      this._hReset();
      this._sig = null;
      if (this._hass) this._hMaybe();
      this._render();
    }

    /** Sparkline: csak az üveg / radiátor csempén és a lista dizájnban. */
    _sparkOn() {
      const c = this._config;
      return !!(c && c.show_sparkline && ["glass", "radiator", "list"].includes(c.design));
    }

    _hRequest(data) {
      const c = this._config, sheetId = this._sheet ? this._sheet.id : null, groups = [];
      if (this._sparkOn()) {
        const light = [], full = [];
        data.rooms.forEach((r) => { if (r.tempSensor) light.push(r.id, r.tempSensor); else full.push(r.id); });
        if (light.length) groups.push({ ids: light, full: false });
        if (full.length) groups.push({ ids: full, full: true });
      }
      if (sheetId && !groups.some((g) => g.full && g.ids.includes(sheetId))) groups.push({ ids: [sheetId], full: true });
      if (!groups.length) return null;
      const hours = Math.max(this._sparkOn() ? Number(c.sparkline_hours) || 24 : 0, sheetId ? 12 : 0);
      return { key: JSON.stringify([hours, groups]), groups, hours: hours + 1 };
    }

    _sigData(data) {
      const base = super._sigData(data);
      return this._sparkOn() || this._sheet ? [base, this._hver, this._hloading, Math.floor(Date.now() / 60000)] : base;
    }

    getCardSize() {
      const n = this._data ? this._data.rooms.length : 4;
      const z = clamp(Number(this._config && this._config.size) || 100, 70, 160) / 100;
      const d = this._config && this._config.design;
      if (d === "list") return Math.max(2, Math.ceil(n * 0.6) + 1);
      if (d === "glass" || d === "radiator") return Math.max(4, Math.ceil(Math.ceil(n / 3) * 7 * z));
      return Math.max(3, Math.ceil(n / 3) * 3);
    }

    _chip(r) {
      if (!this._config.show_status) return "";
      const key = r.status === "windowpend" ? "st_windowpend" : "st_" + r.status;
      const pat = this._config.look === "eink" ? '<i class="pat"></i>' : "";
      return `<span class="chip">${pat}${ic(STATUS_ICON[r.status])}${esc(T(this._hass, key))}</span>`;
    }

    _flags(r) {
      if (!this._config.show_flags) return "";
      const a = r.a, h = this._hass, out = [];
      if (a.valve_control) out.push(`<span title="${esc(T(h, "valve_control"))}">${ic("valve")}</span>`);
      if (a.valve_demand_link) out.push(`<span title="${esc(T(h, "link"))}">${ic("link")}</span>`);
      if (a.valve_dry_run && a.valve_control) out.push(`<span title="${esc(T(h, "dry"))}">${ic("flask")}</span>`);
      return out.length ? `<span class="fl">${out.join("")}</span>` : "";
    }

    _dev(r) {
      if (!this._config.show_deviation || r.dev == null) return "";
      if (r.dev > 0.05) return `<span class="dev">−${this._num(r.dev, 1)}°</span>`;
      return `<span class="dev">✓</span>`;
    }

    _glowCls(r) {
      const c = this._config;
      if (!c.glow) return "";
      const lvl = clamp(Math.round(Number(c.glow_level) || 3), 1, 5);
      const list = Array.isArray(c.glow_states) ? c.glow_states : GLOW_DEFAULT;
      const key = r.status === "windowpend" ? "window" : r.status;
      return list.includes(key) ? `gl${lvl}` : "";
    }

    /** Trend és becslés: nyíl, °/óra, és ha a szoba melegszik, mikorra éri el a célt. */
    _trendRow(r) {
      const c = this._config, h = this._hass;
      if (!c.show_trend || r.trend == null) return "";
      const t = r.trend;
      const kind = Math.abs(t) < TREND_FLAT ? "flat" : t > 0 ? "up" : "down";
      const txt = kind === "flat"
        ? `<b>${esc(T(h, "trend_flat"))}</b>`
        : `<b>${t > 0 ? "+" : "−"}${this._num(Math.abs(t), 1)}${esc(T(h, "per_h"))}</b>`;
      let eta = "";
      const tgt = r.effTarget != null ? r.effTarget : r.target;
      if (c.show_eta && kind === "up" && r.below && r.cur != null && tgt != null && tgt > r.cur) {
        const min = ((tgt - r.cur) / t) * 60;
        if (min >= 1 && min <= ETA_MAX_MIN) {
          eta = `<span>· ${esc(T(h, "eta_word"))} ${esc(fmtMinutes(min > 10 ? Math.round(min / 5) * 5 : min, h))}</span>`;
        }
      }
      return `<div class="trend ${kind}">${ic(kind)}${txt}${eta}</div>`;
    }

    _radSvg(r) {
      const fins = Array.from({ length: 7 }, (_, i) => `<rect class="fin" x="${22 + i * 19}" y="40" width="12" height="60" rx="6"/>`).join("");
      let waves = "";
      if (this._config.animation && (r.status === "demand" || r.status === "boost")) {
        waves = [30, 62, 94, 126, 78].slice(0, r.status === "boost" ? 5 : 3)
          .map((x) => `<path class="wv" d="M${x} 28 q3 -5 6 0 t6 0 t6 0"/>`).join("");
      }
      return `<svg viewBox="0 0 160 112" aria-hidden="true"><rect class="pipe" x="8" y="34" width="144" height="6" rx="3"/><rect class="pipe" x="8" y="100" width="144" height="6" rx="3"/>${fins}${waves}</svg>`;
    }

    _tileGlass(r) {
      const c = this._config, d = Number(c.decimals) || 0, h = this._hass;
      const rd = c.design === "radiator";
      const min = Number(c.gauge_min), max = Number(c.gauge_max), span = Math.max(1, max - min);
      const v = r.valve;
      const pend = this._pending[r.id], pendP = this._pendingPreset[r.id];
      const target = pend ? pend.value : r.target;
      const showCtl = !!(c.show_controls && v && r.target != null);
      const f = r.cur == null ? 0 : (r.cur - min) / span;
      const ft = target == null ? null : (target - min) / span;
      const big = c.show_current ? `<div class="big" data-role="big">${this._bigInner(r.cur, d)}</div>` : "";

      // célhőmérséklet + − / + gombok
      const { lo, hi } = this._bounds(r);
      const canChange = showCtl && v.ok;
      const btn = (dir) => {
        if (!showCtl) return "<span></span>";
        const off = !canChange || (dir < 0 ? target <= lo + 1e-9 : target >= hi - 1e-9);
        return `<button type="button" class="pm" data-act="${dir < 0 ? "dec" : "inc"}" data-room="${esc(r.id)}" aria-label="${esc(T(h, dir < 0 ? "decrease" : "increase"))}"${off ? " disabled" : ""}>${ic(dir < 0 ? "minus" : "plus")}</button>`;
      };
      const showTg = (c.show_target || showCtl) && target != null;

      let visual;
      if (rd) {
        visual = `<div class="rad">${this._radSvg(r)}</div>
          <div class="num">${btn(-1)}${big || "<span></span>"}${btn(1)}</div>
          ${showTg ? `<div class="tg2">${esc(T(h, "target"))} <b>${this._num(target, d)}°</b></div>` : ""}`;
      } else {
        let marker = "", defs = "", stroke = "var(--c)", knob = "";
        if (c.temp_gradient && r.cur != null) {
          const gid = "tg" + (this._gn = (this._gn || 0) + 1);
          defs = `<defs><linearGradient id="${gid}" gradientUnits="userSpaceOnUse" x1="24.6" y1="0" x2="95.4" y2="0">${gradientStops()}</linearGradient></defs>`;
          stroke = `url(#${gid})`;
        }
        if (ft != null && (c.show_target || showCtl)) {
          const [mx, my] = pointOn(60, 60, 50, ft);
          marker = `<circle data-role="mk" cx="${mx.toFixed(2)}" cy="${my.toFixed(2)}" r="4.5" fill="var(--text)" stroke="var(--surface)" stroke-width="2"/>`;
          if (c.drag_target && canChange) knob = `<div class="knob" data-role="knob" style="left:${((mx / 120) * 100).toFixed(2)}%;top:${((my / 120) * 100).toFixed(2)}%"></div>`;
        }
        const tg = showTg ? `<div class="tg">${esc(T(h, "target"))}<b>${this._num(target, d)}°</b></div>` : "<span></span>";
        visual = `<div class="ring">
            <svg viewBox="0 0 120 120">${defs}<path d="${arcPath(60, 60, 50, 1)}" fill="none" stroke="var(--track)" stroke-width="9" stroke-linecap="round"/>
              ${r.cur != null ? `<path data-role="arc" d="${arcPath(60, 60, 50, Math.max(f, 0.001))}" fill="none" stroke="${stroke}" stroke-width="9" stroke-linecap="round"/>` : ""}${marker}</svg>
            <div class="mid">${big}</div>${knob}
            <div class="ctl">${btn(-1)}${tg}${btn(1)}</div>
          </div>`;
      }

      // profil (preset) választó
      const showPre = !!(c.show_presets && v && v.presets.length);
      let pre = "", menu = "";
      if (showPre) {
        const cur = pendP ? pendP.value : v.preset;
        const open = this._open === r.id;
        const label = cur != null ? this._presetLabelFor(v.id, cur) : T(h, "preset_word");
        pre = `<button type="button" class="pre" data-act="menu" data-room="${esc(r.id)}" aria-haspopup="listbox" aria-expanded="${open}"${v.state === "unavailable" ? " disabled" : ""}>${ic(PRESET_ICON[cur] || "tune")}<span>${esc(label)}</span>${ic("chev", "chev")}</button>`;
        if (open) {
          menu = `<div class="menu" role="listbox" data-act="none">${v.presets.map((p) =>
            `<button type="button" class="mi${p === cur ? " on" : ""}" role="option" aria-selected="${p === cur}" data-act="preset" data-room="${esc(r.id)}" data-preset="${esc(p)}">${ic(PRESET_ICON[p] || "tune")}<span>${esc(this._presetLabelFor(v.id, p))}</span>${p === cur ? `<span class="ck">${ic("check")}</span>` : ""}</button>`).join("")}</div>`;
        }
      }

      const info = [this._hum(r), this._dev(r), this._flags(r)].filter(Boolean).join("");
      const status = this._cdHtml(r) || this._chip(r);
      let fx = c.animation ? (rd ? FX_RADIATOR[r.status] : FX[r.status]) || "" : "";
      if (c.look === "eink") fx = '<div class="stripe"></div>';
      return `<div class="t glass${rd ? " rd" : ""}${rd && c.animation ? " anim" : ""} ${this._glowCls(r)}" data-st="${r.status}" data-room="${esc(r.id)}" ${this._tapAttr(r)}>
        ${fx}
        <div class="in">
          <div class="nm">${esc(r.name)}</div>
          ${visual}
          <div class="info">${info}</div>
          ${this._trendRow(r)}
          ${this._sparkBlock(r)}
          ${status || pre ? `<div class="foot">${status}${pre}${menu}</div>` : ""}
        </div>
      </div>`;
    }

    _sparkBlock(r, bare) {
      if (!this._sparkOn() || !this._hist) return "";
      const hours = Number(this._config.sparkline_hours) || 24, to = Date.now(), from = to - hours * 3600000, h = this._hass;
      const svg = sparkHtml(h, r, sparkData(h, this._hist, r), from, to);
      if (!svg) return "";
      return bare ? svg : `<div class="spw">${svg}<div class="spc"><span>${esc(T(h, "hr_" + hours))}</span><span>${esc(T(h, "now"))}</span></div></div>`;
    }

    /** Hőtérkép dizájn: a csempe háttere maga a hőmérséklet (hideg kék → zöld → sárga → narancs). */
    _tileHeat(r) {
      const c = this._config, d = Number(c.decimals) || 0, h = this._hass;
      const lo = Number(c.heat_min), hi = Math.max(lo + 1, Number(c.heat_max));
      const f = r.cur == null ? 0 : clamp((r.cur - lo) / (hi - lo), 0, 1);
      const rgb = tempRgb(f), b1 = mixRgb(rgb, [255, 255, 255], 0.06), b2 = mixRgb(rgb, [12, 16, 26], 0.52);
      const dis = r.status === "stale" || r.status === "off" || r.cur == null;
      let tr = "";
      if (c.show_trend && r.trend != null) {
        const t = r.trend, flat = Math.abs(t) < TREND_FLAT;
        tr = `<span>${flat ? "▬ " + esc(T(h, "trend_flat")) : `${t > 0 ? "▲ +" : "▼ −"}${this._num(Math.abs(t), 1)}${esc(T(h, "per_h"))}`}</span>`;
      }
      const target = r.target;
      const prog = r.cur != null && target != null && target > 0 ? clamp((r.cur / target) * 100, 0, 100) : 0;
      return `<div class="t heat${dis ? " dis" : ""}" data-st="${r.status}" data-room="${esc(r.id)}" ${this._tapAttr(r)}
        style="--b1:rgb(${b1.join(",")});--b2:rgb(${b2.join(",")});--fg:${f > 0.6 ? "#15100a" : "#fff"}">
        <div class="tp"><span class="nm">${esc(r.name)}</span>${ic(STATUS_ICON[r.status])}</div>
        <div class="bg">${c.show_current ? this._bigInner(r.cur, d) : ""}</div>
        <div class="rw2"><span>${c.show_target && target != null ? `${esc(T(h, "target"))} ${this._num(target, d)}°` : ""}</span>${tr}</div>
        <div class="tb"><i style="width:${prog.toFixed(1)}%"></i></div></div>`;
    }

    _tileMinimal(r) {
      const c = this._config, d = Number(c.decimals) || 0, bits = [];
      if (c.show_current) bits.push(`<b>${this._num(r.cur, d)} ${esc(this._unit())}</b>`);
      if (c.show_target && r.target != null) bits.push(`<span>${esc(T(this._hass, "target"))} ${this._num(r.target, d)}°</span>`);
      if (c.show_humidity && r.hum != null) bits.push(this._hum(r));
      if (c.show_deviation && r.dev != null) bits.push(this._dev(r));
      return `<div class="t minimal ${this._glowCls(r)}" data-st="${r.status}" data-room="${esc(r.id)}" ${this._tapAttr(r)}>
        <div class="ib">${ic(STATUS_ICON[r.status])}</div>
        <div class="tx"><div class="nm">${esc(r.name)}</div><div class="sb">${bits.join("")}${this._flags(r)}</div></div>
        ${this._chip(r)}
      </div>`;
    }

    _barVals(r) {
      const c = this._config, min = Number(c.gauge_min), span = Math.max(1, Number(c.gauge_max) - min);
      const f = r.cur == null ? 0 : clamp((r.cur - min) / span, 0, 1) * 100;
      const ft = r.target == null || !c.show_target ? null : clamp((r.target - min) / span, 0, 1) * 100;
      return { f, ft };
    }

    _bar(r) {
      const { f, ft } = this._barVals(r);
      return `<div class="bar"><i style="width:${f.toFixed(1)}%"></i>${ft != null ? `<b style="left:${ft.toFixed(1)}%"></b>` : ""}</div>`;
    }

    _tileGradient(r) {
      const c = this._config, d = Number(c.decimals) || 0, sb = [];
      if (c.show_target && r.target != null) sb.push(`<span>${esc(T(this._hass, "target"))} ${this._num(r.target, d)}°</span>`);
      if (c.show_humidity && r.hum != null) sb.push(this._hum(r));
      if (c.show_deviation && r.dev != null) sb.push(this._dev(r));
      const flags = this._flags(r);
      return `<div class="t gradient ${this._glowCls(r)}" data-st="${r.status}" data-room="${esc(r.id)}" ${this._tapAttr(r)}>
        <div class="top"><span class="nm">${esc(r.name)}</span>${this._chip(r)}</div>
        ${c.show_current ? `<div class="bg">${this._num(r.cur, d)}<small>${esc(this._unit())}</small></div>` : ""}
        <div class="sb">${sb.join("")}${flags}</div>
        ${this._bar(r)}
      </div>`;
    }

    _rowList(r) {
      const c = this._config, d = Number(c.decimals) || 0;
      return `<div class="rw" data-st="${r.status}" data-room="${esc(r.id)}" ${this._tapAttr(r)}>
        <span class="nm">${esc(r.name)}</span>
        <span class="v">${c.show_current ? `${this._num(r.cur, d)}<small> ${esc(this._unit())}</small>` : ""}</span>
        <span class="v">${c.show_target && r.target != null ? `<small>${esc(T(this._hass, "target"))}</small> ${this._num(r.target, d)}°` : ""}</span>
        ${this._sparkBlock(r, true) ? `<span class="rsp">${this._sparkBlock(r, true)}</span>` : this._bar(r)}
        <span>${this._hum(r)} ${this._dev(r)}</span>
        <span style="display:flex;gap:8px;align-items:center;justify-content:flex-end">${this._flags(r)}${this._chip(r)}</span>
      </div>`;
    }

    _header(data) {
      const c = this._config, h = this._hass, pills = [];
      if (c.show_boiler && data.boiler) {
        const on = boilerOn(data.boiler);
        pills.push(`<span class="pill" style="--c:${on ? "var(--c-demand)" : "var(--c-off)"}" ${this._tapOn() ? `data-entity="${esc(data.boilerId)}"` : ""}>${ic("flame")}<span>${esc(T(h, "boiler"))}:</span> <b>${esc(T(h, on ? "on" : "off"))}</b></span>`);
      }
      if (c.show_demand) {
        const n = data.rooms.filter((r) => r.on).length;
        pills.push(`<span class="pill" style="--c:${n ? "var(--c-demand)" : "var(--c-idle)"}">${ic("radiator")}<span>${esc(T(h, "calling"))}:</span> <b>${n}/${data.rooms.length}</b> <small>${esc(T(h, "rooms_word"))}</small></span>`);
      }
      if (c.show_summer && data.summer) {
        const s = data.summer, a = s.attributes, on = s.state === "on", u = this._unit();
        const out = a.outdoor_temperature != null ? `${esc(T(h, "outdoor"))} ${this._num(a.outdoor_temperature, 1)}${esc(u)}` : "";
        const avg = a.outdoor_average_24h != null ? `${esc(T(h, "avg24"))} ${this._num(a.outdoor_average_24h, 1)}${esc(u)}` : "";
        pills.push(`<span class="pill" style="--c:${on ? "var(--c-summer)" : "var(--c-off)"}" ${this._tapOn() ? `data-entity="${esc(s.entity_id)}"` : ""}>${ic("sun")}<span>${esc(T(h, "summer"))}:</span> <b>${esc(T(h, on ? "active" : "inactive"))}</b>${out || avg ? ` <small>${[out, avg].filter(Boolean).join(" · ")}</small>` : ""}</span>`);
      }
      const title = c.title ? `<div class="ttl">${esc(c.title)}</div>` : "";
      if (!pills.length && !title) return "";
      return `<div class="hd">${title}${c.show_header ? pills.join("") : ""}</div>`;
    }

    _build(data) {
      const cfg = this._config;
      const hdr = data.rooms.length || cfg.title ? this._header(data) : "";
      if (!data.rooms.length) return `${hdr}<div class="msg">${esc(T(this._hass, "no_rooms"))}</div>`;
      let body;
      if (cfg.design === "list") body = `<div class="tbl">${data.rooms.map((r) => this._rowList(r)).join("")}</div>`;
      else {
        const tile = { glass: "_tileGlass", radiator: "_tileGlass", minimal: "_tileMinimal", gradient: "_tileGradient", heat: "_tileHeat" }[cfg.design];
        const minw = { glass: 250, radiator: 250, minimal: 300, gradient: 235, heat: 230 }[cfg.design];
        body = `<div class="grid" style="${Number(cfg.columns) > 0 ? "" : `grid-template-columns:repeat(auto-fill,minmax(min(100%,${minw}px),1fr))`}">${data.rooms.map((r) => this[tile](r)).join("")}</div>`;
      }
      return `${hdr}${this._quickHtml(data.rooms)}<div class="zm">${body}</div>`;
    }

    /* ---------- célhőmérséklet húzása a gyűrűn ---------- */
    _wireDrag() {
      if (!this._config.drag_target) return;
      const c = this._config;
      this.shadowRoot.querySelectorAll('[data-role="knob"]').forEach((knob) => {
        const tile = knob.closest("[data-room]"), ring = knob.closest(".ring");
        if (!tile || !ring) return;
        knob.addEventListener("pointerdown", (ev) => {
          const id = tile.dataset.room, r = this._room(id);
          if (!r || !r.valve || !r.valve.ok || ev.button > 0) return;
          ev.preventDefault();
          ev.stopPropagation();
          try { knob.setPointerCapture(ev.pointerId); } catch (e) { /* nem kritikus */ }
          this._dragging = true;
          const { lo, hi, step } = this._bounds(r), min = Number(c.gauge_min), span = Math.max(1, Number(c.gauge_max) - min), d = Number(c.decimals) || 0;
          const rect = ring.getBoundingClientRect(), cx = rect.left + rect.width / 2, cy = rect.top + rect.height / 2;
          const mk = tile.querySelector('[data-role="mk"]'), tgEl = tile.querySelector(".tg b");
          const bubble = document.createElement("div");
          bubble.className = "bubble";
          ring.appendChild(bubble);
          tile.classList.add("dragging");
          if (mk) { mk.setAttribute("r", "8"); mk.setAttribute("stroke-width", "3"); }
          let last = null;
          const move = (e) => {
            let deg = (Math.atan2(e.clientY - cy, e.clientX - cx) * 180) / Math.PI;
            deg = (deg + 360) % 360;
            let rel = (deg - 135 + 360) % 360;
            if (rel > 270) rel = rel > 315 ? 0 : 270;
            const raw = min + (rel / 270) * span;
            const v = Math.round(clamp(Math.round(raw / step) * step, lo, hi) * 100) / 100;
            if (v === last) return;
            last = v;
            const f = clamp((v - min) / span, 0, 1), [x, y] = pointOn(60, 60, 50, f);
            if (mk) { mk.setAttribute("cx", x.toFixed(2)); mk.setAttribute("cy", y.toFixed(2)); }
            knob.style.left = ((x / 120) * 100).toFixed(2) + "%";
            knob.style.top = ((y / 120) * 100).toFixed(2) + "%";
            if (tgEl) tgEl.textContent = this._num(v, d) + "°";
            bubble.textContent = this._num(v, d) + "°";
            bubble.style.left = ((x / 120) * 100).toFixed(2) + "%";
            bubble.style.top = ((y / 120) * 100).toFixed(2) + "%";
            try { if (navigator.vibrate) navigator.vibrate(6); } catch (err) { /* nem kritikus */ }
          };
          const end = () => {
            knob.removeEventListener("pointermove", move);
            knob.removeEventListener("pointerup", end);
            knob.removeEventListener("pointercancel", end);
            bubble.remove();
            this._dragging = false;
            if (last != null && Math.abs(last - (r.target == null ? NaN : r.target)) > 1e-6) this._queueTarget(id, last);
            else { this._sig = null; this._render(); }
          };
          knob.addEventListener("pointermove", move);
          knob.addEventListener("pointerup", end);
          knob.addEventListener("pointercancel", end);
          move(ev);
        });
      });
    }

    /* ---------- hosszú nyomás: részletek lapja ---------- */
    _wireHold() {
      const act = this._config.hold_action;
      if (!act || act === "none") return;
      this.shadowRoot.querySelectorAll("[data-room]").forEach((el) => {
        if (!el.matches(".t, .rw")) return;
        let timer = null, ring = null, sx = 0, sy = 0;
        const cancel = () => {
          if (timer) { clearTimeout(timer); timer = null; }
          if (ring) { ring.remove(); ring = null; }
        };
        el.addEventListener("contextmenu", (ev) => ev.preventDefault());
        el.addEventListener("pointerdown", (ev) => {
          if (ev.button > 0 || (ev.target.closest && ev.target.closest("button, [data-act], [data-role='knob'], .menu"))) return;
          cancel();
          sx = ev.clientX;
          sy = ev.clientY;
          const root = this.shadowRoot.querySelector(".root");
          if (root) {
            root.insertAdjacentHTML("beforeend", `<svg class="holdring" style="left:${sx}px;top:${sy}px" viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="28" pathLength="100"/></svg>`);
            ring = root.lastElementChild;
          }
          timer = setTimeout(() => {
            timer = null;
            cancel();
            this._holdFired = true;
            setTimeout(() => { this._holdFired = false; }, 700);
            try { if (navigator.vibrate) navigator.vibrate(15); } catch (err) { /* nem kritikus */ }
            const id = el.dataset.room;
            if (act === "sheet") this._openSheet(id);
            else {
              const r = this._room(id);
              this.dispatchEvent(new CustomEvent("hass-more-info", { bubbles: true, composed: true, detail: { entityId: r ? this._tapEntity(r) || r.id : id } }));
            }
          }, HOLD_MS);
        });
        el.addEventListener("pointermove", (ev) => { if (timer && Math.hypot(ev.clientX - sx, ev.clientY - sy) > 10) cancel(); });
        ["pointerup", "pointercancel", "pointerleave"].forEach((t) => el.addEventListener(t, cancel));
      });
    }

    /* ---------- a lap (alulról felcsúszó részletek) ---------- */
    _sheetKey = (ev) => { if (ev.key === "Escape" && this._sheet) { ev.stopPropagation(); this._closeSheet(); } };

    _openSheet(id) {
      if (this._sheet) return;
      this._sheet = { id, open: false, fresh: true, sig: null };
      const host = document.createElement("div");
      host.className = "mbs-sheet-host";
      host.attachShadow({ mode: "open" });
      document.body.appendChild(host);
      this._sheetHost = host;
      host.shadowRoot.addEventListener("click", (ev) => {
        const el = ev.target.closest && ev.target.closest("[data-sact]");
        if (!el) return;
        const a = el.dataset.sact, rid = this._sheet && this._sheet.id;
        if (a === "close") this._closeSheet();
        else if (a === "inc") this._adjust(rid, 1);
        else if (a === "dec") this._adjust(rid, -1);
        else if (a === "preset") this._setPreset(rid, el.dataset.preset);
        else if (a === "info") {
          const r = this._room(rid);
          this._closeSheet();
          if (r) this.dispatchEvent(new CustomEvent("hass-more-info", { bubbles: true, composed: true, detail: { entityId: this._tapEntity(r) || r.id } }));
        }
      });
      this._wireSheetSwipe(host.shadowRoot);
      document.addEventListener("keydown", this._sheetKey, true);
      this._hMaybe();
      this._renderSheet();
      requestAnimationFrame(() => requestAnimationFrame(() => {
        if (!this._sheet) return;
        this._sheet.open = true;
        const w = host.shadowRoot.querySelector(".sh-wrap");
        if (w) w.classList.add("open");
      }));
    }

    _closeSheet() {
      const host = this._sheetHost;
      if (!this._sheet) return;
      this._sheet = null;
      this._sheetHost = null;
      document.removeEventListener("keydown", this._sheetKey, true);
      if (host) {
        const w = host.shadowRoot.querySelector(".sh-wrap");
        if (w) w.classList.remove("open");
        setTimeout(() => host.remove(), 320);
      }
      this._hMaybe();
    }

    /** Lehúzással zárható: a fogantyún lefelé húzva a lap követi az ujjat. */
    _wireSheetSwipe(sr) {
      sr.addEventListener("pointerdown", (ev) => {
        const zone = ev.target.closest && ev.target.closest(".grab");
        const sheet = sr.querySelector(".sheet");
        if (!zone || !sheet) return;
        ev.preventDefault();
        const y0 = ev.clientY;
        if (this._sheet) this._sheet.dragging = true;
        sheet.style.transition = "none";
        try { zone.setPointerCapture(ev.pointerId); } catch (e) { /* nem kritikus */ }
        const move = (e) => { sheet.style.transform = `translateY(${Math.max(0, e.clientY - y0)}px)`; };
        const end = (e) => {
          zone.removeEventListener("pointermove", move);
          zone.removeEventListener("pointerup", end);
          zone.removeEventListener("pointercancel", end);
          sheet.style.transition = "";
          if (this._sheet) this._sheet.dragging = false;
          if (e.clientY - y0 > 90) this._closeSheet(); else sheet.style.transform = "";
        };
        zone.addEventListener("pointermove", move);
        zone.addEventListener("pointerup", end);
        zone.addEventListener("pointercancel", end);
      });
    }

    _renderSheet() {
      const sh = this._sheet, host = this._sheetHost;
      if (!sh || !host || sh.dragging) return;
      const h = this._hass, c = this._config, data = this._data;
      const r = data && data.rooms.find((x) => x.id === sh.id);
      if (!r) { this._closeSheet(); return; }
      const pend = this._pending[r.id], pendP = this._pendingPreset[r.id], v = r.valve;
      const hist = this._hist, d = Number(c.decimals) || 0;
      const sig = JSON.stringify([r.a, r.valve, r.valves, pend && pend.value, pendP && pendP.value, this._hver, Math.floor(Date.now() / 60000), langOf(h), c.look, sh.open]);
      if (sig === sh.sig) return;
      sh.sig = sig;
      const old = host.shadowRoot.querySelector(".sheet"), scroll = old ? old.scrollTop : 0;
      const target = pend ? pend.value : r.target, { lo, hi } = this._bounds(r), can = !!(v && v.ok && target != null);
      const key = r.status === "windowpend" ? "st_windowpend" : "st_" + r.status;
      const trend = this._trendRow(r);
      let chart = "";
      if (hist && hist.data["f:" + r.id] != null) {
        const to = Date.now(), from = to - 12 * 3600000, intro = sh.fresh;
        sh.fresh = false;
        chart = roomChartHtml(h, r, rowsOf(h, hist, r.id, true), from, to, 12, intro);
      } else chart = this._hMsg();
      const cur = pendP ? pendP.value : v ? v.preset : null;
      const chips = v && v.presets.length ? `<div class="pchips">${v.presets.map((p) =>
        `<button type="button" class="${p === cur ? "on" : ""}" data-sact="preset" data-preset="${esc(p)}">${ic(PRESET_ICON[p] || "tune")}${esc(this._presetLabelFor(v.id, p))}</button>`).join("")}</div>` : "";
      const valves = r.valves.map((x) => {
        const col = !x.ok ? "var(--c-stale)" : r.a.valve_boosted ? "var(--c-boost)" : "var(--c-idle)";
        return `<div class="vr" style="--c:${col}">${ic("valve")}<span class="vn">${esc(x.name)}</span><span class="a">${x.cur != null ? `<b>${this._num(x.cur, d)}°</b>` : "–"}${x.target != null ? ` → ${this._num(x.target, d)}°` : ""}</span></div>`;
      }).join("");
      const big = this._bigInner(r.cur, d);
      const html = `<style>${CSS}${CSS3}</style><div class="root sheetroot${this._rootCls()}" style="${this._vars(c)};--sz:1">
        <div class="sh-wrap${sh.open ? " open" : ""}"><div class="sh-dim" data-sact="close"></div>
        <div class="sheet" data-st="${r.status}" role="dialog" aria-modal="true" aria-label="${esc(r.name)}">
          <div class="grab" aria-hidden="true"><i></i></div>
          <div class="sh"><span class="n">${esc(r.name)}</span><span class="chip">${ic(STATUS_ICON[r.status])}${esc(T(h, key))}</span>
            <button type="button" class="xb" data-sact="info" aria-label="${esc(T(h, "sh_details"))}" title="${esc(T(h, "sh_details"))}">${ic("tune")}</button>
            <button type="button" class="xb" data-sact="close" aria-label="${esc(T(h, "close"))}">${ic("close")}</button></div>
          <div class="big2"><div class="bv big">${big}</div>${trend}</div>
          ${chart}
          <div class="ctrl"><button type="button" class="pm" data-sact="dec"${can && target > lo + 1e-9 ? "" : " disabled"} aria-label="${esc(T(h, "decrease"))}">${ic("minus")}</button>
            <div class="tv">${target != null ? this._num(target, d) + "°" : "–"}</div>
            <button type="button" class="pm" data-sact="inc"${can && target < hi - 1e-9 ? "" : " disabled"} aria-label="${esc(T(h, "increase"))}">${ic("plus")}</button><span style="flex:1"></span>${this._sheetExtra(r)}</div>
          ${chips}
          <div class="vl">${valves}</div>
        </div></div></div>`;
      host.shadowRoot.innerHTML = html;
      const nw = host.shadowRoot.querySelector(".sheet");
      if (nw && scroll) nw.scrollTop = scroll;
      const root = host.shadowRoot.querySelector(".root");
      if (root && c.night_mode) {
        const k = this._nightK();
        root.classList.add("nt");
        root.classList.toggle("night", k >= 0.5);
        root.style.setProperty("--k", k.toFixed(3));
        root.style.setProperty("--nd", String(clamp(Number(c.night_dim) || 70, 30, 100) / 100));
      }
    }

    /** A lap vezérlősorának jobb oldala (a 2.9-es "Fűts most" gomb ide kerül). */
    _sheetExtra() { return ""; }

    /** A kártya újrarajzolása után a lap is frissül. */
    _render() {
      super._render();
      if (this._sheet) this._renderSheet();
    }

    disconnectedCallback() {
      super.disconnectedCallback();
      if (this._sheet) this._closeSheet();
    }

    /** Sima átmenetek: a gyűrű / sáv / szám az új értékre úszik, nem ugrik. */
    _after() {
      const root = this.shadowRoot, c = this._config, d = Number(c.decimals) || 0;
      const min = Number(c.gauge_min), span = Math.max(1, Number(c.gauge_max) - min);
      root.querySelectorAll("[data-room].t.glass").forEach((el) => {
        const r = this._room(el.dataset.room);
        if (!r) return;
        const arc = el.querySelector('[data-role="arc"]'), mk = el.querySelector('[data-role="mk"]'), big = el.querySelector('[data-role="big"]'), knob = el.querySelector('[data-role="knob"]');
        if (!arc && !big) return;
        const pend = this._pending[r.id];
        const tgt = pend ? pend.value : r.target;
        this._tween(r.id, { cur: r.cur == null ? null : r.cur, tgt: tgt == null ? null : tgt }, (v) => {
          if (arc && v.cur != null) arc.setAttribute("d", arcPath(60, 60, 50, Math.max((v.cur - min) / span, 0.001)));
          if (mk && v.tgt != null) {
            const [x, y] = pointOn(60, 60, 50, (v.tgt - min) / span);
            mk.setAttribute("cx", x.toFixed(2));
            mk.setAttribute("cy", y.toFixed(2));
            if (knob) { knob.style.left = ((x / 120) * 100).toFixed(2) + "%"; knob.style.top = ((y / 120) * 100).toFixed(2) + "%"; }
          }
          if (big && v.cur != null) big.innerHTML = this._bigInner(v.cur, d);
        });
      });
      root.querySelectorAll("[data-room].gradient, [data-room].rw").forEach((el) => {
        const r = this._room(el.dataset.room), fill = el.querySelector(".bar i"), mk = el.querySelector(".bar b");
        if (!r || !fill) return;
        const { f, ft } = this._barVals(r);
        this._tween(r.id + "|bar", { f, ft: ft == null ? 0 : ft }, (v) => {
          fill.style.width = v.f.toFixed(1) + "%";
          if (mk) mk.style.left = v.ft.toFixed(1) + "%";
        });
      });
      this._wireDrag();
      this._wireHold();
    }
  }
  /* ===================================================================
   *  Előzmény-alapú kártyák (2.8): Szoba részletes, Heti hőtérkép, Statisztika
   * =================================================================== */
  /* ---------- Szoba részletes ---------- */
  class MerossBoilerSyncRoomCard extends MerossBoilerSyncCard {
    static getConfigElement() { return document.createElement(ROOM_TAG + "-editor"); }
    static getStubConfig(hass) {
      const room = hass && hass.states ? Object.values(hass.states).find(isRoom) : null;
      return room ? { room: room.entity_id } : {};
    }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...DEFAULTS, ...ROOM_DEFAULTS, ...config, design: "glass", show_status: false, show_header: false, hold_action: "none", show_sparkline: false };
      if (!["valve", "sensor", "none"].includes(c.tap_action)) c.tap_action = "valve";
      c.hours = [6, 12, 24].includes(Number(c.hours)) ? Number(c.hours) : 24;
      c.rooms = c.room ? [c.room] : [];
      this._config = c;
      this._hours = c.hours;
      this._hReset();
      this._sig = null;
      if (this._hass) this._hMaybe();
      this._render();
    }

    getCardSize() { return 6; }
    getGridOptions() { return { columns: 12, min_columns: 6 }; }

    _hRequest(data) {
      const r = data.rooms[0];
      if (!r || !this._config.show_chart) return null;
      return { key: `${r.id}|${this._hours}`, ids: [r.id], hours: this._hours + 1, full: true };
    }

    _act(ds) {
      if (ds.act === "range") {
        const hrs = Number(ds.h);
        if ([6, 12, 24].includes(hrs) && hrs !== this._hours) {
          this._hours = hrs;
          this._hMaybe();
          this._redraw();
        }
        return;
      }
      super._act(ds);
    }

    _sigData(data) {
      return [super._sigData(data), this._hver, this._hours, this._hloading, this._herr, Math.floor(Date.now() / 60000)];
    }

    _valveRows(r) {
      const h = this._hass, d = Number(this._config.decimals) || 0;
      if (!r.valves.length) return "";
      const rows = r.valves.map((v) => {
        const col = !v.ok ? "var(--c-stale)" : r.a.valve_boosted ? "var(--c-boost)" : "var(--c-idle)";
        const label = v.preset != null ? this._presetLabelFor(v.id, v.preset) : "";
        return `<div class="vr" style="--c:${col}" data-entity="${esc(v.id)}">${ic("valve")}<span class="vn">${esc(v.name)}</span>
          <span class="a">${v.cur != null ? `<b>${this._num(v.cur, d)}°</b>` : "–"}${v.target != null ? ` → ${this._num(v.target, d)}°` : ""}</span>
          ${label ? `<span class="pr">${ic(PRESET_ICON[v.preset] || "tune")}${esc(label)}</span>` : "<span></span>"}</div>`;
      }).join("");
      return `<div class="vl"><div class="sm">${esc(F(h, "rc_valves", { n: r.valves.length }))}</div>${rows}</div>`;
    }

    /** Gombok a kártya alján (a 2.9-es "Fűts most" ide kerül). */
    _actions() { return ""; }

    _build(data) {
      const c = this._config, h = this._hass;
      const r = data.rooms[0];
      if (!r) return `<div class="msg">${esc(T(h, c.room ? "rc_missing" : "no_rooms"))}</div>`;
      const key = r.status === "windowpend" ? "st_windowpend" : "st_" + r.status;
      const chips = [`<span class="chip" data-st="${r.status}">${ic(STATUS_ICON[r.status])}${esc(T(h, key))}</span>`];
      if (r.a.valve_boosted && r.status !== "boost") chips.push(`<span class="chip" data-st="boost">${ic("valve")}${esc(T(h, "st_boost"))}</span>`);
      let right = "";
      if (c.show_chart) {
        const hist = this._hist, hours = this._hours;
        const range = `<div class="seg" role="group">${[6, 12, 24].map((x) => `<button type="button" class="${x === hours ? "on" : ""}" data-act="range" data-h="${x}" aria-pressed="${x === hours}">${esc(T(h, "hr_" + x))}</button>`).join("")}</div>`;
        let body;
        if (!hist) body = this._hMsg();
        else {
          const to = Date.now(), from = to - hours * 3600000;
          const intro = this._hfresh;
          this._hfresh = false;
          body = roomChartHtml(h, r, rowsOf(h, hist, r.id, true), from, to, hours, intro);
        }
        right = `<div class="hd2" style="margin-bottom:8px"><div class="sm" style="margin-right:auto">${esc(T(h, "rc_chart"))}</div>${range}</div>${body}`;
      }
      const valves = c.show_valves ? this._valveRows(r) : "";
      const acts = this._actions(r);
      const layout = c.show_chart ? "" : " solo";
      return `<div class="zm"><div class="t pn rc${layout}" data-st="${r.status}">
        <div class="hd2"><div class="ttl" ${this._tapAttr(r)}>${esc(c.title || r.name)}</div><div class="hchips">${chips.join("")}</div></div>
        <div class="body"><div class="left">${this._tileGlass(r)}</div><div class="right">${right}${valves}</div></div>${acts}</div></div>`;
    }
  }

  /* ---------- Heti hőtérkép ---------- */
  class MerossBoilerSyncHeatmapCard extends withHistory(MbsBase) {
    static getConfigElement() { return document.createElement(HEATMAP_TAG + "-editor"); }
    static getStubConfig() { return {}; }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...HEATMAP_DEFAULTS, ...config };
      c.days = [7, 14].includes(Number(c.days)) ? Number(c.days) : 7;
      this._config = c;
      this._days = c.days;
      this._sel = c.entity && c.entity !== "boiler" ? c.entity : "boiler";
      this._hReset();
      this._sig = null;
      if (this._hass) this._hMaybe();
      this._render();
    }

    getCardSize() { return 6; }
    getGridOptions() { return { columns: 12, min_columns: 6 }; }

    _hRequest(data) {
      const ids = data.rooms.map((r) => r.id);
      if (data.boilerId) ids.unshift(data.boilerId);
      return { key: `${this._days}|${ids.join(",")}`, ids, hours: this._days * 24 + 2, full: false };
    }

    _act(ds) {
      if (ds.act === "sel") { this._sel = ds.v; this._redraw(); return; }
      if (ds.act === "days") {
        const n = Number(ds.n);
        if ([7, 14].includes(n) && n !== this._days) { this._days = n; this._hMaybe(); this._redraw(); }
        return;
      }
      super._act(ds);
    }

    _sigData(data) {
      return [data.rooms.map((r) => [r.id, r.name]), data.boilerId, this._hver, this._sel, this._days, this._hloading, this._herr, Math.floor(Date.now() / 60000)];
    }

    /** Óránkénti fűtési idő [nap][óra] ms-ban a kiválasztott entitásra. */
    _grid(data, to, gridStart, days) {
      const h = this._hass, hist = this._hist;
      const roomSegs = (r) => stateSegments(rowsOf(h, hist, r.id, false), gridStart, to, isOnState);
      let segs;
      const room = this._sel !== "boiler" ? data.rooms.find((r) => r.id === this._sel) : null;
      if (room) segs = roomSegs(room);
      else {
        const rows = data.boilerId ? rowsOf(h, hist, data.boilerId, false) : [];
        segs = rows.length ? stateSegments(rows, gridStart, to, isRunState) : mergeSegments(data.rooms.map(roomSegs));
      }
      const g0 = new Date(gridStart), base = Date.UTC(g0.getFullYear(), g0.getMonth(), g0.getDate());
      const cells = Array.from({ length: days }, () => new Array(24).fill(0));
      segs.forEach(([s, e]) => {
        let t = s, guard = 0;
        while (t < e && guard++ < 24 * (days + 2)) {
          const d = new Date(t);
          let next = new Date(d.getFullYear(), d.getMonth(), d.getDate(), d.getHours() + 1).getTime();
          if (next <= t) next = t + 3600000;
          const end = Math.min(e, next), di = Math.round((Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) - base) / DAY_MS);
          if (di >= 0 && di < days) cells[di][d.getHours()] += end - t;
          t = end;
        }
      });
      cells.forEach((row) => row.forEach((v, i) => { row[i] = Math.min(v, 3600000); }));
      return { cells, room };
    }

    _build(data) {
      const c = this._config, h = this._hass;
      if (!data.rooms.length && !data.boilerId) return `<div class="msg">${esc(T(h, "no_rooms"))}</div>`;
      const days = this._days, hist = this._hist;
      const opts = [["boiler", T(h, "boiler")]].concat(data.rooms.map((r) => [r.id, r.name]));
      if (this._sel !== "boiler" && !data.rooms.some((r) => r.id === this._sel)) this._sel = "boiler";
      const sel = c.show_selector && opts.length > 1
        ? `<div class="sel" role="group">${opts.map(([id, nm]) => `<button type="button" class="${id === this._sel ? "on" : ""}" data-act="sel" data-v="${esc(id)}" aria-pressed="${id === this._sel}">${esc(nm)}</button>`).join("")}</div>` : "";
      const range = `<div class="seg" role="group">${[7, 14].map((n) => `<button type="button" class="${n === days ? "on" : ""}" data-act="days" data-n="${n}" aria-pressed="${n === days}">${esc(F(h, "days_n", { n }))}</button>`).join("")}</div>`;
      if (!hist) {
        return `<div class="zm"><div class="t pn hm" style="--c:var(--c-demand)"><div class="hd2"><div class="ttl">${esc(c.title || F(h, "hm_title_boiler", { n: days }))}</div>${range}</div>${sel}${this._hMsg()}</div></div>`;
      }
      const to = Date.now(), gridStart = dayStart(to, days - 1);
      const { cells, room } = this._grid(data, to, gridStart, days);
      const lang = langOf(h), nowDay = days - 1, nowHour = new Date(to).getHours();
      let hdr = `<span></span>`;
      for (let hr = 0; hr < 24; hr++) hdr += `<span class="hn">${hr % 3 === 0 ? hr : ""}</span>`;
      let body = "", total = 0, longest = { i: -1, ms: 0 };
      const hourSum = new Array(24).fill(0);
      cells.forEach((row, di) => {
        const ts = dayStart(to, days - 1 - di);
        const dn = weekdayOf(h, ts, "short");
        const dayOfMonth = new Date(ts).getDate();
        body += `<span class="dn">${esc(dn)}${days > 7 ? `<small>${dayOfMonth}</small>` : ""}</span>`;
        let dayTotal = 0;
        row.forEach((ms, hr) => {
          total += ms; dayTotal += ms; hourSum[hr] += ms;
          const future = di === nowDay && hr > nowHour;
          if (future) { body += `<span class="cell fu"></span>`; return; }
          const v = ms / 3600000;
          const cellTs = new Date(new Date(ts).getFullYear(), new Date(ts).getMonth(), new Date(ts).getDate(), hr).getTime();
          body += `<span class="cell${v < 0.04 ? " z" : ""}${di === nowDay && hr === nowHour ? " now" : ""}" style="--v:${v.toFixed(2)}" data-t="${cellTs}" data-m="${Math.round(ms / 60000)}" data-hr="${hr}" data-di="${di}"></span>`;
        });
        if (dayTotal > longest.ms) longest = { i: di, ms: dayTotal };
      });
      let summary = "";
      if (c.show_summary) {
        const elapsed = Math.max(1, (to - gridStart) / DAY_MS);
        const bits = [F(h, "hm_avg", { v: `<b>${esc(fmtMinutes(total / 60000 / elapsed, h))}</b>` })];
        const order = hourSum.map((v, i) => [v, i]).sort((x, y) => y[0] - x[0]);
        if (order[0][0] > 0) {
          const peaks = [order[0]];
          const second = order.find((x) => Math.abs(x[1] - order[0][1]) >= 3 && x[0] >= order[0][0] * 0.35);
          if (second) peaks.push(second);
          bits.push(F(h, "hm_peak", { v: peaks.sort((x, y) => x[1] - y[1]).map((x) => `<b>${x[1]}–${(x[1] + 1) % 24 || 24}</b>`).join(` ${T(h, "and_word")} `) }));
        }
        if (longest.i >= 0 && longest.ms > 0) {
          bits.push(F(h, "hm_longest", { d: `<b>${esc(weekdayOf(h, dayStart(to, days - 1 - longest.i), "long").toLowerCase())}</b>`, v: esc(fmtMinutes(longest.ms / 60000, h)) }));
        }
        summary = `<div class="sum">${bits.map((b) => `<span>${b}</span>`).join("")}</div>`;
      }
      const title = c.title || (room ? F(h, "hm_title_room", { room: room.name, n: days }) : F(h, "hm_title_boiler", { n: days }));
      return `<div class="zm"><div class="t pn hm" style="--c:var(--c-demand)"><div class="hd2"><div class="ttl">${esc(title)}</div>${range}</div>${sel}
        <div class="hgrid" style="--dnw:${days > 7 ? 46 : 34}px">${hdr}${body}</div>
        <div class="lg"><span>${esc(T(h, "hm_less"))}</span><i></i><span>${esc(T(h, "hm_more"))}</span></div>${summary}</div></div>`;
    }

    _after() {
      const grid = this.shadowRoot.querySelector(".hgrid");
      if (!grid) return;
      const h = this._hass;
      let cur = null;
      const hide = () => { grid.querySelectorAll(".tip").forEach((x) => x.remove()); grid.querySelectorAll(".cell.hi").forEach((x) => x.classList.remove("hi")); cur = null; };
      const show = (cell) => {
        hide();
        if (!cell) return;
        cur = cell;
        cell.classList.add("hi");
        const ts = Number(cell.dataset.t), hr = Number(cell.dataset.hr), m = Number(cell.dataset.m);
        const tip = document.createElement("div");
        tip.className = "tip" + (hr < 4 ? " l" : hr > 19 ? " r" : "");
        tip.innerHTML = `<b>${esc(weekdayOf(h, ts, "long"))} ${hourLabel(hr)}–${hourLabel((hr + 1) % 24)}</b><br>${esc(m > 0 ? F(h, "hm_tip", { m }) : T(h, "hm_tip0"))}`;
        cell.appendChild(tip);
      };
      grid.addEventListener("pointerover", (ev) => {
        const cell = ev.target.closest && ev.target.closest(".cell[data-t]");
        if (ev.pointerType === "mouse" && cell && cell !== cur) show(cell);
      });
      grid.addEventListener("pointerleave", (ev) => { if (ev.pointerType === "mouse") hide(); });
      grid.addEventListener("click", (ev) => {
        const cell = ev.target.closest && ev.target.closest(".cell[data-t]");
        show(cell && cell !== cur ? cell : null);
      });
    }
  }

  /* ---------- Fűtési statisztika ---------- */
  class MerossBoilerSyncStatsCard extends withHistory(MbsBase) {
    static getConfigElement() { return document.createElement(STATS_TAG + "-editor"); }
    static getStubConfig() { return {}; }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...STATS_DEFAULTS, ...config };
      c.days = [7, 14, 30].includes(Number(c.days)) ? Number(c.days) : 7;
      this._config = c;
      this._days = c.days;
      this._hReset();
      this._sig = null;
      if (this._hass) this._hMaybe();
      this._render();
    }

    getCardSize() { return 7; }
    getGridOptions() { return { columns: 12, min_columns: 6 }; }

    _outdoorId(data) {
      return data.summer && data.summer.attributes.outdoor_sensor ? data.summer.attributes.outdoor_sensor : null;
    }

    _hRequest(data) {
      const c = this._config, ids = data.rooms.map((r) => r.id);
      if (data.boilerId) ids.unshift(data.boilerId);
      const out = c.show_outdoor ? this._outdoorId(data) : null;
      if (out) ids.push(out);
      return { key: `${this._days}|${ids.join(",")}`, ids, hours: this._days * 24 + 2, full: false };
    }

    _act(ds) {
      if (ds.act === "days") {
        const n = Number(ds.n);
        if ([7, 14, 30].includes(n) && n !== this._days) { this._days = n; this._hMaybe(); this._redraw(); }
        return;
      }
      super._act(ds);
    }

    _sigData(data) {
      return [data.rooms.map((r) => [r.id, r.name]), data.boilerId, this._hver, this._days, this._hloading, this._herr, Math.floor(Date.now() / 60000),
        data.starts && [data.starts.state, data.starts.attributes], data.cycling && data.cycling.state];
    }

    /** Idősúlyozott átlag egy szám típusú szenzorra egy időablakban. */
    _avgIn(rows, from, to) {
      let sum = 0, w = 0;
      rows.forEach((r, i) => {
        const v = parseFloat(r.s);
        if (isNaN(v)) return;
        const a = Math.max(r.t, from), b = Math.min(i + 1 < rows.length ? rows[i + 1].t : to, to);
        if (b > a) { sum += v * (b - a); w += b - a; }
      });
      return w > 0 ? sum / w : null;
    }

    _chart(daily, outs, labels) {
      const h = this._hass, n = daily.length, W = 460, H = 190, pl = 34, pr = 34, pt0 = 14, ph = 130;
      const slot = (W - pl - pr) / n, bw = Math.min(34, slot * 0.64);
      const maxH = Math.max(...daily.map((x) => x / 3600000));
      const ymax = Math.max(4, Math.ceil(maxH / 2) * 2);
      const Yb = (v) => pt0 + ph - (v / ymax) * ph;
      const have = outs.filter((v) => v != null);
      let oLo = 0, oHi = 10;
      if (have.length) { oLo = Math.floor(Math.min(...have)); oHi = Math.ceil(Math.max(...have)); if (oHi - oLo < 4) oHi = oLo + 4; }
      const Yo = (v) => pt0 + ph - ((v - oLo) / (oHi - oLo)) * ph;
      const uh = T(h, "unit_h"), f1 = (x) => x.toFixed(1);
      let s = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img">`;
      [0, ymax / 2, ymax].forEach((v) => { s += `<line class="gl" x1="${pl}" x2="${W - pr}" y1="${f1(Yb(v))}" y2="${f1(Yb(v))}"/><text x="${pl - 6}" y="${f1(Yb(v) + 3.5)}" text-anchor="end">${v} ${esc(uh)}</text>`; });
      if (have.length) [oLo, oHi].forEach((v) => { s += `<text x="${W - pr + 6}" y="${f1(Yo(v) + 3.5)}" style="fill:#64b5f6">${v}°</text>`; });
      const labelEvery = n <= 8 ? 1 : n <= 16 ? 2 : 5;
      daily.forEach((ms, i) => {
        const x = pl + i * slot + (slot - bw) / 2, v = ms / 3600000, last = i === n - 1;
        const y = Yb(v), bh = Math.max(v > 0 ? 2 : 0, pt0 + ph - y);
        s += `<rect x="${f1(x)}" y="${f1(pt0 + ph - bh)}" width="${f1(bw)}" height="${f1(bh)}" rx="${f1(Math.min(7, bw / 2.5))}" style="fill:var(--c-demand)" opacity="${last ? 1 : 0.78}"/>`;
        if (n <= 8 && v > 0) s += `<text x="${f1(x + bw / 2)}" y="${f1(y - 5)}" text-anchor="middle" style="fill:var(--text);font-size:10px;font-weight:${last ? 700 : 500}">${esc(fmtMinutes(ms / 60000, h))}</text>`;
        if (i % labelEvery === 0 || last) s += `<text x="${f1(x + bw / 2)}" y="${H - 6}" text-anchor="middle" style="${last ? "fill:var(--text);font-weight:600" : ""}">${esc(labels[i])}</text>`;
      });
      const pts = outs.map((v, i) => (v == null ? null : [pl + i * slot + slot / 2, Yo(v)])).filter(Boolean);
      if (pts.length) {
        s += `<path d="${pts.map((p, i) => `${i ? "L" : "M"}${f1(p[0])} ${f1(p[1])}`).join(" ")}" fill="none" stroke="#64b5f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`;
        if (n <= 16) s += pts.map((p) => `<circle cx="${f1(p[0])}" cy="${f1(p[1])}" r="3.2" fill="#64b5f6" stroke="var(--surface)" stroke-width="1.5"/>`).join("");
      }
      return { svg: s + "</svg>", hasOut: have.length > 0 };
    }

    _build(data) {
      const c = this._config, h = this._hass, days = this._days, hist = this._hist;
      const range = `<div class="seg" role="group">${[7, 14, 30].map((n) => `<button type="button" class="${n === days ? "on" : ""}" data-act="days" data-n="${n}" aria-pressed="${n === days}">${esc(F(h, "days_n", { n }))}</button>`).join("")}</div>`;
      const head = `<div class="hd2"><div class="ttl">${esc(c.title || T(h, "stt_title"))}</div>${range}</div>`;
      if (!data.rooms.length && !data.boilerId) return `<div class="msg">${esc(T(h, "no_rooms"))}</div>`;
      if (!hist) return `<div class="zm"><div class="t pn stt" style="--c:var(--c-demand)">${head}${this._hMsg()}</div></div>`;
      const to = Date.now(), gridStart = dayStart(to, days - 1);
      const roomSegs = data.rooms.map((r) => ({ r, segs: stateSegments(rowsOf(h, hist, r.id, false), gridStart, to, isOnState) }));
      const brows = data.boilerId ? rowsOf(h, hist, data.boilerId, false) : [];
      const bsegs = brows.length ? stateSegments(brows, gridStart, to, isRunState) : mergeSegments(roomSegs.map((x) => x.segs));
      const outId = c.show_outdoor ? this._outdoorId(data) : null;
      const orows = outId ? rowsOf(h, hist, outId, false) : [];
      const daily = [], outs = [], labels = [];
      for (let i = 0; i < days; i++) {
        const s0 = dayStart(to, days - 1 - i), s1 = i === days - 1 ? to : dayStart(to, days - 2 - i);
        daily.push(overlapMs(bsegs, s0, s1));
        outs.push(orows.length ? this._avgIn(orows, s0, s1) : null);
        labels.push(days <= 8 ? weekdayOf(h, s0, "short") : String(new Date(s0).getDate()));
      }
      const totalMs = daily.reduce((a, b) => a + b, 0);
      const elapsed = Math.max(1, (to - gridStart) / DAY_MS);
      const outAvg = orows.length ? this._avgIn(orows, gridStart, to) : null;
      const lang = langOf(h);
      let cost = "";
      if (c.show_cost) {
        const m3 = (totalMs / 3600000) * (Number(c.gas_m3_per_hour) || 0), price = Number(c.gas_price) || 0;
        const fmt0 = (v) => Math.round(v).toLocaleString(lang);
        if (price > 0) {
          cost = `<div class="k cost"><div class="l">${esc(T(h, "stt_cost"))}</div><div class="v">≈ ${esc(fmt0(Math.round(m3 * price / 100) * 100))}<small>${esc(c.currency || "")}</small></div>
            <div class="e">${esc(F(h, "stt_cost_note", { m3: this._num(Number(c.gas_m3_per_hour) || 0, 1), price: fmt0(price), cur: c.currency || "" }))}</div></div>`;
        } else {
          cost = `<div class="k cost"><div class="l">${esc(T(h, "stt_gas"))}</div><div class="v">≈ ${esc(fmt0(m3))}<small>m³</small></div><div class="e">${esc(F(h, "stt_gas_note", { m3: this._num(Number(c.gas_m3_per_hour) || 0, 1) }))}</div></div>`;
        }
      }
      const kp = `<div class="kp">
        <div class="k"><div class="l">${esc(T(h, "stt_total"))}</div><div class="v">${esc(fmtMinutes(totalMs / 60000, h))}</div></div>
        <div class="k"><div class="l">${esc(T(h, "stt_avg"))}</div><div class="v">${esc(fmtMinutes(totalMs / 60000 / elapsed, h))}</div></div>
        ${outAvg != null ? `<div class="k"><div class="l">${esc(T(h, "stt_outdoor"))}</div><div class="v">${this._num(outAvg, 1)}<small>${esc(this._unit())}</small></div></div>` : ""}${cost}</div>`;
      const ch = this._chart(daily, outs, labels);
      const lgd = `<div class="lgd"><span style="--k:var(--c-demand)">${esc(T(h, "stt_lg_boiler"))}</span>${ch.hasOut ? `<span style="--k:#64b5f6">${esc(T(h, "stt_lg_out"))}</span>` : ""}</div>`;
      let rank = "";
      if (c.show_rooms && roomSegs.length) {
        const list = roomSegs.map(({ r, segs }) => ({ r, ms: overlapMs(segs, gridStart, to) })).sort((a, b) => b.ms - a.ms);
        const mx = Math.max(1, list[0].ms);
        rank = `<div><h4>${esc(T(h, "stt_rank"))}</h4>${list.map(({ r, ms }) =>
          `<div class="rk" ${this._tapAttr(r)}><span>${esc(r.name)}</span><span class="db"><i style="width:${((ms / mx) * 100).toFixed(1)}%"></i></span><span class="vv">${esc(fmtMinutes(ms / 60000, h))}</span></div>`).join("")}</div>`;
      }
      const cyc = c.show_cycles && data.starts ? `<div class="sub2">${cyclesHtml(h, data, (v, d) => this._num(v, d))}</div>` : "";
      return `<div class="zm"><div class="t pn stt" style="--c:var(--c-demand)">${head}${kp}
        <div class="two${rank ? "" : " one"}"><div><h4>${esc(ch.hasOut ? T(h, "stt_daily_out") : T(h, "stt_daily"))}</h4>${ch.svg}${lgd}</div>${rank}</div>${cyc}</div></div>`;
    }
  }
  /* ===================================================================
   *  Áttekintő / kazán kártya
   * =================================================================== */
  const isHot = (r) => r.on || r.status === "demand" || r.status === "boost";
  const fmtMonthDay = (s) => String(s || "").replace("-", ".");

  function snowHtml() {
    const L = [6, 14, 23, 31, 40, 48, 57, 66, 74, 83, 91, 97, 11, 52, 79, 36];
    return `<div class="amb snow">${L.map((l, i) => `<i style="--l:${l}%;--s:${2 + (i % 3)}px;--d:${i % 2 ? 4 : 2}s;--o:${(-(i * 0.37) % 4).toFixed(2)}s"></i>`).join("")}</div>`;
  }

  class MerossBoilerSyncOverviewCard extends MbsBase {
    static getConfigElement() { return document.createElement(OVERVIEW_TAG + "-editor"); }
    static getStubConfig() { return {}; }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...OVERVIEW_DEFAULTS, ...config };
      if (!["valve", "sensor", "none"].includes(c.tap_action)) c.tap_action = "valve";
      this._config = c;
      this._sig = null;
      this._render();
    }

    getCardSize() {
      const n = this._data ? this._data.rooms.length : 6;
      return 3 + Math.ceil(n / 6) + (this._config && this._config.show_quick ? 1 : 0);
    }

    _outdoorFraction(a) {
      const out = Number(a.outdoor_temperature);
      return clamp((out + 10) / 40, 0, 1) * 100;
    }

    _build(data) {
      const c = this._config, h = this._hass, d = Number(c.decimals) || 0, u = this._unit();
      const sm = data.summer, sa = sm ? sm.attributes : {};
      const summerOn = !!sm && sm.state === "on";
      const bOn = boilerOn(data.boiler);
      const calling = data.rooms.filter((r) => r.on).length;
      const blocks = [];

      if (c.show_boiler && data.boiler) {
        const sub = summerOn ? esc(T(h, "summer"))
          : bOn ? `<b>${calling} / ${data.rooms.length}</b> ${esc(T(h, "rooms_calling"))}` : esc(T(h, "no_demand"));
        blocks.push(`<div class="blk" style="--c:${bOn ? "var(--c-demand)" : "var(--c-off)"}" ${this._tapOn() ? `data-entity="${esc(data.boilerId)}"` : ""}>
          <div class="boiler${bOn && c.flow_animation ? " fxon" : ""}"><svg class="rg" viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="29" fill="color-mix(in srgb, var(--c) 12%, transparent)" stroke="color-mix(in srgb, var(--c) 40%, transparent)" stroke-width="1.5"/></svg>${ic("flame")}</div>
          <div><div class="lbl">${esc(T(h, "boiler"))}</div><div class="val">${esc(T(h, bOn ? "on" : "off"))}</div><div class="sub">${sub}</div></div></div>`);
      }

      if (c.show_outdoor && sm && sa.outdoor_temperature != null && !isNaN(Number(sa.outdoor_temperature))) {
        const thr = num(sa.threshold), avg = num(sa.outdoor_average_24h);
        const tpos = thr == null ? null : clamp((thr + 10) / 40, 0, 1) * 100;
        const subs = [];
        if (avg != null) subs.push(`${esc(T(h, "avg24"))} <b>${this._num(avg, 1)}°</b>`);
        if (thr != null) subs.push(`${esc(T(h, "threshold_word"))} ${this._num(thr, 0)}°`);
        blocks.push(`<div class="blk"><div class="lbl">${esc(T(h, "outdoor"))}</div>
          <div class="val">${this._num(sa.outdoor_temperature, 1)}<small>${esc(u)}</small></div>
          <div class="scale"><i data-role="outbar" style="width:${this._outdoorFraction(sa).toFixed(1)}%"></i>${tpos != null ? `<u style="left:${tpos.toFixed(1)}%"></u>` : ""}</div>
          <div class="sub">${subs.join(" · ")}</div></div>`);
      }

      if (c.show_summer && sm) {
        const per = sa.period_start && sa.period_end ? `${esc(T(h, "period_word"))} ${esc(fmtMonthDay(sa.period_start))} – ${esc(fmtMonthDay(sa.period_end))}` : "";
        blocks.push(`<div class="blk" ${this._tapOn() ? `data-entity="${esc(sm.entity_id)}"` : ""}><div class="lbl">${esc(T(h, "summer"))}</div>
          <div class="val" style="${summerOn ? "color:var(--c-summer)" : ""}">${esc(T(h, summerOn ? "active" : "inactive"))}</div>
          <div class="sub">${per}</div></div>`);
      }

      let flow = "";
      if (c.show_rooms) {
        if (!data.rooms.length) flow = `<div class="msg" style="position:relative;z-index:2;margin-top:14px">${esc(T(h, "no_rooms"))}</div>`;
        else {
          const nodes = data.rooms.map((r) => `<div class="node${isHot(r) ? " hot" : ""}" data-st="${r.status}" ${this._tapAttr(r)}>
            <div class="nchip"><i class="dot"></i><div class="tx"><div class="n">${esc(r.name)}</div><div class="v">${this._num(r.cur, d)}°</div></div></div></div>`).join("");
          flow = `<div class="flow"><div class="src" style="--c:${bOn ? "var(--c-demand)" : "var(--c-off)"}">${ic("flame")}</div>
            <div class="rail${c.flow_animation ? " flowing" : ""}">${nodes}</div></div>`;
        }
      }

      let amb = "";
      if (c.ambience) {
        if (summerOn) amb = '<div class="amb sun"></div>';
        else if (sa.outdoor_temperature != null && Number(sa.outdoor_temperature) <= 1) amb = snowHtml();
      }
      const title = c.title ? `<div class="ottl">${esc(c.title)}</div>` : "";
      const top = blocks.length ? `<div class="top">${blocks.join("")}</div>` : "";
      const quick = this._quickHtml(data.rooms);
      if (!blocks.length && !flow && !title && !quick) return `<div class="msg">${esc(T(h, "no_data"))}</div>`;
      return `<div class="zm"><div class="t ov" style="--c:${bOn ? "var(--c-demand)" : "var(--c-off)"}">${amb}${title}${top}${flow}${quick}</div></div>`;
    }

    _after(data) {
      const bar = this.shadowRoot.querySelector('[data-role="outbar"]');
      if (bar && data.summer) {
        this._tween("out", { f: this._outdoorFraction(data.summer.attributes) }, (v) => { bar.style.width = v.f.toFixed(1) + "%"; });
      }
    }
  }

  /* ===================================================================
   *  Napi fűtési idővonal kártya
   * =================================================================== */
  const toEpochMs = (v) => { const n = Number(v); return n > 1e11 ? n : n * 1000; };

  /** A HA előzmény-websocket választ (tömörített vagy teljes formátum) egységes sorokká alakítja. */
  function parseRows(list, keepAttrs) {
    const out = [];
    let lastA = {};
    (Array.isArray(list) ? list : []).forEach((x) => {
      if (!x) return;
      const s = x.s !== undefined ? x.s : x.state;
      let t = null;
      if (x.lu != null) t = toEpochMs(x.lu);
      else if (x.last_updated) t = Date.parse(x.last_updated);
      else if (x.lc != null) t = toEpochMs(x.lc);
      else if (x.last_changed) t = Date.parse(x.last_changed);
      if (t == null || isNaN(t)) return;
      const a = x.a !== undefined ? x.a : x.attributes;
      if (a) lastA = a;
      out.push({ t, s: String(s), a: keepAttrs ? lastA : {} });
    });
    return out.sort((p, q) => p.t - q.t);
  }

  /** Egymást követő szakaszok [kezdet, vég] kinds szerint (hőt kért / szelep kinyitva / ablak / elavult). */
  function segmentsOf(rows, from, to) {
    const out = { demand: [], boost: [], window: [], stale: [] };
    const add = (k, s, e) => {
      const l = out[k], last = l[l.length - 1];
      if (last && s <= last[1] + 1) last[1] = Math.max(last[1], e); else l.push([s, e]);
    };
    rows.forEach((r, i) => {
      const s = Math.max(r.t, from), e = Math.min(i + 1 < rows.length ? rows[i + 1].t : to, to);
      if (e <= s) return;
      if (r.s === "on") add("demand", s, e);
      if (r.a.valve_boosted) add("boost", s, e);
      if (r.a.window_open) add("window", s, e);
      if (r.a.temperature_sensor_stale) add("stale", s, e);
    });
    return out;
  }

  function onSegments(rows, from, to) {
    const out = [];
    rows.forEach((r, i) => {
      if (["off", "unavailable", "unknown", "undefined"].includes(r.s)) return;
      const s = Math.max(r.t, from), e = Math.min(i + 1 < rows.length ? rows[i + 1].t : to, to);
      if (e <= s) return;
      const last = out[out.length - 1];
      if (last && s <= last[1] + 1) last[1] = Math.max(last[1], e); else out.push([s, e]);
    });
    return out;
  }

  function unionSegments(lists) {
    const all = [].concat(...lists).sort((a, b) => a[0] - b[0]);
    const out = [];
    all.forEach(([s, e]) => {
      const last = out[out.length - 1];
      if (last && s <= last[1] + 1) last[1] = Math.max(last[1], e); else out.push([s, e]);
    });
    return out;
  }

  class MerossBoilerSyncTimelineCard extends MbsBase {
    static getConfigElement() { return document.createElement(TIMELINE_TAG + "-editor"); }
    static getStubConfig() { return { hours: 24 }; }

    constructor() {
      super();
      this._hours = 24;
      this._hist = null;
      this._fetchKey = null;
      this._fetchedAt = 0;
      this._loading = false;
      this._err = false;
      this._ver = 0;
      this._kinds = "";
      this._introPending = false;
    }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...TIMELINE_DEFAULTS, ...config };
      c.hours = HISTORY_RANGES.includes(Number(c.hours)) ? Number(c.hours) : 24;
      if (!["valve", "sensor", "none"].includes(c.tap_action)) c.tap_action = "valve";
      this._config = c;
      this._hours = c.hours;
      this._hist = null;
      this._fetchKey = null;
      this._sig = null;
      if (this._hass) this._maybeFetch();
      this._render();
    }

    set hass(hass) {
      this._hass = hass;
      this._maybeFetch();
      this._render();
    }

    getCardSize() { return 3 + Math.ceil(((this._data && this._data.rooms.length) || 6) * 0.55); }

    /* ---------- előzmények lekérése ---------- */
    _maybeFetch() {
      if (!this._config || !this._hass || typeof this._hass.callWS !== "function") return;
      const data = collect(this._hass, this._config);
      const ids = data.rooms.map((r) => r.id);
      if (!ids.length) return;
      const key = `${this._hours}|${ids.join(",")}|${data.boilerId || ""}`;
      const kinds = JSON.stringify([data.rooms.map((r) => [r.on, !!r.a.valve_boosted, !!r.a.window_open, !!r.a.temperature_sensor_stale]),
        data.boiler && data.boiler.state]);
      const now = Date.now();
      if (this._fetchKey !== key
        || (!this._loading && (now - this._fetchedAt > 300000 || (this._kinds !== kinds && now - this._fetchedAt > 20000)))) {
        this._kinds = kinds;
        this._fetch(key, data);
      }
    }

    async _fetch(key, data) {
      if (!this._hist || this._hist.key !== key) { this._hist = null; this._err = false; }
      const firstOfKey = !this._hist;
      this._loading = true;
      this._fetchKey = key;
      this._fetchedAt = Date.now();
      const hours = this._hours, end = Date.now(), start = end - hours * 3600000, full = hours <= 24;
      const base = {
        type: "history/history_during_period", start_time: new Date(start).toISOString(), end_time: new Date(end).toISOString(),
        include_start_time_state: true, significant_changes_only: false,
      };
      try {
        const roomsP = this._hass.callWS({ ...base, entity_ids: data.rooms.map((r) => r.id), minimal_response: !full, no_attributes: !full });
        const boilerP = data.boilerId
          ? this._hass.callWS({ ...base, entity_ids: [data.boilerId], minimal_response: true, no_attributes: true }).catch(() => ({}))
          : Promise.resolve({});
        const [rooms, boiler] = await Promise.all([roomsP, boilerP]);
        if (this._fetchKey !== key) return;
        this._hist = { key, start, end, full, rooms: rooms || {}, boiler: (boiler && data.boilerId && boiler[data.boilerId]) || null };
        this._err = false;
        if (firstOfKey) this._introPending = true;
      } catch (err) {
        if (this._fetchKey !== key) return;
        this._hist = null;
        this._err = true;
      } finally {
        if (this._fetchKey === key) {
          this._loading = false;
          this._ver++;
          this._sig = null;
          this._render();
        }
      }
    }

    /* ---------- kirajzolás ---------- */
    _act(ds) {
      if (ds.act === "range") {
        const h = Number(ds.h);
        if (HISTORY_RANGES.includes(h) && h !== this._hours) {
          this._hours = h;
          this._maybeFetch();
          this._redraw();
        }
        return;
      }
      super._act(ds);
    }

    _sigData(data) {
      return [data.rooms.map((r) => [r.id, r.name, r.status, r.on, !!r.a.valve_boosted, !!r.a.window_open, !!r.a.temperature_sensor_stale]),
        data.boiler && data.boiler.state, this._ver, this._hours, this._loading, this._err, Math.floor(Date.now() / 60000)];
    }

    _fmtDuration(ms) {
      const min = Math.round(ms / 60000);
      if (min <= 0) return "–";
      const h = this._hass, hh = Math.floor(min / 60), mm = min % 60;
      if (!hh) return `${mm} ${T(h, "unit_min")}`;
      return `${hh} ${T(h, "unit_h")} ${pad2(mm)} ${T(h, "unit_min")}`;
    }

    _ticks(from, to) {
      const hours = this._hours;
      const stepH = hours <= 6 ? 1 : hours <= 12 ? 2 : hours <= 24 ? 6 : 24;
      const lang = langOf(this._hass);
      const d = new Date(from);
      d.setMinutes(0, 0, 0);
      const fits = () => d.getTime() >= from && (stepH === 24 ? d.getHours() === 0 : d.getHours() % stepH === 0);
      let guard = 0;
      while (!fits() && guard++ < 60) d.setHours(d.getHours() + 1);
      const out = [];
      guard = 0;
      while (d.getTime() < to && guard++ < 60) {
        const pos = (d.getTime() - from) / (to - from);
        if (pos <= 0.94) {
          const label = hours > 24
            ? d.toLocaleDateString(lang, { weekday: "short" })
            : d.toLocaleTimeString(lang, { hour: "2-digit", minute: "2-digit" });
          out.push({ pos: pos * 100, label });
        }
        if (stepH === 24) d.setDate(d.getDate() + 1); else d.setHours(d.getHours() + stepH);
      }
      return out;
    }

    _bars(segs, from, span, order, live) {
      return order.map((kind) => (segs[kind] || []).map((s) => {
        const isLive = live && s[1] >= from + span - 1000 && (kind === "demand" || kind === "boost");
        return `<i class="${isLive ? "live" : ""}" style="left:${(((s[0] - from) / span) * 100).toFixed(3)}%;width:${(((s[1] - s[0]) / span) * 100).toFixed(3)}%;--k:var(--c-${kind === "window" ? "window" : kind === "stale" ? "stale" : kind === "boost" ? "boost" : "demand"})"></i>`;
      }).join("")).join("");
    }

    _build(data) {
      const c = this._config, h = this._hass;
      if (!data.rooms.length) return `<div class="msg">${esc(T(h, "no_rooms"))}</div>`;
      const hist = this._hist;
      const hours = this._hours;
      const title = esc(c.title || T(h, "tl_default"));
      const range = c.show_range
        ? `<div class="seg" role="group">${HISTORY_RANGES.map((x) => `<button type="button" class="${x === hours ? "on" : ""}" data-act="range" data-h="${x}" aria-pressed="${x === hours}">${esc(T(h, "hr_" + x))}</button>`).join("")}</div>` : "";

      let inner = "", total = "";
      if (!hist) {
        inner = `<div class="msg">${esc(T(h, this._err ? "tl_empty" : "tl_loading"))}</div>`;
      } else {
        const to = Date.now(), from = to - hours * 3600000, span = to - from;
        const states = (h && h.states) || {};
        const live = (id, rows) => {
          // a legutóbbi előzmény-sor óta érkezett állapot: a jobb szél mindig az élő állapotot mutatja
          const st = states[id];
          if (!st) return rows;
          const lu = Date.parse(st.last_updated || st.last_changed || "");
          const last = rows[rows.length - 1];
          if (!isNaN(lu) && (!last || lu > last.t + 1000)) return rows.concat([{ t: lu, s: String(st.state), a: hist.full ? st.attributes || {} : {} }]);
          return rows;
        };
        const roomRows = data.rooms.map((r) => ({ r, segs: segmentsOf(live(r.id, parseRows(hist.rooms[r.id], hist.full)), from, to) }));
        let boilerSegs = null;
        if (c.show_boiler_row) {
          const brows = hist.boiler ? live(data.boilerId, parseRows(hist.boiler, false)) : null;
          boilerSegs = brows && brows.length ? onSegments(brows, from, to) : unionSegments(roomRows.map((x) => x.segs.demand));
        }
        const sum = (list) => list.reduce((a, s) => a + (s[1] - s[0]), 0);
        const row = (name, segs, dur, cls, entity) => `<div class="tlrow${cls ? " " + cls : ""}" ${entity ? `data-entity="${esc(entity)}"` : ""}>
            <div class="rn">${esc(name)}</div><div class="track">${this._bars(segs, from, span, ["demand", "window", "stale", "boost"], true)}</div><div class="du">${esc(this._fmtDuration(dur))}</div></div>`;
        const rows = [];
        if (boilerSegs) {
          rows.push(row(T(h, "boiler"), { demand: boilerSegs }, sum(boilerSegs), "boilerrow", this._tapOn() ? data.boilerId : null));
          total = `<div class="total">${esc(T(h, "tl_total"))} <b>${esc(this._fmtDuration(sum(boilerSegs)))}</b></div>`;
        }
        roomRows.forEach(({ r, segs }) => rows.push(row(r.name, segs, sum(segs.demand), "", this._tapEntity(r))));
        const ticks = this._ticks(from, to);
        const grid = ticks.map((t) => `<span style="left:${t.pos.toFixed(2)}%"></span>`).join("") + '<span class="nowline" style="left:100%"></span>';
        const axis = ticks.map((t) => `<span style="left:${t.pos.toFixed(2)}%">${esc(t.label)}</span>`).join("") + `<span class="now">${esc(T(h, "now"))}</span>`;
        const lg = hist.full
          ? [["demand", "lg_demand"], ["boost", "lg_boost"], ["window", "lg_window"], ["stale", "lg_stale"]]
          : [["demand", "lg_demand"]];
        const legend = c.show_legend
          ? `<div class="legend">${lg.map(([k, t]) => `<span style="--k:var(--c-${k})">${esc(T(h, t))}</span>`).join("")}</div>` : "";
        const note = !hist.full ? `<div class="tlnote">${esc(T(h, "tl_week_note"))}</div>` : "";
        inner = `<div class="tlbody"><div class="tlgrid">${grid}</div>${rows.join("")}</div>
          <div class="axis"><div></div><div class="ticks">${axis}</div><div></div></div>${legend}${note}`;
      }
      const intro = this._introPending && c.intro_animation && hist;
      if (hist) this._introPending = false;
      const fx = c.intro_animation ? " tlfx" : "";
      return `<div class="zm"><div class="t tl${fx}${intro ? " intro" : ""}">
        <div class="thd"><div class="tt">${title}</div>${c.show_total ? total : ""}${range}</div>${inner}</div></div>`;
    }
  }

  /* ===================================================================
   *  Chip-sor kártya
   * =================================================================== */
  class MerossBoilerSyncChipsCard extends MbsBase {
    static getConfigElement() { return document.createElement(CHIPS_TAG + "-editor"); }
    static getStubConfig() { return { style: "chip" }; }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...CHIPS_DEFAULTS, ...config };
      if (!["chip", "chip_target", "dot"].includes(c.style)) c.style = "chip";
      if (!["valve", "sensor", "none"].includes(c.tap_action)) c.tap_action = "valve";
      this._config = c;
      this._sig = null;
      this._render();
    }

    getCardSize() { return 1 + Math.floor((this._data ? this._data.rooms.length : 6) / 8); }

    _summary(data) {
      const h = this._hass, on = boilerOn(data.boiler);
      const calling = data.rooms.filter((r) => r.on).length;
      const val = on ? `${esc(T(h, "sum_on"))} · ${calling}/${data.rooms.length}` : esc(T(h, "sum_off"));
      const col = on ? "var(--c-demand)" : "var(--c-off)";
      const tap = this._tapOn() && data.boilerId ? `data-entity="${esc(data.boilerId)}"` : "";
      if (this._config.style === "dot") {
        return `<span class="dtc${on ? " hot" : ""}" style="--c:${col}" ${tap}><i></i><span>${esc(T(h, "boiler"))}</span><b>${val}</b></span>`;
      }
      return `<span class="cp sum${on ? "" : " off"}${on ? " hot" : ""}" style="--c:${col}" ${tap}><span class="ri">${ic("flame")}</span><span class="pn">${esc(T(h, "boiler"))}</span><span class="pv">${val}</span></span>`;
    }

    _build(data) {
      const c = this._config, d = Number(c.decimals) || 0;
      if (!data.rooms.length) return `<div class="msg">${esc(T(this._hass, "no_rooms"))}</div>`;
      const sum = c.show_summary && data.boiler ? this._summary(data) : "";
      if (c.style === "dot") {
        return `<div class="zm"><div class="dts">${sum}${data.rooms.map((r) =>
          `<span class="dtc${isHot(r) ? " hot" : ""}" data-st="${r.status}" ${this._tapAttr(r)}><i></i><span>${esc(r.name)}</span><b>${this._num(r.cur, d)}°</b></span>`).join("")}</div></div>`;
      }
      const withTarget = c.style === "chip_target";
      return `<div class="zm"><div class="cps">${sum}${data.rooms.map((r) =>
        `<span class="cp${isHot(r) ? " hot" : ""}" data-st="${r.status}" ${this._tapAttr(r)}><span class="ri">${ic(STATUS_ICON[r.status])}</span><span class="pn">${esc(r.name)}</span><span class="pv">${this._num(r.cur, d)}°</span>${withTarget && r.target != null ? `<span class="pt">${ic("flat")}${this._num(r.target, d)}°</span>` : ""}</span>`).join("")}</div></div>`;
    }
  }

  /* ===================================================================
   *  Vizuális szerkesztők (ha-form alapú) – egy gyár, négy kártyához
   * =================================================================== */
  const B = (name) => ({ name, selector: { boolean: {} } });
  const colorFields = () => COLOR_KEYS.map((k) => ({ name: "color_" + k, selector: { color_rgb: {} } }));
  const numBox = (name, min, max, step, unit) => ({ name, selector: { number: { min, max, step, mode: "box", ...(unit ? { unit_of_measurement: unit } : {}) } } });
  const numSlider = (name, min, max, step, unit) => ({ name, selector: { number: { min, max, step, mode: "slider", ...(unit ? { unit_of_measurement: unit } : {}) } } });
  const look = () => [
    numSlider("radius", 0, 40, 1, "px"), numSlider("opacity", 0, 100, 1, "%"), numSlider("blur", 0, 30, 1, "px"),
  ];
  const tapSelect = (ed) => ({ name: "tap_action", selector: { select: { mode: "dropdown", options: ["valve", "sensor", "none"].map((v) => ({ value: v, label: ed._label("ta_" + v) })) } } });
  const decimalsSelect = () => ({ name: "decimals", selector: { select: { mode: "dropdown", options: [{ value: "0", label: "0" }, { value: "1", label: "1" }, { value: "2", label: "2" }] } } });

  /** A szerkesztő mezőiben a kijelzett érték (alapértékek + a felhasználó beállításai). */
  function plainDisplay(defaults, cfg) {
    const c = { ...defaults, ...cfg };
    if (!Array.isArray(c.rooms)) c.rooms = [];
    if (c.decimals !== undefined) c.decimals = String(c.decimals);
    if (c.hours !== undefined) c.hours = String(c.hours);
    if (c.days !== undefined) c.days = String(c.days);
    return c;
  }

  /** A mentett beállításból kiszedi az üres / felesleges értékeket. */
  function plainEmit(value) {
    const v = { ...value };
    if (v.decimals !== undefined) v.decimals = Number(v.decimals);
    if (v.hours !== undefined) v.hours = Number(v.hours);
    if (v.days !== undefined) v.days = Number(v.days);
    Object.keys(v).forEach((k) => { if (v[k] === undefined || v[k] === null || v[k] === "") delete v[k]; });
    ["rooms", "quick_presets"].forEach((k) => { if (Array.isArray(v[k]) && !v[k].length) delete v[k]; });
    return v;
  }

  function makeEditor(opts) {
    return class extends HTMLElement {
      constructor() {
        super();
        this.attachShadow({ mode: "open" });
        this._config = { ...opts.defaults };
        this._built = false;
      }

      setConfig(config) {
        this._config = { ...config };
        this._update();
      }

      set hass(hass) {
        this._hass = hass;
        this._update();
      }

      connectedCallback() { this._update(); }

      _label(name) { return T(this._hass, name); }

      _roomOptions() {
        const states = (this._hass && this._hass.states) || {};
        return Object.values(states).filter(isRoom)
          .map((s) => ({ value: s.entity_id, label: s.attributes.room_name || s.attributes.friendly_name || s.entity_id }))
          .sort((a, b) => a.label.localeCompare(b.label, langOf(this._hass)));
      }

      /** A szelepek által ismert profilok (a gyorsgomb listához). */
      _presetOptions() {
        const states = (this._hass && this._hass.states) || {};
        const seen = [];
        Object.values(states).filter(isRoom).forEach((s) => {
          (Array.isArray(s.attributes.valves) ? s.attributes.valves : []).forEach((id) => {
            const v = states[id];
            const list = v && v.attributes && Array.isArray(v.attributes.preset_modes) ? v.attributes.preset_modes : [];
            list.forEach((p) => { if (!seen.includes(String(p))) seen.push(String(p)); });
          });
        });
        return seen.map((p) => ({ value: p, label: STR.en["p_" + p.toLowerCase()] ? T(this._hass, "p_" + p.toLowerCase()) : p.charAt(0).toUpperCase() + p.slice(1).replace(/[_-]+/g, " ") }));
      }

      _display() { return opts.display ? opts.display(this._config) : plainDisplay(opts.defaults, this._config); }

      _emit(value) {
        const v = opts.emit ? opts.emit(value, this._config) : plainEmit(value);
        this._config = v;
        this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: v }, bubbles: true, composed: true }));
      }

      _build() {
        this._built = true;
        const style = document.createElement("style");
        style.textContent = `
          :host { display:block; }
          details { border:1px solid var(--divider-color, #444); border-radius:12px; margin:0 0 10px; overflow:hidden; }
          summary { cursor:pointer; padding:12px 14px; font-weight:600; background:color-mix(in srgb, var(--primary-text-color, #fff) 5%, transparent); }
          .body { padding:12px 14px 4px; }
          .hint { color:var(--secondary-text-color); font-size:.85rem; margin:0 0 10px; }
          button { margin:4px 0 12px; padding:8px 14px; border-radius:8px; border:1px solid var(--divider-color, #555);
            background:transparent; color:var(--primary-text-color); cursor:pointer; font:inherit; }
        `;
        this.shadowRoot.appendChild(style);
        this._wrap = document.createElement("div");
        this.shadowRoot.appendChild(this._wrap);
        this._forms = [];
      }

      _update() {
        if (!this._hass && !this.isConnected) return;
        if (!this._built) this._build();
        const sections = opts.sections(this);
        const data = this._display();
        if (!this._wrap.children.length) {
          sections.forEach((sec) => {
            const det = document.createElement("details");
            if (sec.open) det.open = true;
            const sum = document.createElement("summary");
            sum.dataset.key = sec.id;
            det.appendChild(sum);
            const body = document.createElement("div");
            body.className = "body";
            det.appendChild(body);
            const form = document.createElement("ha-form");
            form.addEventListener("value-changed", (ev) => { ev.stopPropagation(); this._emit(ev.detail.value); });
            body.appendChild(form);
            if (sec.reset) {
              const btn = document.createElement("button");
              btn.dataset.key = "reset_colors";
              btn.addEventListener("click", () => {
                const v = { ...this._config };
                COLOR_KEYS.forEach((k) => delete v["color_" + k]);
                this._config = v;
                this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: v }, bubbles: true, composed: true }));
                this._update();
              });
              body.appendChild(btn);
            }
            this._wrap.appendChild(det);
            this._forms.push({ form, sec });
          });
        }
        const helpers = opts.helpers || {};
        this._wrap.querySelectorAll("summary").forEach((s) => { s.textContent = this._label(s.dataset.key); });
        this._wrap.querySelectorAll("button").forEach((b) => { b.textContent = this._label(b.dataset.key); });
        this._forms.forEach(({ form }, i) => {
          form.hass = this._hass;
          form.data = data;
          form.schema = sections[i].schema;
          form.computeLabel = (s) => this._label((opts.labelKeys && opts.labelKeys[s.name]) || s.name);
          form.computeHelper = (s) => (helpers[s.name] ? this._label(helpers[s.name]) : "");
        });
        const noRooms = !this._roomOptions().length;
        let hint = this._wrap.querySelector(".hint");
        if (noRooms && !hint) {
          hint = document.createElement("p");
          hint.className = "hint";
          this._wrap.insertBefore(hint, this._wrap.firstChild);
        }
        if (hint) { if (noRooms) hint.textContent = this._label("editor_no_rooms"); else hint.remove(); }
      }
    };
  }

  const roomsField = (ed) => ({ name: "rooms", selector: { select: { multiple: true, mode: "list", options: ed._roomOptions() } } });
  const quickFields = (ed) => [B("show_quick"),
    { name: "quick_presets", selector: { select: { multiple: true, custom_value: true, mode: "list", options: ed._presetOptions() } } }];
  const COMMON_HELPERS = { rooms: "h_rooms", size: "h_size", quick_presets: "h_quick_presets", smooth: "h_smooth" };

  /* ---------- csempe kártya ---------- */
  const MerossBoilerSyncCardEditor = makeEditor({
    defaults: DEFAULTS,
    helpers: { ...COMMON_HELPERS, columns: "h_columns", gauge_min: "h_gauge", gauge_max: "h_gauge", step: "h_step",
      show_sparkline: "h_show_sparkline", drag_target: "h_drag_target", hold_action: "h_hold_action", look: "h_look", night_mode: "h_night_mode", heat_min: "h_heat", heat_max: "h_heat",
      glow_states: "h_glow_states", animation: "h_animation", temp_gradient: "h_temp_gradient", show_trend: "h_show_trend",
      show_countdown: "h_show_countdown" },
    sections: (ed) => [
      { id: "sec_general", open: true, schema: [
        { name: "design", selector: { select: { mode: "dropdown", options: DESIGNS.map((d) => ({ value: d, label: ed._label("d_" + d) })) } } },
        { name: "title", selector: { text: {} } },
        roomsField(ed),
        numBox("columns", 0, 8, 1),
        numSlider("size", 70, 160, 5, "%"),
        tapSelect(ed),
      ] },
      { id: "sec_controls", schema: [B("show_controls"), numBox("step", 0, 2, 0.1, "°C"), B("show_presets"), ...quickFields(ed)] },
      { id: "sec_effects", schema: [
        B("glow"), numSlider("glow_level", 1, 5, 1),
        { name: "glow_states", selector: { select: { multiple: true, mode: "list", options: GLOW_STATES.map((k) => ({ value: k, label: ed._label("st_" + k) })) } } },
        B("animation"), B("temp_gradient"), B("show_trend"), B("show_eta"), B("show_countdown"), B("smooth"),
      ] },
      { id: "sec_features", schema: [
        B("show_sparkline"), { name: "sparkline_hours", selector: { select: { mode: "dropdown", options: [6, 12, 24].map((x) => ({ value: String(x), label: ed._label("hr_" + x) })) } } },
        B("drag_target"),
        { name: "hold_action", selector: { select: { mode: "dropdown", options: HOLD_ACTIONS.map((x) => ({ value: x, label: ed._label("ha_" + x.replace("-", "_")) })) } } },
        { name: "look", selector: { select: { mode: "dropdown", options: LOOKS.map((x) => ({ value: x, label: ed._label("lk_" + x) })) } } },
        B("night_mode"), { name: "night_from", selector: { text: {} } }, { name: "night_to", selector: { text: {} } }, numSlider("night_dim", 30, 100, 5, "%"),
        numBox("heat_min", -20, 40, 0.5, "°C"), numBox("heat_max", -10, 60, 0.5, "°C"),
      ] },
      { id: "sec_show", schema: ["show_header", "show_boiler", "show_demand", "show_summer", "show_current", "show_target",
        "show_humidity", "show_deviation", "show_status", "show_flags"].map(B) },
      { id: "sec_values", schema: [
        numBox("gauge_min", -20, 40, 0.5, "°C"), numBox("gauge_max", -10, 60, 0.5, "°C"), decimalsSelect(), ...look(),
      ] },
      { id: "sec_colors", schema: colorFields(), reset: true },
    ],
    display: (cfg) => {
      const c = { ...DEFAULTS, ...cfg };
      if (!DESIGNS.includes(c.design)) c.design = "glass";
      const p = PRESET[c.design];
      ["radius", "opacity", "blur"].forEach((k) => { if (c[k] == null) c[k] = p[k]; });
      c.decimals = String(c.decimals);
      c.sparkline_hours = String(c.sparkline_hours);
      if (!Array.isArray(c.rooms)) c.rooms = [];
      if (!Array.isArray(c.quick_presets)) c.quick_presets = [];
      if (cfg.tap_action === undefined && cfg.tap_more_info === false) c.tap_action = "none";
      delete c.tap_more_info;
      if (!Array.isArray(c.glow_states)) c.glow_states = GLOW_DEFAULT.slice();
      return c;
    },
    emit: (value, old) => {
      const v = { ...value };
      v.decimals = Number(v.decimals);
      if (v.sparkline_hours !== undefined) v.sparkline_hours = Number(v.sparkline_hours);
      // ami az előző vagy az új dizájn alapértéke, az nem egyéni beállítás (dizájnváltáskor ne ragadjon be)
      const pNew = PRESET[DESIGNS.includes(v.design) ? v.design : "glass"];
      const pOld = PRESET[DESIGNS.includes(old.design) ? old.design : "glass"];
      ["radius", "opacity", "blur"].forEach((k) => { if (Number(v[k]) === pNew[k] || Number(v[k]) === pOld[k]) delete v[k]; });
      Object.keys(v).forEach((k) => { if (v[k] === undefined || v[k] === null || v[k] === "") delete v[k]; });
      ["rooms", "quick_presets"].forEach((k) => { if (Array.isArray(v[k]) && !v[k].length) delete v[k]; });
      delete v.tap_more_info;
      // az alapértelmezett állapotlista nem egyéni beállítás
      if (Array.isArray(v.glow_states) && v.glow_states.length === GLOW_DEFAULT.length && GLOW_DEFAULT.every((k) => v.glow_states.includes(k))) delete v.glow_states;
      return v;
    },
  });

  /* ---------- áttekintő kártya ---------- */
  const MerossBoilerSyncOverviewEditor = makeEditor({
    defaults: OVERVIEW_DEFAULTS,
    helpers: { ...COMMON_HELPERS, flow_animation: "h_flow_animation", ambience: "h_ambience" },
    sections: (ed) => [
      { id: "sec_general", open: true, schema: [
        { name: "title", selector: { text: {} } }, roomsField(ed), numSlider("size", 70, 160, 5, "%"), tapSelect(ed),
      ] },
      { id: "sec_blocks", schema: ["show_boiler", "show_outdoor", "show_summer", "show_rooms"].map(B) },
      { id: "sec_effects", schema: [B("flow_animation"), B("ambience"), B("smooth")] },
      { id: "sec_controls", schema: quickFields(ed) },
      { id: "sec_values", schema: [decimalsSelect(), ...look()] },
      { id: "sec_colors", schema: colorFields(), reset: true },
    ],
  });

  /* ---------- idővonal kártya ---------- */
  const MerossBoilerSyncTimelineEditor = makeEditor({
    defaults: TIMELINE_DEFAULTS,
    helpers: { ...COMMON_HELPERS },
    sections: (ed) => [
      { id: "sec_general", open: true, schema: [
        { name: "title", selector: { text: {} } }, roomsField(ed),
        { name: "hours", selector: { select: { mode: "dropdown", options: HISTORY_RANGES.map((x) => ({ value: String(x), label: ed._label("hr_" + x) })) } } },
        numSlider("size", 70, 160, 5, "%"), tapSelect(ed),
      ] },
      { id: "sec_show", schema: ["show_boiler_row", "show_total", "show_range", "show_legend"].map(B) },
      { id: "sec_effects", schema: [B("intro_animation")] },
      { id: "sec_values", schema: look() },
      { id: "sec_colors", schema: colorFields(), reset: true },
    ],
  });

  /* ---------- chip-sor kártya ---------- */
  const MerossBoilerSyncChipsEditor = makeEditor({
    defaults: CHIPS_DEFAULTS,
    helpers: { ...COMMON_HELPERS },
    sections: (ed) => [
      { id: "sec_general", open: true, schema: [
        { name: "style", selector: { select: { mode: "dropdown", options: ["chip", "chip_target", "dot"].map((v) => ({ value: v, label: ed._label("s_" + v) })) } } },
        roomsField(ed), numSlider("size", 70, 160, 5, "%"), tapSelect(ed),
      ] },
      { id: "sec_show", schema: [B("show_summary")] },
      { id: "sec_values", schema: [decimalsSelect(), ...look()] },
      { id: "sec_colors", schema: colorFields(), reset: true },
    ],
  });

  /* ---------- új kártyák (2.8) ---------- */
  const daysSelect = (list) => ({ name: "days", selector: { select: { mode: "dropdown", options: list.map((n) => ({ value: String(n), label: String(n) })) } } });
  const hoursSelect = (ed, list) => ({ name: "hours", selector: { select: { mode: "dropdown", options: list.map((x) => ({ value: String(x), label: ed._label("hr_" + x) })) } } });

  const MerossBoilerSyncWhyEditor = makeEditor({
    defaults: WHY_DEFAULTS,
    helpers: { ...COMMON_HELPERS },
    sections: (ed) => [
      { id: "sec_general", open: true, schema: [
        { name: "title", selector: { text: {} } }, roomsField(ed), numSlider("size", 70, 160, 5, "%"), tapSelect(ed),
      ] },
      { id: "sec_show", schema: [B("compact"), B("show_list"), numBox("max_rows", 1, 12, 1), B("show_notes"), B("show_countdown")] },
      { id: "sec_values", schema: [decimalsSelect(), ...look()] },
      { id: "sec_colors", schema: colorFields(), reset: true },
    ],
  });

  const MerossBoilerSyncAlertsEditor = makeEditor({
    defaults: ALERTS_DEFAULTS,
    helpers: { ...COMMON_HELPERS, show_when_ok: "h_show_when_ok", window_minutes: "h_window_minutes" },
    sections: (ed) => [
      { id: "sec_general", open: true, schema: [
        { name: "title", selector: { text: {} } }, roomsField(ed), numSlider("size", 70, 160, 5, "%"), tapSelect(ed),
      ] },
      { id: "sec_alerts", schema: [B("alert_stale"), B("alert_unavailable"), B("alert_window"), numBox("window_minutes", 1, 240, 1, "min"), B("alert_max_boost"), B("alert_cycling")] },
      { id: "sec_show", schema: [B("compact"), B("show_when_ok"), B("show_cycles")] },
      { id: "sec_values", schema: look() },
      { id: "sec_colors", schema: colorFields(), reset: true },
    ],
  });

  const MerossBoilerSyncRoomEditor = makeEditor({
    defaults: ROOM_DEFAULTS,
    helpers: { ...COMMON_HELPERS, show_trend: "h_show_trend", show_countdown: "h_show_countdown", step: "h_step", gauge_min: "h_gauge", gauge_max: "h_gauge" },
    sections: (ed) => [
      { id: "sec_general", open: true, schema: [
        { name: "room", selector: { select: { mode: "dropdown", options: ed._roomOptions() } } },
        { name: "title", selector: { text: {} } },
        hoursSelect(ed, [6, 12, 24]),
        numSlider("size", 70, 160, 5, "%"), tapSelect(ed),
      ] },
      { id: "sec_show", schema: [B("show_chart"), B("show_valves"), B("show_trend"), B("show_eta"), B("show_countdown"), B("smooth")] },
      { id: "sec_controls", schema: [B("show_controls"), numBox("step", 0, 2, 0.1, "°C"), B("show_presets")] },
      { id: "sec_values", schema: [numBox("gauge_min", -20, 40, 0.5, "°C"), numBox("gauge_max", -10, 60, 0.5, "°C"), decimalsSelect(), ...look()] },
      { id: "sec_colors", schema: colorFields(), reset: true },
    ],
  });

  const MerossBoilerSyncHeatmapEditor = makeEditor({
    defaults: HEATMAP_DEFAULTS,
    helpers: { ...COMMON_HELPERS },
    sections: (ed) => [
      { id: "sec_general", open: true, schema: [
        { name: "title", selector: { text: {} } },
        { name: "entity", selector: { select: { mode: "dropdown", options: [{ value: "boiler", label: ed._label("boiler") }].concat(ed._roomOptions()) } } },
        daysSelect([7, 14]), roomsField(ed), numSlider("size", 70, 160, 5, "%"),
      ] },
      { id: "sec_show", schema: [B("show_selector"), B("show_summary")] },
      { id: "sec_values", schema: look() },
      { id: "sec_colors", schema: colorFields(), reset: true },
    ],
  });

  const MerossBoilerSyncStatsEditor = makeEditor({
    defaults: STATS_DEFAULTS,
    helpers: { ...COMMON_HELPERS, show_cost: "h_show_cost", gas_m3_per_hour: "h_gas", gas_price: "h_gas_price" },
    labelKeys: { show_outdoor: "show_outdoor_stat", show_rooms: "show_rooms_stat" },
    sections: (ed) => [
      { id: "sec_general", open: true, schema: [
        { name: "title", selector: { text: {} } }, daysSelect([7, 14, 30]), roomsField(ed), numSlider("size", 70, 160, 5, "%"),
      ] },
      { id: "sec_show", schema: [B("show_outdoor"), B("show_rooms"), B("show_cycles")] },
      { id: "sec_cost", schema: [B("show_cost"), numBox("gas_m3_per_hour", 0, 20, 0.1, "m³/h"), numBox("gas_price", 0, 100000, 1), { name: "currency", selector: { text: {} } }] },
      { id: "sec_values", schema: look() },
      { id: "sec_colors", schema: colorFields(), reset: true },
    ],
  });

  /* ===================================================================
   *  Regisztráció
   * =================================================================== */
  // ha a fájl valamiért kétszer fut le (pl. kézi erőforrás + automatikus), az ne okozzon hibát
  const define = (tag, cls) => {
    try { if (!customElements.get(tag)) customElements.define(tag, cls); }
    catch (err) { console.warn("[meross-boiler-sync-card] " + tag + ":", err); }
  };
  define(TAG, MerossBoilerSyncCard);
  define(EDITOR_TAG, MerossBoilerSyncCardEditor);
  define(OVERVIEW_TAG, MerossBoilerSyncOverviewCard);
  define(OVERVIEW_TAG + "-editor", MerossBoilerSyncOverviewEditor);
  define(TIMELINE_TAG, MerossBoilerSyncTimelineCard);
  define(TIMELINE_TAG + "-editor", MerossBoilerSyncTimelineEditor);
  define(CHIPS_TAG, MerossBoilerSyncChipsCard);
  define(CHIPS_TAG + "-editor", MerossBoilerSyncChipsEditor);
  define(WHY_TAG, MerossBoilerSyncWhyCard);
  define(WHY_TAG + "-editor", MerossBoilerSyncWhyEditor);
  define(ROOM_TAG, MerossBoilerSyncRoomCard);
  define(ROOM_TAG + "-editor", MerossBoilerSyncRoomEditor);
  define(HEATMAP_TAG, MerossBoilerSyncHeatmapCard);
  define(HEATMAP_TAG + "-editor", MerossBoilerSyncHeatmapEditor);
  define(STATS_TAG, MerossBoilerSyncStatsCard);
  define(STATS_TAG + "-editor", MerossBoilerSyncStatsEditor);
  define(ALERTS_TAG, MerossBoilerSyncAlertsCard);
  define(ALERTS_TAG + "-editor", MerossBoilerSyncAlertsEditor);

  window.customCards = window.customCards || [];
  const hu = (navigator.language || "").toLowerCase().startsWith("hu");
  const L = (k) => (hu ? STR.hu : STR.en)[k];
  [
    { type: TAG, name: "Meross Boiler Sync", description: L("description") },
    { type: OVERVIEW_TAG, name: L("card_overview"), description: L("desc_overview") },
    { type: TIMELINE_TAG, name: L("card_timeline"), description: L("desc_timeline") },
    { type: CHIPS_TAG, name: L("card_chips"), description: L("desc_chips") },
    { type: WHY_TAG, name: L("card_why"), description: L("desc_why") },
    { type: ROOM_TAG, name: L("card_room"), description: L("desc_room") },
    { type: HEATMAP_TAG, name: L("card_heatmap"), description: L("desc_heatmap") },
    { type: STATS_TAG, name: L("card_stats"), description: L("desc_stats") },
    { type: ALERTS_TAG, name: L("card_alerts"), description: L("desc_alerts") },
  ].forEach((card) => {
    if (!window.customCards.some((c) => c && c.type === card.type)) window.customCards.push({ ...card, preview: true });
  });
})();

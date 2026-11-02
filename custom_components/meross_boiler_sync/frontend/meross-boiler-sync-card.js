/*!
 * Meross Boiler Sync – Lovelace kártyák / Lovelace cards
 * Verzió / version: 2.7.0
 *
 * Felvétel: Irányítópult szerkesztése → Kártya hozzáadása → "Meross Boiler Sync".
 * Add: Edit dashboard → Add card → "Meross Boiler Sync".
 *
 * Kártyák / cards:
 *   type: custom:meross-boiler-sync-card            (csempék / tiles: glass, radiator, minimal, gradient, list)
 *   type: custom:meross-boiler-sync-overview-card   (áttekintő / overview)
 *   type: custom:meross-boiler-sync-timeline-card   (fűtési idővonal / heating timeline)
 *   type: custom:meross-boiler-sync-chips-card      (chip-sor / chip row)
 */
(() => {
  "use strict";
  const TAG = "meross-boiler-sync-card";
  const EDITOR_TAG = "meross-boiler-sync-card-editor";
  const OVERVIEW_TAG = "meross-boiler-sync-overview-card";
  const TIMELINE_TAG = "meross-boiler-sync-timeline-card";
  const CHIPS_TAG = "meross-boiler-sync-chips-card";
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
   *  Alapértékek, dizájn előbeállítások, színek
   * =================================================================== */
  const DESIGNS = ["glass", "radiator", "minimal", "gradient", "list"];
  const DEFAULTS = {
    design: "glass", title: "", rooms: [], columns: 0, size: 100, tap_action: "valve",
    show_controls: true, step: 0, show_presets: true, show_quick: false,
    glow: true, glow_level: 3, animation: false,
    temp_gradient: false, show_trend: true, show_eta: true, show_countdown: true, smooth: true,
    show_header: true, show_boiler: true, show_demand: true, show_summer: true,
    show_current: true, show_target: true, show_humidity: true, show_deviation: true,
    show_status: true, show_flags: true,
    gauge_min: 15, gauge_max: 28, decimals: 1,
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
        id: v.entity_id, state: v.state,
        preset: v.attributes.preset_mode == null ? null : String(v.attributes.preset_mode),
        presets: Array.isArray(v.attributes.preset_modes) ? v.attributes.preset_modes.map(String) : [],
        min: num(v.attributes.min_temp), max: num(v.attributes.max_temp), step: num(v.attributes.target_temp_step),
        ok: v.state !== "unavailable" && v.state !== "unknown" && v.state !== "off",
      });
      const valves = vs.map(mkValve);
      const valve = valves.find((x) => x.state !== "unavailable" && x.state !== "unknown") || valves[0] || null;
      return {
        id: s.entity_id, on, a, valve, valves,
        valveIds: vs.map((x) => x.entity_id),
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
    return { rooms, summer, boiler: boilerId ? states[boilerId] || null : null, boilerId };
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
      v = Math.round(clamp(v, lo, hi) * 100) / 100;
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

    _render() {
      if (!this._config || !this._hass) return;
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
      this.shadowRoot.innerHTML = `<style>${CSS}</style><div class="root" style="${this._vars(cfg)};--sz:${sz}">${this._build(data)}</div>`;
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
   *  Csempe kártya: glass, radiator, minimal, gradient, list
   * =================================================================== */
  class MerossBoilerSyncCard extends MbsBase {
    static getConfigElement() { return document.createElement(EDITOR_TAG); }
    static getStubConfig() { return { design: "glass" }; }

    setConfig(config) {
      if (!config) throw new Error("Hiányzó konfiguráció / missing configuration");
      const c = { ...DEFAULTS, ...config };
      if (!DESIGNS.includes(c.design)) c.design = "glass";
      // régi (2.5) beállítás: tap_more_info: false  ->  tap_action: none
      if (config.tap_action === undefined && config.tap_more_info === false) c.tap_action = "none";
      if (!["valve", "sensor", "none"].includes(c.tap_action)) c.tap_action = "valve";
      this._config = c;
      this._sig = null;
      this._render();
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
      return `<span class="chip">${ic(STATUS_ICON[r.status])}${esc(T(this._hass, key))}</span>`;
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
        let marker = "", defs = "", stroke = "var(--c)";
        if (c.temp_gradient && r.cur != null) {
          const gid = "tg" + (this._gn = (this._gn || 0) + 1);
          defs = `<defs><linearGradient id="${gid}" gradientUnits="userSpaceOnUse" x1="24.6" y1="0" x2="95.4" y2="0">${gradientStops()}</linearGradient></defs>`;
          stroke = `url(#${gid})`;
        }
        if (ft != null && (c.show_target || showCtl)) {
          const [mx, my] = pointOn(60, 60, 50, ft);
          marker = `<circle data-role="mk" cx="${mx.toFixed(2)}" cy="${my.toFixed(2)}" r="4.5" fill="var(--text)" stroke="var(--surface)" stroke-width="2"/>`;
        }
        const tg = showTg ? `<div class="tg">${esc(T(h, "target"))}<b>${this._num(target, d)}°</b></div>` : "<span></span>";
        visual = `<div class="ring">
            <svg viewBox="0 0 120 120">${defs}<path d="${arcPath(60, 60, 50, 1)}" fill="none" stroke="var(--track)" stroke-width="9" stroke-linecap="round"/>
              ${r.cur != null ? `<path data-role="arc" d="${arcPath(60, 60, 50, Math.max(f, 0.001))}" fill="none" stroke="${stroke}" stroke-width="9" stroke-linecap="round"/>` : ""}${marker}</svg>
            <div class="mid">${big}</div>
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
      const fx = c.animation ? (rd ? FX_RADIATOR[r.status] : FX[r.status]) || "" : "";
      return `<div class="t glass${rd ? " rd" : ""}${rd && c.animation ? " anim" : ""} ${this._glowCls(r)}" data-st="${r.status}" data-room="${esc(r.id)}" ${this._tapAttr(r)}>
        ${fx}
        <div class="in">
          <div class="nm">${esc(r.name)}</div>
          ${visual}
          <div class="info">${info}</div>
          ${this._trendRow(r)}
          ${status || pre ? `<div class="foot">${status}${pre}${menu}</div>` : ""}
        </div>
      </div>`;
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
        ${this._bar(r)}
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
        const tile = { glass: "_tileGlass", radiator: "_tileGlass", minimal: "_tileMinimal", gradient: "_tileGradient" }[cfg.design];
        const minw = { glass: 250, radiator: 250, minimal: 300, gradient: 235 }[cfg.design];
        body = `<div class="grid" style="${Number(cfg.columns) > 0 ? "" : `grid-template-columns:repeat(auto-fill,minmax(min(100%,${minw}px),1fr))`}">${data.rooms.map((r) => this[tile](r)).join("")}</div>`;
      }
      return `${hdr}${this._quickHtml(data.rooms)}<div class="zm">${body}</div>`;
    }

    /** Sima átmenetek: a gyűrű / sáv / szám az új értékre úszik, nem ugrik. */
    _after() {
      const root = this.shadowRoot, c = this._config, d = Number(c.decimals) || 0;
      const min = Number(c.gauge_min), span = Math.max(1, Number(c.gauge_max) - min);
      root.querySelectorAll("[data-room].t.glass").forEach((el) => {
        const r = this._room(el.dataset.room);
        if (!r) return;
        const arc = el.querySelector('[data-role="arc"]'), mk = el.querySelector('[data-role="mk"]'), big = el.querySelector('[data-role="big"]');
        if (!arc && !big) return;
        const pend = this._pending[r.id];
        const tgt = pend ? pend.value : r.target;
        this._tween(r.id, { cur: r.cur == null ? null : r.cur, tgt: tgt == null ? null : tgt }, (v) => {
          if (arc && v.cur != null) arc.setAttribute("d", arcPath(60, 60, 50, Math.max((v.cur - min) / span, 0.001)));
          if (mk && v.tgt != null) {
            const [x, y] = pointOn(60, 60, 50, (v.tgt - min) / span);
            mk.setAttribute("cx", x.toFixed(2));
            mk.setAttribute("cy", y.toFixed(2));
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
    return c;
  }

  /** A mentett beállításból kiszedi az üres / felesleges értékeket. */
  function plainEmit(value) {
    const v = { ...value };
    if (v.decimals !== undefined) v.decimals = Number(v.decimals);
    if (v.hours !== undefined) v.hours = Number(v.hours);
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
          form.computeLabel = (s) => this._label(s.name);
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

  window.customCards = window.customCards || [];
  const hu = (navigator.language || "").toLowerCase().startsWith("hu");
  const L = (k) => (hu ? STR.hu : STR.en)[k];
  [
    { type: TAG, name: "Meross Boiler Sync", description: L("description") },
    { type: OVERVIEW_TAG, name: L("card_overview"), description: L("desc_overview") },
    { type: TIMELINE_TAG, name: L("card_timeline"), description: L("desc_timeline") },
    { type: CHIPS_TAG, name: L("card_chips"), description: L("desc_chips") },
  ].forEach((card) => {
    if (!window.customCards.some((c) => c && c.type === card.type)) window.customCards.push({ ...card, preview: true });
  });
})();

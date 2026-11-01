/*!
 * Meross Boiler Sync – Lovelace kártya / Lovelace card
 * Verzió / version: 2.6.2
 */
(() => {
  "use strict";
  const TAG = "meross-boiler-sync-card";
  const EDITOR_TAG = "meross-boiler-sync-card-editor";
  if (customElements.get(TAG)) return;

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
      sec_general: "General", sec_show: "What to show", sec_values: "Values and look", sec_colors: "Colors",
      design: "Design", d_glass: "Glass – ring gauge", d_minimal: "Minimal – compact rows",
      d_gradient: "Gradient tiles", d_list: "List – table with bar",
      title: "Title (optional)", rooms: "Rooms to show",
      h_rooms: "Leave empty to show all rooms. The order is the order you pick them in.",
      columns: "Columns", h_columns: "0 = automatic (fits the card width)",
      tap_more_info: "Open details on tap",
      show_header: "Show header", show_boiler: "Boiler state", show_demand: "Number of rooms calling for heat",
      show_summer: "Summer mode and outdoor temperature", show_current: "Current temperature",
      show_target: "Target temperature", show_humidity: "Humidity", show_deviation: "Deviation from target",
      show_status: "Status chip", show_flags: "Flags (valve control, link, dry run)",
      show_controls: "Valve temperature controls (+/-)", show_presets: "Preset profiles",
      show_glow: "Glow effect", show_animations: "Animated glass design",
      gauge_min: "Gauge minimum (°C)", gauge_max: "Gauge maximum (°C)", decimals: "Decimals",
      radius: "Corner radius (px)", opacity: "Background opacity (%)", blur: "Background blur (px)",
      h_gauge: "The ring / bar scale", reset_colors: "Reset colors",
      color_idle: "Color: not calling", color_demand: "Color: calling for heat", color_boost: "Color: valve forced open",
      color_waiting: "Color: waiting", color_rest: "Color: resting", color_stale: "Color: stale sensor",
      color_window: "Color: window open", color_off: "Color: valve off", color_summer: "Color: summer mode",
      editor_no_rooms: "No Meross Boiler Sync rooms found yet – the room list will fill in once they exist.",
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
      design: "Dizájn", d_glass: "Üveg – gyűrűs mérő", d_minimal: "Minimál – kompakt sorok",
      d_gradient: "Színátmenetes csempék", d_list: "Lista – táblázat sávval",
      title: "Cím (opcionális)", rooms: "Megjelenítendő szobák",
      h_rooms: "Üresen hagyva az összes szoba megjelenik. A sorrend a kiválasztás sorrendje.",
      columns: "Oszlopok száma", h_columns: "0 = automatikus (a kártya szélességéhez igazodik)",
      tap_more_info: "Érintésre részletek megnyitása",
      show_header: "Fejléc megjelenítése", show_boiler: "Kazán állapota", show_demand: "Hőt kérő szobák száma",
      show_summer: "Nyári mód és kinti hőmérséklet", show_current: "Aktuális hőmérséklet",
      show_target: "Célhőmérséklet", show_humidity: "Páratartalom", show_deviation: "Eltérés a céltól",
      show_status: "Állapotcímke", show_flags: "Jelzők (szelepvezérlés, kötés, próbaüzem)",
      show_controls: "Szelep hőmérséklet szabályzás (+/-)", show_presets: "Profilok (preset-ek) megjelenítése",
      show_glow: "Glow (izzás) hatás", show_animations: "Animált üveg dizájn",
      gauge_min: "Mérő alsó értéke (°C)", gauge_max: "Mérő felső értéke (°C)", decimals: "Tizedesjegyek",
      radius: "Sarkok lekerekítése (px)", opacity: "Háttér átlátszatlansága (%)", blur: "Háttér elmosása (px)",
      h_gauge: "A gyűrű / sáv skálája", reset_colors: "Színek visszaállítása",
      color_idle: "Szín: nem kér hőt", color_demand: "Szín: hőt kér", color_boost: "Szín: szelep kinyitva",
      color_waiting: "Szín: vár", color_rest: "Szín: pihenő", color_stale: "Szín: elavult szenzor",
      color_window: "Szín: ablak nyitva", color_off: "Szín: szelep ki", color_summer: "Szín: nyári mód",
      editor_no_rooms: "Még nincs Meross Boiler Sync szoba – a szobalista akkor töltődik fel, ha lesznek.",
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

  const DESIGNS = ["glass", "minimal", "gradient", "list"];
  const DEFAULTS = {
    design: "glass", title: "", rooms: [], columns: 0, tap_more_info: true,
    show_header: true, show_boiler: true, show_demand: true, show_summer: true,
    show_current: true, show_target: true, show_humidity: true, show_deviation: true,
    show_status: true, show_flags: true,
    show_controls: true, show_presets: false, show_glow: true, show_animations: true,
    gauge_min: 15, gauge_max: 28, decimals: 1,
  };
  const PRESET = {
    glass: { radius: 24, opacity: 55, blur: 14 },
    minimal: { radius: 16, opacity: 40, blur: 0 },
    gradient: { radius: 24, opacity: 100, blur: 0 },
    list: { radius: 14, opacity: 45, blur: 8 },
  };
  const COLOR_KEYS = ["idle", "demand", "boost", "waiting", "rest", "stale", "window", "off", "summer"];
  const DEFAULT_COLORS = {
    idle: [102, 187, 106], demand: [255, 152, 0], boost: [255, 87, 34], waiting: [255, 202, 40],
    rest: [100, 181, 246], stale: [239, 83, 80], window: [79, 195, 247], off: [130, 140, 150],
    summer: [255, 213, 79],
  };

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function cssColor(value, alpha) {
    const a = alpha == null ? 1 : alpha;
    let rgb = null;
    if (Array.isArray(value) && value.length >= 3) rgb = value.slice(0, 3).map((n) => clamp(Math.round(Number(n) || 0), 0, 255));
    else if (typeof value === "string" && /^#[0-9a-f]{6}$/i.test(value.trim())) {
      const h = value.trim().slice(1);
      rgb = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
    }
    if (rgb) return a >= 1 ? `rgb(${rgb[0]},${rgb[1]},${rgb[2]})` : `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${a})`;
    if (typeof value === "string" && value) return a >= 1 ? value : `color-mix(in srgb, ${value}${Math.round(a * 100)}%, transparent)`;
    return "transparent";
  }

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
    plus: '<path d="M12 5v14M5 12h14"/>',
    minus: '<path d="M5 12h14"/>',
  };
  const ic = (name, cls) => `<svg class="ic ${cls || ""}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] \vert{}\vert{} ""}</svg>`; const STATUS_ICON = { idle: "thermo", demand: "flame", boost: "valve", waiting: "clock", rest: "pause", stale: "alert", window: "window", windowpend: "window", off: "power", };  const isRoom = (s) => !!(s && s.entity_id && s.entity_id.startsWith("binary_sensor.") && s.attributes && "room_below_target" in s.attributes && "valves" in s.attributes); const isSummer = (s) => !!(s && s.entity_id && s.entity_id.startsWith("binary_sensor.") && s.attributes && "in_summer_period" in s.attributes);  function statusOf(a, on) { if (a.temperature_sensor_stale) return "stale"; if (a.window_open) return "window"; if (a.window_open_pending) return "windowpend"; if (a.valve_boosted) return "boost"; if (a.valve_boost_resting) return "rest"; if (a.valve_boost_waiting) return "waiting"; if (on) return "demand"; if (a.valve_active === false) return "off"; return "idle"; }  function collect(hass, cfg) { const states = (hass && hass.states) \vert{}\vert{} {}; let list; if (cfg.rooms && cfg.rooms.length) list = cfg.rooms.map((id) => states[id]).filter(isRoom); else { const lang = langOf(hass); list = Object.values(states).filter(isRoom).sort((x, y) => String(x.attributes.room_name \vert{}\vert{} x.attributes.friendly_name).localeCompare(String(y.attributes.room_name \vert{}\vert{} y.attributes.friendly_name), lang)); } const summer = Object.values(states).find(isSummer) \vert{}\vert{} null; const boilerId = (summer && summer.attributes.boiler_entity) \vert{}\vert{} cfg.boiler \vert{}\vert{} null; const rooms = list.map((s) => { const a = s.attributes; const on = s.state === "on"; const valves = a.valves \vert{}\vert{} []; const firstValveState = valves.length ? states[valves[0]] : null; return { id: s.entity_id, on, a, valves, firstValveState, name: a.room_name \vert{}\vert{} a.friendly_name \vert{}\vert{} s.entity_id, status: statusOf(a, on), cur: a.current_temperature == null ? null : Number(a.current_temperature), target: a.target_temperature == null ? null : Number(a.target_temperature), hum: a.humidity == null ? null : Number(a.humidity), dev: a.deviation == null ? null : Number(a.deviation), }; }); return { rooms, summer, boiler: boilerId ? states[boilerId] \vert{}\vert{} null : null, boilerId }; }  function arcPath(cx, cy, r, f) { const a0 = (135 * Math.PI) / 180; const sweep = 270 * clamp(f, 0, 1); const a1 = ((135 + sweep) * Math.PI) / 180; const x0 = cx + r * Math.cos(a0), y0 = cy + r * Math.sin(a0); const x1 = cx + r * Math.cos(a1), y1 = cy + r * Math.sin(a1); return `M ${x0.toFixed(2)} ${y0.toFixed(2)} A${r} ${r} 0${sweep > 180 ? 1 : 0} 1 ${x1.toFixed(2)}${y1.toFixed(2)}`;
  }
  function pointOn(cx, cy, r, f) {
    const ang = ((135 + 270 * clamp(f, 0, 1)) * Math.PI) / 180;
    return [cx + r * Math.cos(ang), cy + r * Math.sin(ang)];
  }

  const CSS = `
    :host { display:block; }
    * { box-sizing:border-box; }
    .root {
      --r: var(--mbs-radius, 24px);
      --op: var(--mbs-opacity, 55%);
      --blur: var(--mbs-blur, 14px);
      --surface: color-mix(in srgb, var(--card-background-color, #1c1c1e) var(--op), transparent);
      --border: color-mix(in srgb, var(--primary-text-color, #fff) 12%, transparent);
      --muted: var(--secondary-text-color, #9aa0a6);
      --text: var(--primary-text-color, #f2f2f2);
      --track: color-mix(in srgb, var(--primary-text-color, #fff) 14%, transparent);
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
    .pill[data-entity], .t[data-entity] { cursor:pointer; }
    .grid { display:grid; gap:16px; grid-template-columns:repeat(var(--cols), minmax(0,1fr)); }
    
    /* Csempe alapok és Glow réteg */
    .t { position:relative; border-radius:var(--r); background:var(--surface); border:1px solid var(--border);
      backdrop-filter:blur(var(--blur)); -

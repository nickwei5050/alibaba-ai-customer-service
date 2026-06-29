/**
 * products.ts — STARGO model catalog, synced from the Notion
 * "STARGO 产品知识库 / Product Catalog" database
 * (collection://a93053f6-0b1d-4b2d-8ea7-2b262111cde2).
 *
 * Last sync: 2026-06-29. 83 models enumerated from Notion via scoped search.
 * The catalog count is 84 (CATALOG_COUNT) per owner; one model is a `draft`
 * row not surfaced by semantic search — see PENDING_CONFIRMATION below.
 * Re-sync with the Notion MCP (SQL dump needs a Business plan) when models change.
 *
 * Specs (motor/voltage/range/top speed/load) are intentionally NOT duplicated
 * here — they live in Notion and must be confirmed per order. Use this file for
 * the product grid, routing, series filtering and internal links; pull full
 * specs from Notion / the per-model page when building each product page.
 */

export const CATALOG_COUNT = 84;

/** The 84th model was not returned by Notion semantic search (likely a draft). */
export const PENDING_CONFIRMATION =
  "1 model (84 total per owner vs 83 enumerated) — confirm the missing/draft model name in Notion.";

export type WheelType = "2-wheel" | "3-wheel" | "e-bike";

export type Series =
  | "Retro Scooter"
  | "Smart Commuter"
  | "Off-Road/Sport"
  | "Premium E-Motorcycle"
  | "Delivery & Cargo Scooter"
  | "E-Bike"
  | "Cargo Tricycle"
  | "Compact Pod"
  | "Standard Pod"
  | "Premium Pod";

export type Product = {
  name: string;
  slug: string;
  series: Series;
  wheels: WheelType;
  /** Short positioning line from the catalog (English). */
  tagline: string;
};

const slug = (s: string) =>
  s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");

const make = (
  name: string,
  series: Series,
  wheels: WheelType,
  tagline: string,
): Product => ({ name, slug: slug(name), series, wheels, tagline });

export const products: Product[] = [
  // ── Retro Scooter (12) ──────────────────────────────────────────────
  make("Rabbit", "Retro Scooter", "2-wheel", "Lemon-yellow retro smart scooter with dual NFC anti-theft."),
  make("Macaron", "Retro Scooter", "2-wheel", "5-color pastel retro scooter for fashion-forward urban markets."),
  make("MOONCHASE", "Retro Scooter", "2-wheel", "Ultra-light 52 kg retro scooter for women, students and beginners."),
  make("NOVA", "Retro Scooter", "2-wheel", "Anti-theft Italian-retro scooter for security-conscious markets."),
  make("U-RIDER", "Retro Scooter", "2-wheel", "52 kg lightweight dopamine-retro scooter for women and students."),
  make("Phantom", "Retro Scooter", "2-wheel", "Puncture-proof retro scooter for unpredictable road conditions."),
  make("LUNA", "Retro Scooter", "2-wheel", "1200W women's lifestyle retro with cloud-comfort seating."),
  make("Sunny", "Retro Scooter", "2-wheel", "Lightweight entry retro at the best price point; global best-seller."),
  make("Avatar", "Retro Scooter", "2-wheel", "72V 1500W retro with 14-inch wide tires and anti-theft — LatAm focus."),
  make("Atlas", "Retro Scooter", "2-wheel", "60V 1000W retro, 200 kg load, LED night visibility, 5 colors."),
  make("Chroma", "Retro Scooter", "2-wheel", "Cyber-retro camouflage design with GPS tracking and anti-theft."),
  make("PARIS", "Retro Scooter", "2-wheel", "Italian-retro 72V scooter with big under-seat storage."),

  // ── Smart Commuter (12) ─────────────────────────────────────────────
  make("JOVA", "Smart Commuter", "2-wheel", "GPS + NFC + IP-rated smart scooter for e-commerce and fleets."),
  make("Cowboy", "Smart Commuter", "2-wheel", "1200W graphene smart commuter optimized for e-commerce sellers."),
  make("CUBIX", "Smart Commuter", "2-wheel", "2500W / 72V smart commuter with flexible battery options."),
  make("Star Amber", "Smart Commuter", "2-wheel", "45 km/h NFC city commuter with TCS and black-orange cyber styling."),
  make("Warrior", "Smart Commuter", "2-wheel", "GPS + APP keyless smart scooter, 200 kg load."),
  make("Venice", "Smart Commuter", "2-wheel", "NFC keyless unlock, 12-inch wheels, dual-battery platform."),
  make("Warlord", "Smart Commuter", "2-wheel", "High-tech city commuter with 12-tube controller and 27-magnet motor."),
  make("Neon Shadow", "Smart Commuter", "2-wheel", "1200W smart scooter with TCS anti-slip and phone unlock."),
  make("Nebula", "Smart Commuter", "2-wheel", "Smart 1000W commuter (2000W peak) with sunlight-readable display."),
  make("STARGO X-Pro", "Smart Commuter", "2-wheel", "Smart commuter with reinforced rear cargo rack for daily utility."),
  make("Shadow Armor", "Smart Commuter", "2-wheel", "Black-white armored design, 2800W peak, 65 km/h, NFC."),
  make("Silver Armor", "Smart Commuter", "2-wheel", "Mecha 4G smart scooter with 55,000-cd headlight and battery swap."),

  // ── Off-Road / Sport (11) ───────────────────────────────────────────
  make("Titan", "Off-Road/Sport", "2-wheel", "3000W / 100 km/h / 64V 32Ah graphene — STARGO's strongest e-moto."),
  make("NINJA", "Off-Road/Sport", "2-wheel", "1000–1500W retro, 70 km/h, EEC COC certified."),
  make("King Kong", "Off-Road/Sport", "2-wheel", "1000W / 70 km/h / 260 kg load — rugged heavy-duty urban sport."),
  make("Vector", "Off-Road/Sport", "2-wheel", "1200W / 2600W peak / 72V 32Ah with front+rear disc, 75 km range."),
  make("Pulse", "Off-Road/Sport", "2-wheel", "800W DC brushless, 60V, 60 km range, 7 colors, dual disc."),
  make("Monolith", "Off-Road/Sport", "2-wheel", "400W / 60V 32Ah lithium, GBS linked brake, 25 km/h NSC-compliant."),
  make("Wolf Warrior", "Off-Road/Sport", "2-wheel", "250 kg heavy-duty load, 80 km range, 14-inch wheels, dual disc."),
  make("APEX", "Off-Road/Sport", "2-wheel", "48V 1000W, 200 kg load, front+rear disc, lightweight sport."),
  make("Pathfinder", "Off-Road/Sport", "2-wheel", "1000W / 60V lithium / 55 km/h retro-style urban commuter."),
  make("Rover", "Off-Road/Sport", "2-wheel", "1000W mecha-design sport scooter, GPS anti-theft, 60 km/h, EEC CE."),
  make("Defender", "Off-Road/Sport", "2-wheel", "72V 32Ah lithium / 3000W peak / 400 kg high-capacity hauler."),

  // ── Premium E-Motorcycle (10) ───────────────────────────────────────
  make("OBSIDIAN", "Premium E-Motorcycle", "2-wheel", "Flagship: 72V–120V, up to 8600W peak, up to 230 km range (per config)."),
  make("Shark", "Premium E-Motorcycle", "2-wheel", "Bionic shark cyber styling, 1200W / 72V 32Ah, unlockable to 60 km/h."),
  make("WINDRUNNER", "Premium E-Motorcycle", "2-wheel", "Premium urban e-motorcycle with refined metallic styling, 75 km."),
  make("VENUS", "Premium E-Motorcycle", "2-wheel", "Cyber-retro metallic-silver premium e-motorcycle, 70V/32Ah."),
  make("FALCON", "Premium E-Motorcycle", "2-wheel", "Cyber-mecha sport e-motorcycle, 1200W / 72V 32Ah, 55 km/h."),
  make("BLAZE", "Premium E-Motorcycle", "2-wheel", "Cyberpunk e-motorcycle, 72V 2500W peak, multi-shock, 120 km range."),
  make("VELORA", "Premium E-Motorcycle", "2-wheel", "Premium urban e-motorcycle, 2500W 72V 32Ah, triple storage."),
  make("HERO", "Premium E-Motorcycle", "2-wheel", "Aggressive mecha-styled lithium sport scooter for fast urban use."),
  make("AEGIS", "Premium E-Motorcycle", "2-wheel", "Armored e-motorcycle, 72V 2500W, guard-bar armor frame."),
  make("Urban Courier Pro", "Premium E-Motorcycle", "2-wheel", "2000W 12-inch high-speed delivery e-motorcycle."),

  // ── Delivery & Cargo Scooter — two-wheel (8) ────────────────────────
  make("Urban Ranger", "Delivery & Cargo Scooter", "2-wheel", "High-performance scooter built for safer braking and stronger structure."),
  make("BladeGo", "Delivery & Cargo Scooter", "2-wheel", "1500W peak delivery scooter, dual-layer 12-tube controller, linked disc."),
  make("BlueGuard", "Delivery & Cargo Scooter", "2-wheel", "1500W magnetic motor, 60V–72V, battery-swap delivery scooter."),
  make("LoadStar", "Delivery & Cargo Scooter", "2-wheel", "Heavy-duty utility scooter with front basket and 150 kg load."),
  make("SILVERWING", "Delivery & Cargo Scooter", "2-wheel", "72V 2500W long-frame scooter, 65–120 km range, rear storage box."),
  make("Iron Guard", "Delivery & Cargo Scooter", "2-wheel", "Delivery-grade lightweight cage frame with 25-tube guard rack."),
  make("Golden Bull II", "Delivery & Cargo Scooter", "2-wheel", "Heavy-duty cargo e-scooter, 72V 30-magnet motor, 300 kg."),
  make("TANK", "Delivery & Cargo Scooter", "2-wheel", "Heavy-duty 2000W retro (3100W peak), 75 km/h, fleet-grade."),

  // ── E-Bike (4) ──────────────────────────────────────────────────────
  make("CANDY", "E-Bike", "e-bike", "500W family utility e-bike with front basket."),
  make("Goldberry", "E-Bike", "e-bike", "500W dual-seat utility e-bike with large carrying capacity."),
  make("JUMBO", "E-Bike", "e-bike", "500W family e-bike, large front basket, wide twin seat, multi-battery."),
  make("FARREACH", "E-Bike", "e-bike", "500W safe low-speed commuter e-bike, 48V multi-battery, 100–150 kg."),

  // ── Cargo Tricycle (11) ─────────────────────────────────────────────
  make("IronRider Cargo", "Cargo Tricycle", "3-wheel", "Heavy-duty commercial cargo trike for high-frequency last-mile."),
  make("RedHaul Cargo", "Cargo Tricycle", "3-wheel", "72V 60Ah long-range cargo trike for high-frequency business use."),
  make("Redway Cargo", "Cargo Tricycle", "3-wheel", "72V 60Ah enclosed-cabin cargo trike for heavy-duty delivery."),
  make("Flame Cargo", "Cargo Tricycle", "3-wheel", "1200W high-torque trike for heavy-duty short-distance cargo."),
  make("CargoPod", "Cargo Tricycle", "3-wheel", "1200W semi-enclosed cabin, 72V 60Ah, 90–95 km range."),
  make("GROUNDTIGER", "Cargo Tricycle", "3-wheel", "600W / 60V–72V / 300 kg / 35° climb / IPX6 / manual dump box."),
  make("PICKUP TRICYCLE", "Cargo Tricycle", "3-wheel", "Intelligent 600W pickup trike with hydraulic cargo box, 60 km."),
  make("RIDGEVALE", "Cargo Tricycle", "3-wheel", "Enclosed 600W pickup trike with hydraulic dump cargo box."),
  make("STARGO Electric Cargo Tricycle", "Cargo Tricycle", "3-wheel", "Enclosed-cabin all-weather cargo trike (快递王), 300 kg, 60–100 km."),
  make("Golden Bull III", "Cargo Tricycle", "3-wheel", "Heavy-duty cargo trike, 45-magnet mid-mount differential motor."),
  make("Golden Bull GB6", "Cargo Tricycle", "3-wheel", "Heavy-duty cargo trike (金牛六代), 270 N·m, dual-layer frame."),

  // ── Compact Pod — passenger tricycle (8) ────────────────────────────
  make("Lumina", "Compact Pod", "3-wheel", "Panda-inspired canopy trike, 600W, 60 km+, 300 kg payload."),
  make("Mocha", "Compact Pod", "3-wheel", "Smart sunshade trike, 600W, 60 km, tri-brake, leather seat."),
  make("Panda GO", "Compact Pod", "3-wheel", "OEM-ready family canopy trike, 3-seater with hidden child seat."),
  make("Pudding", "Compact Pod", "3-wheel", "All-weather canopy trike, 300 kg payload, 600W."),
  make("Sweet Puff", "Compact Pod", "3-wheel", "Mini Pudding trike, 600W, 60 km, hidden child seat, 300 kg."),
  make("CoCo Pod", "Compact Pod", "3-wheel", "600W canopy + wiper trike, 300 kg payload."),
  make("Amber", "Compact Pod", "3-wheel", "600W fully enclosed cabin, roof rack, 300 kg payload, 60 km+."),
  make("Bella", "Compact Pod", "3-wheel", "Lithium-powered compact trike, 300 kg payload, dual variants."),

  // ── Standard Pod — passenger tricycle (4) ───────────────────────────
  make("JOYride", "Standard Pod", "3-wheel", "Retro-style 600W trike with rear storage box, 300 kg load."),
  make("Oasis", "Standard Pod", "3-wheel", "Intelligent passenger trike with smart display and anti-theft."),
  make("Zephyr", "Standard Pod", "3-wheel", "Cute Bear Series enclosed trike for family and community use."),
  make("BlissWay", "Standard Pod", "3-wheel", "600W family trike, canopy + windshield, 300 kg."),

  // ── Premium Pod — passenger tricycle (3) ────────────────────────────
  make("Aero", "Premium Pod", "3-wheel", "600W enclosed trike, anti-collision beam, explosion-proof tires."),
  make("Veloce Air", "Premium Pod", "3-wheel", "6-color IPX6 family trike with wiper and integrated canopy."),
  make("TimeCatcher", "Premium Pod", "3-wheel", "60 km/h+ enclosed trike, 300 kg load — premium lifestyle commuter."),
];

/** Group products by series for grid/filter UIs. */
export const productsBySeries = products.reduce<Record<string, Product[]>>((acc, p) => {
  (acc[p.series] ??= []).push(p);
  return acc;
}, {});

/** Group products by wheel type (2-wheel / 3-wheel / e-bike). */
export const productsByWheels = products.reduce<Record<string, Product[]>>((acc, p) => {
  (acc[p.wheels] ??= []).push(p);
  return acc;
}, {});

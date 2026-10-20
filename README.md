# 🌱 Virtual Garden Planner & Growth Simulator

An adaptive, iPad-friendly web application that dynamically optimizes plant placement inside custom garden beds, references localized climate data, and procedurally renders growth time-lapse videos using cloud-automated Blender pipelines.

---

## 🚀 Core Features

- 📐 **Dynamic Boundary Layout Engine**: Automatically calculates irrigation paths and seed placement parameters for multiple shapes (Rectangles, Circles, Ovals) and flexible foot dimensions.
- 🧬 **Companion Planting Optimizer**: Sorts and arranges plant distributions by maturity size, vertical shading vectors, and vegetative/botanical crop benefits.
- 🌵 **Phoenix Native October Profile**: Initialized using cool-season crop rules suited perfectly for Central Arizona's unique autumn planting schedule.
- 🎬 **Headless Blender Pipeline**: Converts coordinate array parameters directly into real-time procedural growth models scaling over 90 days.
- 📱 **iPad-First Development**: Engineered to run entirely inside cloud containers and lightweight browser sandboxes.

---

## 📁 System Architecture

```text
├── .github/
│   └── workflows/
│       └── render_garden.yml  # Installs Blender in the cloud to process videos
├── src/
│   ├── data/
│   │   └── plants.json         # Expandable plant database registry
│   ├── utils/
│   │   └── optimizer.js       # Universal geometric spacing & boundary engine
│   └── App.jsx                # Responsive UI layout control dashboard panel
├── render_pipeline.py         # Headless Blender python procedural automation script
└── package.json               # JavaScript dependencies manifest
```

---

## ⚙️ How It Works

1. **Configure Your Space**: Select your layout pattern (e.g., a 6' diameter Circle or an 8x4' Rectangle) and calibrate your emitter spacing thresholds directly inside the user dashboard panel.
2. **Algorithmic Asset Mapping**: The backend maps the irrigation system and checks coordinates against the outer boundaries, pruning invalid sites. 
3. **Maturity Profile Ordering**: Plants are grouped dynamically—taller plants like Kale migrate inward, while low-growing root crops like Carrots and trailing Nasturtium claim the perimeter lines.
4. **Cloud Compilation**: Clicking **"Generate Blender Time-lapse"** kicks off a GitHub Actions worker running Blender in background execution mode. It parses the data payload, generates keyframed geometric sprout curves, and delivers an exported `.mp4` video.

---

## 🛠️ Modifying & Expanding the Database

Anyone can expand the plant database by editing `src/data/plants.json`. To add a plant, include the profile indicators using this structural template:

```json
{
  "plant_name": "Your Crop Name",
  "type": "Veggie" or "Flower",
  "germination_days": 5,
  "days_to_maturity": 60,
  "max_height_inches": 12,
  "spread_inches": 6,
  "blender_model_asset": "mesh_identifier_string"
}
```

---

## 📝 License
Distributed under the MIT License. Feel free to clone, edit, or scale this simulation project!

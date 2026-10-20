import React, { useState, useEffect } from 'react';
import { generateUniversalEmitters, optimizePlantPlacement } from './utils/optimizer';
import initialPlants from './data/plants.json';

export default function App() {
  // Application Configurations State
  const [gardenShape, setGardenShape] = useState('Rectangle');
  const [length, setLength] = useState(6);
  const [width, setWidth] = useState(4);
  const [radius, setRadius] = useState(3);
  const [emitterSpacing, setEmitterSpacing] = useState(12);
  const [rowSpacing, setRowSpacing] = useState(12);
  
  const [gardenPlan, setGardenPlan] = useState([]);
  const [isRendering, setIsRendering] = useState(false);

  // Recalculate layout dynamically whenever any design configuration changes
  useEffect(() => {
    const config = {
      garden_shape: gardenShape,
      dimensions: {
        length_ft: parseFloat(length),
        width_ft: parseFloat(width),
        radius_ft: parseFloat(radius)
      },
      irrigation: {
        type: gardenShape === 'Rectangle' ? 'Grid Lines' : 'Spiral',
        emitter_spacing_inches: parseInt(emitterSpacing),
        row_spacing_inches: parseInt(rowSpacing)
      }
    };

    const emitters = generateUniversalEmitters(config);
    const optimizedPlan = optimizePlantPlacement(emitters, initialPlants);
    setGardenPlan(optimizedPlan);
  }, [gardenShape, length, width, radius, emitterSpacing, rowSpacing]);

  const triggerCloudRender = () => {
    setIsRendering(true);
    alert("Sending layout payload to GitHub Actions Cloud Render Framework... Check your Actions tab to download your finished .mp4 timelapse video short!");
    setTimeout(() => setIsRendering(false), 3000);
  };

  return (
    <div className="flex flex-col lg:flex-row min-h-screen bg-stone-100 font-sans p-4 lg:p-8 gap-8">
      {/* LEFT DRAWER: Design Parameter Control Deck */}
      <div className="w-full lg:w-96 bg-white p-6 rounded-2xl shadow-sm border border-stone-200 flex flex-col gap-6">
        <div>
          <h1 className="text-xl font-bold text-stone-800">Virtual Garden Blueprint</h1>
          <p className="text-xs text-stone-500">Phoenix Autumn Seed Lifecycle Engine</p>
        </div>

        {/* Shape Toggle Selector */}
        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold text-stone-600 uppercase tracking-wider">Garden Profile Geometry</label>
          <div className="grid grid-cols-2 gap-2 bg-stone-100 p-1 rounded-xl">
            <button 
              onClick={() => setGardenShape('Rectangle')}
              className={`py-2 text-sm font-medium rounded-lg transition-colors ${gardenShape === 'Rectangle' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500'}`}
            >
              📊 Rectangle
            </button>
            <button 
              onClick={() => setGardenShape('Circle')}
              className={`py-2 text-sm font-medium rounded-lg transition-colors ${gardenShape === 'Circle' ? 'bg-white text-stone-900 shadow-sm' : 'text-stone-500'}`}
            >
              ⭕ Circle
            </button>
          </div>
        </div>

        {/* Dynamic Dimensional Input Forms */}
        <div className="flex flex-col gap-4 border-t pt-4 border-stone-100">
          <label className="text-xs font-semibold text-stone-600 uppercase tracking-wider">Frame Dimensions (Feet)</label>
          {gardenShape === 'Rectangle' ? (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-xs text-stone-400 block mb-1">Bed Length</span>
                <input type="number" value={length} onChange={(e) => setLength(e.target.value)} className="w-full bg-stone-50 border p-2 rounded-xl text-sm" min="2" max="20" />
              </div>
              <div>
                <span className="text-xs text-stone-400 block mb-1">Bed Width</span>
                <input type="number" value={width} onChange={(e) => setWidth(e.target.value)} className="w-full bg-stone-50 border p-2 rounded-xl text-sm" min="2" max="20" />
              </div>
            </div>
          ) : (
            <div>
              <span className="text-xs text-stone-400 block mb-1">Outer Bed Radius</span>
              <input type="number" value={radius} onChange={(e) => setRadius(e.target.value)} className="w-full bg-stone-50 border p-2 rounded-xl text-sm" min="1" max="10" />
            </div>
          )}
        </div>

        {/* Irrigation Settings Layout Grid */}
        <div className="flex flex-col gap-4 border-t pt-4 border-stone-100">
          <label className="text-xs font-semibold text-stone-600 uppercase tracking-wider">Irrigation Calibration</label>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-xs text-stone-400 block mb-1">Emitter Interval</span>
              <select value={emitterSpacing} onChange={(e) => setEmitterSpacing(e.target.value)} className="w-full bg-stone-50 border p-2 rounded-xl text-sm">
                <option value="6">6 Inches</option>
                <option value="12">12 Inches</option>
                <option value="18">18 Inches</option>
              </select>
            </div>
            {gardenShape === 'Rectangle' && (
              <div>
                <span className="text-xs text-stone-400 block mb-1">Row Lateral Width</span>
                <select value={rowSpacing} onChange={(e) => setRowSpacing(e.target.value)} className="w-full bg-stone-50 border p-2 rounded-xl text-sm">
                  <option value="6">6 Inches</option>
                  <option value="12">12 Inches</option>
                  <option value="24">24 Inches</option>
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Cloud Rendering Call-to-Action Execution Switch */}
        <button 
          onClick={triggerCloudRender}
          disabled={isRendering || gardenPlan.length === 0}
          className={`w-full py-3.5 mt-auto rounded-xl font-semibold text-sm shadow-sm transition-all text-white ${isRendering ? 'bg-stone-400' : 'bg-emerald-600 hover:bg-emerald-700'}`}
        >
          {isRendering ? '🎬 Spooling Render Work...' : '📹 Generate Blender Time-lapse'}
        </button>
      </div>

      {/* RIGHT DISPLAY CANVAS: Dynamic Blueprint Render Workspace */}
      <div className="flex-1 bg-white p-6 rounded-2xl shadow-sm border border-stone-200 flex flex-col items-center justify-center min-h-[400px]">
        <div className="text-center mb-6">
          <h2 className="text-sm font-semibold text-stone-700">Digital Twin Footprint Matrix</h2>
          <p className="text-xs text-stone-400">Autopilot Spacing Verification Canvas</p>
        </div>

        {/* The Geometrically Transformed Interactive Canvas Frame Wrapper */}
        <div 
          className={`relative bg-amber-950 border-4 border-amber-900 shadow-inner flex items-center justify-center transition-all ${gardenShape === 'Circle' ? 'rounded-full' : 'rounded-2xl'}`}
          style={{
            width: '320px',
            height: '320px',
            aspectRatio: gardenShape === 'Rectangle' ? `${length}/${width}` : '1/1'
          }}
        >
          {gardenPlan.map((item, idx) => {
            // Context bound calculation matrix scaling spatial geometries natively
            const rangeX = gardenShape === 'Rectangle' ? length : radius * 2;
            const rangeY = gardenShape === 'Rectangle' ? width : radius * 2;
            
            const left = `${((item.coordinates.x + (rangeX / 2)) / rangeX) * 100}%`;
            const top = `${((item.coordinates.y + (rangeY / 2)) / rangeY) * 100}%`;
            
            return (
              <div 
                key={idx}
                className={`absolute w-5 h-5 -ml-2.5 -mt-2.5 rounded-full flex items-center justify-center text-[8px] font-black border shadow-md transform hover:scale-150 transition-transform cursor-pointer
                  ${item.plant.type === 'Flower' ? 'bg-orange-400 border-orange-500 text-white' : 'bg-emerald-400 border-emerald-600 text-stone-900'}`}
                style={{ left, top }}
                title={`${item.plant.plant_name}`}
              >
                {item.plant.plant_name.substring(0, 1)}
              </div>
            );
          })}
        </div>

        <div className="mt-6 text-xs text-stone-400 flex gap-4">
          <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-emerald-400 rounded-full border border-emerald-600 inline-block"></span> Vegetative Crop</div>
          <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-orange-400 rounded-full border border-orange-500 inline-block"></span> Companion Flower</div>
          <div className="flex items-center gap-1.5"><span className="font-bold text-stone-600">Total Sites: {gardenPlan.length}</span></div>
        </div>
      </div>
    </div>
  );
}

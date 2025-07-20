"use client";

import { useState } from 'react';
import axios from 'axios';
import { Calendar, Clock, MapPin, Star } from 'lucide-react';
import mbxGeocoding from '@mapbox/mapbox-sdk/services/geocoding';
import ChatBot from './components/Chatbot';

const mapboxToken = 'pk.eyJ1IjoiY2hhaXRhbnlhLXBhcmFuanBlIiwiYSI6ImNtY3FkNTRrYjBoejcyanNiN20wcm1iNm8ifQ.0fjQBVi_N04Gx-R4awT4dw';
const geocodingClient = mbxGeocoding({ accessToken: mapboxToken });

const planetIcons = {
  'Sun': '☉', 'Moon': '☽', 'Mars': '♂', 'Mercury': '☿',
  'Jupiter': '♃', 'Venus': '♀', 'Saturn': '♄',
  'Rahu': '☊', 'Ketu': '☋', 'Ascendant': '⇧'
};

const planetColors = {
  'Sun': 'text-yellow-400', 'Moon': 'text-blue-300', 'Mars': 'text-red-400',
  'Mercury': 'text-green-400', 'Jupiter': 'text-orange-400',
  'Venus': 'text-pink-400', 'Saturn': 'text-gray-400',
  'Rahu': 'text-purple-400', 'Ketu': 'text-indigo-400', 'Ascendant': 'text-white'
};

export default function Home() {
  const [dob, setDob] = useState('');
  const [tob, setTob] = useState('');
  const [placeQuery, setPlaceQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [selectedCoords, setSelectedCoords] = useState({ lat: null, lon: null });
  const [loading, setLoading] = useState(false);

  const [d1Chart, setD1Chart] = useState(null);
  const [d9Chart, setD9Chart] = useState(null);
  const [d20Chart, setD20Chart] = useState(null);
  const [selectedChart, setSelectedChart] = useState('d1');

  const [currentView, setCurrentView] = useState('charts'); // 'charts' or 'chat'

  const handlePlaceChange = async (e) => {
    const query = e.target.value;
    setPlaceQuery(query);

    if (query.length > 2) {
      const res = await geocodingClient.forwardGeocode({
        query,
        limit: 5,
        countries: ['IN'],
      }).send();

      const results = res.body.features.map(feature => ({
        place_name: feature.place_name,
        lat: feature.center[1],
        lon: feature.center[0],
      }));

      setSuggestions(results);
    } else {
      setSuggestions([]);
    }
  };

  const handlePlaceSelect = (place) => {
    setPlaceQuery(place.place_name);
    setSelectedCoords({ lat: place.lat, lon: place.lon });
    setSuggestions([]);
  };

  const handleSubmit = async () => {
    if (!selectedCoords.lat || !selectedCoords.lon) {
      alert('Please select a valid place.');
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post('http://localhost:5000/charts', {
        dob, tob, lat: selectedCoords.lat, lon: selectedCoords.lon
      });

      setD1Chart(res.data.d1 || null);
      setD9Chart(res.data.d9 || null);
      setD20Chart(res.data.d20 || null);
      setSelectedChart('d1');
      // Inside handleSubmit success block
      localStorage.setItem("astro_user_info", JSON.stringify({
        dob, tob,
        lat: selectedCoords.lat,
        lon: selectedCoords.lon,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      }));

    } catch (error) {
      console.error('API Error:', error);
      setD1Chart(null);
      setD9Chart(null);
      setD20Chart(null);
    } finally {
      setLoading(false);
    }
  };

  const renderHouse = (houseNumber, planets) => {
    const houseNames = {
      1: 'Self', 2: 'Wealth', 3: 'Courage', 4: 'Home',
      5: 'Children', 6: 'Health', 7: 'Partner', 8: 'Transformation',
      9: 'Fortune', 10: 'Career', 11: 'Gains', 12: 'Loss'
    };

    return (
      <div key={houseNumber} className="relative bg-gradient-to-br from-indigo-900/50 to-purple-900/50 border-2 border-yellow-400/30 rounded-lg p-3 h-28 flex flex-col items-center justify-center hover:border-yellow-400/60 transition-all duration-300 hover:shadow-lg group animate-fade-in">
        <div className="absolute top-2 left-2 text-sm text-yellow-300 font-semibold bg-black/30 rounded-full w-6 h-6 flex items-center justify-center group-hover:bg-black/50 transition-colors duration-200">
          {houseNumber}
        </div>
        <div className="absolute top-2 right-2 text-xs text-gray-300 font-medium bg-black/30 rounded px-2 py-0.5 group-hover:bg-black/50 transition-colors duration-200">
          {houseNames[houseNumber]}
        </div>

        <div className="flex flex-wrap gap-1 items-center justify-center mt-1">
          {planets.length === 0 ? (
            <div className="text-gray-500 text-xs">Empty</div>
          ) : (
            planets.map((planet, idx) => (
              <div key={idx} className="relative group/planet cursor-pointer">
                <div className={`text-2xl ${planetColors[planet] || 'text-white'} group-hover/planet:brightness-125 transition-all duration-200`}>
                  {planetIcons[planet] || planet}
                </div>
                <div className="absolute top-full mt-1 left-1/2 transform -translate-x-1/2 scale-0 group-hover/planet:scale-100 opacity-0 group-hover/planet:opacity-100 transition-all duration-200 bg-black/90 text-white text-xs px-2 py-1 rounded shadow-lg whitespace-nowrap z-10">
                  {planet}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    );
  };

  const ChartComponent = ({ title, ascendant, chart }) => (
    <div className="bg-white/10 rounded-2xl shadow-2xl backdrop-blur-md p-6 border border-white/20 mb-6 hover:border-white/30 transition-all duration-300 animate-slide-up">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-yellow-300 mb-2 animate-fade-in">{title}</h2>
        <p className="text-gray-300 text-sm">Ascendant: <span className="text-yellow-400 font-semibold">{ascendant}</span></p>
      </div>

      <div className="grid grid-cols-4 gap-3 max-w-4xl mx-auto">
        <div className="col-span-4 grid grid-cols-4 gap-3">
          {[12, 1, 2, 3].map(h => renderHouse(h, chart[h] || []))}
        </div>
        <div className="col-span-4 grid grid-cols-4 gap-3">
          {renderHouse(11, chart[11] || [])}
          <div className="col-span-2 flex items-center justify-center">
            <div className="text-center p-6 bg-gradient-to-r from-yellow-400/20 to-pink-400/20 rounded-xl border-2 border-yellow-400/50 hover:border-yellow-400/70 transition-all duration-300 hover:shadow-lg">
              <div className="text-3xl mb-2 animate-pulse-slow">🔯</div>
              <div className="text-yellow-300 font-bold text-sm">{title}</div>
              <div className="text-xs text-gray-300">Rashi Chart</div>
            </div>
          </div>
          {renderHouse(4, chart[4] || [])}
        </div>
        <div className="col-span-4 grid grid-cols-4 gap-3">
          {renderHouse(10, chart[10] || [])}
          <div className="col-span-2"></div>
          {renderHouse(5, chart[5] || [])}
        </div>
        <div className="col-span-4 grid grid-cols-4 gap-3">
          {[9, 8, 7, 6].map(h => renderHouse(h, chart[h] || []))}
        </div>
      </div>
    </div>
  );

  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-black text-white flex flex-col items-center justify-center p-4 relative overflow-hidden">

      <div className="max-w-6xl w-full z-10">
        <div className="text-center mb-6 animate-fade-in">
          <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 bg-clip-text text-transparent animate-pulse-slow">
            🔯 Astro Chart Generator
          </h1>
          <p className="text-base text-gray-300 max-w-2xl mx-auto">
            Discover your cosmic blueprint through Vedic astrology
          </p>
        </div>

        {currentView === 'charts' && (
          <div className="bg-white/10 rounded-2xl shadow-2xl backdrop-blur-md p-6 mb-6 border border-white/20 hover:border-white/30 transition-all duration-300 hover:shadow-2xl animate-slide-up">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="relative group">
                <label className="block text-sm font-medium text-yellow-300 mb-2 transition-colors duration-200 group-hover:text-yellow-200">
                  <Calendar className="inline w-4 h-4 mr-2" />Date of Birth
                </label>
                <input 
                  type="date" 
                  value={dob} 
                  onChange={(e) => setDob(e.target.value)} 
                  className="w-full rounded-lg p-3 bg-white/20 text-white border border-white/30 focus:ring-2 focus:ring-yellow-400 transition-all duration-200 hover:bg-white/25 focus:border-yellow-400" 
                />
              </div>

              <div className="relative group">
                <label className="block text-sm font-medium text-yellow-300 mb-2 transition-colors duration-200 group-hover:text-yellow-200">
                  <Clock className="inline w-4 h-4 mr-2" />Time of Birth
                </label>
                <input 
                  type="time" 
                  value={tob} 
                  onChange={(e) => setTob(e.target.value)} 
                  className="w-full rounded-lg p-3 bg-white/20 text-white border border-white/30 focus:ring-2 focus:ring-yellow-400 transition-all duration-200 hover:bg-white/25 focus:border-yellow-400" 
                />
              </div>

              <div className="relative group">
                <label className="block text-sm font-medium text-yellow-300 mb-2 transition-colors duration-200 group-hover:text-yellow-200">
                  <MapPin className="inline w-4 h-4 mr-2" />Place of Birth
                </label>
                <input 
                  type="text" 
                  value={placeQuery} 
                  onChange={handlePlaceChange} 
                  placeholder="Search your birth place..." 
                  className="w-full rounded-lg p-3 bg-white/20 text-white border border-white/30 focus:ring-2 focus:ring-yellow-400 placeholder-gray-400 transition-all duration-200 hover:bg-white/25 focus:border-yellow-400" 
                />
                {suggestions.length > 0 && (
                  <div className="absolute z-20 bg-white/95 text-gray-800 w-full rounded-lg mt-2 max-h-48 overflow-y-auto shadow-xl animate-fade-in">
                    {suggestions.map((sug, idx) => (
                      <div 
                        key={idx} 
                        onClick={() => handlePlaceSelect(sug)} 
                        className="px-4 py-3 hover:bg-yellow-100 cursor-pointer text-sm border-b border-gray-100 last:border-b-0 transition-colors duration-150"
                      >
                        {sug.place_name}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="md:col-span-3 flex justify-center mt-4">
                <button 
                  onClick={handleSubmit} 
                  disabled={loading} 
                  className="px-8 py-3 rounded-lg bg-gradient-to-r from-yellow-500 via-pink-500 to-purple-500 text-white font-semibold text-base hover:from-yellow-400 hover:via-pink-400 hover:to-purple-400 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                >
                  {loading ? (
                    <span className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating...
                    </span>
                  ) : (
                    'Generate My Chart'
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {(d1Chart || d9Chart || d20Chart) && currentView === 'charts' && (
          <div className="flex justify-center mb-6 space-x-3 animate-fade-in">
            <button 
              onClick={() => setSelectedChart('d1')} 
              className={`px-5 py-2 rounded-lg font-medium text-sm transition-all duration-200 transform hover:-translate-y-0.5 ${
                selectedChart === 'd1' 
                  ? 'bg-yellow-500 text-black shadow-lg' 
                  : 'bg-white/10 text-white hover:bg-white/20 border border-white/20 hover:border-white/40'
              }`}
            >
              D1 Chart
            </button>
            <button 
              onClick={() => setSelectedChart('d9')} 
              className={`px-5 py-2 rounded-lg font-medium text-sm transition-all duration-200 transform hover:-translate-y-0.5 ${
                selectedChart === 'd9' 
                  ? 'bg-yellow-500 text-black shadow-lg' 
                  : 'bg-white/10 text-white hover:bg-white/20 border border-white/20 hover:border-white/40'
              }`}
            >
              D9 Chart
            </button>
            <button 
              onClick={() => setSelectedChart('d20')} 
              className={`px-5 py-2 rounded-lg font-medium text-sm transition-all duration-200 transform hover:-translate-y-0.5 ${
                selectedChart === 'd20' 
                  ? 'bg-yellow-500 text-black shadow-lg' 
                  : 'bg-white/10 text-white hover:bg-white/20 border border-white/20 hover:border-white/40'
              }`}
            >
              D20 Chart
            </button>
          </div>
        )}

        {currentView === 'charts' && (
          <>
            {selectedChart === 'd1' && d1Chart && <ChartComponent title="D1 Rashi Chart" ascendant={d1Chart.ascendant} chart={d1Chart.chart} />}
            {selectedChart === 'd9' && d9Chart && <ChartComponent title="D9 Navamsa Chart" ascendant={d9Chart.ascendant} chart={d9Chart.chart} />}
            {selectedChart === 'd20' && d20Chart && <ChartComponent title="D20 Vimsamsa Chart" ascendant={d20Chart.ascendant} chart={d20Chart.chart} />}
          </>
        )}

        {currentView === 'chat' && (
          <div className="bg-white/10 rounded-2xl shadow-2xl backdrop-blur-md border border-white/20 min-h-[600px] flex flex-col animate-slide-up">
            <div className="p-5 border-b border-white/20 flex justify-between items-center">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                🔮 AstroBot Chat
              </h2>
              <button 
                onClick={() => setCurrentView('charts')}
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium text-sm hover:from-purple-400 hover:to-pink-400 transition-all duration-200 transform hover:-translate-y-0.5 shadow-md hover:shadow-lg"
              >
                Back to Charts
              </button>
            </div>
            <div className="flex-1 p-5">
              <ChatBot visible={true} setVisible={() => {}} isFullView={true} />
            </div>
          </div>
        )}
      </div>
      
      {/* Switch to Chat Button - Show after charts are generated */}
      {(d1Chart || d9Chart || d20Chart) && currentView === 'charts' && (
        <div className="text-center mt-6 mb-6 animate-fade-in">
          <button
            onClick={() => setCurrentView('chat')}
            className="px-6 py-3 rounded-lg bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 text-black font-semibold text-base hover:from-yellow-300 hover:via-pink-300 hover:to-purple-300 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            💬 Chat with AstroBot
          </button>
        </div>
      )}
      
      {/* Only show planet legend in charts view */}
      {currentView === 'charts' && (
        <div className="mt-6 bg-white/5 rounded-xl p-5 hover:bg-white/10 transition-all duration-300 animate-fade-in">
          <h3 className="text-lg font-bold text-yellow-300 mb-3 text-center">Planet Legend</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {Object.entries(planetIcons).map(([planet, icon]) => (
              <div key={planet} className="flex items-center justify-center bg-white/10 rounded-lg p-3 hover:bg-white/20 transition-all duration-200 group">
                <span className={`text-xl mr-2 ${planetColors[planet] || 'text-white'} group-hover:brightness-125 transition-all duration-200`}>
                  {icon}
                </span>
                <span className="text-sm text-gray-300 group-hover:text-white transition-colors duration-200">{planet}</span>
              </div>
            ))}
          </div>
        </div>
      )}
       
       {/* Footer */}
        <div className="text-center mt-6 animate-fade-in">
          <p className="text-gray-400 text-sm hover:text-gray-300 transition-colors duration-200">
            ✨ Powered by ancient Vedic wisdom and modern technology ✨
          </p>
        </div>  

    </main>
  );
}

const DEFAULT_STATIONS = [
    { nombre: "Estación Policial Centro (Tegucigalpa)", lat: 14.1131, lon: -87.1852 },
    { nombre: "Estación Policial Norte - Belén (Tegucigalpa)", lat: 14.1290, lon: -87.1960 },
    { nombre: "Estación Policial Sur - Loarque (Tegucigalpa)", lat: 14.0720, lon: -87.2200 },
    { nombre: "Estación Policial Kennedy (Tegucigalpa)", lat: 14.0880, lon: -87.1750 },
    { nombre: "Estación Policial El Manchén (Tegucigalpa)", lat: 14.1120, lon: -87.1890 },
    { nombre: "Estación Policial Suncery (San Pedro Sula)", lat: 15.4990, lon: -88.0128 },
    { nombre: "Posta Policial Estadio Olímpico (San Pedro Sula)", lat: 15.4766, lon: -88.0211 },
    { nombre: "Primera Estación Policial S.O. (San Pedro Sula)", lat: 15.4995, lon: -88.0298 },
    { nombre: "Estación Policial Barrio Guamilito (San Pedro Sula)", lat: 15.5098, lon: -88.0264 },
    { nombre: "Jefatura de Policía - UDEP-3 (Comayagua)", lat: 14.4612, lon: -87.6375 },
    { nombre: "Posta Policial La Zarcita (Comayagua)", lat: 14.4485, lon: -87.6292 }
];

// Haversine formula implemented in JS for offline/local fallback
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Elements
const form = document.getElementById('search-form');
const btnGeo = document.getElementById('btn-geolocation');
const inputLat = document.getElementById('latitude');
const inputLon = document.getElementById('longitude');
const inputApiUrl = document.getElementById('api-url');
const resultsList = document.getElementById('results-list');
const resultsCount = document.getElementById('results-count');
const loadingState = document.getElementById('loading-state');

// Attempt to use Geolocation API
btnGeo.addEventListener('click', () => {
    if (!navigator.geolocation) {
        alert("La geolocalización no es soportada por tu navegador.");
        return;
    }
    
    btnGeo.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Obteniendo...';
    btnGeo.disabled = true;

    navigator.geolocation.getCurrentPosition(
        (position) => {
            inputLat.value = position.coords.latitude.toFixed(6);
            inputLon.value = position.coords.longitude.toFixed(6);
            btnGeo.innerHTML = '<i class="fa-solid fa-gps"></i> Mi Ubicación';
            btnGeo.disabled = false;
        },
        (error) => {
            console.error(error);
            alert("No se pudo obtener tu ubicación. Por favor, ingresa las coordenadas manualmente.");
            btnGeo.innerHTML = '<i class="fa-solid fa-gps"></i> Mi Ubicación';
            btnGeo.disabled = false;
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
});

// Form Submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const lat = parseFloat(inputLat.value);
    const lon = parseFloat(inputLon.value);
    const apiUrl = inputApiUrl.value.trim();

    if (isNaN(lat) || isNaN(lon)) {
        alert("Por favor, ingresa coordenadas válidas.");
        return;
    }

    // Reset UI
    resultsList.innerHTML = '';
    loadingState.classList.remove('hidden');
    resultsCount.textContent = 'Calculando...';

    // Small timeout simulation for smooth animation feeling
    setTimeout(async () => {
        let results = [];
        let sourceUsed = '';

        if (apiUrl) {
            try {
                // Construct URL with parameters
                const fetchUrl = new URL(apiUrl);
                fetchUrl.searchParams.append('lat', lat);
                fetchUrl.searchParams.append('lon', lon);
                fetchUrl.searchParams.append('limite', 3);

                const response = await fetch(fetchUrl);
                if (!response.ok) throw new Error("API response not OK");
                
                results = await response.json();
                sourceUsed = 'API en la nube';
            } catch (err) {
                console.warn("Fallo al conectar con la API, usando cálculo local de respaldo:", err);
                results = calculateLocalNearest(lat, lon, 3);
                sourceUsed = 'Cálculo Local (Respaldo)';
            }
        } else {
            results = calculateLocalNearest(lat, lon, 3);
            sourceUsed = 'Cálculo Local';
        }

        loadingState.classList.add('hidden');
        renderResults(results, sourceUsed);
    }, 400);
});

// Local calculation utility
function calculateLocalNearest(userLat, userLon, limit) {
    return DEFAULT_STATIONS.map(station => {
        const distance = calculateDistance(userLat, userLon, station.lat, station.lon);
        return {
            nombre: station.nombre,
            lat: station.lat,
            lon: station.lon,
            distancia_km: parseFloat(distance.toFixed(2))
        };
    })
    .sort((a, b) => a.distancia_km - b.distancia_km)
    .slice(0, limit);
}

// Render findings to screen
function renderResults(stations, source) {
    if (stations.length === 0) {
        resultsList.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-triangle-exclamation"></i>
                <p>No se encontraron estaciones.</p>
            </div>
        `;
        resultsCount.textContent = 'Mostrando 0 resultados';
        return;
    }

    resultsCount.textContent = `3 estaciones (${source})`;

    stations.forEach((station, index) => {
        const card = document.createElement('div');
        card.className = 'station-card';
        card.style.animationDelay = `${index * 0.1}s`;

        card.innerHTML = `
            <div class="station-info">
                <span class="station-name">${index + 1}. ${station.nombre}</span>
                <span class="station-coords">
                    <span><i class="fa-solid fa-location-dot"></i> Lat: ${station.lat}</span>
                    <span>Lon: ${station.lon}</span>
                </span>
            </div>
            <div class="station-distance">
                <span class="distance-val">${station.distancia_km}</span>
                <span class="distance-unit">km</span>
            </div>
        `;
        resultsList.appendChild(card);
    });
}

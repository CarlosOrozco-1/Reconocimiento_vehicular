#!/bin/sh
cat > /usr/share/nginx/html/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Traffic Map Guatemala</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f172a; color: #e2e8f0; }
        .header { background: #1e293b; padding: 12px 20px; display: flex; align-items: center; gap: 20px; border-bottom: 1px solid #334155; }
        .brand { font-size: 1.25rem; font-weight: 600; color: #38bdf8; }
        .controls { display: flex; gap: 10px; }
        .btn { background: #0284c7; color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
        .btn:hover { background: #0369a1; }
        .main { display: flex; height: calc(100vh - 60px); }
        .sidebar { width: 320px; background: #1e293b; padding: 16px; overflow-y: auto; }
        .sidebar h2 { color: #38bdf8; margin-bottom: 12px; font-size: 1.1rem; }
        .route-list { display: flex; flex-direction: column; gap: 8px; }
        .route-btn { background: #0f172a; color: #cbd5e1; border: 1px solid #334155; padding: 10px 12px; border-radius: 8px; cursor: pointer; text-align: left; font-size: 0.9rem; }
        .route-btn:hover { background: #1e293b; border-color: #38bdf8; }
        .route-btn.active { background: #0c4a6e; border-color: #38bdf8; color: white; }
        .route-info { margin-top: 16px; padding: 12px; background: #0f172a; border-radius: 8px; }
        .route-info p { margin: 6px 0; font-size: 0.9rem; color: #94a3b8; }
        .route-info strong { color: #e2e8f0; }
        #map { flex: 1; height: 100%; }
        .loading { color: #64748b; padding: 20px; }
    </style>
</head>
<body>
    <header class="header">
        <div class="brand">Traffic Map Guatemala</div>
        <div class="controls">
            <button class="btn" onclick="toggleRoutes()">Ocultar Rutas</button>
            <button class="btn" onclick="toggleDepartments()">Ocultar Departamentos</button>
        </div>
    </header>
    <div class="main">
        <div class="sidebar">
            <h2>Rutas Principales</h2>
            <div class="route-list" id="route-list"><div class="loading">Cargando...</div></div>
            <div class="route-info" id="route-info" style="display: none;">
                <h3 id="selected-route-name" style="color: #38bdf8; margin-bottom: 8px;"></h3>
                <p><strong>Flujo normal:</strong> <span id="normal-flow">0</span> veh/h</p>
                <p><strong>Flujo pico:</strong> <span id="peak-flow">0</span> veh/h</p>
                <p><strong>Hora pico:</strong> <span id="peak-hour">-</span></p>
            </div>
        </div>
        <div id="map"></div>
    </div>
    <script>
        var API_URL = "http://localhost:8000";
        var map, routesLayer, departmentsLayer, routesData, selectedRoute = null;
        var routesVisible = true, departmentsVisible = true;
        var colors = ["#e11d48", "#d97706", "#16a34a", "#0891b2", "#4f46e5", "#c026d3", "#7c3aed", "#ea580c", "#0284c7"];
        function init() {
            map = L.map("map", { center: [14.6349, -90.5069], zoom: 7 });
            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 18, attribution: "OpenStreetMap" }).addTo(map);
            loadData();
        }
        async function loadData() {
            try {
                var routesRes = await fetch(API_URL + "/routes/main");
                var deptsRes = await fetch(API_URL + "/departments");
                routesData = await routesRes.json();
                var deptsData = await deptsRes.json();
                renderRoutes(routesData.data);
                renderDepartments(deptsData.data);
                renderRouteList(routesData.data);
            } catch (e) {
                document.getElementById("route-list").innerHTML = "<div class=loading>Error cargando datos</div>";
            }
        }
        function renderRoutes(geojson) {
            if (routesLayer) map.removeLayer(routesLayer);
            var colorIdx = 0;
            routesLayer = L.geoJSON(geojson, {
                style: function(f) {
                    var color = colors[colorIdx++ % colors.length];
                    return { color: color, weight: 5, opacity: 0.8 };
                },
                onEachFeature: function(f, layer) {
                    layer.bindTooltip(f.properties.name);
                    layer.on("click", function() { selectRoute(f.properties.route_code, f.properties.name); });
                }
            });
            if (routesVisible) routesLayer.addTo(map);
        }
        function renderDepartments(geojson) {
            if (departmentsLayer) map.removeLayer(departmentsLayer);
            departmentsLayer = L.geoJSON(geojson, {
                style: { color: "#38bdf8", weight: 1.2, fillColor: "#0ea5e9", fillOpacity: 0.1 },
                onEachFeature: function(f, layer) { layer.bindTooltip(f.properties.name); }
            });
            if (departmentsVisible) departmentsLayer.addTo(map);
        }
        function renderRouteList(geojson) {
            var list = document.getElementById("route-list");
            var features = geojson.features || [];
            if (features.length === 0) { list.innerHTML = "<div class=loading>No hay rutas</div>"; return; }
            list.innerHTML = features.map(function(f) {
                return "<button class=route-btn onclick=\"selectRoute('" + f.properties.route_code + "', '" + f.properties.name + "')\">" + f.properties.route_code + " - " + f.properties.name + "</button>";
            }).join("");
        }
        async function selectRoute(routeCode, routeName) {
            selectedRoute = routeCode;
            var buttons = document.querySelectorAll(".route-btn");
            buttons.forEach(function(btn) {
                btn.classList.toggle("active", btn.textContent.indexOf(routeCode) > -1);
            });
            document.getElementById("selected-route-name").textContent = routeName;
            document.getElementById("route-info").style.display = "block";
            try {
                var res = await fetch(API_URL + "/routes/" + routeCode + "/summary");
                var data = await res.json();
                document.getElementById("normal-flow").textContent = data.data.normal_flow || 0;
                document.getElementById("peak-flow").textContent = data.data.peak_flow || 0;
                document.getElementById("peak-hour").textContent = data.data.peak_hour !== null ? data.data.peak_hour + ":00" : "-";
            } catch (e) { console.error(e); }
        }
        function toggleRoutes() {
            routesVisible = !routesVisible;
            if (routesLayer) { routesVisible ? routesLayer.addTo(map) : map.removeLayer(routesLayer); }
        }
        function toggleDepartments() {
            departmentsVisible = !departmentsVisible;
            if (departmentsLayer) { departmentsVisible ? departmentsLayer.addTo(map) : map.removeLayer(departmentsLayer); }
        }
        init();
    </script>
</body>
</html>
HTMLEOF
echo "Done"
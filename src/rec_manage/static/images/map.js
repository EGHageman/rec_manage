

let draggedEmployeeId = null;
let draggedEmployeeName = null;
let selectedColumnIndex = null;
let slotMarkers = {};

function initMap() {
    var date = '2026-02-10';
    var tileMatrixSet = 'GoogleMapsCompatible_Level9';
    const center = window.initialMapCenter || { lat: 44.4605, lng: -110.8281 };
    map = L.map('map').setView([center.lat, center.lng], 15);
    
    //39.1886, -96.5810 K-state
    //44.4605, -110.8281 yellowstone


    //'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}' ArcGis World Imagery Free Satelite
    //https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/${date}/${tileMatrixSet}/{z}/{y}/{x}.jpg Nasa Satelite

    L.tileLayer(
        `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`,
        {
            //The map does not get happy with any zoom higher then 19
            maxZoom: 19
        }).addTo(map);

    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    drawing();
    draganddrop();
}

function drawing() {
    // Add or remove features
    const drawControl = new L.Control.Draw({
        edit: { featureGroup: drawnItems },
        draw: {
            polygon: true,
            rectangle: false,
            circle: false,
            circlemarker: false,
            marker: false,
            polyline: false
        }
    });
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, zonemaker);
}

//based on the documentation from leaflet draw library
function zonemaker(item) {
    const layer = item.layer;

    const label = prompt("Zone label");
    if (!label) {
        drawnItems.removeLayer(layer);
        return;
    }
    
    const color = prompt("Enter in color", "blue");

    layer.setStyle({ color });
    layer.bindPopup(label);

    drawnItems.addLayer(layer);

    const zoneData = {
        label,
        color,
        geojson: layer.toGeoJSON()
    };
    fetch("/zones", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(zoneData)
    })
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            console.log("Zone added successfully:", data);
            alert("Zone added successfully!");
        })
        .catch(error => {
            console.error("Error adding zone:", error);
            alert("Error adding zone: " + error.message);
            drawnItems.removeLayer(layer);
        });
}

function initzones() {
    //Uses the flask api in order to get the zones from the json file for the map.
    fetch("/zones")
        .then(res => res.json())
        .then(zones => {
            zones.forEach(z => {
                const layer = L.geoJSON(z.geojson, {
                    style: { color: z.color }
                }).addTo(drawnItems);
                layer.bindPopup(z.label);
            });
        });
}

function addemployee() {
    document.getElementById("addEmployeeBtn").addEventListener("click", () => {

        const first_name = prompt("Employee first name:");
        if (!first_name) return;
        
        const last_name = prompt("Employee last name:");
        if (!last_name) return;
        
        fetch("/employees", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                first_name: first_name,
                last_name: last_name
            })
        })
            .then(res => {
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            })
            .then(data => {
                console.log("Employee added successfully:", data);
                alert(`Employee added password: ${data.password}`);
                location.reload();
            })
            .catch(error => {
                console.error("Error adding employee:", error);
                alert("Error adding employee: " + error.message);
            });

    });
}



function draganddrop() {
    // drag feature (inspired from geeks for geeks):

    document.querySelectorAll(".draggable").forEach(card => {
        card.addEventListener("dragstart", () => {
            draggedEmployeeId = card.dataset.id;
            draggedEmployeeName = card.dataset.name;
        });
    });

    const mapContainer = map.getContainer();

    mapContainer.addEventListener("dragover", (items) => {
        items.preventDefault();
    });

    mapContainer.addEventListener("drop", (items) => {
        items.preventDefault();
        if (selectedColumnIndex === null) {
            alert("Please select a calendar time before dropping an employee.");
            return;
        }

        const headers = document.querySelectorAll("th.selectable");
        const selectedTime = headers[selectedColumnIndex]?.textContent.trim();
        const rect = mapContainer.getBoundingClientRect();
        const x = items.clientX - rect.left;
        const y = items.clientY - rect.top;
        const latlng = map.containerPointToLatLng([x, y]);
        console.log(`Dropped ${draggedEmployeeName} at ${latlng.lat}, ${latlng.lng}`);

        fetch('/check_zone', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                employee_name: draggedEmployeeName,
                employee_id: draggedEmployeeId,
                lat: latlng.lat,
                lng: latlng.lng,
                selected_time: selectedTime,
                shift_date: document.getElementById("shiftDate").value
            })
        })
            .then(res => res.json())
            .then(data => {
                if (!data.in_zone) {
                    alert('Employee dropped outside any zone. No assignment created.');
                    return;
                }
                addschedule(data.zone_name, data.employee, data.start_time, data.assigned_id, data.zone_lat, data.zone_lng);
            })
            .catch(error => {
                console.error('Error assigning employee:', error);
                alert('Error assigning employee: ' + error.message);
            });
    });
}

function initScheduleSelection() {
    const headers = document.querySelectorAll("th.selectable");

    headers.forEach((header, index) => {
        header.addEventListener("click", () => {
            headers.forEach(h => h.classList.remove("selected"));
            header.classList.add("selected");
            selectedColumnIndex = index;

            Object.values(slotMarkers).forEach(({ marker, columnIndex }) => {
                if (columnIndex === index) marker.addTo(map);
                else marker.remove();
            });
        });
    });
}



function addschedule(zone, employee, time, assigned_id, zone_lat, zone_lng) {
    const tbody = document.querySelector("#employeeZoneTable");
    var row = tbody.querySelector("tr");
    if (!row) {
        row = document.createElement("tr");
        for (var i = 0; i < 15; i++) {
            row.appendChild(document.createElement("td"));
        }
        tbody.appendChild(row);
    }

    const cell = row.children[selectedColumnIndex];
    const card = document.createElement("div");
    card.className = "schedule-card";
    card.textContent = `${zone} : ${employee}`;
    card.style.cursor = "pointer";

    card.addEventListener("click", () => {
        if (!confirm("Remove this assignment?")) return;
        fetch(`/unassign/${assigned_id}`, { method: "DELETE" })
            .then(() => cell.removeChild(card));
    });

    cell.appendChild(card);

    const icon = L.divIcon({
        html: `<div style="background:white; border: 4px solid #ccc; padding: 2px; ">${employee}</div>`,
        className: ""
    });

    const marker = L.marker([zone_lat, zone_lng], { icon });
    slotMarkers[assigned_id] = { marker, columnIndex: selectedColumnIndex };
}

function loadDaySchedule() {
    const date = document.getElementById("shiftDate").value;
    const tbody = document.querySelector("#employeeZoneTable");
    const row = tbody.querySelector("tr");
    row.querySelectorAll("td").forEach(td => td.innerHTML = "");
    slotMarkers = {};  // clear existing markers

    fetch(`/schedule?date=${date}`)
        .then(res => res.json())
        .then(assignments => {
            const headers = document.querySelectorAll("th.selectable");
            assignments.forEach(a => {
                const hour = a.start_time.split(":")[0];
                const matchLabel = `${parseInt(hour)}:00`;
                headers.forEach((header, index) => {
                    if (header.textContent.trim() === matchLabel) {
                        selectedColumnIndex = index;
                        addschedule(a.zone_name, a.employee_name, a.start_time, a.slot_assignment_id, a.zone_lat, a.zone_lng);
                    }
                });
            });
            selectedColumnIndex = null;
        })
        .catch(error => console.error("Error loading schedule:", error));
}

document.getElementById("generateKey").addEventListener("click", () => {
    fetch("/generate_invite", {
        method: "POST"
    })
    .then(res => {
        if (!res.ok) throw new Error(`error status: ${res.status}`);
        return res.json();
    })
    .then(data => {
        document.getElementById("inviteKeyText").textContent = data.invite_code;
        document.getElementById("inviteKeyDisplay").style.display = "block";
    })
    .catch(error => {
        console.error("Error generating invite key:", error);
        alert("Error generating invite key: " + error.message);
    });
});

const shiftDateInput = document.getElementById("shiftDate");
shiftDateInput.value = new Date().toISOString().split("T")[0]; // default to today

document.getElementById("prevDay").addEventListener("click", () => {
    const d = new Date(shiftDateInput.value);
    d.setDate(d.getDate() - 1);
    shiftDateInput.value = d.toISOString().split("T")[0];
    loadDaySchedule();
});

document.getElementById("nextDay").addEventListener("click", () => {
    const d = new Date(shiftDateInput.value);
    d.setDate(d.getDate() + 1);
    shiftDateInput.value = d.toISOString().split("T")[0];
    loadDaySchedule();
});

document.querySelectorAll(".delete-emp").forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation(); // don't trigger drag
        if (!confirm("Delete this employee?")) return;
        fetch(`/employees/${btn.dataset.id}`, { method: "DELETE" })
            .then(() => location.reload());
    });
});

shiftDateInput.addEventListener("change", loadDaySchedule);

initMap();
initzones();
addemployee();
initScheduleSelection();
loadDaySchedule();

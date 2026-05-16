
const center = window.initialMapCenter || { lat: 44.4605, lng: -110.8281 };
const map = L.map('map').setView([center.lat, center.lng], 15);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19
}).addTo(map);

// Load zones as read-only
fetch("/zones")
    .then(res => res.json())
    .then(zones => {
        zones.forEach(z => {
            L.geoJSON(z.geojson, { style: { color: z.color } })
                .addTo(map)
                .bindPopup(z.label);
        });
    });

// Date picker
const shiftDateInput = document.getElementById("shiftDate");
shiftDateInput.value = new Date().toISOString().split("T")[0];

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

shiftDateInput.addEventListener("change", loadDaySchedule);

function loadDaySchedule() {
    const date = shiftDateInput.value;
    const row = document.querySelector("#employeeZoneTable tr");
    row.querySelectorAll("td").forEach(td => td.innerHTML = "");

    fetch(`/schedule?date=${date}`)
        .then(res => res.json())
        .then(assignments => {
            const headers = document.querySelectorAll("thead th");
            assignments.forEach(a => {
                const hour = a.start_time.split(":")[0];
                const matchLabel = `${parseInt(hour)}:00`;
                headers.forEach((header, index) => {
                    if (header.textContent.trim() === matchLabel) {
                        const cell = row.children[index];
                        const card = document.createElement("div");
                        card.className = "schedule-card";
                        card.textContent = `${a.zone_name} : ${a.employee_name}`;
                        cell.appendChild(card);
                    }
                });
            });
        });
}

loadDaySchedule();
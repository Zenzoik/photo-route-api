    // Дістаємо shareToken з URL виду /share/{shareToken}
    const pathParts = window.location.pathname.split('/');
    const shareToken = pathParts[pathParts.length - 1];

    // Запитуємо публічний маршрут за shareToken
    fetch(`/api/v1/shared_route/${shareToken}`, { method: 'GET' })
      .then(res => {
        if (!res.ok) {
          return res.json().then(err => { throw new Error(err.detail || res.statusText) });
        }
        return res.json();
      })
      .then(route => {
        if (!Array.isArray(route) || !route.length) {
          alert('За цим токеном немає збережених точок або маршрут порожній.');
          return;
        }

        // Ініціалізуємо карту за першою точкою
        const first = route[0];
        const map = L.map('map').setView([first.lat, first.lng], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // Додаємо маркери з відображенням фото (з обмеженням розміру)
        route.forEach(p => {
          const marker = L.marker([p.lat, p.lng]).addTo(map);
          const imageUrl = `/uploads/${p.owner_token}/${p.filename}`;
          const popupHtml = `
            <b>${new Date(p.time).toLocaleString()}</b><br>
            <i>${p.filename}</i><br>
            <img src="${imageUrl}" alt="${p.filename}" />
          `;
          marker.bindPopup(popupHtml);
        });

        // Малюємо полілінію маршруту
        const latlngs = route.map(p => [p.lat, p.lng]);
        L.polyline(latlngs, { color: 'blue' }).addTo(map);

        // Підганяємо зум
        const bounds = L.latLngBounds(latlngs);
        map.fitBounds(bounds, { padding: [50, 50] });
      })
      .catch(err => {
        console.error(err);
        alert('Помилка під час відображення маршруту: ' + err.message);
      });

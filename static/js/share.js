    // Парсим shareToken из URL вида /share/{shareToken}
    const pathParts = window.location.pathname.split('/');
    const shareToken = pathParts[pathParts.length - 1];

    // Запрашиваем публичный маршрут по shareToken
    fetch(`/api/v1/shared_route/${shareToken}`, { method: 'GET' })
      .then(res => {
        if (!res.ok) {
          return res.json().then(err => { throw new Error(err.detail || res.statusText) });
        }
        return res.json();
      })
      .then(route => {
        if (!Array.isArray(route) || !route.length) {
          alert('По этому токену нет сохранённых точек или маршрут пуст.');
          return;
        }

        // Инициализируем карту по первой точке
        const first = route[0];
        const map = L.map('map').setView([first.lat, first.lng], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // Добавляем маркеры с отображением фото (с ограничением размера)
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

        // Рисуем полилинию маршрута
        const latlngs = route.map(p => [p.lat, p.lng]);
        L.polyline(latlngs, { color: 'blue' }).addTo(map);

        // Подгоняем зум
        const bounds = L.latLngBounds(latlngs);
        map.fitBounds(bounds, { padding: [50, 50] });
      })
      .catch(err => {
        console.error(err);
        alert('Ошибка при отрисовке маршрута: ' + err.message);
      });
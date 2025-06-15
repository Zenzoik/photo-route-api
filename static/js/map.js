    // Переменная для токена шаринга (получим, когда загрузится маршрут)
    let shareToken = null;

    // Функция, срабатывающая по клику «Поделиться маршрутом»
    function shareRoute() {
      if (!shareToken) {
        alert("Маршрут пока не загружен, попробуйте чуть позже.");
        return;
      }
      const shareUrl = `${window.location.origin}/share/${shareToken}`;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(shareUrl).then(
          () => alert("Ссылка для шаринга скопирована:\n\n" + shareUrl),
          () => prompt("Скопируйте этот URL:", shareUrl)
        );
      } else {
        prompt("Скопируйте этот URL:", shareUrl);
      }
    }

    // Делаем запрос к своему маршруту и рисуем карту
    fetch("/api/v1/route/", {
      method: "GET",
      credentials: "include"
    })
      .then(res => {
        if (!res.ok) {
          return res.json().then(err => {
            throw new Error(err.detail || res.statusText);
          });
        }
        return res.json();
      })
      .then(route => {
        if (!Array.isArray(route) || !route.length) {
          alert("Нет точек для отображения маршрута.");
          return;
        }

        // Запоминаем токен (owner_token) у первой точки
        shareToken = route[0].owner_token;

        // Инициализируем карту на первой точке
        const first = route[0];
        const map = L.map("map").setView([first.lat, first.lng], 13);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // Добавляем маркеры с изображением (оригиналом)
        route.forEach(p => {
          const marker = L.marker([p.lat, p.lng]).addTo(map);

          // Вот тут важно правильно закрыть кавычку и тег <img>
          const popupHtml = `
            <b>${new Date(p.time).toLocaleString()}</b><br>
            <i>${p.filename}</i><br>
            <img
              src="/uploads/${p.owner_token}/${p.filename}"
              onerror="this.onerror=null;this.src='/uploads/${p.owner_token}/${p.filename}';"
              style="max-width:100px;max-height:100px;"
            />
          `;
          marker.bindPopup(popupHtml);
        });

        // Рисуем линию между точками
        const latlngs = route.map(p => [p.lat, p.lng]);
        L.polyline(latlngs, { color: "blue" }).addTo(map);

        // Подгоняем область просмотра, чтобы все точки поместились
        const bounds = L.latLngBounds(latlngs);
        map.fitBounds(bounds, { padding: [50, 50] });
      })
      .catch(err => {
        console.error(err);
        alert("Ошибка при загрузке маршрута: " + err.message);
      });
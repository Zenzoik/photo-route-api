    // Змінна для токена шерінгу (отримаємо, коли завантажиться маршрут)
    let shareToken = null;

    // Функція, що спрацьовує по кліку «Поділитися маршрутом»
    function shareRoute() {
      if (!shareToken) {
        alert("Маршрут ще не завантажено, спробуйте трохи пізніше.");
        return;
      }
      const shareUrl = `${window.location.origin}/share/${shareToken}`;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(shareUrl).then(
          () => alert("Посилання для поширення скопійовано:\n\n" + shareUrl),
          () => prompt("Скопіюйте цей URL:", shareUrl)
        );
      } else {
        prompt("Скопіюйте цей URL:", shareUrl);
      }
    }

    // Тягнемо свій маршрут і малюємо карту
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
          alert("Немає точок для відображення маршруту.");
          return;
        }

        // Запам'ятовуємо токен (owner_token) з першої точки
        shareToken = route[0].owner_token;

        // Ініціалізуємо карту на першій точці
        const first = route[0];
        const map = L.map("map").setView([first.lat, first.lng], 13);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // Додаємо маркери з зображенням (оригіналом)
        route.forEach(p => {
          const marker = L.marker([p.lat, p.lng]).addTo(map);

          // Тут важливо правильно закрити лапку і тег <img>
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

        // Малюємо лінію між точками
        const latlngs = route.map(p => [p.lat, p.lng]);
        L.polyline(latlngs, { color: "blue" }).addTo(map);

        // Підганяємо область перегляду, щоби всі точки помістилися
        const bounds = L.latLngBounds(latlngs);
        map.fitBounds(bounds, { padding: [50, 50] });
      })
      .catch(err => {
        console.error(err);
        alert("Помилка під час завантаження маршруту: " + err.message);
      });

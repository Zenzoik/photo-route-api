   let selectedFiles = [];

    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadArea = document.querySelector('.upload-area');

    // Обработка выбора файлов
    fileInput.addEventListener('change', function(e) {
      handleFiles(e.target.files);
    });

    // Drag & Drop
    uploadArea.addEventListener('dragover', function(e) {
      e.preventDefault();
      uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', function(e) {
      e.preventDefault();
      uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', function(e) {
      e.preventDefault();
      uploadArea.classList.remove('dragover');
      handleFiles(e.dataTransfer.files);
    });

    function handleFiles(files) {
      selectedFiles = Array.from(files);
      updateFileList();
      uploadBtn.disabled = selectedFiles.length === 0;
    }

    function updateFileList() {
      fileList.innerHTML = '';
      selectedFiles.forEach((file, index) => {
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `
          <span>${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</span>
          <button onclick="removeFile(${index})" style="background: #dc3545; padding: 5px 10px; font-size: 12px;">Удалить</button>
        `;
        fileList.appendChild(div);
      });
    }

    function removeFile(index) {
      selectedFiles.splice(index, 1);
      updateFileList();
      uploadBtn.disabled = selectedFiles.length === 0;
    }

    function clearAll() {
      selectedFiles = [];
      updateFileList();
      uploadBtn.disabled = true;
    }

    async function uploadFiles() {
      if (selectedFiles.length === 0) return;

      uploadBtn.disabled = true;
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });

      try {
        const response = await fetch('/api/v1/uploadfiles/', {
          method: 'POST',
          body: formData,
          credentials: 'include'
        });
        if (response.ok) {
          alert(`Успешно загружено ${selectedFiles.length} фото!`);
          document.querySelectorAll('.file-item').forEach(el => {
            el.classList.add('success');
          });
          selectedFiles = [];
          updateFileList();
        } else {
          const error = await response.json();
          alert('Ошибка при загрузке: ' + (error.detail || JSON.stringify(error)));
        }
      } catch (err) {
        console.error(err);
        alert('Ошибка сети при загрузке: ' + err.message);
      } finally {
        uploadBtn.disabled = false;
      }
    }

    function viewMap() {
      window.open('/map', '_blank');
    }


    async function showPhotos() {
      const previewContainer = document.getElementById('preview-container');
      previewContainer.innerHTML = ''; // очищаем контейнер
      try {
        const response = await fetch('/api/v1/photos/', {
          method: 'GET',
          credentials: 'include'
        });
        if (response.status === 401) {
          alert('Сессия не найдена. Зайдите сначала на главную (/).');
          return;
        }
        const data = await response.json();
        if (!response.ok) {
          alert('Не удалось получить список фото: ' + (data.detail || JSON.stringify(data)));
          return;
        }
        if (data.length === 0) {
          previewContainer.innerHTML = '<p>Фото не найдены.</p>';
          return;
        }
        data.forEach(photo => {
          const thumbDiv = document.createElement('div');
          thumbDiv.className = 'thumbnail';
          const removeIcon = document.createElement('div');
          removeIcon.className = 'remove-icon';
          removeIcon.innerHTML = '&times;'; // символ ×
          removeIcon.title = 'Удалить это фото';
          removeIcon.onclick = () => deletePhoto(photo.id, thumbDiv);

          // Сама картинка
          const img = document.createElement('img');
          img.src = `/uploads/${photo.owner_token}/${photo.filename}`;
          img.alt = photo.filename;
          img.onerror = () => {
            img.alt = 'Ошибка загрузки';
            img.style.border = '1px solid red';
          };

          // Подпись с именем файла
          const nameSpan = document.createElement('span');
          nameSpan.className = 'filename';
          nameSpan.textContent = photo.filename;

          thumbDiv.appendChild(removeIcon);
          thumbDiv.appendChild(img);
          thumbDiv.appendChild(nameSpan);
          previewContainer.appendChild(thumbDiv);
        });
      } catch (err) {
        console.error(err);
        alert('Ошибка при получении фото: ' + err.message);
      }
    }

    async function deletePhotos() {
      if (!confirm('Вы уверены, что хотите удалить ВСЕ свои фото? Это действие необратимо!')) {
        return;
      }
      try {
        const response = await fetch('/api/v1/photos/', {
          method: 'DELETE',
          credentials: 'include'
        });
        if (response.status === 204) {
          alert('Все ваши фото удалены.');
          document.getElementById('preview-container').innerHTML = '';
        } else if (response.status === 401) {
          alert('Сессия не найдена. Зайдите сначала на главную (/).');
        } else {
          const data = await response.json();
          alert('Ошибка при удалении: ' + (data.detail || JSON.stringify(data)));
        }
      } catch (err) {
        console.error(err);
        alert('Ошибка сети при удалении фото: ' + err.message);
      }
    }

    async function deletePhoto(photoId, thumbDiv) {
      if (!confirm('Удалить это фото?')) {
        return;
      }
      try {
        const response = await fetch(`/api/v1/photos/${photoId}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        if (response.status === 204) {
          // Если удалилось успешно, убираем миниатюру из DOM
          thumbDiv.remove();
        } else if (response.status === 401) {
          alert('Сессия не найдена. Зайдите сначала на главную (/).');
        } else if (response.status === 404) {
          alert('Фото не найдено или уже удалено.');
          thumbDiv.remove();
        } else {
          const data = await response.json();
          alert('Ошибка при удалении: ' + (data.detail || JSON.stringify(data)));
        }
      } catch (err) {
        console.error(err);
        alert('Ошибка сети при удалении фото: ' + err.message);
      }
    }
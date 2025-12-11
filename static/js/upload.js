   let selectedFiles = [];

    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadArea = document.querySelector('.upload-area');

    // Обробка вибору файлів
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
          <button onclick="removeFile(${index})" style="background: #dc3545; padding: 5px 10px; font-size: 12px;">Видалити</button>
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
          alert(`Успішно завантажено ${selectedFiles.length} фото!`);
          document.querySelectorAll('.file-item').forEach(el => {
            el.classList.add('success');
          });
          selectedFiles = [];
          updateFileList();
        } else {
          const error = await response.json();
          alert('Помилка під час завантаження: ' + (error.detail || JSON.stringify(error)));
        }
      } catch (err) {
        console.error(err);
        alert('Помилка мережі під час завантаження: ' + err.message);
      } finally {
        uploadBtn.disabled = false;
      }
    }

    function viewMap() {
      window.open('/map', '_blank');
    }


    async function showPhotos() {
      const previewContainer = document.getElementById('preview-container');
      previewContainer.innerHTML = ''; // очищуємо контейнер
      try {
        const response = await fetch('/api/v1/photos/', {
          method: 'GET',
          credentials: 'include'
        });
        if (response.status === 401) {
          alert('Сесію не знайдено. Спочатку зайдіть на головну (/).');
          return;
        }
        const data = await response.json();
        if (!response.ok) {
          alert('Не вдалося отримати список фото: ' + (data.detail || JSON.stringify(data)));
          return;
        }
        if (data.length === 0) {
          previewContainer.innerHTML = '<p>Фото не знайдені.</p>';
          return;
        }
        data.forEach(photo => {
          const thumbDiv = document.createElement('div');
          thumbDiv.className = 'thumbnail';
          const removeIcon = document.createElement('div');
          removeIcon.className = 'remove-icon';
          removeIcon.innerHTML = '&times;'; // символ ×
          removeIcon.title = 'Видалити це фото';
          removeIcon.onclick = () => deletePhoto(photo.id, thumbDiv);

          // Саме зображення
          const img = document.createElement('img');
          img.src = `/uploads/${photo.owner_token}/${photo.filename}`;
          img.alt = photo.filename;
          img.onerror = () => {
            img.alt = 'Помилка завантаження';
            img.style.border = '1px solid red';
          };

          // Підпис з ім'ям файла
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
        alert('Помилка під час отримання фото: ' + err.message);
      }
    }

    async function deletePhotos() {
      if (!confirm('Ви впевнені, що хочете видалити ВСІ свої фото? Це дія незворотна!')) {
        return;
      }
      try {
        const response = await fetch('/api/v1/photos/', {
          method: 'DELETE',
          credentials: 'include'
        });
        if (response.status === 204) {
          alert('Усі ваші фото видалені.');
          document.getElementById('preview-container').innerHTML = '';
        } else if (response.status === 401) {
          alert('Сесію не знайдено. Спочатку зайдіть на головну (/).');
        } else {
          const data = await response.json();
          alert('Помилка під час видалення: ' + (data.detail || JSON.stringify(data)));
        }
      } catch (err) {
        console.error(err);
        alert('Помилка мережі під час видалення фото: ' + err.message);
      }
    }

    async function deletePhoto(photoId, thumbDiv) {
      if (!confirm('Видалити це фото?')) {
        return;
      }
      try {
        const response = await fetch(`/api/v1/photos/${photoId}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        if (response.status === 204) {
          // Якщо видалилося успішно, прибираємо мініатюру з DOM
          thumbDiv.remove();
        } else if (response.status === 401) {
          alert('Сесію не знайдено. Спочатку зайдіть на головну (/).');
        } else if (response.status === 404) {
          alert('Фото не знайдено або вже видалено.');
          thumbDiv.remove();
        } else {
          const data = await response.json();
          alert('Помилка під час видалення: ' + (data.detail || JSON.stringify(data)));
        }
      } catch (err) {
        console.error(err);
        alert('Помилка мережі під час видалення фото: ' + err.message);
      }
    }

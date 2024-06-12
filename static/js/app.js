class FileUpload {
    constructor(input) {
        this.input = input;
        this.max_length = 1024 * 1024 * 10; // 10 MB
    }
    
    upload() {
        this.file = this.input.files[0];
        if (this.file.type !== 'text/csv') {
            alert('Please select a CSV file.');
            return;
        }
        this.create_progress_bar();
        this.initFileUpload();
    }

    initFileUpload() {
        this.upload_file(0, null);
    }

    upload_file(start, path) {
        let end;
        let self = this;
        let existingPath = path;
        let formData = new FormData();
        let nextChunk = start + this.max_length;
        let currentChunk = this.file.slice(start, nextChunk);
        let uploadedChunk = start + currentChunk.size;

        if (uploadedChunk >= this.file.size) {
            end = 1;
        } else {
            end = 0;
        }

        formData.append('file', currentChunk);
        formData.append('filename', this.file.name);
        formData.append('end', end);
        formData.append('existingPath', existingPath);
        formData.append('nextSlice', nextChunk);

        document.querySelector('.filename').textContent = this.file.name;
        document.querySelector('.textbox').textContent = "Uploading file";
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        let xhr = new XMLHttpRequest();
        xhr.upload.addEventListener('progress', function (e) {
            if (e.lengthComputable) {
                let percent;
                if (self.file.size < self.max_length) {
                    percent = Math.round((e.loaded / e.total) * 100);
                } else {
                    percent = Math.round((uploadedChunk / self.file.size) * 100);
                }
                document.querySelector('.progress-bar').style.width = percent + '%';
                document.querySelector('.progress-bar').textContent = percent + '%';
            }
        });

        xhr.open('POST', '/upload_file/', true);
        xhr.setRequestHeader('X-CSRFToken', csrfToken);

        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    let res = JSON.parse(xhr.responseText);
                    if (nextChunk < self.file.size) {
                        existingPath = res.existingPath;
                        self.upload_file(nextChunk, existingPath);
                    } else {
                        document.querySelector('.textbox').textContent = res.data;
                        alert(res.data);
                    }
                } else {
                    alert('Error: ' + xhr.statusText);
                }
            }
        };

        xhr.send(formData);
    }

    create_progress_bar() {
        let progress = `<div class="file-icon">
                            <i class="fa fa-file-o" aria-hidden="true"></i>
                        </div>
                        <div class="file-details">
                            <p class="filename"></p>
                            <small class="textbox"></small>
                            <div class="progress" style="margin-top: 5px;">
                                <div class="progress-bar bg-success" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%">
                                </div>
                            </div>
                        </div>`;
        document.getElementById('uploaded_files').innerHTML = progress;
    }
}

document.getElementById('submit').addEventListener('click', function (event) {
    event.preventDefault();
    let uploader = new FileUpload(document.getElementById('fileupload'));
    uploader.upload();
});

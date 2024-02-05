import convertWebmToWav from './utils/webm2wav.js'
import sendAudio_Wait from './utils/useAudioModelPredict.js'

$(document).ready(function() {
    var isRecording = false;
    let mediaRecorder, chunks = [], audioURL = '';
    let startTime, timerInterval, timeDisplay, elapsedTime;
    const maxRecordingTime = 30000;
    const minRecordingTime = 5000;
    const whiteSection = document.getElementById('white-section');
    const headerText = document.getElementById('header-text');
    const Spinner = document.getElementById('spinner');

    var device = navigator.mediaDevices.getUserMedia({ audio: true });
    if (navigator.mediaDevices && device) {
        console.log('mediaDevices supported.');

        device
            .then(function(stream) {
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.ondataavailable = function(e) {
                    chunks.push(e.data);
                };

                mediaRecorder.onstart = function() {
                    startTime = new Date().getTime();
                    timerInterval = setInterval(updateRecordingTime, 0); 
                };

                mediaRecorder.onstop = function() {
                    clearInterval(timerInterval);
                    timeDisplay.textContent = '';
                    if (elapsedTime >= minRecordingTime/1000) {
                        const blob = new Blob(chunks, { type: 'audio/wav; codecs=MS_PCM' });
                        const keyID = generateRandomKey(20);
                        convertWebmToWav(blob)
                        .then((blobWav)=>{
                            const formData = new FormData();

                            formData.append('audio', blobWav, 'recording.wav');
                            formData.append('key', keyID);
                            formData.append('nItems', 4);
                            
                            chunks = [];
                            audioURL = window.URL.createObjectURL(blobWav);
                            console.log(audioURL);
                            return formData;
                        })
                        .then((formData) => {
                            console.log("formData: ",formData);
                            console.log("keyID: ",keyID);
                            return sendAudio_Wait(formData,keyID);
                        })
                        .then((data_model) => {
                            console.log("In main stream data_model, ", data_model);
                            
                            updateWhiteSection(data_model);
                        })
                        .catch((error) => {
                            console.error('Error converting WebM to WAV or handling data_model:', error);
                        })
                        .finally(() => {
                            chunks = [];
                        });;
                    } else {
                        updateAnotherHeader();
                    }
                    stopAnimation();
                };
            })
            .catch(function(error) {
                console.log('Following error has occurred: ', error);
            });
            
    } else {
        updateHeaderText('Your browser does not support mediaDevices!');
    }

    // Toggle audio recording when clicking on the image
    $('#record-image').click(function() {
        toggleRecording();
    });

    function generateRandomKey(length) {
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let key = '';
      
        for (let i = 0; i < length; i++) {
          const randomIndex = Math.floor(Math.random() * characters.length);
          key += characters.charAt(randomIndex);
        }
      
        return key;
    }

    function toggleRecording() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }

    function startRecording() {
        mediaRecorder.start();
        isRecording = true;
        console.log(elapsedTime);
        startAnimation();
        displaySpinner();
        updateHeaderText('Recording');
    }

    function stopRecording() {
        mediaRecorder.stop();
        isRecording = false;
        console.log(elapsedTime)
        updateFindingHeader();
    }

    $('#download-button').click(function() {
        if (audioURL) {
            const downloadLink = document.createElement('a');
            downloadLink.href = audioURL;
            downloadLink.download = 'recorded_audio.wav';
            downloadLink.click();
        }
    });

    function startAnimation() {
        $('#record-image').addClass('animate');
    }

    function stopAnimation() {
        $('#record-image').removeClass('animate');
    }

    function displaySpinner() {
        $('#spinner').removeClass('d-none');
    }

    function updateRecordingTime() {
        const currentTime = new Date().getTime();
        elapsedTime = Math.floor((currentTime - startTime) / 1000);
        timeDisplay = document.getElementById('recording-time');
        if (elapsedTime >= 10)
            timeDisplay.textContent = `00:${elapsedTime} (Max 30s)`;
        else
            timeDisplay.textContent = `00:0${elapsedTime} (Max 30s)`;

        if (elapsedTime == maxRecordingTime/1000)
            stopRecording();
    }

    function updateHeaderText(text) {
        whiteSection.textContent = ''
        headerText.textContent = text
        displaySpinner()
        whiteSection.append(headerText)
        whiteSection.append(Spinner)
    }
    
    function updateAnotherHeader() {
        $('#spinner').addClass('d-none');
        headerText.textContent = `Recording at least ${minRecordingTime/1000} seconds. Please try again!`
    }
    function updateFindingHeader() {
        // $('#spinner').addClass('d-none');
        headerText.textContent = `Please wait for a moment while your songs are being located!`
    }
    
    // After recording is done, update the white section with the recorded audio
    function updateWhiteSection(data) {
        const whiteSection = document.getElementById('white-section');
        const cardHTML = Object.entries(data).map(([key, value], index) => {
            const string = `${value.singer_name}`
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[\u0044\u24B9\uFF24\u1E0A\u010E\u1E0C\u1E10\u1E12\u1E0E\u0110\u018B\u018A\u0189\uA779]/g, "D")
            .replace(/\s/g, "");
            
            const imageSource = `static/imgs/singer_pics/${string}/${string}.jpg`;
            const imgTag = document.createElement('img');
            imgTag.src = imageSource;
            
            return `
                <div class="card" style="width: 18rem;">
                    <img src=${imgTag.src} class="card-img-top">
                    <div class="card-body">
                        <h5 class="card-title">Top ${index + 1}</h5>
                        <p class="card-text">${value.song_name} <br> ${value.singer_name}<br></p>
                        <a href=${value.singer_YT_channel} class="btn btn-primary">Channel</a>
                        <a href=${value.song_YT_playlist} class="btn btn-primary">Playlist</a>
                    </div>
                </div>
            `;
        }).join('');
    
        whiteSection.innerHTML = `
            <h1 id="header-text" class="black-header fade-in"> 
                Your Songs <img src="static/imgs/logos/music.png" class="music-logo">
            </h1>
            <div class="image-container">   
                ${cardHTML}
            </div>
        `;
    }
    
    
    
  
  
});
function convertWebmToWav(webmBlob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = function () {
        const webmArrayBuffer = reader.result;
        console.log("File audio format: ",getAudioFileFormat(webmArrayBuffer))
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        audioContext.decodeAudioData(webmArrayBuffer, (audioBuffer) => {
          const wavData = encodeWav(audioBuffer);
          const wavBlob = new Blob([wavData], { type: 'audio/wav' });
          resolve(wavBlob);
        }, (error) => {
          console.log(error)
          reject(error);
        });
      };
      reader.readAsArrayBuffer(webmBlob);
    });
  }
  
function encodeWav(audioBuffer) {
    const numberOfChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const length = audioBuffer.length;
    const samples = new Float32Array(length * numberOfChannels);
  
    // Interleave channels
    for (let channel = 0; channel < numberOfChannels; channel++) {
      const channelData = audioBuffer.getChannelData(channel);
      for (let i = 0; i < length; i++) {
        samples[i * numberOfChannels + channel] = channelData[i];
      }
    }
  
    const buffer = new ArrayBuffer(samples.length * 2);
    const view = new DataView(buffer);
    let offset = 0;
    for (let i = 0; i < samples.length; i++, offset += 2) {
      const sample = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
    }
  
    const wavHeader = createWavHeader(sampleRate, numberOfChannels, samples.length);
  
    const wavData = new Uint8Array(wavHeader.length + buffer.byteLength);
    wavData.set(wavHeader);
    wavData.set(new Uint8Array(buffer), wavHeader.length);
  
    return wavData;
}
  
function createWavHeader(sampleRate, numChannels, dataLength) {
    const blockAlign = numChannels * 2;
    const byteRate = sampleRate * blockAlign;
    const dataSize = dataLength * 2;
  
    const buffer = new ArrayBuffer(44);
    const view = new DataView(buffer);
  
    // RIFF chunk descriptor
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataSize, true);
    writeString(view, 8, 'WAVE');
  
    // Format chunk
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);  // Sub-chunk size (16 for PCM)
    view.setUint16(20, 1, true);   // Audio format (1 for PCM)
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, 16, true);  // Bits per sample (16 for PCM)
  
    // Data chunk
    writeString(view, 36, 'data');
    view.setUint32(40, dataSize, true);
  
    return new Uint8Array(buffer);
}
  
function writeString(view, offset, value) {
    for (let i = 0; i < value.length; i++) {
      view.setUint8(offset + i, value.charCodeAt(i));
    }
}

function getAudioFileFormat(arrayBuffer) {
  const headerBytes = new Uint8Array(arrayBuffer, 0, 4);

  // Compare the header bytes to known signatures
  if (headerBytes[0] === 0x52 && headerBytes[1] === 0x49 && headerBytes[2] === 0x46 && headerBytes[3] === 0x46) {
    return 'WAV';
  } else if (headerBytes[0] === 0x49 && headerBytes[1] === 0x44 && headerBytes[2] === 0x33) {
    return 'MP3';
  } else if (headerBytes[0] === 0x4F && headerBytes[1] === 0x67 && headerBytes[2] === 0x67 && headerBytes[3] === 0x53) {
    return 'OGG';
  } else if (headerBytes[0] === 0x1A && headerBytes[1] === 0x45 && headerBytes[2] === 0xDF && headerBytes[3] === 0xA3) {
    return 'WebM';
  } else if (headerBytes[0] === 0x66 && headerBytes[1] === 0x4C && headerBytes[2] === 0x61 && headerBytes[3] === 0x43) {
    return 'FLAC';
  } else {
    return 'Unknown';
  }
}

export default convertWebmToWav;
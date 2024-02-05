// Replace with your API server URL
const uriApiServer = "http://localhost:3241";

// Function to check if the server is ready
async function checkServerStatus() {
  const response = await fetch(`${uriApiServer}/check-server-status`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error('Failed to check server status');
  }

  const { server_status } = await response.json();
  return server_status === 'ready';
}

// Function to send audio file to the backend
async function sendAudioToBackend(formData) {
//   const formData = new FormData();
//   formData.append('audio', audioFile);
  console.log("sendAudioToBackend - formData: ",formData)
  const response = await fetch(`${uriApiServer}/send-query`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error('Failed to upload audio');
  }

  // Extract and return the key or unique identifier for the uploaded audio
//   const { key } = await response.json();
//   return key;
}

// Function to continuously poll for the status of the model
async function pollModelStatus(key) {
    const maxAttempts = 10; // Maximum number of polling attempts
    const delayBetweenAttempts = 5000; // Delay in milliseconds between each polling attempt
  
    let attempt = 1;
    while (attempt <= maxAttempts) {
      await sleep(delayBetweenAttempts); // Delay between each polling attempt
  
      const response = await fetch(`${uriApiServer}/get-predict/${key}`, {
        method: 'GET'
      });
  
      if (!response.ok) {
        throw new Error('Failed to get model status');
      }
  
      const { status_model, data_model } = await response.json();
      console.log("status_model in pollModelStatus: ",status_model);
      console.log("data_model in pollModelStatus: ",data_model);
      if (status_model != 'working' && status_model != null) {
        // const { data_model } = await response.json();
        console.log("data_model in pollModelStatus: ", data_model)
        return data_model; // Return the final result
      }
  
      attempt++;
    }
}

// Helper function to introduce a delay
function sleep(delay) {
  return new Promise((resolve) => setTimeout(resolve, delay));
}

// Usage example
// const audioFile = document.getElementById('audioFileInput').files[0]; // Replace with your audio file input element
export default function sendAudio_Wait(audioFile,key){
    return  checkServerStatus()
            .then((isReady) => {
                if (isReady) {
                    return sendAudioToBackend(audioFile);
                } 
                else {
                    throw new Error('Server is not ready');
                }
            })
            .then(() => pollModelStatus(key))
            .then((result) => {
                // Process the final result
                console.log(result);
                return result;
            })
            .catch((error) => {
                // Handle errors
                console.error(error);
            });
}


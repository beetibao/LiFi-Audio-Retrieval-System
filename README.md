# LiFi: AI-Powered Audio Discovery
This project is an application that helps people search for the song's name based on a given audio from the user. We use the Neural Audio Fingerprint model which was proposed in a paper published in 2021, [NEURAL AUDIO FINGERPRINT FOR HIGH-SPECIFIC AUDIO RETRIEVAL BASED ON CONTRASTIVE LEARNING](https://arxiv.org/pdf/2010.11910.pdf) to embed audio, FAISS for getting items, and design the metric to calculate the similarity between each candidate song and the input audio.

## Install
You can also run the application by Docker thorough running the below commands:
```
cd YOUR_PROJECT_PATH
docker compose up -d
```

## Limitation
The system can only recommend the name of the song in the document, so if you give it the audio that is out of the dataset, it will return the names of the songs in the document, and they will be similar given audio.

## Reference
- [NEURAL AUDIO FINGERPRINT FOR HIGH-SPECIFIC AUDIO RETRIEVAL BASED ON CONTRASTIVE LEARNING, ICASSP - 2021](https://arxiv.org/pdf/2010.11910.pdf)

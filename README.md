# LiFi: AI-Powered Audio Discovery
This project is an application that helps people search for the song's name based on a given audio from the user. We use the Neural Audio Fingerprint model which was proposed in a paper published in 2021, [NEURAL AUDIO FINGERPRINT FOR HIGH-SPECIFIC AUDIO RETRIEVAL BASED ON CONTRASTIVE LEARNING](https://arxiv.org/pdf/2010.11910.pdf) to embed audio, FAISS for getting items, and we use our method that we self-design to calculate the similarity between each candidate song and the input audio.

## Install
You can also run the application by Docker thorough running the below commands:
```
cd YOUR_PROJECT_PATH
docker compose up -d
```

## Limitation
Because of the lack of resources to crawl music audio, we have to train the model in our small dataset which makes the system's accuracy unstable. In addition, the system can only recommend the name of the song in the dataset, so if you give it audio out of the dataset, it will return names of songs in our dataset and they will be similar given audio.

## Reference
- [NEURAL AUDIO FINGERPRINT FOR HIGH-SPECIFIC AUDIO RETRIEVAL BASED ON CONTRASTIVE LEARNING, ICASSP - 2021](https://arxiv.org/pdf/2010.11910.pdf)

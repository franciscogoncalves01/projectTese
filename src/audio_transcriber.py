from google.cloud import speech


class AudioTranscriber:
    def __init__(self, queue, socket, rate=16000):
        self.queue = queue
        self.socket = socket
        self.rate = rate
        self.client = speech.SpeechClient()
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.rate,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config,
            interim_results=False,  # Disable interim results
        )
        self.silence_duration = 0

    def transcribe_audio(self):
        def request_generator():
            while True:
                item = self.queue.get()
                if item is None:
                    return
                audio_chunk, duration = item
                yield speech.StreamingRecognizeRequest(
                    audio_content=audio_chunk
                ), duration

        try:
            for request, duration in request_generator():
                try:
                    responses = self.client.streaming_recognize(
                        config=self.streaming_config, requests=[request]
                    )

                    transcription_collected = False

                    for response in responses:
                        for result in response.results:
                            transcription = result.alternatives[0].transcript
                            self.send_transcription(duration, transcription)
                            transcription_collected = True

                    # if not transcription_collected:
                    #     self.send_transcription(duration, -1, "")

                except Exception as e:
                    self.send_transcription(duration, "")

        except KeyboardInterrupt:
            pass

    def send_transcription(self, duration, transcription):
        #message = f"[{duration:.2f}] {transcription}"
        # Send transcription to the server
        self.socket.sendall(transcription.encode())

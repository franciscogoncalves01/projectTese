import os
import sys
import time
import socket
import multiprocessing
import webrtcvad
import collections
import sounddevice as sd

from audio_transcriber import AudioTranscriber


# Audio recording parameters
RATE = 16000
FRAME_DURATION = 30  # 30ms
CHUNK = int(RATE * FRAME_DURATION / 1000)  # 30ms frames
TIMEOUT = 1.0  # Timeout period in seconds to determine end of speech

debug = True

# Setting Google credential
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'pathtojson'

def find_input_device_index(device_name):
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if device_name in dev["name"]:
            return i
    return None


def update_status(socket, message, duration):
    socket.sendall(message.encode())


def audio_listener(
    queue, input_device_index, channel, socket
):
    vad = webrtcvad.Vad(1)  # Change for more aggressive filtering
    if debug:
        print(f"Listening on channel {channel}...")

    triggered = [False]
    ring_buffer = collections.deque(maxlen=10)
    speech_buffer = []
    start_time = [None]
    last_speech_time = [None]

    chunk_duration = 5  # Duration for each chunk in seconds
    chunk_size = int(RATE * chunk_duration * 2)

    def callback(indata, frames, callback_time, status):
        if status and debug:
            print(status)

        # Extract the specific channel
        mono_frame = indata[:, channel - 1].copy()
        mono_frame_bytes = mono_frame.tobytes()

        # Voice Activity Detection
        is_speech = vad.is_speech(mono_frame_bytes, RATE)
        if is_speech:
            if not triggered[0]:
                update_status(socket, "START", -1)
                triggered[0] = True
                if (
                        last_speech_time[0]
                        and (time.time() - last_speech_time[0]) < TIMEOUT
                ):
                    if debug:
                        print("Merging segments")
                else:
                    speech_buffer.clear()
                    start_time[0] = time.time()
                speech_buffer.extend(ring_buffer)
                ring_buffer.clear()

            speech_buffer.append(mono_frame_bytes)
            last_speech_time[0] = time.time()

        if triggered[0] and (time.time() - last_speech_time[0]) > TIMEOUT:
            end_time = time.time()
            speaking_duration = end_time - start_time[0]
            update_status(
                socket,
                "END",
                round(speaking_duration, 2),
            )
            if len(speech_buffer) > 0:
                queue.put((b"".join(speech_buffer), speaking_duration))
            speech_buffer.clear()
            triggered[0] = False

        if not triggered[0]:
            ring_buffer.append(mono_frame_bytes)

        # Check if the buffer has reached the chunk size or if the speech ends
        if len(speech_buffer) * len(mono_frame_bytes) >= chunk_size:
            queue.put((b"".join(speech_buffer), chunk_duration))
            speech_buffer.clear()
            start_time[0] = time.time()
        elif not is_speech and len(speech_buffer) > 0:
            short_duration = len(speech_buffer) * len(mono_frame_bytes) / RATE / 2
            queue.put((b"".join(speech_buffer), short_duration))
            speech_buffer.clear()

    try:
        stream = sd.InputStream(
            samplerate=RATE,
            device=input_device_index,
            channels=1,
            dtype="int16",
            callback=callback,
            blocksize=CHUNK,
        )

        with stream:
            while True:
                time.sleep(0.1)

    except Exception as e:
        print(f"Error during listening: {e}")
        queue.put(None)


def run_audio_transcriber(queue, socket):
    transcriber = AudioTranscriber(queue, socket)
    transcriber.transcribe_audio()


def main():

    device_name = "Microphone"
    input_device_index = find_input_device_index(device_name)
    if input_device_index is None:
        print(f"Input device '{device_name}' not found.")
        sys.exit(1)

    channel = 1

    if debug:
        print(
        f"Using input device '{device_name}' at index {input_device_index}, channel {channel}"
        )

    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 8080))

    audio_queue = multiprocessing.Queue()

    listener_process = multiprocessing.Process(
        target=audio_listener,
        args=(audio_queue, input_device_index, channel, s),
    )
    transcriber_process = multiprocessing.Process(
        target=run_audio_transcriber, args=(audio_queue, s)
    )

    listener_process.start()
    transcriber_process.start()

    try:
        listener_process.join()
        transcriber_process.join()

    except KeyboardInterrupt:
        listener_process.terminate()
        transcriber_process.terminate()

        listener_process.join()
        transcriber_process.join()


if __name__ == "__main__":
    main()

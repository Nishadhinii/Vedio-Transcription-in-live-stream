import cv2
import speech_recognition as sr
import threading
import numpy as np

# Global variable to store the current subtitle
current_subtitle = ""


# Function to listen and update the subtitle
def listen_and_update():
    global current_subtitle
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    while True:
        with mic as source:
            try:
                print("Listening...")
                audio = recognizer.listen(source, phrase_time_limit=2)
                text = recognizer.recognize_google(audio)
                current_subtitle = text
                print("Recognized:", text)
            except sr.UnknownValueError:
                current_subtitle = ""
            except sr.RequestError as e:
                current_subtitle = f"[Error: {e}]"


# Start speech recognition in a separate thread
threading.Thread(target=listen_and_update, daemon=True).start()

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape

    # Create a black strip to show subtitles
    subtitle_strip = np.zeros((60, width, 3), dtype=np.uint8)

    # --- Centering the Subtitle ---
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2

    # Get text size
    text_size, _ = cv2.getTextSize(current_subtitle, font, font_scale, thickness)
    text_width = text_size[0]

    # Calculate center position
    x_pos = (width - text_width) // 2
    y_pos = 40  # Vertically within the black strip

    # Put text on the subtitle strip
    cv2.putText(subtitle_strip, current_subtitle, (x_pos, y_pos),
                font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    # Combine frame and subtitle strip
    combined_frame = np.vstack((frame, subtitle_strip))

    # Show the result
    cv2.imshow("Live Video with Centered Subtitles", combined_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

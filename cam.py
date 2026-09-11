import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ Could not access the camera.")
    exit()

print("✅ Camera connected!")
print("Press Q to close the camera.")

while True:
    success, frame = camera.read()

    if not success:
        print("❌ Could not read camera frame.")
        break

    # Mirror the camera like a normal selfie camera
    frame = cv2.flip(frame, 1)

    cv2.imshow("Camera Test", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
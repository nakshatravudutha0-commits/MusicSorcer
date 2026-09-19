// ============================================
// AI GESTURE MUSIC CONTROLLER
// MediaPipe + Local Python Controller
// Controls YouTube, Spotify, VLC, etc. on Windows
// ============================================


// ============================================
// MEDIAPIPE IMPORT
// ============================================

import {
    HandLandmarker,
    FilesetResolver
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/vision_bundle.mjs";


// ============================================
// HTML ELEMENTS
// ============================================

const video =
    document.getElementById("webcam");

const canvas =
    document.getElementById("canvas");

const ctx =
    canvas.getContext("2d");

const startButton =
    document.getElementById("startButton");

const statusText =
    document.getElementById("status");

const gestureText =
    document.getElementById("gesture");

const actionText =
    document.getElementById("action");

const cameraMessage =
    document.getElementById("camera-message");

const youtubeButton =
    document.getElementById("youtubeButton");

const spotifyButton =
    document.getElementById("spotifyButton");

const youtubeSection =
    document.getElementById("youtubeSection");

const spotifySection =
    document.getElementById("spotifySection");


// ============================================
// VARIABLES
// ============================================

let handLandmarker = null;

let running = false;

let lastVideoTime = -1;


// ============================================
// MUSIC SOURCE
// ============================================

let musicSource = "youtube";


// ============================================
// GESTURE CONTROL
// ============================================

let lastGesture = "NO HAND";

let lastActionTime = 0;

const ACTION_COOLDOWN = 1000;


// ============================================
// SWIPE CONTROL
// ============================================

let swipeStartX = null;

let lastSwipeTime = 0;

const SWIPE_DISTANCE = 0.20;

const SWIPE_COOLDOWN = 1000;


// ============================================
// PYTHON CONTROLLER
// ============================================

const CONTROLLER_URL =
    "http://127.0.0.1:5000/control";


// ============================================
// SEND COMMAND TO PYTHON
// ============================================

async function sendCommand(action) {

    try {

        const response =
            await fetch(
                CONTROLLER_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        action: action
                    })
                }
            );


        if (!response.ok) {

            throw new Error(
                "Python controller returned " +
                response.status
            );

        }


        const result =
            await response.json();


        console.log(
            "Computer controller:",
            result
        );


        if (result.success) {

            return true;

        }


        return false;

    }

    catch (error) {

        console.error(
            "Controller connection error:",
            error
        );


        actionText.textContent =
            "❌ Start Python controller";


        statusText.textContent =
            "Python controller is not connected.";


        return false;

    }

}


// ============================================
// LOAD MEDIAPIPE
// ============================================

async function loadHandLandmarker() {

    statusText.textContent =
        "Loading AI hand detection...";


    const vision =
        await FilesetResolver.forVisionTasks(

            "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm"

        );


    handLandmarker =
        await HandLandmarker.createFromOptions(

            vision,

            {

                baseOptions: {

                    modelAssetPath:
                        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

                },

                runningMode:
                    "VIDEO",

                numHands:
                    1,

                minHandDetectionConfidence:
                    0.5,

                minHandPresenceConfidence:
                    0.5,

                minTrackingConfidence:
                    0.5

            }

        );


    statusText.textContent =
        "AI model loaded.";

}


// ============================================
// START CAMERA
// ============================================

async function startCamera() {

    const stream =
        await navigator.mediaDevices.getUserMedia({

            video: {
                width: 640,
                height: 480
            },

            audio: false

        });


    video.srcObject =
        stream;


    await video.play();


    running =
        true;


    cameraMessage.style.display =
        "none";


    startButton.textContent =
        "🟢 Controller Running";


    statusText.textContent =
        "AI ready — show your hand.";


    predictWebcam();

}


// ============================================
// FINGER DETECTION
// ============================================

function fingerOpen(
    landmarks,
    tip,
    pip
) {

    return (
        landmarks[tip].y <
        landmarks[pip].y
    );

}


// ============================================
// GESTURE DETECTION
// ============================================

function detectGesture(landmarks) {

    const index =
        fingerOpen(
            landmarks,
            8,
            6
        );


    const middle =
        fingerOpen(
            landmarks,
            12,
            10
        );


    const ring =
        fingerOpen(
            landmarks,
            16,
            14
        );


    const pinky =
        fingerOpen(
            landmarks,
            20,
            18
        );


    const openCount =
        Number(index) +
        Number(middle) +
        Number(ring) +
        Number(pinky);


    // ========================================
    // PALM
    // ========================================

    if (openCount === 4) {

        return "PALM";

    }


    // ========================================
    // PEACE
    // ========================================

    if (
        index &&
        middle &&
        !ring &&
        !pinky
    ) {

        return "PEACE";

    }


    // ========================================
    // ONE
    // ========================================

    if (
        index &&
        !middle &&
        !ring &&
        !pinky
    ) {

        return "ONE";

    }


    // ========================================
    // CLOSED HAND
    // ========================================

    if (openCount === 0) {

        const thumbTip =
            landmarks[4];

        const thumbIP =
            landmarks[3];

        const wrist =
            landmarks[0];


        // THUMB UP

        if (
            thumbTip.y <
            thumbIP.y &&
            thumbTip.y <
            wrist.y - 0.04
        ) {

            return "THUMB_UP";

        }


        // THUMB DOWN

        if (
            thumbTip.y >
            thumbIP.y &&
            thumbTip.y >
            wrist.y + 0.04
        ) {

            return "THUMB_DOWN";

        }


        // FIST

        return "FIST";

    }


    return "UNKNOWN";

}


// ============================================
// DRAW HAND
// ============================================

function drawHand(landmarks) {

    canvas.width =
        video.videoWidth;

    canvas.height =
        video.videoHeight;


    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    const connections = [

        [0,1],
        [1,2],
        [2,3],
        [3,4],

        [0,5],
        [5,6],
        [6,7],
        [7,8],

        [5,9],
        [9,10],
        [10,11],
        [11,12],

        [9,13],
        [13,14],
        [14,15],
        [15,16],

        [13,17],
        [17,18],
        [18,19],
        [19,20],

        [0,17]

    ];


    ctx.strokeStyle =
        "#00ff88";

    ctx.lineWidth =
        3;


    for (
        const [a, b]
        of connections
    ) {

        const x1 =
            landmarks[a].x *
            canvas.width;

        const y1 =
            landmarks[a].y *
            canvas.height;

        const x2 =
            landmarks[b].x *
            canvas.width;

        const y2 =
            landmarks[b].y *
            canvas.height;


        ctx.beginPath();

        ctx.moveTo(
            x1,
            y1
        );

        ctx.lineTo(
            x2,
            y2
        );

        ctx.stroke();

    }


    ctx.fillStyle =
        "#00ff88";


    for (
        const point
        of landmarks
    ) {

        const x =
            point.x *
            canvas.width;

        const y =
            point.y *
            canvas.height;


        ctx.beginPath();

        ctx.arc(
            x,
            y,
            5,
            0,
            Math.PI * 2
        );

        ctx.fill();

    }

}


// ============================================
// MUSIC ACTIONS
// ============================================

async function playPause() {

    const success =
        await sendCommand(
            "play_pause"
        );


    if (success) {

        actionText.textContent =
            "▶️ / ⏸️ PLAY / PAUSE";

    }

}


async function mute() {

    const success =
        await sendCommand(
            "mute"
        );


    if (success) {

        actionText.textContent =
            "🔇 MUTE / UNMUTE";

    }

}


async function volumeUp() {

    const success =
        await sendCommand(
            "volume_up"
        );


    if (success) {

        actionText.textContent =
            "🔊 VOLUME UP";

    }

}


async function volumeDown() {

    const success =
        await sendCommand(
            "volume_down"
        );


    if (success) {

        actionText.textContent =
            "🔉 VOLUME DOWN";

    }

}


async function nextTrack() {

    const success =
        await sendCommand(
            "next"
        );


    if (success) {

        actionText.textContent =
            "⏭️ NEXT TRACK";

    }

}


async function previousTrack() {

    const success =
        await sendCommand(
            "previous"
        );


    if (success) {

        actionText.textContent =
            "⏮️ PREVIOUS TRACK";

    }

}


// ============================================
// PERFORM GESTURE ACTION
// ============================================

function performAction(gesture) {

    const now =
        performance.now();


    // Prevent repeated actions

    if (
        now - lastActionTime <
        ACTION_COOLDOWN
    ) {

        return;

    }


    // Don't repeatedly trigger
    // the same gesture

    if (
        gesture === lastGesture
    ) {

        return;

    }


    // Remember gesture

    lastGesture =
        gesture;


    // ========================================
    // PALM
    // ========================================

    if (
        gesture === "PALM"
    ) {

        playPause();

    }


    // ========================================
    // FIST
    // ========================================

    else if (
        gesture === "FIST"
    ) {

        mute();

    }


    // ========================================
    // THUMB UP
    // ========================================

    else if (
        gesture === "THUMB_UP"
    ) {

        volumeUp();

    }


    // ========================================
    // THUMB DOWN
    // ========================================

    else if (
        gesture === "THUMB_DOWN"
    ) {

        volumeDown();

    }


    else {

        return;

    }


    lastActionTime =
        now;

}


// ============================================
// SWIPE DETECTION
// ============================================

function detectSwipe(x) {

    const now =
        performance.now();


    if (
        now - lastSwipeTime <
        SWIPE_COOLDOWN
    ) {

        return null;

    }


    if (
        swipeStartX === null
    ) {

        swipeStartX =
            x;

        return null;

    }


    const distance =
        x -
        swipeStartX;


    // RIGHT

    if (
        distance >
        SWIPE_DISTANCE
    ) {

        swipeStartX =
            x;

        lastSwipeTime =
            now;

        return "RIGHT";

    }


    // LEFT

    if (
        distance <
        -SWIPE_DISTANCE
    ) {

        swipeStartX =
            x;

        lastSwipeTime =
            now;

        return "LEFT";

    }


    return null;

}


// ============================================
// MAIN AI LOOP
// ============================================

function predictWebcam() {

    if (!running) {

        return;

    }


    const now =
        performance.now();


    if (
        video.currentTime !==
        lastVideoTime
    ) {

        lastVideoTime =
            video.currentTime;


        const result =
            handLandmarker.detectForVideo(
                video,
                now
            );


        // ====================================
        // HAND FOUND
        // ====================================

        if (
            result.landmarks &&
            result.landmarks.length > 0
        ) {

            const landmarks =
                result.landmarks[0];


            // Draw landmarks

            drawHand(
                landmarks
            );


            // Detect gesture

            const gesture =
                detectGesture(
                    landmarks
                );


            // Display gesture

            gestureText.textContent =
                gesture;


            // Detect swipe

            const swipe =
                detectSwipe(
                    landmarks[0].x
                );


            if (
                swipe === "RIGHT"
            ) {

                nextTrack();

                lastActionTime =
                    performance.now();

            }


            else if (
                swipe === "LEFT"
            ) {

                previousTrack();

                lastActionTime =
                    performance.now();

            }


            else {

                performAction(
                    gesture
                );

            }

        }


        // ====================================
        // NO HAND
        // ====================================

        else {

            gestureText.textContent =
                "NO HAND";


            ctx.clearRect(
                0,
                0,
                canvas.width,
                canvas.height
            );


            swipeStartX =
                null;


            // This allows the same gesture
            // to be used again.

            lastGesture =
                "NO HAND";

        }

    }


    requestAnimationFrame(
        predictWebcam
    );

}


// ============================================
// START BUTTON
// ============================================

startButton.addEventListener(
    "click",
    async function () {

        if (running) {

            return;

        }


        startButton.disabled =
            true;


        try {

            await loadHandLandmarker();

            await startCamera();

        }

        catch (error) {

            console.error(
                error
            );


            statusText.textContent =
                "❌ " +
                error.message;


            startButton.disabled =
                false;

        }

    }
);


// ============================================
// MUSIC SOURCE BUTTONS
// ============================================

youtubeButton.addEventListener(
    "click",
    function () {

        musicSource =
            "youtube";


        youtubeButton.classList.add(
            "active"
        );


        spotifyButton.classList.remove(
            "active"
        );


        youtubeSection.style.display =
            "block";


        spotifySection.style.display =
            "none";


        actionText.textContent =
            "▶️ YouTube selected";


        statusText.textContent =
            "Play YouTube normally on your computer.";

    }
);


spotifyButton.addEventListener(
    "click",
    function () {

        musicSource =
            "spotify";


        spotifyButton.classList.add(
            "active"
        );


        youtubeButton.classList.remove(
            "active"
        );


        youtubeSection.style.display =
            "none";


        spotifySection.style.display =
            "block";


        actionText.textContent =
            "🎵 Spotify selected";


        statusText.textContent =
            "Play Spotify normally on your computer.";

    }
);


// ============================================
// INITIAL STATUS
// ============================================

console.log(
    "AI Gesture Music Controller loaded."
);

console.log(
    "Computer controller:",
    CONTROLLER_URL
);

const video = document.getElementById("camera");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

const peopleText = document.getElementById("people");
const vehiclesText = document.getElementById("vehicles");
const eventCount = document.getElementById("totalEvents");
const eventList = document.getElementById("eventList");

let stream = null;
let running = false;

const sleep = ms =>
    new Promise(resolve => setTimeout(resolve, ms));


async function startCamera() {

    try {

        stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        });

        video.srcObject = stream;

        await video.play();

        running = true;

        document.getElementById("systemStatus")
            .textContent = "Camera Active";

        processFrames();

    } catch (error) {

        alert("Camera permission required!");

        console.error(error);
    }
}


async function processFrames() {

    while (running) {

        if (video.readyState >= 2) {

            canvas.width = Math.min(video.videoWidth, 640);
            canvas.height = Math.round(
                canvas.width *
                video.videoHeight / video.videoWidth
            );

            context.drawImage(
                video,
                0,
                0,
                canvas.width,
                canvas.height
            );

            const blob = await new Promise(resolve => {
                canvas.toBlob(resolve, "image/jpeg", 0.7);
            });

            if (blob) {

                const formData = new FormData();

                formData.append("frame", blob, "frame.jpg");

                try {

                    const response = await fetch("/api/frame", {
                        method: "POST",
                        body: formData
                    });

                    const result = await response.json();

                    if (response.ok) {

                        peopleText.textContent = result.people;
                        vehiclesText.textContent = result.vehicles;

                    } else {

                        console.error(result.error);
                    }

                } catch (error) {

                    console.error("Backend connection error", error);
                }
            }
        }

        await sleep(800);
    }
}


function stopCamera() {

    running = false;

    if (stream) {

        stream.getTracks().forEach(track => track.stop());

        stream = null;
    }

    video.srcObject = null;

    document.getElementById("systemStatus")
        .textContent = "Camera Stopped";
}


async function loadEvents() {

    try {

        const response = await fetch("/api/events");

        const events = await response.json();

        eventCount.textContent = events.length;

        eventList.innerHTML = "";

        if (events.length === 0) {

            eventList.textContent = "No events detected.";

            return;
        }

        events.forEach(item => {

            const div = document.createElement("div");

            div.className = "event";

            div.textContent =
                item.event + " | " +
                item.camera + " | " +
                item.time;

            eventList.appendChild(div);
        });

    } catch (error) {

        console.error("Event loading error", error);
    }
}


async function checkStatus() {

    try {

        const response = await fetch("/api/status");

        const data = await response.json();

        document.getElementById("systemStatus")
            .textContent = data.status.toUpperCase();

    } catch {

        document.getElementById("systemStatus")
            .textContent = "Backend Offline";
    }
}


document.getElementById("startBtn")
    .addEventListener("click", startCamera);

document.getElementById("stopBtn")
    .addEventListener("click", stopCamera);


checkStatus();
loadEvents();

setInterval(loadEvents, 3000);

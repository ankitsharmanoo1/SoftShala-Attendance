
// Register the Service Worker with Auto-Update Handling
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/service-worker.js")
            .then((registration) => {
                console.log("Service Worker Registered!", registration);

                // Listen for updates and force reload when a new version is found
                registration.onupdatefound = () => {
                    const newWorker = registration.installing;
                    newWorker.onstatechange = () => {
                        if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
                            console.log("New update found! Reloading...");
                            window.location.reload();
                        }
                    };
                };
            })
            .catch((err) => console.log("Service Worker Registration Failed!", err));

        // Ensure updates are checked when the page loads
        navigator.serviceWorker.ready.then((registration) => {
            registration.update();
        });
    });
}

let deferredPrompt;

window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;

    const installButton = document.createElement("button");
    installButton.textContent = "Install App";
    installButton.style.cssText = `
        position: fixed; bottom: 20px; left: 50%;
        transform: translateX(-50%);
        background: #0288d1; color: white; border: none;
        padding: 10px 20px; border-radius: 5px;
        font-size: 16px; cursor: pointer;
        z-index: 1000;
    `;
    document.body.appendChild(installButton);

    installButton.addEventListener("click", () => {
        installButton.style.display = "none";
        deferredPrompt.prompt();

        deferredPrompt.userChoice.then(choiceResult => {
            if (choiceResult.outcome === "accepted") {
                console.log("User accepted A2HS prompt");
            } else {
                console.log("User dismissed A2HS prompt");
            }
            deferredPrompt = null;
        });
    });
});

window.addEventListener("appinstalled", () => {
    console.log("PWA Installed Successfully!");
});

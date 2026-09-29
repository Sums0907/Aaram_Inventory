const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
window.AARAM_CONFIG = {
    API_URL: isLocalhost ? "http://127.0.0.1:8100" : "https://api-inventory.aarambooks.cloud",
    IDENTITY_URL: "https://identity.aarambooks.cloud",
    IDENTITY_API_URL: "https://api-identity.aarambooks.cloud"
};

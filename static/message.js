const message = document.getElementById("message")
const sendButton = document.getElementById("send_button")



sendButton.addEventListener("click", () => {
    const msgVal = message.value
    if (msgVal.trim() !== "") {
        socket.emit("send_message", {"message": msgVal});
    }
})
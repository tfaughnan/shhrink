function copyUrlout() {
    console.log("function worked!");
    var copyText = document.getElementById("urlout");
    copyText.select();
    document.execCommand("copy");
    alert("Copied the text: " + copyText.value);
}


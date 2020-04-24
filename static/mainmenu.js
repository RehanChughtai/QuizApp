
function deleteAccount(){
    console.log("Delete Account?")
    if (confirm("Click 'Ok' to confirm account deletion!")) {
        console.log("Sending delete instruction.")
        window.location.href = 'deleteaccount'
      } else {
        console.log("Cancelled")
    }
}
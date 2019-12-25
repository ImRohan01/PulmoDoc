function displayQuestion(answer) {

  document.getElementById(answer + 'Question').style.display = "block";

  if (answer == "yes") { // hide the div that is not selected

    document.getElementById('noQuestion').style.display = "none";

  } else if (answer == "no") {

    document.getElementById('yesQuestion').style.display = "none";

  }
}

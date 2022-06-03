var setUpSubmitButton = function() {
  $("#agreement-form").on("submit", function() {
    var $spinner = $("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>");
    $("#submit-button").prepend($spinner).prop("disabled", true);
  });
};

$(function() {
  setUpSubmitButton();
});

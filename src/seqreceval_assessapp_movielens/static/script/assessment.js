var setUpTooltip = function() {
  $("[data-bs-toggle='tooltip']").tooltip();
};

var setUpProgressBar = function() {
  var total_count = parseInt($("#info-total-count").text());
  var countAssessments = function() {
    var isEachAssessed = $(".card-assessment-form").map(function() {
      var movieId = $(this).data("movieId");
      var isUserWatchMovieAssessed = $("input[name='user-watch-movie-" + movieId + "-radio']").is(":checked");
      var isAssessorWatchMovieAssessed = $("input[name='assessor-watch-movie-" + movieId + "-radio']").is(":checked");

      return isUserWatchMovieAssessed && isAssessorWatchMovieAssessed;
    }).get();

    return isEachAssessed.reduce(function(acc, flag) { return acc + flag; }, 0);
  };

  $(".card-assessment-form input[type='radio']").on("change", function() {
    var assessed_count = countAssessments();
    var progress = Math.round(100 * assessed_count / total_count);

    $("#info-assessed-count").text(assessed_count);
    $("#info-progress-bar").attr("aria-valuenow", assessed_count).css("width", progress + "%");
  });
};

var setUpSkipButton = function() {
  $("#skip-button").on("click", function() {
    var $spinner = $("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>");
    $(this).prepend($spinner);

    var $formButtons = $("#assessor-form button");
    $formButtons.prop("disabled", true);

    var data = {
      user_id: parseInt($("#user-id").val()),
      condition_id: parseInt($("#condition-id").val()),
      started_at: $("#started-at").val()
    };
    var settings = {
      contentType: "application/json",
      data: JSON.stringify(data),
      dataType: "json",
      method: "POST",
      url: $(this).attr("formaction")
    };

    $.ajax(settings)
      .done(function(data, textStatus, jqXHR) {
        location.href = data.redirect;
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
        var data = jqXHR.responseJSON;
        var messageHTML = (
          "判定データのスキップ処理に失敗しました。<br>" +
          "スキップボタンを再度クリックすればデータが変わらないかをご確認ください。<br>" +
          "それでも問題が解決しない場合は、下記のエラーメッセージとともにご連絡いただけると大変助かります。"
        );
        var detailText = (
          "type: " + data.type + "\n" +
          "message: " + data.message
        );
        var $modal = $("#error-modal");
        $modal.find(".error-modal-message").html(messageHTML);
        $modal.find(".error-modal-detail").text(detailText);
        bootstrap.Modal.getOrCreateInstance($modal).show();

        $formButtons.prop("disabled", false);
        $spinner.remove();
      });

    return false;
  });
};

var setUpCompleteButton = function() {
  var startDate = new Date();
  var collectResponses = function() {
    var getCheckedValue = function(radioSelector) {
      if (!$(radioSelector).is(":checked")) {
        return null;
      }

      var numberStr = $(radioSelector + ":checked").val()

      return parseInt(numberStr);
    };

    return $(".card-assessment-form").map(function() {
      var movieId = $(this).data("movieId");
      var userWatchMovie = getCheckedValue("input[name='user-watch-movie-" + movieId + "-radio']");
      var assessorWatchMovie = getCheckedValue("input[name='assessor-watch-movie-" + movieId + "-radio']");

      return {
        movie_id: movieId,
        user_watch_movie: userWatchMovie,
        assessor_watch_movie: assessorWatchMovie
      };
    }).get();
  };

  $("#assessor-form").on("submit", function() {
    var submitDate = new Date();
    var elapsedTime = submitDate.getTime() - startDate.getTime();

    if (elapsedTime < 60 * 1000) {
      var message = (
        "判定開始から時間があまり経過していません。\n" +
        "まじめに判定しないことが判明した場合、報酬をお支払いできません。\n" +
        "現在の判定結果をこのまま送信してもいいですか？\n"
      );
      var confirmed = window.confirm(message);

      if (!confirmed) {
        return false;
      }
    }

    var $spinner = $("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>");
    $("#complete-button").prepend($spinner);

    var $formButtons = $("#assessor-form button");
    $formButtons.prop("disabled", true);

    var data = {
      user_id: parseInt($("#user-id").val()),
      condition_id: parseInt($("#condition-id").val()),
      started_at: $("#started-at").val(),
      responses: collectResponses()
    };

    var settings = {
      contentType: "application/json",
      data: JSON.stringify(data),
      dataType: "json",
      method: "POST",
      url: $(this).attr("action")
    };

    $.ajax(settings)
      .done(function(data, textStatus, jqXHR) {
        location.href = data.redirect;
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
        var data = jqXHR.responseJSON;
        var messageHTML = (
          "判定データの送信に失敗しました。<br>" +
          "全て判定済みであるかや、完了ボタンを再度クリックすれば成功しないかをご確認ください。<br>" +
          "それでも問題が解決しない場合は、下記のエラーメッセージとともにご連絡いただけると大変助かります。"
        );
        var detailText = (
          "type: " + data.type + "\n" +
          "message: " + data.message
        );
        var $modal = $("#error-modal");
        $modal.find(".error-modal-message").html(messageHTML);
        $modal.find(".error-modal-detail").text(detailText);
        bootstrap.Modal.getOrCreateInstance($modal).show();

        $formButtons.prop("disabled", false);
        $spinner.remove();
      });

    return false;
  });
};

var setUpItemContainer = function() {
  var fitToViewport = function() {
    var $target = $(".fit-to-viewport-item-container");
    var viewportHeight = $(window).height();
    var headerHeight = $("header").height();
    var otherMainHeight = (function() {
      var infoSectionHeight = $(".info-section").height();
      var itemSectionOffsetY = $(".item-section").offset().top;
      var targetOffsetY = $target.offset().top;
      var targetRelativeOffsetY = targetOffsetY - itemSectionOffsetY;
      var targetOuterHeight = 3 * parseInt($target.css("padding-top"));

      return infoSectionHeight + targetRelativeOffsetY + targetOuterHeight;
    })();
    var footerHeight = $("footer").height();
    var newTargetHeight = viewportHeight - headerHeight - otherMainHeight - footerHeight;

    if (newTargetHeight > 0) {
      $target.height(newTargetHeight);
    }
  };

  fitToViewport();
  $(window).on("resize", fitToViewport);
};

var showManual = function() {
  var isRookie = !!parseInt($("#is-rookie").val());

  if (isRookie) {
    var $manual = $("#manual-modal");
    bootstrap.Modal.getOrCreateInstance($manual).show();
  }
};

$(function() {
  setUpTooltip();
  setUpProgressBar();
  setUpSkipButton();
  setUpCompleteButton();
  setUpItemContainer();
  showManual();
});

function ajaxifyVideoUploadForm(modal) {
  $('form.video-upload', modal.body).on('submit', function () {
    var formdata = new FormData(this);

    if (!$('#id_video-chooser-upload-title', modal.body).val()) {
      var li = $('#id_video-chooser-upload-title', modal.body).closest('li');
      if (!li.hasClass('error')) {
        li.addClass('error');
        $('#id_video-chooser-upload-title', modal.body)
          .closest('.field-content')
          .append(
            '<p class="error-message"><span>This field is required.</span></p>',
          );
      }
      setTimeout(cancelSpinner, 500);
    } else {
      $.ajax({
        url: this.action,
        data: formdata,
        processData: false,
        contentType: false,
        type: 'POST',
        dataType: 'text',
        success: modal.loadResponseText,
        error: function (response, textStatus, errorThrown) {
          var message =
            jsonData.error_message +
            '<br />' +
            errorThrown +
            ' - ' +
            response.status;
          $('#upload').append(
            '<div class="help-block help-critical">' +
              '<strong>' +
              jsonData.error_label +
              ': </strong>' +
              message +
              '</div>',
          );
        },
      });
    }

    return false;
  });

  var fileWidget = $('#id_video-chooser-upload-file', modal.body);
  fileWidget.on('change', function () {
    var titleWidget = $('#id_video-chooser-upload-title', modal.body);
    var title = titleWidget.val();
    // do not override a title that already exists (from manual editing or previous upload)
    if (title === '') {
      // The file widget value example: `C:\fakepath\video.jpg`
      var parts = fileWidget.val().split('\\');
      var filename = parts[parts.length - 1];

      // allow event handler to override filename (used for title) & provide maxLength as int to event
      var maxTitleLength =
        parseInt(titleWidget.attr('maxLength') || '0', 10) || null;
      var data = { title: filename.replace(/\.[^.]+$/, '') };

      // allow an event handler to customise data or call event.preventDefault to stop any title pre-filling
      var form = fileWidget.closest('form').get(0);
      var event = form.dispatchEvent(
        new CustomEvent('wagtail:videos-upload', {
          bubbles: true,
          cancelable: true,
          detail: {
            data: data,
            filename: filename,
            maxTitleLength: maxTitleLength,
          },
        }),
      );

      if (!event) return; // do not set a title if event.preventDefault(); is called by handler

      titleWidget.val(data.title);
    }
  });
}

IMAGE_CHOOSER_MODAL_ONLOAD_HANDLERS = {
  chooser: function (modal, jsonData) {
    var searchForm = $('form.video-search', modal.body);
    var searchUrl = searchForm.attr('action');

    function ajaxifyLinks(context) {
      $('.listing a', context).on('click', function () {
        modal.loadUrl(this.href);
        return false;
      });

      $('.pagination a', context).on('click', function () {
        fetchResults(this.href);
        return false;
      });
    }
    var request;

    function fetchResults(url, requestData) {
      var opts = {
        url: url,
        success: function (data, status) {
          request = null;
          $('#video-results').html(data);
          ajaxifyLinks($('#video-results'));
        },
        error: function () {
          request = null;
        },
      };
      if (requestData) {
        opts.data = requestData;
      }
      request = $.ajax(opts);
    }

    function search() {
      fetchResults(searchUrl, searchForm.serialize());
      return false;
    }

    ajaxifyLinks(modal.body);
    ajaxifyVideoUploadForm(modal);

    $('form.video-search', modal.body).on('submit', search);

    $('#id_q').on('input', function () {
      if (request) {
        request.abort();
      }
      clearTimeout($.data(this, 'timer'));
      var wait = setTimeout(search, 200);
      $(this).data('timer', wait);
    });
    $('#collection_chooser_collection_id').on('change', search);
    $('a.suggested-tag').on('click', function () {
      $('#id_q').val('');
      fetchResults(searchUrl, {
        tag: $(this).text(),
        collection_id: $('#collection_chooser_collection_id').val(),
      });
      return false;
    });
  },
  video_chosen: function (modal, jsonData) {
    modal.respond('videoChosen', jsonData.result);
    modal.close();
  },
  reshow_upload_form: function (modal, jsonData) {
    $('#upload', modal.body).replaceWith(jsonData.htmlFragment);
    ajaxifyVideoUploadForm(modal);
  },
  select_format: function (modal) {
    var decorativeVideo = document.querySelector(
      '#id_video-chooser-insertion-video_is_decorative',
    );
    var altText = document.querySelector(
      '#id_video-chooser-insertion-alt_text',
    );
    var altTextLabel = document.querySelector(
      '[for="id_video-chooser-insertion-alt_text"]',
    );

    if (decorativeVideo.checked) {
      disableAltText();
    } else {
      enableAltText();
    }

    decorativeVideo.addEventListener('change', function (event) {
      if (event.target.checked) {
        disableAltText();
      } else {
        enableAltText();
      }
    });

    function disableAltText() {
      altText.setAttribute('disabled', 'disabled');
      altTextLabel.classList.remove('required');
    }

    function enableAltText() {
      altText.removeAttribute('disabled');
      altTextLabel.classList.add('required');
    }

    $('form', modal.body).on('submit', function () {
      $.post(this.action, $(this).serialize(), modal.loadResponseText, 'text');

      return false;
    });
  },
};

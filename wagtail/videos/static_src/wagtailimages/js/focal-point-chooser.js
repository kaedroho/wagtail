var jcropapi;

function setupJcrop(video, original, focalPointOriginal, fields) {
  video.Jcrop(
    {
      trueSize: [original.width, original.height],
      bgColor: 'rgb(192, 192, 192)',
      onSelect: function (box) {
        var x = Math.floor((box.x + box.x2) / 2);
        var y = Math.floor((box.y + box.y2) / 2);
        var w = Math.floor(box.w);
        var h = Math.floor(box.h);

        fields.x.val(x);
        fields.y.val(y);
        fields.width.val(w);
        fields.height.val(h);
      },

      onRelease: function () {
        fields.x.val(focalPointOriginal.x);
        fields.y.val(focalPointOriginal.y);
        fields.width.val(focalPointOriginal.width);
        fields.height.val(focalPointOriginal.height);
      },
    },
    function () {
      jcropapi = this;

      // Set alt="" on the video so its src is not read out loud to screen reader users.
      var $holderVideo = $('img', jcropapi.ui.holder);
      $holderVideo.attr('alt', '');
    },
  );
}

$(function () {
  var $chooser = $('div.focal-point-chooser');
  var $indicator = $('.current-focal-point-indicator', $chooser);
  var $video = $('img', $chooser);

  var original = {
    width: $video.data('originalWidth'),
    height: $video.data('originalHeight'),
  };

  var focalPointOriginal = {
    x: $chooser.data('focalPointX'),
    y: $chooser.data('focalPointY'),
    width: $chooser.data('focalPointWidth'),
    height: $chooser.data('focalPointHeight'),
  };

  var fields = {
    x: $('input.focal_point_x'),
    y: $('input.focal_point_y'),
    width: $('input.focal_point_width'),
    height: $('input.focal_point_height'),
  };

  var left = focalPointOriginal.x - focalPointOriginal.width / 2;
  var top = focalPointOriginal.y - focalPointOriginal.height / 2;
  var width = focalPointOriginal.width;
  var height = focalPointOriginal.height;

  $indicator.css('left', (left * 100) / original.width + '%');
  $indicator.css('top', (top * 100) / original.height + '%');
  $indicator.css('width', (width * 100) / original.width + '%');
  $indicator.css('height', (height * 100) / original.height + '%');

  var params = [$video, original, focalPointOriginal, fields];

  setupJcrop.apply(this, params);

  $(window).on(
    'resize',
    $.debounce(300, function () {
      // jcrop doesn't support responsive videos so to cater for resizing the browser
      // we have to destroy() it, which doesn't properly do it,
      // so destroy it some more, then re-apply it
      jcropapi.destroy();
      $video.removeAttr('style');
      $('.jcrop-holder').remove();
      setupJcrop.apply(this, params);
    }),
  );

  $('.remove-focal-point').on('click', function () {
    jcropapi.destroy();
    $video.removeAttr('style');
    $('.jcrop-holder').remove();
    $('.current-focal-point-indicator').remove();
    fields.x.val('');
    fields.y.val('');
    fields.width.val('');
    fields.height.val('');
    setupJcrop.apply(this, params);
  });
});

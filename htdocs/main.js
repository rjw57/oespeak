$(document).ready(function() {
  //var speak_root = 'http://localhost:8000/';
  var speak_root = '../oespeak-service';
  var audio = $('#audio').get(0);

  $('button').button();
  
  $('#play').click(function() {
    var input_text = $('#text').val();

    // normalise the text
    input_text = input_text.replace(/aeq/g, 'ǣ');
    input_text = input_text.replace(/aq/g, 'ā');
    input_text = input_text.replace(/eq/g, 'ē');
    input_text = input_text.replace(/iq/g, 'ī');
    input_text = input_text.replace(/oq/g, 'ō');
    input_text = input_text.replace(/uq/g, 'ū');

    input_text = input_text.replace(/Aeq/g, 'Ǣ');
    input_text = input_text.replace(/Aq/g, 'Ā');
    input_text = input_text.replace(/Eq/g, 'Ē');
    input_text = input_text.replace(/Iq/g, 'Ī');
    input_text = input_text.replace(/Oq/g, 'Ō');
    input_text = input_text.replace(/Uq/g, 'Ū');

    input_text = input_text.replace(/th/g, 'þ');
    input_text = input_text.replace(/Th/g, 'Þ');

    $('button').button('disable');
    $('button').button('option', { label: 'Ðreodiende' });

    audio.src = speak_root + '?' + $.param({ text: input_text });
    audio.play();

    $(audio).bind('loadeddata', function() {
      $('button').button('option', { label: 'Cweðende' });
    });

    $(audio).bind('ended', function() {
      $('button').button('enable');
      $('button').button('option', { label: 'Cweðan' });
    });

    return false;
  });

  console.log(audio);
});

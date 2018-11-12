$(function (){
  var $conversation = $('#conversation');
  var $chat = $('#chat');
  var cblegend = '<fieldset style="background-color:lavender; color: indigo; font-family:verdana;"> <legend style="color: indigo; font-family:impact;"><b>CHATBOT</b></legend><b><i>';
  var uslegend = '<fieldset style="background-color:#bbff99; color: darkgreen; font-family:verdana;"> <legend style="color: darkgreen; font-family:impact;"><b>USER</b></legend><b><i>';

  var usrinp = document.getElementById("chat");
  usrinp.addEventListener("keyup", function(event) {
      event.preventDefault();
      if (event.keyCode === 13) {
        document.getElementById('submit').click();
      }
  });

  $('#submit').on('click', function() {
    var curr = new Date();
    var ts = curr.toISOString();

    var uchat = {
        "messages": [{
          "type": "type1",
          "unstructured": {
            "id": "01",
            "text": $chat.val(),
            "timestamp": ts}
          }]
    };

    $conversation.append(uslegend+$chat.val()+'</fieldset></b></i>');

    $.ajax({
      type:'POST',
      url:'https://vc3wygxqsc.execute-api.us-east-2.amazonaws.com/testing',
      data: JSON.stringify(uchat),
      crossDomain: true,
      dataType: 'json',
      contentType:'application/json',
      headers:{'x-api-key': 'k9Vat2xLdrAmy9e7jrO63ina8Y7E1Ts2U7M1Tjpj'},
      success: function(chatresp){
        $conversation.append(cblegend+chatresp.messages[0].unstructured.text+'</b></i></fieldset>');
      },
      error: function(){
        alert('Error! No response!');
      }
    });
    $('#chat').val('');
  });
});

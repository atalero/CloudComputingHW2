$(function (){
  var $conversation = $('#conversation');
  var $chat = $('#chat');

  $('#submit').on('click', function() {
      var uchat = {
        "messages": [{
          "type": "type1",
          "unstructured": {
            "id": "01",
            "text": $chat.val(),
            "timestamp": "2018-10-10T12:59:06.495694"}
          }]
        };

    $conversation.append('<li>USER:    '+uchat.messages[0].unstructured.text+'</li>');

    $.ajax({
      type:'POST',
      url:'https://vc3wygxqsc.execute-api.us-east-2.amazonaws.com/testing',
      data: JSON.stringify(uchat),
      crossDomain: true,
      dataType: 'json',
      contentType:'application/json',
      headers:{'x-api-key': 'k9Vat2xLdrAmy9e7jrO63ina8Y7E1Ts2U7M1Tjpj'},
      success: function(chatresp){
        $conversation.append('<li>CHATBOT: '+chatresp.messages[0].unstructured.text+'</li>');
      },
      error: function(){
        alert('Error! No response!');
      }
    });
  });
});

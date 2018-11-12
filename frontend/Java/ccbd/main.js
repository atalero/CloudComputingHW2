$(function (){
  var $conversation = $('#conversation');
  var $chat = $('#chat');
  var cblegend = '<fieldset style="background-color:lavender; color: indigo; font-family:verdana;"> <legend style="color: indigo; font-family:impact;"><b>CHATBOT</b></legend><b><i>';
  var uslegend = '<fieldset style="background-color:#bbff99; color: darkgreen; font-family:verdana;"> <legend style="color: darkgreen; font-family:impact;"><b>USER</b></legend><b><i>';

// code for extracting query parameter values from url courtesy of:
// https://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript

  var qs = (function(a) {
    if (a == "") return {};
    var b = {};
    for (var i = 0; i < a.length; ++i)
    {
      var p=a[i].split('=', 2);
      if (p.length == 1)
        b[p[0]] = "";
      else
        b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
    }
    return b;
  })(window.location.search.substr(1).split('&'));
// code for extracting query parameter values from url ends here

  function godown() {
//    var scrollingElement = (document.scrollingElement || document.body);
    var scrollingElement = (document.scrollingElement || document.body);
    scrollingElement.scrollTop = scrollingElement.scrollHeight;
  }


  $('#submit').on('click', function() {
    var curr = new Date();
    var ts = curr.toISOString();

    var uchat = {
        "messages": [{
          "type": "type1",
          "unstructured": {
            "id": qs["code"],
            "text": $chat.val(),
            "timestamp": ts}
          }]
    };

    $conversation.append(uslegend+$chat.val()+'</fieldset></b></i>');
    godown();

    $.ajax({
      type:'POST',
      url:'https://fpptgifvnc.execute-api.us-east-1.amazonaws.com/Development',
      data: JSON.stringify(uchat),
      crossDomain: true,
      dataType: 'json',
      contentType:'application/json',
      headers:{'x-api-key': 'm0G11EN2Ao5AZZDEDEkDC5R3hZGkh4qx1Ku3DmUv'},
      success: function(chatresp){
        $conversation.append(cblegend+chatresp.messages[0].unstructured.text+'</b></i></fieldset>');
        godown();
      },
      error: function(){
        alert('Error! No response!');
      }
    });
    $('#chat').val('');
  });
});

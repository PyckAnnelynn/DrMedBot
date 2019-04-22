// /static/custom.js

const chat_container = $('.chat-container');
const input_message_form = $('#input_message');

function loading(){
	$('#botface').remove();
	new_message = $('#new_message');
	new_message.css('margin-left', '35px');
	new_message.removeAttr('id');
	chat_container.append('<img id="botface" src="static/img/botface.png">');
	chat_container.append(`<div class="chat-message bot-message" id="loading"> <div class="dots"><span class="dot dot-1"></span><span class="dot dot-2"></span><span class="dot dot-3"></span></div> </div>`);

}

function submit_message(message) {

	$.post( "/send_message", {message: message}, handle_response);

	function handle_response(data) {

	    // append the bot repsonse to the div
		$('#botface').remove();

		// remove the loading indicator
	    $("#loading").remove();

	    // make make older suggestions unclickable
		$('.clickable').removeClass("clickable");

	    // add bot response to chat window
		if(data.hasOwnProperty("queryResult") && data.queryResult.hasOwnProperty("fulfillmentText")){
			chat_container.append('<img id="botface" src="static/img/botface.png">');
			chat_container.append(`<div class="chat-message bot-message" id="new_message"> ${data.queryResult.fulfillmentText}</div>`);
		}
		else{
			chat_container.append('<img id="botface" src="static/img/botface.png">');
			var text = "I didn't understand that."
			if(language === "nl"){text = "Dat versta ik niet."}
			chat_container.append(`<div class="chat-message bot-message" id="new_message"> ${text} </div>`);
		}

        // append suggestions
        if( data.hasOwnProperty("queryResult") && data.queryResult.hasOwnProperty("webhookPayload") && data.queryResult.webhookPayload.hasOwnProperty("google") && data.queryResult.webhookPayload.google.hasOwnProperty("richResponse") && data.queryResult.webhookPayload.google.richResponse.hasOwnProperty("suggestions"))
        {
        	// hide input field
			input_message_form.css("display", "none");

            // create parent div
            chat_container.append(`<div class="suggestions" id="new_div"></div>`);
            new_div = $('#new_div');
                // add child divs for each suggestion
		        for(let index in data.queryResult.webhookPayload.google.richResponse.suggestions)
    		    {
    		        new_div.append(`
            			<div class="suggestion clickable"> ${data.queryResult.webhookPayload.google.richResponse.suggestions[index].title}</div>
            		`)
                }
            // div isn't new anymore so remove the "new div" id
            new_div.removeAttr('id');
        }
        else
		{
			// show input field
			input_message_form.css("display", "block");
		}

        // scroll to newest chat-message
        chat_container.scrollTop(chat_container.prop('scrollHeight') - chat_container.height());

	}
}

$('#target').on('submit', function(e){
    // prevent submitting the form and refreshing the page
	e.preventDefault();

	// get message from form
	const input_message = input_message_form.val();

	// return if the user does not enter any text
	if (!input_message)
	{
		return
	}

    // append the user message to the chat window
	chat_container.append(`<div class="chat-message human-message">${input_message}</div>`);

	// loading
	loading();

	// scroll to newest chat-message
    chat_container.scrollTop(chat_container.prop('scrollHeight') - chat_container.height());

	// clear the text input
	input_message_form.val('');

	// send the message
	submit_message(input_message);
});


$(document).on('click', '.clickable' , function() {
    const choice = $(this).html();

    // append the user message to the chat window
	chat_container.append(`<div class="chat-message human-message">${choice}</div>`);

	// loading
	loading();

	// scroll to newest chat-message
    chat_container.scrollTop(chat_container.prop('scrollHeight') - chat_container.height());

	// clear the text input
	input_message_form.val('');

	// send the message
	submit_message(choice);

	//put autofocus back on input field
	input_message_form.focus();

});

submit_message("Hello Dr. MedBot");
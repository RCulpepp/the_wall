$(document).ready(function(){
	$('button').click(function(){
		var parent = $(this).parent();
		$(parent).slideUp();

		//for buttons
		if ($(this).attr('id') == 'register-button'){
			console.log('It worked');
			$('#register').slideDown();
		} else {
			$('#login').slideDown();
		}
		$("#error").html("")

	});
		//For A tags
	$('.back').click(function(){
		var parent = $(this).parent();
		var grandparent = $(parent).parent();
		console.log(grandparent.attr('id'));
		$(grandparent).slideUp();
		if ($(grandparent).attr('id') == 'login'){
			$('#register').slideDown();
		} else if ($(grandparent).attr('id') == 'register'){
			$('#login').slideDown();
		}
	});

	
});
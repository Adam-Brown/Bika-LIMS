(function( $ ) {

function openCCBrowser(event){
	event.preventDefault();
	contact_uid = $('#primary_contact').attr('value');
	cc_uids = $('#cc_uids').attr('value');
	window.open('ar_select_cc?hide_uids=' + contact_uid + '&selected_uids=' + cc_uids,
		'ar_select_cc','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=600,height=550');
}

$(document).ready(function(){

	_ = window.jsi18n;

	$('#open_cc_browser').click(openCCBrowser);

});
}(jQuery));

$(function() {
	var path = window.location.pathname;
	if (path != '/home') {
		$('#menu a').each(function() {
			if ($(this).attr('href') == path) {
				var list = $(this).closest('.list-group');
				if (list.hasClass('list-group-child')) {
					list.addClass('in');
				}

				$(this).addClass('active-link');
				return false;
			}
		})
	}
});
odoo.define('stem_frontend_theme.setting_menu', function (require) {

	var indexSelected = Math.round($('[name=bd_year] option').length - 10);
	$('[name=bd_year] option')[indexSelected].selected = true;

	

});

var table;
var selected = [];

$(document).ready(function() {
	table = $('#studentModal table').DataTable({
        'serverSide': true,
		'ajax': '/home/get_student',
		'ordering': false,
		'lengthMenu': [[5, 10, 25, -1], [5, 10, 25, "All"]],
		'columns': [
            { 'data': "action", 'className': 'action' },
            { 'data': "email" },
            { 'data': "name" }
        ]
	});

	//----------------------------------------
	var datapost = [];

	$('.forum-post-list .post-name').each(function(){
	    datapost.push(this.innerText.trim());
	});
		
	var questions = new Bloodhound({
		datumTokenizer: Bloodhound.tokenizers.whitespace,
		queryTokenizer: Bloodhound.tokenizers.whitespace,
		local: datapost
	});

	questions.initialize();

	$('.name-question').typeahead({
		hint: false,
		highlight: true,
		minLength: 1
		},
		{
		source: questions,
		templates: {
			empty: '<a href="#" class="jsabutton" onclick="addQuestionClick()" data-toggle="modal" data-target="#addQuestion"><button class="btn btn-default">Đặt câu hỏi</button></a>',
		    suggestion: function(el){
		    	var id = el.split("-")[0];
		    	var html = '<div class="tt-suggestion tt-selectable">';
		    	html += '<a href="/forum/2/question/'+ id +'">' + el +'</a>';
		    	html += '</div>';
		    	return html;
		    }
		}
	});

	//------------------------------------------

	if ($('[name=bd_year] option').length) {
		var indexSelected = Math.round($('[name=bd_year] option').length - 10);
		$('[name=bd_year] option')[indexSelected].selected = true;
	}

});

function addQuestionClick(){
	$('#questionname').val($('.name-question').val());
}

function selectChildren() {
	$('#studentModal table tbody tr').each(function() {
		var id = table.row( this ).id();

		if ($(this).find('input[type="checkbox"]').is(':checked')) {
			$(this).find('input[type="checkbox"]').attr('checked', false);

			if (selected.indexOf(id) === -1) {
				var tr = '<tr data-id="' + id + '">';
				tr += '<td>' + $(this).find('td:eq(1)').html() + '</td>';
				tr += '<td>' + $(this).find('td:eq(2)').html() + '</td>';
				tr += '<td class="action"><i class="fa fa-fw fa-trash-o" onclick="deleteChild(this)"/></td></tr>';
				$('#parentModal table tbody').append(tr);
				selected.push(id);
			}
		}
	});
	$('#studentModal').modal('hide');
}

function deleteChild(elm) {
	var tr = $(elm).closest('tr');
	var id = tr.data('id');
	tr.remove();

	var index = selected.indexOf(Number(id));
	selected.splice(index, 1);
};

function submitParent(elm) {
	var studentIds = [];

	$('#parentModal table tbody tr').each(function() {
		var id = $(this).data('id');
		if (id) {
			studentIds.push(id);
		}
	})

	$('#parentModal input[name="student_ids"]').val(studentIds.join(','));
}

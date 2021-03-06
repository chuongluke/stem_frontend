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

	$('.x-name-question').typeahead({
		hint: false,
		highlight: true,
		minLength: 1
		},
		{
		source: questions,
		templates: {
			empty: '<form method="POST" action="/ask"><input type="hidden" name="questionname"/><input type="hidden" name="questioncontent"/><div class="jsabutton"><button type="submit" class="btn btn-danger" onclick="askQuestionClick(this)">Đặt câu hỏi nhanh</button><a href="#" onclick="addQuestionClick()" data-toggle="modal" data-target="#addQuestion" style="margin-left: 5px;"><button class="btn btn-default">Đặt câu hỏi</button></a></div></form>',
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


	if($('.list-attachment') != undefined){
		$.ajax({
	        url: '/web/binary/render_attachment',
	        type: 'POST',
	        data: {},
	        cache: false,
	        processData: false,  
	        contentType: false,
	        success: function(result){
	            showResult(result);
	        },
	        error: function(result){
	        	showResult(result);
	        },
	    });
	}
	

});

function showResult(result){
	var resz = JSON.parse(result);
	if(resz['attach'] != undefined){
		$('.ufile_attachment').val('');
		$('#title_file').val('');
		$('#content_file').val('');
		$('.note-editable').empty();
		for(var i = 0; i < resz["attach"].length; i++){
			var icon = '<i class="fa fa-picture-o text-info fa-2 MR10" aria-hidden="true"></i>'
			if((resz["attach"][i].mimetype).includes('text')){
				icon = '<i class="fa fa-file-text-o text-success fa-2 MR10" aria-hidden="true"></i>'
			}
			if((resz["attach"][i].mimetype).includes('application')){
				icon = '<i class="fa fa-file-pdf-o text-warning fa-2 MR10" aria-hidden="true"></i>'
			}
			var html = '<li class="list-group-item" style="padding-left: 20px;">';
				html += icon;
				html += resz["attach"][i].name;
				html += '<i class="fa fa-trash pull-right text-danger" onclick="removeAttachment('+ resz["attach"][i].id +')" title="Xóa" aria-hidden="true"></i></li>';
			$('.list-attachment').append(html);
		}
	}
}


function uploadAttachment(){
	var targets = document.getElementById('ufile').files;
	var title_file = $('#title_file').val();
	var content_file = $('#content_file').val();
	if(title_file == ""){
		$('.msg-att').append('<p class="alert alert-danger">Bạn chưa nhập tiêu đề tập tin.</p>');
	}
    if (targets.length > 0) {
        
        for(var i = 0; i < targets.length; i++ ){
            var querydata = new FormData();
            querydata.append('callback', 'oe_fileupload_attachment');
            querydata.append('ufile', targets[i]);
            querydata.append('model', 'res.partner');
            querydata.append('id', '0');
            querydata.append('multi', 'true');
            querydata.append('title', title_file);
            querydata.append('content', content_file);
            $.ajax({
                url: '/web/binary/upload_attachment',
                type: 'POST',
                data: querydata,
                cache: false,
                processData: false,  
                contentType: false,
                success: function(result){
                    uploadResult(result);
                },
                error: function(result){
                	uploadResult(result);
                },
            });

        }
    }else{
    	$('.msg-att').append('<p class="alert alert-danger">Bạn chưa chọn tệp tin nào.</p>');
    }
}

function removeAttachment(id){
	var deleted = confirm("Bạn có chắc chắn muốn xóa tập tin này không ?");
	if (deleted) {
		$('i[onclick="removeAttachment('+id+')"]').parent().remove();
		var querydata = new FormData();
	    querydata.append('id', id);
		$.ajax({
	        url: '/web/binary/delete_attachment',
	        type: 'POST',
	        data: querydata,
	        cache: false,
	        processData: false,  
	        contentType: false,
	        success: function(result){
	            deleteResult(result);
	        },
	        error: function(result){
	        	deleteResult(result);
	        },
	    });
    }
}

function deleteResult(result){
	$('.msg-att').empty();
	var res = JSON.parse(result);
	if(res['error'] == undefined){
		$('.msg-att').append('<p class="alert alert-success">' + res["success"] + '</p>');
	}else{
		$('.msg-att').append('<p class="alert alert-danger">' + res["error"] + '</p>');
	}
}

function uploadResult(result){
	$('.msg-att').empty();
	var res = JSON.parse(result);
	if(res['error'] == undefined){
		showResult(result);
		$('.msg-att').append('<p class="alert alert-success">' + res["success"] + '</p>');
	}else{
		$('.msg-att').append('<p class="alert alert-danger">' + res["error"] + '</p>');
	}
}

function cancelButton(caller){
	$(caller).parent().parent().next().children().css('display', 'block');
	$(caller).parent().parent().css('height','');
	var parents = $(caller).parent().parent();
	var value = $(caller).parent().prev().attr('data-custom-value');
	
	//console.log(value);
	parents.text(value);
}


function saveButton(caller){
	var value = $(caller).parent().prev().val().trim();
	var classname = $(caller).parent().prev().attr('name').trim();
	var editfield = $(caller).parent().parent().prev().text().trim().toLowerCase();
	/*console.log(value);
	console.log(classname);
	console.log(editfield);*/


	$.ajax({
        url: "/home/session/change_profile",
        data:{
        	"value": value,
        	"model": classname.split('-')[0],
        	"fields": classname.split('-')[1],
        	"editfield": editfield
        },
        type: "POST",
        dataType: 'json',
        traditional: true,
        success: function(result){
        	editResult(caller, result);
		},
        error: function(result){
        	editResult(caller, result);
        }

    });
}

function editResult(caller, result){
	$('.msg-info').empty();
	if(result.error == undefined){
		$(caller).parent().parent().next().children().css('display', 'block');
		$(caller).parent().parent().css('height','');
		var parents = $(caller).parent().parent();
		var values = result.values;
		if(values == 'male'){
			values = 'Nam';
		}
		if(values == 'female'){
			values = 'Nữ';
		}
		parents.text(values);
		$('.msg-info').append('<p class="alert alert-success">' + result.success + '</p>');
	}else{
		$('.msg-info').append('<p class="alert alert-danger">' + result.error + '</p>');
	}
}

function editButton(caller){
	$(caller).parent().prev().css('height', '80px');
	var value = $(caller).parent().prev().text();
	var classname = $(caller).parent().prev().attr('class');
	//console.log(classname);
	$(caller).parent().prev().text('');
	if(classname.includes('name')  || classname.includes('street') || classname.includes('login') || classname.includes('phone')){
		$(caller).parent().prev().append(
			"<input type='text' required='required' data-custom-value='"+value.trim()+
			"' name='"+ classname +"' class='form-control' value='" + value.trim() + 
			"'/><div style='margin-top: 8px;'><button class='btn btn-primary' onclick='saveButton(this)'>Save</button><button onclick='cancelButton(this)' class='btn btn-danger btn-cancel' style='margin-left: 5px;'>Cancel</button></div>");
	}
	if(classname.includes('birthday')){
		var d = new Date(value.trim());
		var birthday = [d.getDate(), (d.getMonth() + 1), d.getFullYear()].join('/');
		$(caller).parent().prev().append(
			"<input type='text' data-toggle='datepicker' required='required' data-custom-value='"+value.trim()+
			"' name='"+ classname +"' class='form-control' value='" + birthday + 
			"'/><div style='margin-top: 8px;'><button class='btn btn-primary' onclick='saveButton(this)'>Save</button><button onclick='cancelButton(this)' class='btn btn-danger btn-cancel' style='margin-left: 5px;'>Cancel</button></div>");
		$('input[data-toggle="datepicker"]').datepicker({
		  	format: 'dd/mm/yyyy',
		  	autoPick: true,
		  	months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
		  	days: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
		});
	}
	if(classname.includes('gender')){
		var optionMale = '';
		var optionFemale = '';
		if(value.trim().includes('Nữ')){
			optionFemale = "selected";
		}else{
			optionMale = 'selected';
		}
		$(caller).parent().prev().append(
			"<select required='required' data-custom-value='"+value.trim()+
			"' name='"+ classname +"' class='form-control'><option value='male' "+ optionMale +
			">Nam</option><option value='female' "+ optionFemale +
			">Nữ</option></select><div style='margin-top: 8px;'><button class='btn btn-primary' onclick='saveButton(this)'>Save</button><button onclick='cancelButton(this)' class='btn btn-danger btn-cancel' style='margin-left: 5px;'>Cancel</button></div>");
	}

	$(caller).css('display', 'none');
}


function changePassword(){
	var old_pwd = $('input[name=old_pwd]').val();
	var new_password = $('input[name=new_password]').val();
	var confirm_pwd = $('input[name=confirm_pwd]').val();
	
	$.ajax({
        url: "/home/session/change_password",
        data:{
        	"old_password": old_pwd,
        	"new_password": new_password,
        	"confirm_password": confirm_pwd
        },
        type: "POST",
        dataType: 'json',
        traditional: true,
        success: function(result){
        	findItem(result);
		},
        error: function(result){
        	findItem(result);
        }

    });

}

function findItem(result){
	$('.msg').empty();
	if(result.error == undefined){
		$("input[type='password']").val('');
		$('.msg').append('<p class="alert alert-success">' + result.success + '</p>');
	}else{
		$('.msg').append('<p class="alert alert-danger">' + result.error + '</p>');
	}
}

function addQuestionClick(){
	$('#questionname').val($('.x-name-question').val());
}

function askQuestionClick(elm){
	var question = $('.x-name-question').val();
	$(elm).parent().parent().find('input[name="questionname"]').val(question);
	$(elm).parent().parent().find('input[name="questioncontent"]').val(question);
	

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

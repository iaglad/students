function initMultidel()
{
    let mc = false;
    $('.multidel input[type="checkbox"]').click(function(event) {
        $('input').each(function(i, el) {
            if ($(el).attr('type') === 'checkbox') {
                mc = $(el).is(':checked') || mc;
            }
        });
        $('#multidel_button').prop('disabled', !mc);
        mc = false;
    });
}

function initJournal()
{
    var indicator = $('#ajax-progress-indicator');
    $('.day-box input[type="checkbox"]').click(function(event)
    {
        var box = $(this);
        $.ajax(box.data('url'),
            {
                'type': 'POST',
                'async': true,
                'dataType': 'json',
                'data':
                    {
                        'pk': box.data('student-id'),
                        'date': box.data('date'),
                        'present': box.is(':checked') ? '1': '0',
                        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                    },
                'beforeSend': function(xhr, settings)
                    {
                        indicator.show();
                    },
                'error': function(xhr, status, error)
                    {
                        alert(error);
                        indicator.hide();
                    },
                'success': function(data, status, xhr)
                    {
                        indicator.hide();
                    }
            });
    });
}

function initGroupSelector()
{
    $('#group-selector select').change(function(event)
        {
            var group = $(this).val();
            if (group)
            {
                Cookies.set('current_group', group, {'path': '/', 'expires': 365});
            } else
            {
                Cookies.remove('current_group', {'path': '/'});
            }
            location.reload(true);
            return true;
        }
    )
}

function initDateFields()
{
    $('input.dateinput').flatpickr(
        {
            dateFormat: 'd.m.Y'
        }
    );
}

function initEditStudentPage()
{
    $('a.student-edit-form-link, input.student-edit-form-link').click(function(event)
    {
        event.preventDefault();
        var link = $(this);
        $.ajax(
            {
                'url': link.attr('href'),
                'dataType': 'html',
                'type': 'get',
                'success': function(data, status, xhr)
                {
                    if (status != 'success')
                    {
                        alert('Error on server');
                        return false;
                    }
                    var modal = $('#myModal'),
                        html = $(data),
                        form = html.find('#content-column form');
                    modal.find('modal-title').html(html.find('#content-column h2').text());
                    modal.find('.modal-body').html(form);
                    initEditStudentForm(form, modal);
                    modal.modal('show');
                },
                'error': function()
                {
                    alert('Error on server');
                    return false;
                }
            }
        );
        return false;
    });
}

$(document).ready(function()
{
    initJournal();
    initGroupSelector();
    initDateFields();
    initEditStudentPage();
    initMultidel();
})

function initEditStudentForm(form, modal)
{
    initDateFields();
    form.find('input[name="cancel_button"]').click(function(event)
    {
        modal.modal('hide');
        return false;
    });
    form.ajaxForm(
        {
            'dataType': 'html',
            'error': function()
                {
                    alert('Error on server');
                    return false;
                },
            'success': function(data, status, xhr)
            {
                var html = $(data), newform = html.find('#content-column form .student-form');
                modal.find('.modal-body').html(html.find('.alert'));
                if (newform.length > 0)
                {
                    modal.find('.modal-body').append(newform);
                    initEditStudentForm(newform, modal);
                } else
                {
                    setTimeout(function(){location.reload(true);}, 500)
                }
            }
        }
    );
}

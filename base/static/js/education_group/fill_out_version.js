    $("#btn_fill_out_version").on( "click", function() {
            $('#btn_copy_transition_version').attr('disabled', 'disabled');

            $.ajax({
              method: "POST",
              url: "{% url 'available_versions_for_copy' offer.acronym offer.academic_year.year %}",
              success: function(data){
                $("#div_originals_to_copy").empty();
                jQuery.each(data, function (index){
                    var key = data[index]['id'];
                    var val = data[index]['label'];
                    $('#div_originals_to_copy').append('<input id="" class="radio_original_to_copy" name="radio_original_to_copy" type="radio" value="' + key + '" /> ' + val + '<br />');
                })
              }
            })
        });

    $(document).on('click', '.radio_original_to_copy', function(){
        $('#btn_copy_transition_version').removeAttr('disabled');
    });

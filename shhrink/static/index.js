function copyUrlout() {
    var copyText = document.getElementById('urlout');
    copyText.select();
    document.execCommand('copy');
}

function fmtBytes(bytes) {
    if (bytes == 0) {
        return '0 B';
    }

    var sizes = ['B', 'KB', 'MB', 'GB'];
    var decimals = 2;
    var k = 1000;
    var i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
}

$(function() {
    $('#filein-delete').hide();
    $('input:file[id=filein]').on('change', function() {
        var fileBytes = this.files[0].size;
        if (fileBytes > maxFileBytes) {
            $('input:file[id=filein]').val('');
            alert(`${fmtBytes(fileBytes)} file exceeds limit (${fmtBytes(maxFileBytes)})`);
        } else {
            $('#urlin').prop( 'value', 'file: ' + $(this).val().split('\\').pop() );
            $('#urlin').prop( 'readonly', true );
            $('#filein-upload').hide();
            $('#filein-delete').show();
        }
    });
});

$(function() {
    $('#filein-delete').on('click', function() {
        $('input:file[id=filein]').val('');
        $('#urlin').prop( 'value', '' );
        $('#urlin').prop( 'readonly', false );
        $('#filein-delete').hide();
        $('#filein-upload').show();
    });
});

